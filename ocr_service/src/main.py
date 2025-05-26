from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .logger_config import logger
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

# Initialize rate limiter
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

def extract_text_with_confidence(image: Image.Image) -> Dict[str, Any]:
    """
    Extract text from image with confidence scores.

    Args:
        image: PIL Image object

    Returns:
        Dictionary containing extracted text and confidence data
    """
    try:
        # Get detailed OCR data with confidence scores
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang="fra")

        # Extract text and calculate confidence
        words = []
        confidences = []

        for i, word in enumerate(ocr_data['text']):
            if word.strip():  # Only include non-empty words
                words.append(word)
                confidences.append(int(ocr_data['conf'][i]))

        # Calculate overall confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        # Get full text
        full_text = pytesseract.image_to_string(image, lang="fra").strip()

        return {
            "text": full_text,
            "words": words,
            "word_confidences": confidences,
            "average_confidence": round(avg_confidence, 2),
            "word_count": len(words)
        }
    except Exception as e:
        logger.error(f"OCR with confidence failed: {e}")
        # Fallback to basic OCR
        text = pytesseract.image_to_string(image, lang="fra").strip()
        return {
            "text": text,
            "words": text.split(),
            "word_confidences": [],
            "average_confidence": 0,
            "word_count": len(text.split())
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

@app.post("/extract")
@limiter.limit("10/minute")  # Strict limit for OCR processing
async def extract_text(request: Request, file: UploadFile = File(...)):
    """
    Extract text from an uploaded image or PDF using enhanced OCR.
    """
    logger.info("Received file {name} (content_type={ct})", name=file.filename, ct=file.content_type)

    try:
        # Read file content
        contents = await file.read()

        # Handle PDF files
        if file.content_type == 'application/pdf':
            logger.info(f"Processing PDF file: {file.filename}")
            result = extract_text_from_pdf(contents)

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

            # Extract text with confidence scores
            ocr_result = extract_text_with_confidence(processed_image)

            logger.info("Extracted {} characters with {}% confidence",
                       len(ocr_result["text"]), ocr_result["average_confidence"])

            return {
                "filename": file.filename,
                "file_type": "image",
                "text": ocr_result["text"],
                "average_confidence": ocr_result["average_confidence"],
                "word_count": ocr_result["word_count"],
                "word_confidences": ocr_result["word_confidences"],
                "preprocessing_applied": True,
                "status": "success"
            }

        else:
            logger.warning("Rejected unsupported format: {}", file.content_type)
            raise HTTPException(
                status_code=415,
                detail=f"Format non supporté : {file.content_type}. Formats supportés: images (PNG, JPG, etc.)" +
                       (" et PDF" if PDF_SUPPORT else "")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("OCR failure")
        raise HTTPException(500, f"Erreur OCR : {e}")
@app.get("/health")
def health_check():
    return {"status": "ok"}
