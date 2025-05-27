"""
MLflow tracking for OCR service performance and confidence metrics.
"""
import os
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager
from .logger_config import logger

# Try to import MLflow, make it optional
try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not available. OCR tracking will be disabled.")

class OCRMLflowTracker:
    """MLflow tracker for OCR operations and performance metrics."""

    def __init__(self):
        """Initialize MLflow tracker with OCR-specific configuration."""
        if not MLFLOW_AVAILABLE:
            logger.info("MLflow tracking disabled - MLflow not available")
            return

        try:
            # Set MLflow tracking URI (can be overridden by environment variable)
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
            mlflow.set_tracking_uri(tracking_uri)

            # Set experiment name
            experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "ocr_service_tracking")
            mlflow.set_experiment(experiment_name)
            logger.info(f"MLflow experiment set to: {experiment_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize MLflow: {e}")

    @contextmanager
    def track_ocr_operation(self, operation_type: str = "text_extraction"):
        """
        Context manager for tracking OCR operations.

        Args:
            operation_type: Type of OCR operation (e.g., 'text_extraction', 'pdf_processing')
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

        except Exception as mlflow_error:
            # MLflow initialization failed, continue without tracking
            logger.error(f"MLflow tracking initialization error: {mlflow_error}")
            mlflow_run_started = False

        try:
            # Yield control to the application code
            yield self

        except Exception as app_error:
            # Log application errors if MLflow is working
            if mlflow_run_started:
                try:
                    if hasattr(app_error, 'status_code'):
                        # This is likely an HTTPException - log it as an error metric
                        self.log_error_metrics(f"http_{app_error.status_code}", str(app_error.detail))
                    else:
                        self.log_error_metrics("application_error", str(app_error))
                except Exception as log_error:
                    logger.warning(f"Failed to log error metrics: {log_error}")

            # Always re-raise the application error
            raise

        finally:
            # Clean up MLflow run and log duration
            if mlflow_run_started:
                try:
                    duration = time.time() - start_time
                    mlflow.log_metric("operation_duration_seconds", duration)
                    mlflow.end_run()
                except Exception as e:
                    logger.warning(f"Failed to finalize MLflow run: {e}")

    def log_confidence_metrics(self, ocr_result: Dict[str, Any], min_confidence_threshold: float = 0.0):
        """
        Log confidence-related metrics from OCR results.

        Args:
            ocr_result: OCR result dictionary with confidence data
            min_confidence_threshold: Confidence threshold used for filtering
        """
        if not MLFLOW_AVAILABLE:
            return

        try:
            # Basic confidence metrics
            mlflow.log_metric("average_confidence", ocr_result.get("average_confidence", 0))
            mlflow.log_metric("filtered_average_confidence", ocr_result.get("filtered_average_confidence", 0))
            mlflow.log_metric("word_count", ocr_result.get("word_count", 0))
            mlflow.log_metric("filtered_word_count", ocr_result.get("filtered_word_count", 0))

            # Confidence threshold and filtering stats
            mlflow.log_param("min_confidence_threshold", min_confidence_threshold)

            confidence_stats = ocr_result.get("confidence_stats", {})
            if confidence_stats:
                mlflow.log_metric("high_confidence_words", confidence_stats.get("high_confidence_count", 0))
                mlflow.log_metric("medium_confidence_words", confidence_stats.get("medium_confidence_count", 0))
                mlflow.log_metric("low_confidence_words", confidence_stats.get("low_confidence_count", 0))
                mlflow.log_metric("words_filtered_out", confidence_stats.get("words_filtered_out", 0))

                # Calculate confidence distribution percentages
                total_words = confidence_stats.get("total_words", 1)
                if total_words > 0:
                    mlflow.log_metric("high_confidence_percentage",
                                    (confidence_stats.get("high_confidence_count", 0) / total_words) * 100)
                    mlflow.log_metric("medium_confidence_percentage",
                                    (confidence_stats.get("medium_confidence_count", 0) / total_words) * 100)
                    mlflow.log_metric("low_confidence_percentage",
                                    (confidence_stats.get("low_confidence_count", 0) / total_words) * 100)

            # Text length metrics
            text_length = len(ocr_result.get("text", ""))
            filtered_text_length = len(ocr_result.get("filtered_text", ""))
            mlflow.log_metric("text_length_characters", text_length)
            mlflow.log_metric("filtered_text_length_characters", filtered_text_length)

            if text_length > 0:
                mlflow.log_metric("text_retention_percentage", (filtered_text_length / text_length) * 100)

        except Exception as e:
            logger.warning(f"Failed to log confidence metrics: {e}")

    def log_file_metadata(self, filename: str, file_type: str, file_size: Optional[int] = None):
        """
        Log file metadata for the processed document.

        Args:
            filename: Name of the processed file
            file_type: Type of file (image, pdf)
            file_size: Size of file in bytes (optional)
        """
        if not MLFLOW_AVAILABLE:
            return

        try:
            mlflow.log_param("filename", filename)
            mlflow.log_param("file_type", file_type)

            if file_size is not None:
                mlflow.log_metric("file_size_bytes", file_size)
                mlflow.log_metric("file_size_kb", file_size / 1024)

        except Exception as e:
            logger.warning(f"Failed to log file metadata: {e}")

    def log_processing_metrics(self, preprocessing_applied: bool = False,
                             processing_time: Optional[float] = None):
        """
        Log processing-related metrics.

        Args:
            preprocessing_applied: Whether image preprocessing was applied
            processing_time: Time taken for processing in seconds
        """
        if not MLFLOW_AVAILABLE:
            return

        try:
            mlflow.log_param("preprocessing_applied", preprocessing_applied)

            if processing_time is not None:
                mlflow.log_metric("processing_time_seconds", processing_time)

        except Exception as e:
            logger.warning(f"Failed to log processing metrics: {e}")

    def log_error_metrics(self, error_type: str, error_message: str):
        """
        Log error information for failed OCR operations.

        Args:
            error_type: Type of error (e.g., 'ocr_failure', 'file_error')
            error_message: Error message
        """
        if not MLFLOW_AVAILABLE:
            return

        try:
            mlflow.log_param("error_occurred", True)
            mlflow.log_param("error_type", error_type)
            mlflow.log_param("error_message", error_message[:500])  # Truncate long messages

        except Exception as e:
            logger.warning(f"Failed to log error metrics: {e}")

# Global tracker instance
ocr_tracker = OCRMLflowTracker()
