"""
Rate limiting middleware for DDoS protection.
"""
import os
import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from ..logger_config import logger

# Initialize Redis connection
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(redis_url, decode_responses=True)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=redis_url,
    default_limits=["100/minute"]  # Default limit for all endpoints
)

# Custom rate limit exceeded handler
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors.
    """
    # Calculate retry after time (default to 60 seconds)
    retry_after = getattr(exc, 'retry_after', 60)

    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Please try again later.",
            "retry_after_seconds": retry_after
        }
    )
    response.headers["Retry-After"] = str(retry_after)

    # Log the rate limit violation
    client_ip = get_remote_address(request)
    logger.warning(f"Rate limit exceeded for IP {client_ip}")

    return response

# Rate limiting decorators for different endpoint types
def auth_rate_limit():
    """Rate limit for authentication endpoints (stricter)"""
    return limiter.limit("20/minute")

def api_rate_limit():
    """Rate limit for general API endpoints"""
    return limiter.limit("100/minute")

def upload_rate_limit():
    """Rate limit for file upload endpoints (more restrictive)"""
    return limiter.limit("10/minute")

def ai_rate_limit():
    """Rate limit for AI service endpoints (most restrictive)"""
    return limiter.limit("5/minute")

# Health check function for Redis
def check_redis_health():
    """
    Check if Redis is healthy and accessible.
    """
    try:
        redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False

# Get rate limit info for a client
def get_rate_limit_info(request: Request, limit_string: str):
    """
    Get current rate limit information for a client.

    Args:
        request: FastAPI request object
        limit_string: Rate limit string (e.g., "5/minute")

    Returns:
        Dict with rate limit information
    """
    try:
        client_ip = get_remote_address(request)
        # Parse limit string
        limit_parts = limit_string.split("/")
        if len(limit_parts) != 2:
            return {"error": "Invalid limit format"}

        limit_count = int(limit_parts[0])
        limit_period = limit_parts[1]

        # Get current usage from Redis
        key = f"slowapi:{client_ip}:{limit_period}"
        current_usage = redis_client.get(key)
        current_usage = int(current_usage) if current_usage else 0

        # Get TTL
        ttl = redis_client.ttl(key)

        return {
            "limit": limit_count,
            "period": limit_period,
            "current_usage": current_usage,
            "remaining": max(0, limit_count - current_usage),
            "reset_in_seconds": ttl if ttl > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error getting rate limit info: {e}")
        return {"error": "Unable to get rate limit info"}
