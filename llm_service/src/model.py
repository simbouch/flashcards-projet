"""
LLM model interface for flashcard generation.
"""
import os
import torch
import re
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from .logger_config import logger
from typing import List, Dict, Any, Optional, Tuple
import nltk
from nltk.tokenize import sent_tokenize
import time
import zipfile

# NOTE: We intentionally do *not* call `nltk.download()` at runtime.
# In Docker/CI environments this can hang (network/DNS restrictions) and makes
# benchmarks non-deterministic. We already handle missing/corrupted punkt in the
# `sent_tokenize` call-site by falling back to `_fallback_sentence_split`.


def _fallback_sentence_split(text: str) -> List[str]:
    """Fallback sentence splitter when NLTK punkt isn't available."""
    # Insert line breaks after sentence end punctuation, then split.
    normalized = re.sub(r"([.!?])\s+", r"\1\n", text.strip())
    parts = [p.strip() for p in normalized.splitlines() if p.strip()]
    return parts or ([text.strip()] if text.strip() else [])


def parse_qa_pairs(text: str) -> List[Dict[str, str]]:
    """Parse question/answer pairs from generated text.

    Supports common formats (French/English), multi-line answers,
    and provides a non-empty fallback when parsing fails.
    """

    def _strip_leading_markers(line: str) -> str:
        # e.g. "1. Q:", "- Q:", "• R:"...
        return re.sub(r"^\s*[-*•\d\.)\]]+\s*", "", line).strip()

    q_prefixes = ("Q:", "Question:")
    a_prefixes = ("R:", "Réponse:", "Reponse:", "A:", "Answer:")

    lines = [ln.strip() for ln in text.splitlines()]

    flashcards: List[Dict[str, str]] = []
    current_q: Optional[str] = None
    current_a_lines: List[str] = []

    def _flush():
        nonlocal current_q, current_a_lines
        if current_q and current_a_lines:
            answer = " ".join([x for x in current_a_lines if x]).strip()
            if answer:
                flashcards.append({"question": current_q.strip(), "answer": answer})
        current_q = None
        current_a_lines = []

    for raw in lines:
        if not raw:
            continue

        line = _strip_leading_markers(raw)

        # Inline format: "Q: ... R: ..."
        if any(line.startswith(p) for p in q_prefixes) and any(ap in line for ap in a_prefixes):
            # flush previous pair if any
            _flush()
            # split at the first answer prefix occurrence
            q_part = line
            a_part = ""
            for ap in a_prefixes:
                idx = q_part.find(ap)
                if idx != -1 and idx > 0:
                    a_part = q_part[idx + len(ap):].strip()
                    q_part = q_part[:idx].strip()
                    break
            # remove Q prefix
            for qp in q_prefixes:
                if q_part.startswith(qp):
                    q_part = q_part[len(qp):].strip()
                    break
            if q_part and a_part:
                flashcards.append({"question": q_part, "answer": a_part})
            continue

        if any(line.startswith(p) for p in q_prefixes):
            _flush()
            for qp in q_prefixes:
                if line.startswith(qp):
                    current_q = line[len(qp):].strip()
                    break
            continue

        if current_q and any(line.startswith(p) for p in a_prefixes):
            # start answer collection
            for ap in a_prefixes:
                if line.startswith(ap):
                    current_a_lines = [line[len(ap):].strip()]
                    break
            continue

        # Continuation lines for an answer (until next Q:)
        if current_q and current_a_lines:
            current_a_lines.append(line)

    _flush()

    if flashcards:
        return flashcards

    # Fallback: return a single card so the pipeline stays functional.
    excerpt = " ".join([ln for ln in lines if ln]).strip()
    excerpt = (excerpt[:600] + "…") if len(excerpt) > 600 else excerpt
    if not excerpt:
        excerpt = "(Aucun contenu généré)"
    logger.warning("Unable to parse Q/A pairs from model output; returning fallback flashcard")
    return [{"question": "Carte générée (format non standard)", "answer": excerpt}]


class LLMModel:
    """
    Interface for the language model used to generate flashcards.
    This class is designed to be extensible for future fine-tuning.
    """

    def __init__(self, model_name: str = None):
        """
        Initialize the LLM model.

        Args:
            model_name: The name or path of the model to load.
                        If None, uses the MODEL_NAME environment variable
                        or falls back to a default model.
        """
        self.model_name = model_name or os.getenv("MODEL_NAME", "bigscience/bloom-560m")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(f"Initializing LLM model: {self.model_name} on {self.device}")

        # Load tokenizer and model
        self.tokenizer = None
        self.model = None
        self.generator = None
        self._load_model()

    @staticmethod
    def _normalize_question(q: str) -> str:
        return " ".join((q or "").strip().lower().split())

    @classmethod
    def _postprocess_cards(cls, cards: List[Dict[str, Any]], *, limit: int) -> List[Dict[str, str]]:
        """Filter + de-duplicate cards and cap to `limit`.

        This makes outputs comparable across models (some models over-generate or repeat).
        """
        out: List[Dict[str, str]] = []
        seen: set[str] = set()

        for c in cards or []:
            q = str((c or {}).get("question", "") or "").strip()
            a = str((c or {}).get("answer", "") or "").strip()

            # Keep thresholds aligned with benchmark validity heuristics.
            if len(q) < 5 or len(a) < 3:
                continue

            key = cls._normalize_question(q)
            if not key or key in seen:
                continue

            seen.add(key)
            out.append({"question": q, "answer": a})

            if limit and len(out) >= int(limit):
                break

        # If everything got filtered out, keep at least one non-empty card if present.
        if not out:
            for c in cards or []:
                q = str((c or {}).get("question", "") or "").strip()
                a = str((c or {}).get("answer", "") or "").strip()
                if q and a:
                    return [{"question": q, "answer": a}]

        return out

    def _build_prompt(self, *, chunk: str, num_cards: int, avoid_questions: Optional[List[str]] = None) -> str:
        """Build a prompt. Uses chat templates when available (instruct/chat models)."""
        avoid_questions = avoid_questions or []
        avoid_block = ""
        if avoid_questions:
            avoid_qs = "\n".join(f"- {q}" for q in avoid_questions[:12] if str(q).strip())
            if avoid_qs.strip():
                avoid_block = (
                    "\n\nÉvite de répéter ces questions déjà proposées :\n" + avoid_qs + "\n"
                )

        user_content = (
            f"TEXTE:\n{chunk}\n\n"
            f"Génère exactement {int(num_cards)} cartes mémoire (question/réponse) basées sur le TEXTE."
            "\nRéponds uniquement avec les cartes, sans titre, sans explication."
            "\nFormat STRICT (une carte = 2 lignes) :"
            "\nQ: <question>"
            "\nR: <réponse>"
            "\nContraintes : questions courtes et distinctes; réponses factuelles."
            + avoid_block
        )

        # Prefer chat templates when the tokenizer supports it.
        try:
            if getattr(self.tokenizer, "apply_chat_template", None) and getattr(self.tokenizer, "chat_template", None):
                messages = [
                    {
                        "role": "system",
                        "content": "Tu es un assistant pédagogique. Tu produis des cartes mémoire utiles et non répétitives.",
                    },
                    {"role": "user", "content": user_content},
                ]
                return self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
        except Exception as e:
            logger.debug(f"Chat template not used ({type(e).__name__}: {e}); falling back to plain prompt")

        return user_content

    def _load_model(self):
        """Load the model and tokenizer."""
        try:
            start_time = time.time()

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            # Load model with appropriate configuration for memory efficiency
            cpu_dtype_name = os.getenv("LLM_CPU_DTYPE", "float32").strip().lower()
            cpu_dtype_map = {
                "float32": torch.float32,
                "fp32": torch.float32,
                "float16": torch.float16,
                "fp16": torch.float16,
                "bfloat16": torch.bfloat16,
                "bf16": torch.bfloat16,
            }
            cpu_dtype = cpu_dtype_map.get(cpu_dtype_name, torch.float32)

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else cpu_dtype,
                low_cpu_mem_usage=True,
                device_map="auto" if self.device == "cuda" else None
            )

            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )

            elapsed_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {elapsed_time:.2f} seconds")

        except Exception as e:
            logger.exception(f"Failed to load model: {e}")
            raise

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess the text before generating flashcards.

        Args:
            text: The text to preprocess.

        Returns:
            The preprocessed text.
        """
        # Basic preprocessing: remove extra whitespace
        text = " ".join(text.split())
        return text

    def chunk_text(self, text: str, max_chunk_size: int = 500) -> List[str]:
        """
        Split text into manageable chunks for processing.

        Args:
            text: The text to chunk.
            max_chunk_size: Maximum number of characters per chunk.

        Returns:
            List of text chunks.
        """
        # Split text into sentences
        try:
            sentences = sent_tokenize(text)
        except (LookupError, zipfile.BadZipFile, OSError) as e:
            logger.warning(f"NLTK punkt data missing ({e}); using fallback sentence splitter")
            sentences = _fallback_sentence_split(text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # If adding this sentence would exceed max_chunk_size,
            # save the current chunk and start a new one
            if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence

        # Add the last chunk if it's not empty
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks

    def generate_flashcards(self, text: str, num_cards: int = 5) -> List[Dict[str, str]]:
        """
        Generate flashcards from text.

        Args:
            text: The text to generate flashcards from.
            num_cards: The number of flashcards to generate.

        Returns:
            A list of dictionaries with 'question' and 'answer' keys.
        """
        logger.info(f"Generating {num_cards} flashcards from text ({len(text)} chars)")

        # Preprocess the text
        text = self.preprocess_text(text)

        # Split text into chunks if it's too long
        chunks = self.chunk_text(text)

        # Calculate how many cards to generate per chunk
        cards_per_chunk = [num_cards // len(chunks)] * len(chunks)
        # Distribute any remainder
        for i in range(num_cards % len(chunks)):
            cards_per_chunk[i] += 1

        all_flashcards = []

        for i, chunk in enumerate(chunks):
            cards_to_generate = cards_per_chunk[i]
            if cards_to_generate == 0:
                continue

            # Generate flashcards for this chunk
            chunk_cards = self._generate_from_chunk(chunk, cards_to_generate)
            all_flashcards.extend(chunk_cards)

        final_cards = self._postprocess_cards(all_flashcards, limit=int(num_cards))
        logger.info(f"Generated {len(final_cards)} flashcards (requested={num_cards}, raw={len(all_flashcards)})")
        return final_cards

    def _generate_from_chunk(self, chunk: str, num_cards: int) -> List[Dict[str, str]]:
        """
        Generate flashcards from a single text chunk.

        Args:
            chunk: The text chunk.
            num_cards: Number of cards to generate from this chunk.

        Returns:
            List of flashcard dictionaries.
        """
        try:
            # Some small models under-generate or repeat. We do a small bounded retry loop
            # to try to reach the requested count, then we cap/dedupe.
            max_attempts = int(os.getenv("LLM_CHUNK_GEN_ATTEMPTS", "3"))
            collected: List[Dict[str, Any]] = []

            # Bound the amount of generation; using max_length based on prompt size can
            # result in very long generations (and timeouts) on CPU.
            gen_kwargs = {
                "max_new_tokens": min(128 * max(1, int(num_cards)), 512),
                "num_return_sequences": 1,
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
                "top_p": float(os.getenv("LLM_TOP_P", "0.9")),
                "do_sample": True,
                "repetition_penalty": float(os.getenv("LLM_REPETITION_PENALTY", "1.15")),
                "return_full_text": False,
            }
            eos_id = getattr(self.tokenizer, "eos_token_id", None)
            if eos_id is not None:
                gen_kwargs["eos_token_id"] = eos_id
                if getattr(self.tokenizer, "pad_token_id", None) is None:
                    gen_kwargs["pad_token_id"] = eos_id

            for attempt in range(max(1, max_attempts)):
                remaining = int(num_cards) - len(self._postprocess_cards(collected, limit=int(num_cards)))
                if remaining <= 0:
                    break

                avoid_qs = [c.get("question", "") for c in self._postprocess_cards(collected, limit=int(num_cards))]
                prompt = self._build_prompt(chunk=chunk, num_cards=remaining, avoid_questions=avoid_qs)

                # Slightly increase randomness on retries to escape repetition.
                if attempt >= 1:
                    gen_kwargs["temperature"] = min(1.0, float(gen_kwargs["temperature"]) + 0.2)

                outputs = self.generator(prompt, **gen_kwargs)
                generated_text = outputs[0]["generated_text"]
                collected.extend(parse_qa_pairs(generated_text))

            return self._postprocess_cards(collected, limit=int(num_cards))

        except Exception as e:
            logger.exception(f"Error generating flashcards: {e}")
            # Return a default card indicating the error
            return [{"question": "Erreur de génération", "answer": f"Une erreur s'est produite: {str(e)}"}]

    # NOTE: parsing is implemented as a module-level function `parse_qa_pairs`
    # so it can be unit-tested without loading the model.

    def save_model(self, path: str):
        """
        Save the model for future use or fine-tuning.

        Args:
            path: The path to save the model to.
        """
        if self.model and self.tokenizer:
            try:
                logger.info(f"Saving model to {path}")
                self.model.save_pretrained(path)
                self.tokenizer.save_pretrained(path)
                logger.info("Model saved successfully")
            except Exception as e:
                logger.exception(f"Failed to save model: {e}")
                raise
        else:
            logger.error("Cannot save model: model or tokenizer not initialized")
            raise ValueError("Model or tokenizer not initialized")

    def fine_tune(self, training_data: List[Dict[str, str]], epochs: int = 3):
        """
        Fine-tune the model on flashcard data.
        This is a placeholder for future implementation.

        Args:
            training_data: List of dictionaries with 'text', 'question', and 'answer' keys.
            epochs: Number of training epochs.
        """
        logger.info(f"Fine-tuning requested with {len(training_data)} examples for {epochs} epochs")
        logger.warning("Fine-tuning not yet implemented")
        # This would be implemented in the future
        pass
