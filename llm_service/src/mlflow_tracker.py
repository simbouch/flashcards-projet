"""
MLflow tracking for LLM service performance and generation metrics.
"""
import os
import time
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from .logger_config import logger

# Try to import MLflow, make it optional
try:
    import mlflow
    import mlflow.transformers
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not available. LLM tracking will be disabled.")

class LLMMLflowTracker:
    """MLflow tracker for LLM operations and performance metrics."""

    def __init__(self):
        """Initialize MLflow tracker with LLM-specific configuration."""
        if not MLFLOW_AVAILABLE:
            logger.info("MLflow tracking disabled - MLflow not available")
            return

        try:
            # Set MLflow tracking URI (can be overridden by environment variable)
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
            mlflow.set_tracking_uri(tracking_uri)

            # Set experiment name
            experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "llm_service_tracking")
            mlflow.set_experiment(experiment_name)
            logger.info(f"MLflow experiment set to: {experiment_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize MLflow: {e}")

    @contextmanager
    def track_generation_operation(self, operation_type: str = "flashcard_generation"):
        """
        Context manager for tracking LLM generation operations.

        Args:
            operation_type: Type of generation operation
        """
        if not MLFLOW_AVAILABLE:
            # If MLflow is not available, just yield without tracking
            yield self
            return

        start_time = time.time()
        mlflow_run_started = False

        try:
            # Try to start MLflow run
            mlflow.start_run()
            mlflow_run_started = True

            # Log operation metadata
            mlflow.log_param("operation_type", operation_type)
            mlflow.log_param("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))

            yield self

        except Exception as e:
            logger.warning(f"MLflow tracking error: {e}")
            yield self

        finally:
            if mlflow_run_started:
                try:
                    # Log total processing time
                    processing_time = time.time() - start_time
                    mlflow.log_metric("processing_time_seconds", processing_time)
                    mlflow.end_run()
                except Exception as e:
                    logger.warning(f"Failed to finalize MLflow run: {e}")

    def log_generation_metrics(self, 
                             input_text_length: int,
                             num_cards_requested: int,
                             num_cards_generated: int,
                             processing_time: float,
                             model_name: str = None,
                             temperature: float = None,
                             max_tokens: int = None):
        """
        Log flashcard generation metrics.

        Args:
            input_text_length: Length of input text
            num_cards_requested: Number of cards requested
            num_cards_generated: Number of cards actually generated
            processing_time: Time taken for generation
            model_name: Name of the model used
            temperature: Generation temperature
            max_tokens: Maximum tokens for generation
        """
        if not MLFLOW_AVAILABLE:
            return

        try:
            # Log metrics
            mlflow.log_metric("input_text_length", input_text_length)
            mlflow.log_metric("cards_requested", num_cards_requested)
            mlflow.log_metric("cards_generated", num_cards_generated)
            mlflow.log_metric("processing_time_seconds", processing_time)
            mlflow.log_metric("generation_success_rate", num_cards_generated / max(num_cards_requested, 1))
            mlflow.log_metric("cards_per_second", num_cards_generated / max(processing_time, 0.001))

            # Log parameters
            if model_name:
                mlflow.log_param("model_name", model_name)
            if temperature is not None:
                mlflow.log_param("temperature", temperature)
            if max_tokens is not None:
                mlflow.log_param("max_tokens", max_tokens)

        except Exception as e:
            logger.warning(f"Failed to log generation metrics: {e}")

    def log_quality_metrics(self, 
                           cards: List[Dict[str, str]],
                           quality_scores: Optional[List[float]] = None,
                           user_rating: Optional[float] = None):
        """
        Log quality metrics for generated flashcards.

        Args:
            cards: List of generated flashcards
            quality_scores: Optional quality scores for each card
            user_rating: Optional user rating (1-5)
        """
        if not MLFLOW_AVAILABLE:
            return

        try:
            # Calculate basic quality metrics
            total_cards = len(cards)
            avg_question_length = sum(len(card.get("question", "")) for card in cards) / max(total_cards, 1)
            avg_answer_length = sum(len(card.get("answer", "")) for card in cards) / max(total_cards, 1)

            # Log quality metrics
            mlflow.log_metric("total_cards_generated", total_cards)
            mlflow.log_metric("avg_question_length", avg_question_length)
            mlflow.log_metric("avg_answer_length", avg_answer_length)

            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                mlflow.log_metric("avg_quality_score", avg_quality)
                mlflow.log_metric("min_quality_score", min(quality_scores))
                mlflow.log_metric("max_quality_score", max(quality_scores))

            if user_rating is not None:
                mlflow.log_metric("user_rating", user_rating)

        except Exception as e:
            logger.warning(f"Failed to log quality metrics: {e}")

    def log_error_metrics(self, error_type: str, error_message: str = None):
        """
        Log error metrics for failed operations.

        Args:
            error_type: Type of error (e.g., 'generation_failed', 'model_error')
            error_message: Optional error message
        """
        if not MLFLOW_AVAILABLE:
            return

        try:
            mlflow.log_param("error_type", error_type)
            if error_message:
                mlflow.log_param("error_message", error_message[:500])  # Truncate long messages
            mlflow.log_metric("error_occurred", 1)

        except Exception as e:
            logger.warning(f"Failed to log error metrics: {e}")

    def log_model_metadata(self, model_name: str, model_size: Optional[str] = None, 
                          model_version: Optional[str] = None):
        """
        Log model metadata.

        Args:
            model_name: Name of the model
            model_size: Size of the model (e.g., "560M", "1.7B")
            model_version: Version of the model
        """
        if not MLFLOW_AVAILABLE:
            return

        try:
            mlflow.log_param("model_name", model_name)
            if model_size:
                mlflow.log_param("model_size", model_size)
            if model_version:
                mlflow.log_param("model_version", model_version)

        except Exception as e:
            logger.warning(f"Failed to log model metadata: {e}")

# Global tracker instance
llm_tracker = LLMMLflowTracker()
