"""
FastAPI application for the LLM service.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import os
import time
from .logger_config import logger
from .flashcard_generator import FlashcardGenerator

# Initialize FastAPI app
app = FastAPI(
    title="LLM Service",
    description="Service for generating flashcards from text using a language model",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize flashcard generator
generator = None

# Pydantic models for request/response validation
class TextGenerationRequest(BaseModel):
    """Request model for text-based flashcard generation."""
    text: str = Field(..., description="The text to generate flashcards from")
    num_cards: int = Field(5, description="Number of flashcards to generate", ge=1, le=20)
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v

class ChunksGenerationRequest(BaseModel):
    """Request model for chunk-based flashcard generation."""
    chunks: List[str] = Field(..., description="List of text chunks to generate flashcards from")
    num_cards: int = Field(5, description="Total number of flashcards to generate", ge=1, le=20)
    
    @validator('chunks')
    def chunks_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Chunks list cannot be empty')
        if any(not chunk.strip() for chunk in v):
            raise ValueError('All chunks must contain non-empty text')
        return v

class Flashcard(BaseModel):
    """Model for a flashcard."""
    question: str
    answer: str

class GenerationResponse(BaseModel):
    """Response model for flashcard generation."""
    flashcards: List[Flashcard]
    metadata: Dict[str, Any]
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    global generator
    try:
        logger.info("Initializing LLM service")
        generator = FlashcardGenerator()
        logger.info("LLM service initialized successfully")
    except Exception as e:
        logger.exception(f"Failed to initialize LLM service: {e}")
        # We'll initialize the generator on the first request if it fails here

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "ok", "service": "llm"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global generator
    
    # Check if generator is initialized
    if generator is None:
        try:
            generator = FlashcardGenerator()
            return {"status": "ok", "message": "LLM service is healthy (initialized on demand)"}
        except Exception as e:
            logger.exception(f"Health check failed: {e}")
            return {"status": "error", "message": f"LLM service initialization failed: {str(e)}"}
    
    return {"status": "ok", "message": "LLM service is healthy"}

@app.post("/generate", response_model=GenerationResponse)
async def generate_flashcards(request: TextGenerationRequest):
    """
    Generate flashcards from text.
    """
    global generator
    
    # Initialize generator if not already done
    if generator is None:
        try:
            generator = FlashcardGenerator()
        except Exception as e:
            logger.exception(f"Failed to initialize generator: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize LLM service: {str(e)}")
    
    # Generate flashcards
    try:
        result = await generator.generate_flashcards(request.text, request.num_cards)
        return result
    except Exception as e:
        logger.exception(f"Error generating flashcards: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating flashcards: {str(e)}")

@app.post("/generate/chunks", response_model=GenerationResponse)
async def generate_flashcards_from_chunks(request: ChunksGenerationRequest):
    """
    Generate flashcards from multiple text chunks.
    """
    global generator
    
    # Initialize generator if not already done
    if generator is None:
        try:
            generator = FlashcardGenerator()
        except Exception as e:
            logger.exception(f"Failed to initialize generator: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize LLM service: {str(e)}")
    
    # Generate flashcards
    try:
        result = await generator.generate_flashcards_from_chunks(request.chunks, request.num_cards)
        return result
    except Exception as e:
        logger.exception(f"Error generating flashcards from chunks: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating flashcards: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
