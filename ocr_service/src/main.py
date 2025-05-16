from fastapi import FastAPI, File, UploadFile, HTTPException
from .logger_config import logger
from PIL import Image
import pytesseract, io

logger.add("logs/ocr_{time:YYYY-MM-DD}.log", rotation="1 day", retention="7 days", level="INFO")
app = FastAPI(title="OCR Service")

@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
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
