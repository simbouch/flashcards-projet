from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .logger_config import logger
from PIL import Image
import pytesseract, io
import os
import redis

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

app = FastAPI(title="OCR Service")

# Add rate limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

@app.post("/extract")
@limiter.limit("10/minute")  # Strict limit for OCR processing
async def extract_text(request: Request, file: UploadFile = File(...)):
    logger.info("Received file {name} (content_type={ct})", name=file.filename, ct=file.content_type)
    if not file.content_type.startswith("image/"):
        logger.warning("Rejected unsupported format: {}", file.content_type)
        raise HTTPException(415, f"Format non supporté : {file.content_type}")
    data = await file.read()
    try:
        img = Image.open(io.BytesIO(data))
        text = pytesseract.image_to_string(img, lang="fra")
        logger.info("Extracted {} characters of text", len(text))
    except Exception as e:
        logger.exception("OCR failure")
        raise HTTPException(500, f"Erreur OCR : {e}")
    return {"text": text}
@app.get("/health")
def health_check():
    return {"status": "ok"}
