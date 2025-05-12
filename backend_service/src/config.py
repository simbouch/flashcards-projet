"""
Configuration settings for the backend service.
"""
import os
from pathlib import Path
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=str(env_path))

class Settings(BaseSettings):
    """Application settings."""

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Flashcards API"

    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:8080", "http://127.0.0.1:8080"]

    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "supersecretkey")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    # Service URLs
    OCR_SERVICE_URL: str = os.getenv("OCR_SERVICE_URL", "http://ocr-service:8000")
    LLM_SERVICE_URL: str = os.getenv("LLM_SERVICE_URL", "http://llm-service:8001")

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/flashcards.db")

    # File upload settings
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "./uploads"))
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10 MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf"]

    # Security settings
    SECURITY_PASSWORD_SALT: str = os.getenv("SECURITY_PASSWORD_SALT", "salt")

    @field_validator("UPLOAD_DIR")
    def create_upload_dir(cls, v):
        """Create upload directory if it doesn't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("CORS_ORIGINS")
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string if needed."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings object
settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
