"""
FastAPI application for the LLM service.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import os
import time
import redis
from datetime import datetime
from .logger_config import logger
from .flashcard_generator import FlashcardGenerator
from .model_evaluator import ModelEvaluator
from .data_collector import DataCollector, UserInteraction, UserFeedback

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
        default_limits=["30/minute"]
    )
else:
    # Use Redis for production
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=redis_url,
        default_limits=["30/minute"]  # Default limit for LLM service
    )

# Custom rate limit exceeded handler
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors."""
    retry_after = getattr(exc, 'retry_after', 60)

    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many AI generation requests. Please try again later.",
            "retry_after_seconds": retry_after
        }
    )
    response.headers["Retry-After"] = str(retry_after)

    # Log the rate limit violation
    client_ip = get_remote_address(request)
    logger.warning(f"LLM rate limit exceeded for IP {client_ip}")

    return response

# Initialize FastAPI app
app = FastAPI(
    title="LLM Service",
    description="Service for generating flashcards from text using a language model",
    version="0.1.0"
)

# Add rate limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Initialize Prometheus metrics
if PROMETHEUS_AVAILABLE:
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app)

# Custom Prometheus metrics for LLM Service
llm_generation_requests_total = Counter(
    'llm_generation_requests_total',
    'Total number of flashcard generation requests',
    ['request_type', 'status']
)

llm_generation_duration = Histogram(
    'llm_generation_duration_seconds',
    'Time spent generating flashcards',
    ['request_type']
)

llm_flashcards_generated = Counter(
    'llm_flashcards_generated_total',
    'Total number of flashcards generated',
    ['request_type']
)

llm_model_load_duration = Histogram(
    'llm_model_load_duration_seconds',
    'Time spent loading the LLM model'
)

llm_token_usage = Histogram(
    'llm_token_usage',
    'Number of tokens used in generation',
    ['token_type']  # input, output
)

llm_active_generations = Gauge(
    'llm_active_generations',
    'Number of currently active generation requests'
)

llm_model_memory_usage = Gauge(
    'llm_model_memory_usage_bytes',
    'Memory usage of the LLM model'
)

llm_generation_errors = Counter(
    'llm_generation_errors_total',
    'Total number of generation errors',
    ['error_type']
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize flashcard generator and monitoring components
generator = None
model_evaluator = ModelEvaluator()
data_collector = DataCollector()

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

class FeedbackRequest(BaseModel):
    """Request model for user feedback."""
    interaction_id: str = Field(..., description="ID of the interaction being rated")
    rating: int = Field(..., description="Overall rating (1-5)", ge=1, le=5)
    feedback_text: Optional[str] = Field(None, description="Optional feedback text")
    card_quality_rating: Optional[int] = Field(None, description="Card quality rating (1-5)", ge=1, le=5)
    educational_value_rating: Optional[int] = Field(None, description="Educational value rating (1-5)", ge=1, le=5)

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
@limiter.limit("5/minute")  # Very strict limit for AI generation
async def generate_flashcards(request: Request, generation_request: TextGenerationRequest):
    """
    Generate flashcards from text with comprehensive monitoring.
    """
    global generator

    # Start monitoring
    start_time = time.time()
    session_id = f"session_{int(start_time)}"
    client_ip = get_remote_address(request)

    # Update active generations metric
    llm_active_generations.inc()

    try:
        # Initialize generator if not already done
        if generator is None:
            try:
                generator = FlashcardGenerator()
            except Exception as e:
                logger.exception(f"Failed to initialize generator: {e}")
                llm_generation_errors.labels(error_type="initialization").inc()
                raise HTTPException(status_code=500, detail=f"Failed to initialize LLM service: {str(e)}")

        # Generate flashcards
        llm_generation_requests_total.labels(request_type="text", status="started").inc()

        result = await generator.generate_flashcards(generation_request.text, generation_request.num_cards)

        # Calculate metrics
        response_time = time.time() - start_time
        llm_generation_duration.labels(request_type="text").observe(response_time)

        # Count generated flashcards
        num_generated = len(result.get('flashcards', []))
        llm_flashcards_generated.labels(request_type="text").inc(num_generated)

        # Record user interaction for training data collection
        interaction = UserInteraction(
            session_id=session_id,
            user_id=client_ip,  # Using IP as user identifier for now
            input_text=generation_request.text,
            generated_cards=result.get('flashcards', []),
            response_time=response_time,
            timestamp=datetime.now()
        )
        data_collector.record_user_interaction(interaction)

        # Update success metrics
        llm_generation_requests_total.labels(request_type="text", status="success").inc()

        logger.info(f"Generated {num_generated} flashcards in {response_time:.2f}s for session {session_id}")

        return result

    except Exception as e:
        # Record error metrics
        llm_generation_errors.labels(error_type="generation").inc()
        llm_generation_requests_total.labels(request_type="text", status="error").inc()

        logger.exception(f"Error generating flashcards: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating flashcards: {str(e)}")

    finally:
        # Update active generations metric
        llm_active_generations.dec()

@app.post("/generate/chunks", response_model=GenerationResponse)
@limiter.limit("5/minute")  # Very strict limit for AI generation
async def generate_flashcards_from_chunks(request: Request, chunks_request: ChunksGenerationRequest):
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
        result = await generator.generate_flashcards_from_chunks(chunks_request.chunks, chunks_request.num_cards)
        return result
    except Exception as e:
        logger.exception(f"Error generating flashcards from chunks: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating flashcards: {str(e)}")

@app.post("/feedback")
async def submit_feedback(feedback_request: FeedbackRequest):
    """
    Submit user feedback for a generation interaction.
    """
    try:
        # Create feedback object
        feedback = UserFeedback(
            interaction_id=feedback_request.interaction_id,
            rating=feedback_request.rating,
            feedback_text=feedback_request.feedback_text,
            card_quality_rating=feedback_request.card_quality_rating,
            educational_value_rating=feedback_request.educational_value_rating,
            timestamp=datetime.now()
        )

        # Record feedback
        data_collector.record_user_feedback(feedback)

        logger.info(f"Received feedback for interaction {feedback_request.interaction_id}: rating={feedback_request.rating}")

        return {"status": "success", "message": "Feedback recorded successfully"}

    except Exception as e:
        logger.exception(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")

@app.get("/metrics/performance")
async def get_performance_metrics():
    """
    Get current model performance metrics.
    """
    try:
        # Get recent performance data
        performance_trend = model_evaluator.get_performance_trend(days=7)
        feedback_summary = data_collector.get_user_feedback_summary(days=7)

        return {
            "performance_trend": performance_trend,
            "user_feedback_summary": feedback_summary,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
