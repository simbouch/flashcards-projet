"""
Flashcard generation logic.
"""
from .model import LLMModel
from .logger_config import logger
from .mlflow_tracker import llm_tracker
from typing import List, Dict, Any, Optional
import os
import time

class FlashcardGenerator:
    """
    Service for generating flashcards from text.
    """

    def __init__(self):
        """Initialize the flashcard generator with the LLM model."""
        # Load model name from environment variable or use default
        model_name = os.getenv("MODEL_NAME")

        # Initialize the LLM model
        try:
            self.model = LLMModel(model_name)
            logger.info("FlashcardGenerator initialized successfully")
        except Exception as e:
            logger.exception(f"Failed to initialize FlashcardGenerator: {e}")
            raise

    async def generate_flashcards(self, text: str, num_cards: int = 5) -> Dict[str, Any]:
        """
        Generate flashcards from text.

        Args:
            text: The text to generate flashcards from.
            num_cards: The number of flashcards to generate.

        Returns:
            A dictionary with the generated flashcards and metadata.
        """
        start_time = time.time()
        logger.info(f"Generating {num_cards} flashcards from {len(text)} characters of text")

        # Use MLflow tracking context
        with llm_tracker.track_generation_operation("flashcard_generation"):
            try:
                # Log model metadata
                llm_tracker.log_model_metadata(
                    model_name=self.model.model_name,
                    model_size="560M"  # For bloom-560m
                )

                # Generate flashcards using the LLM model
                flashcards = self.model.generate_flashcards(text, num_cards)

                # Calculate processing time
                processing_time = time.time() - start_time

                # Log generation metrics to MLflow
                llm_tracker.log_generation_metrics(
                    input_text_length=len(text),
                    num_cards_requested=num_cards,
                    num_cards_generated=len(flashcards),
                    processing_time=processing_time,
                    model_name=self.model.model_name
                )

                # Log quality metrics
                llm_tracker.log_quality_metrics(flashcards)

                # Prepare response
                response = {
                    "flashcards": flashcards,
                    "metadata": {
                        "text_length": len(text),
                        "requested_cards": num_cards,
                        "generated_cards": len(flashcards),
                        "processing_time_seconds": round(processing_time, 2)
                    }
                }

                logger.info(f"Generated {len(flashcards)} flashcards in {processing_time:.2f} seconds")
                return response

            except Exception as e:
                logger.exception(f"Error generating flashcards: {e}")

                # Log error metrics
                llm_tracker.log_error_metrics("generation_failed", str(e))

                # Return error response
                return {
                    "error": str(e),
                    "flashcards": [],
                    "metadata": {
                        "text_length": len(text),
                        "requested_cards": num_cards,
                        "generated_cards": 0,
                        "processing_time_seconds": round(time.time() - start_time, 2)
                    }
                }

    async def generate_flashcards_from_chunks(self, chunks: List[str], num_cards: int = 5) -> Dict[str, Any]:
        """
        Generate flashcards from multiple text chunks.

        Args:
            chunks: List of text chunks to generate flashcards from.
            num_cards: The total number of flashcards to generate.

        Returns:
            A dictionary with the generated flashcards and metadata.
        """
        start_time = time.time()
        total_length = sum(len(chunk) for chunk in chunks)
        logger.info(f"Generating {num_cards} flashcards from {len(chunks)} chunks ({total_length} total characters)")

        try:
            all_flashcards = []

            # Calculate cards per chunk, distributing evenly
            cards_per_chunk = [num_cards // len(chunks)] * len(chunks)
            # Distribute any remainder
            for i in range(num_cards % len(chunks)):
                cards_per_chunk[i] += 1

            # Process each chunk
            for i, chunk in enumerate(chunks):
                if cards_per_chunk[i] > 0:
                    chunk_cards = self.model.generate_flashcards(chunk, cards_per_chunk[i])
                    all_flashcards.extend(chunk_cards)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Prepare response
            response = {
                "flashcards": all_flashcards,
                "metadata": {
                    "chunks": len(chunks),
                    "total_text_length": total_length,
                    "requested_cards": num_cards,
                    "generated_cards": len(all_flashcards),
                    "processing_time_seconds": round(processing_time, 2)
                }
            }

            logger.info(f"Generated {len(all_flashcards)} flashcards from {len(chunks)} chunks in {processing_time:.2f} seconds")
            return response

        except Exception as e:
            logger.exception(f"Error generating flashcards from chunks: {e}")
            # Return error response
            return {
                "error": str(e),
                "flashcards": [],
                "metadata": {
                    "chunks": len(chunks),
                    "total_text_length": total_length,
                    "requested_cards": num_cards,
                    "generated_cards": 0,
                    "processing_time_seconds": round(time.time() - start_time, 2)
                }
            }
