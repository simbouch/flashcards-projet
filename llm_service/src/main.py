"""
FastAPI application for the LLM service.
"""
import asyncio

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
# NOTE: Model initialization can be very slow (download + load). We must not
# block the FastAPI startup event, otherwise Uvicorn won't accept connections
# and callers may see RemoteDisconnected/connection errors.
generator: Optional[FlashcardGenerator] = None
_generator_init_task: Optional[asyncio.Task] = None
_generator_init_lock: Optional[asyncio.Lock] = None
_generator_last_init_error: Optional[str] = None


def _record_init_task_result(task: asyncio.Task) -> None:
    """Record background init task outcome for health endpoints."""

    global generator, _generator_last_init_error
    try:
        gen = task.result()
    except Exception as e:  # noqa: BLE001 (background task result)
        _generator_last_init_error = f"{type(e).__name__}: {e}"
        return
    if generator is None:
        generator = gen
    _generator_last_init_error = None


async def _ensure_generator_initialized() -> FlashcardGenerator:
    """Ensure the global FlashcardGenerator is initialized.

    - Non-blocking startup: initialization can be scheduled on startup.
    - First request to /generate will await initialization if still running.
    - Safe for concurrent requests (single initialization task).
    """

    global generator, _generator_init_task, _generator_init_lock, _generator_last_init_error

    if generator is not None:
        return generator

    if _generator_init_lock is None:
        # Lazily create the lock in the running event loop.
        _generator_init_lock = asyncio.Lock()

    # Create/reuse a single init task.
    async with _generator_init_lock:
        if generator is not None:
            return generator

        if _generator_init_task is None:
            _generator_last_init_error = None
            _generator_init_task = asyncio.create_task(asyncio.to_thread(FlashcardGenerator))
            _generator_init_task.add_done_callback(_record_init_task_result)

        task = _generator_init_task

    try:
        gen = await task
    except Exception as e:
        _generator_last_init_error = f"{type(e).__name__}: {e}"
        # Allow retry on next call.
        async with _generator_init_lock:
            if _generator_init_task is task:
                _generator_init_task = None
        raise

    generator = gen
    _generator_last_init_error = None
    return generator


def _generator_status() -> Dict[str, Any]:
    """Small status payload for health/readiness endpoints."""

    initializing = _generator_init_task is not None and not _generator_init_task.done()
    return {
        "loaded": generator is not None,
        "initializing": initializing,
        "last_init_error": _generator_last_init_error,
    }
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
    interaction_id: int = Field(..., description="ID of the interaction being rated")
    rating: int = Field(..., description="Overall rating (1-5)", ge=1, le=5)
    feedback_text: Optional[str] = Field(None, description="Optional feedback text")
    card_quality_rating: Optional[int] = Field(None, description="Card quality rating (1-5)", ge=1, le=5)
    educational_value_rating: Optional[int] = Field(None, description="Educational value rating (1-5)", ge=1, le=5)

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup (non-blocking)."""
    global _generator_init_lock, _generator_init_task

    logger.info("Starting LLM service (non-blocking startup)")
    _generator_init_lock = asyncio.Lock()

    warmup = os.getenv("LLM_WARMUP_ON_STARTUP", "true").strip().lower() in {"1", "true", "yes"}
    if not warmup:
        logger.info("LLM warmup on startup disabled (LLM_WARMUP_ON_STARTUP=false)")
        return

    # Schedule model load in the background so the HTTP server becomes reachable quickly.
    try:
        async with _generator_init_lock:
            if generator is None and _generator_init_task is None:
                _generator_init_task = asyncio.create_task(asyncio.to_thread(FlashcardGenerator))
                _generator_init_task.add_done_callback(_record_init_task_result)
        logger.info("LLM warmup task scheduled")
    except Exception as e:
        logger.exception(f"Failed to schedule LLM warmup task: {type(e).__name__}: {e}")

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "ok", "service": "llm"}

@app.get("/health")
async def health_check():
    """Liveness health check endpoint.

    This must stay fast and should NOT trigger model loading.
    """

    return {
        "status": "ok",
        "message": "LLM service is alive",
        "model": _generator_status(),
    }


@app.get("/ready")
async def ready_check():
    """Readiness endpoint.

    Returns 200 only when the model is loaded and ready to serve generations.
    """

    if generator is not None:
        return {"status": "ok", "message": "LLM model is ready", "model": _generator_status()}

    payload = {"status": "starting", "message": "LLM model is not ready", "model": _generator_status()}
    # If we already have an init error, report it as error (still 503).
    if _generator_last_init_error:
        payload["status"] = "error"
        payload["message"] = "LLM model failed to initialize"
    return JSONResponse(status_code=503, content=payload)

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
        # Ensure generator is initialized (await background warmup if needed)
        try:
            generator = await _ensure_generator_initialized()
        except Exception as e:
            logger.exception(f"Failed to initialize generator: {type(e).__name__}: {e}")
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
        interaction_id = data_collector.record_user_interaction(interaction)

        # Expose interaction_id so clients can submit feedback
        if isinstance(result, dict):
            metadata = result.setdefault("metadata", {})
            if isinstance(metadata, dict):
                metadata["interaction_id"] = interaction_id

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

    # Ensure generator is initialized (await background warmup if needed)
    if generator is None:
        try:
            generator = await _ensure_generator_initialized()
        except Exception as e:
            logger.exception(f"Failed to initialize generator: {type(e).__name__}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize LLM service: {str(e)}")

    # Basic monitoring
    start_time = time.time()
    session_id = f"session_{int(start_time)}"
    client_ip = get_remote_address(request)
    llm_active_generations.inc()

    try:
        result = await generator.generate_flashcards_from_chunks(chunks_request.chunks, chunks_request.num_cards)

        response_time = time.time() - start_time
        llm_generation_duration.labels(request_type="chunks").observe(response_time)

        # Record user interaction for training data collection
        interaction = UserInteraction(
            session_id=session_id,
            user_id=client_ip,
            input_text="\n\n".join(chunks_request.chunks),
            generated_cards=result.get('flashcards', []),
            response_time=response_time,
            timestamp=datetime.now()
        )
        interaction_id = data_collector.record_user_interaction(interaction)

        if isinstance(result, dict):
            metadata = result.setdefault("metadata", {})
            if isinstance(metadata, dict):
                metadata["interaction_id"] = interaction_id

        return result
    except Exception as e:
        logger.exception(f"Error generating flashcards from chunks: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating flashcards: {str(e)}")
    finally:
        llm_active_generations.dec()

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
