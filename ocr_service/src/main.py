from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .logger_config import logger
from .mlflow_tracker import ocr_tracker

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    from prometheus_fastapi_instrumentator import Instrumentator
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Create dummy classes for metrics when Prometheus is not available
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def dec(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    logger.warning("Prometheus dependencies not available. Monitoring disabled.")
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract, io
import os
import redis
import cv2
import numpy as np
from typing import Dict, Any
try:
    import fitz  # PyMuPDF for PDF support
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logger.warning("PyMuPDF not available - PDF support disabled")

logger.add("logs/ocr_{time:YYYY-MM-DD}.log", rotation="1 day", retention="7 days", level="INFO")

# Initialize Redis connection for rate limiting
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

# Check if we're in testing mode
is_testing = os.getenv("TESTING", "false").lower() == "true"

# Initialize rate limiter with fallback for testing
if is_testing:
    # Use memory storage for testing to avoid Redis dependency
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri="memory://",
        default_limits=["50/minute"]
    )
else:
    # Use Redis for production
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=redis_url,
        default_limits=["50/minute"]  # Default limit for OCR service
    )

# Custom rate limit exceeded handler
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors."""
    retry_after = getattr(exc, 'retry_after', 60)

    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many OCR requests. Please try again later.",
            "retry_after_seconds": retry_after
        }
    )
    response.headers["Retry-After"] = str(retry_after)

    # Log the rate limit violation
    client_ip = get_remote_address(request)
    logger.warning(f"OCR rate limit exceeded for IP {client_ip}")

    return response

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image to improve OCR quality.

    Args:
        image: PIL Image object

    Returns:
        Preprocessed PIL Image object
    """
    try:
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')

        # Convert PIL to OpenCV format
        img_array = np.array(image)

        # Apply Gaussian blur to reduce noise
        img_array = cv2.GaussianBlur(img_array, (1, 1), 0)

        # Apply threshold to get better contrast
        _, img_array = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Convert back to PIL
        processed_image = Image.fromarray(img_array)

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(processed_image)
        processed_image = enhancer.enhance(2.0)

        return processed_image
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}, using original image")
        return image

def extract_text_with_confidence(image: Image.Image, min_confidence: float = 0.0) -> Dict[str, Any]:
    """
    Extract text from image with confidence scores and optional filtering.

    Args:
        image: PIL Image object
        min_confidence: Minimum confidence threshold (0-100). Words below this threshold will be filtered out.

    Returns:
        Dictionary containing extracted text and confidence data
    """
    try:
        # Get detailed OCR data with confidence scores
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang="fra")

        # Extract text and calculate confidence with filtering
        all_words = []
        all_confidences = []
        filtered_words = []
        filtered_confidences = []
        low_confidence_words = []

        for i, word in enumerate(ocr_data['text']):
            if word.strip():  # Only include non-empty words
                confidence = int(ocr_data['conf'][i])
                all_words.append(word)
                all_confidences.append(confidence)

                if confidence >= min_confidence:
                    filtered_words.append(word)
                    filtered_confidences.append(confidence)
                else:
                    low_confidence_words.append({"word": word, "confidence": confidence})

        # Calculate confidence statistics
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
        filtered_avg_confidence = sum(filtered_confidences) / len(filtered_confidences) if filtered_confidences else 0

        # Categorize confidence levels
        high_confidence_count = len([c for c in all_confidences if c >= 80])
        medium_confidence_count = len([c for c in all_confidences if 50 <= c < 80])
        low_confidence_count = len([c for c in all_confidences if c < 50])

        # Get full text (original and filtered)
        full_text = pytesseract.image_to_string(image, lang="fra").strip()
        filtered_text = " ".join(filtered_words) if filtered_words else ""

        return {
            "text": full_text,
            "filtered_text": filtered_text,
            "words": all_words,
            "filtered_words": filtered_words,
            "word_confidences": all_confidences,
            "filtered_confidences": filtered_confidences,
            "average_confidence": round(avg_confidence, 2),
            "filtered_average_confidence": round(filtered_avg_confidence, 2),
            "word_count": len(all_words),
            "filtered_word_count": len(filtered_words),
            "low_confidence_words": low_confidence_words,
            "confidence_stats": {
                "high_confidence_count": high_confidence_count,
                "medium_confidence_count": medium_confidence_count,
                "low_confidence_count": low_confidence_count,
                "total_words": len(all_words),
                "filtering_threshold": min_confidence,
                "words_filtered_out": len(all_words) - len(filtered_words)
            }
        }
    except Exception as e:
        logger.error(f"OCR with confidence failed: {e}")
        # Fallback to basic OCR
        text = pytesseract.image_to_string(image, lang="fra").strip()
        words = text.split()
        return {
            "text": text,
            "filtered_text": text,  # No filtering in fallback
            "words": words,
            "filtered_words": words,
            "word_confidences": [],
            "filtered_confidences": [],
            "average_confidence": 0,
            "filtered_average_confidence": 0,
            "word_count": len(words),
            "filtered_word_count": len(words),
            "low_confidence_words": [],
            "confidence_stats": {
                "high_confidence_count": 0,
                "medium_confidence_count": 0,
                "low_confidence_count": 0,
                "total_words": len(words),
                "filtering_threshold": min_confidence,
                "words_filtered_out": 0
            }
        }

def extract_text_from_pdf(pdf_content: bytes) -> Dict[str, Any]:
    """
    Extract text from PDF document.

    Args:
        pdf_content: PDF file content as bytes

    Returns:
        Dictionary containing extracted text from all pages
    """
    if not PDF_SUPPORT:
        raise HTTPException(status_code=501, detail="PDF support not available")

    try:
        doc = fitz.open(stream=pdf_content, filetype="pdf")

        all_text = []
        page_texts = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            page_texts.append({
                "page": page_num + 1,
                "text": text.strip()
            })
            all_text.append(text)

        doc.close()

        combined_text = "\n\n".join(all_text).strip()

        return {
            "text": combined_text,
            "pages": page_texts,
            "page_count": len(page_texts),
            "total_characters": len(combined_text)
        }
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

app = FastAPI(title="OCR Service")

# Add rate limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Initialize Prometheus metrics
if PROMETHEUS_AVAILABLE:
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app)

# Custom Prometheus metrics
ocr_operations_total = Counter(
    'ocr_operations_total',
    'Total number of OCR operations',
    ['status', 'file_type']
)

ocr_processing_duration = Histogram(
    'ocr_processing_duration_seconds',
    'Time spent processing OCR requests',
    ['file_type']
)

ocr_confidence_score = Histogram(
    'ocr_confidence_score',
    'OCR confidence scores',
    ['file_type'],
    buckets=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

ocr_word_count = Histogram(
    'ocr_word_count',
    'Number of words extracted',
    ['file_type']
)

ocr_filtered_words = Histogram(
    'ocr_filtered_words',
    'Number of words after confidence filtering',
    ['file_type']
)

ocr_file_size = Histogram(
    'ocr_file_size_bytes',
    'Size of processed files',
    ['file_type']
)

ocr_active_requests = Gauge(
    'ocr_active_requests',
    'Number of currently active OCR requests'
)

@app.post("/extract")
@limiter.limit("10/minute")  # Strict limit for OCR processing
async def extract_text(
    request: Request,
    file: UploadFile = File(...),
    min_confidence: float = Query(0.0, ge=0.0, le=100.0, description="Minimum confidence threshold (0-100) for text filtering")
):
    """
    Extract text from an uploaded image or PDF using enhanced OCR with confidence filtering.

    Args:
        file: Image or PDF file to process
        min_confidence: Minimum confidence threshold (0-100). Words below this threshold will be filtered out.

    Returns:
        JSON response with extracted text, confidence scores, and filtering statistics
    """
    import time
    start_time = time.time()

    logger.info("Received file {name} (content_type={ct})", name=file.filename, ct=file.content_type)

    # Increment active requests gauge
    ocr_active_requests.inc()

    # Start MLflow tracking for this OCR operation
    with ocr_tracker.track_ocr_operation("text_extraction"):
        try:
            # Read file content
            contents = await file.read()
            file_size = len(contents)

            # Log file metadata
            ocr_tracker.log_file_metadata(file.filename,
                                        "pdf" if file.content_type == 'application/pdf' else "image",
                                        file_size)

            # Handle PDF files
            if file.content_type == 'application/pdf':
                logger.info(f"Processing PDF file: {file.filename}")
                result = extract_text_from_pdf(contents)

                # Record Prometheus metrics
                processing_time = time.time() - start_time
                ocr_processing_duration.labels(file_type="pdf").observe(processing_time)
                ocr_file_size.labels(file_type="pdf").observe(file_size)
                ocr_operations_total.labels(status="success", file_type="pdf").inc()
                ocr_active_requests.dec()

                return {
                    "filename": file.filename,
                    "file_type": "pdf",
                    "text": result["text"],
                    "pages": result["pages"],
                    "page_count": result["page_count"],
                    "total_characters": result["total_characters"],
                    "status": "success"
                }

            # Handle image files
            elif file.content_type.startswith('image/'):
                logger.info(f"Processing image file: {file.filename}")

                # Load and preprocess image
                original_image = Image.open(io.BytesIO(contents))
                processed_image = preprocess_image(original_image)

                # Extract text with confidence scores and filtering
                ocr_result = extract_text_with_confidence(processed_image, min_confidence)

                # Log confidence metrics to MLflow
                ocr_tracker.log_confidence_metrics(ocr_result, min_confidence)
                ocr_tracker.log_processing_metrics(preprocessing_applied=True)

                logger.info("Extracted {} characters with {}% confidence (filtered: {} words)",
                           len(ocr_result["text"]), ocr_result["average_confidence"],
                           ocr_result["filtered_word_count"])

                # Record Prometheus metrics for image processing
                processing_time = time.time() - start_time
                ocr_processing_duration.labels(file_type="image").observe(processing_time)
                ocr_file_size.labels(file_type="image").observe(file_size)
                ocr_confidence_score.labels(file_type="image").observe(ocr_result["average_confidence"])
                ocr_word_count.labels(file_type="image").observe(ocr_result["word_count"])
                ocr_filtered_words.labels(file_type="image").observe(ocr_result["filtered_word_count"])
                ocr_operations_total.labels(status="success", file_type="image").inc()
                ocr_active_requests.dec()

                return {
                    "filename": file.filename,
                    "file_type": "image",
                    "text": ocr_result["text"],
                    "filtered_text": ocr_result["filtered_text"],
                    "average_confidence": ocr_result["average_confidence"],
                    "filtered_average_confidence": ocr_result["filtered_average_confidence"],
                    "word_count": ocr_result["word_count"],
                    "filtered_word_count": ocr_result["filtered_word_count"],
                    "word_confidences": ocr_result["word_confidences"],
                    "filtered_confidences": ocr_result["filtered_confidences"],
                    "low_confidence_words": ocr_result["low_confidence_words"],
                    "confidence_stats": ocr_result["confidence_stats"],
                    "preprocessing_applied": True,
                    "status": "success"
                }

            else:
                logger.warning("Rejected unsupported format: {}", file.content_type)
                # Record error metrics
                ocr_operations_total.labels(status="error_unsupported_format", file_type="unknown").inc()
                ocr_active_requests.dec()
                raise HTTPException(
                    status_code=415,
                    detail=f"Format non supporté : {file.content_type}. Formats supportés: images (PNG, JPG, etc.)" +
                           (" et PDF" if PDF_SUPPORT else "")
                )

        except HTTPException:
            # Decrement active requests for HTTP exceptions
            ocr_active_requests.dec()
            raise
        except Exception as e:
            # Log error to MLflow and Prometheus
            ocr_tracker.log_error_metrics("ocr_failure", str(e))
            ocr_operations_total.labels(status="error_processing", file_type="unknown").inc()
            ocr_active_requests.dec()
            logger.exception("OCR failure")
            raise HTTPException(500, f"Erreur OCR : {e}")
@app.get("/health")
def health_check():
    return {"status": "ok"}
