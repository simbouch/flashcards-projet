"""
LLM model interface for flashcard generation.
"""
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from .logger_config import logger
from typing import List, Dict, Any, Optional, Tuple
import nltk
from nltk.tokenize import sent_tokenize
import time

# Download NLTK data for sentence tokenization
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab')
    except Exception:
        # Fallback to older punkt if punkt_tab is not available
        try:
            nltk.download('punkt')
        except Exception as e:
            logger.warning(f"Failed to download NLTK data: {e}")
            # We'll handle this gracefully in the code

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

    def _load_model(self):
        """Load the model and tokenizer."""
        try:
            start_time = time.time()

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            # Load model with appropriate configuration for memory efficiency
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
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
        sentences = sent_tokenize(text)

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

        logger.info(f"Generated {len(all_flashcards)} flashcards")
        return all_flashcards

    def _generate_from_chunk(self, chunk: str, num_cards: int) -> List[Dict[str, str]]:
        """
        Generate flashcards from a single text chunk.

        Args:
            chunk: The text chunk.
            num_cards: Number of cards to generate from this chunk.

        Returns:
            List of flashcard dictionaries.
        """
        # Construct a prompt for the model
        prompt = f"""
        Texte: {chunk}

        Génère {num_cards} cartes mémoire (question/réponse) basées sur le texte ci-dessus.
        Format:
        Q: [Question]
        R: [Réponse]
        """

        try:
            # Generate text
            outputs = self.generator(
                prompt,
                max_length=len(self.tokenizer.encode(prompt)) + 500,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )

            generated_text = outputs[0]['generated_text']

            # Extract Q/A pairs from the generated text
            return self._parse_qa_pairs(generated_text)

        except Exception as e:
            logger.exception(f"Error generating flashcards: {e}")
            # Return a default card indicating the error
            return [{"question": "Erreur de génération", "answer": f"Une erreur s'est produite: {str(e)}"}]

    def _parse_qa_pairs(self, text: str) -> List[Dict[str, str]]:
        """
        Parse question-answer pairs from generated text.

        Args:
            text: The generated text containing Q/A pairs.

        Returns:
            List of flashcard dictionaries.
        """
        flashcards = []

        # Split the text by lines
        lines = text.split('\n')

        current_question = None

        for line in lines:
            line = line.strip()

            # Check for question line
            if line.startswith('Q:'):
                current_question = line[2:].strip()

            # Check for answer line if we have a question
            elif line.startswith('R:') and current_question:
                answer = line[2:].strip()

                # Add the pair to our flashcards
                if current_question and answer:
                    flashcards.append({
                        "question": current_question,
                        "answer": answer
                    })
                    current_question = None

        return flashcards

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
