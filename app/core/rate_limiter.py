"""
Rate limiting utilities for protecting against abuse.
Provides decorators and middleware for rate limiting API endpoints.
"""
import time
from typing import Optional, Callable, Any
from functools import wraps
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status
import redis
from app.core.config import settings


# ===== Redis-based Rate Limiter =====

class RedisRateLimiter:
    """
    Redis-based rate limiter for distributed rate limiting.
    Supports per-user, per-IP, and global rate limiting.
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize rate limiter with Redis client.
        
        Args:
            redis_client: Optional custom Redis client. If None, creates new connection.
        """
        try:
            self.redis_client = redis_client or redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                decode_responses=True,
            )
            # Test connection
            self.redis_client.ping()
            self.available = True
        except Exception as e:
            # Fall back to in-memory if Redis unavailable
            print(f"Redis not available for rate limiting: {e}")
            self.redis_client = None
            self.available = False
            self.in_memory_cache = {}  # Fallback in-memory cache

    def is_rate_limited(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        """
        Check if a key has exceeded rate limit.
        
        Args:
            key: Unique identifier (e.g., user_id, IP address)
            max_requests: Maximum allowed requests
            window_seconds: Time window in seconds
            
        Returns:
            True if rate limited (exceeded), False otherwise
        """
        if self.available and self.redis_client:
            return self._check_redis_limit(key, max_requests, window_seconds)
        else:
            return self._check_memory_limit(key, max_requests, window_seconds)

    def _check_redis_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        """Use Redis for rate limiting"""
        try:
            current = self.redis_client.incr(key)
            if current == 1:
                # First request in window, set expiry
                self.redis_client.expire(key, window_seconds)
            
            return current > max_requests
        except Exception as e:
            print(f"Redis rate limit check failed: {e}")
            # Fall through to memory check on Redis error
            return self._check_memory_limit(key, max_requests, window_seconds)

    def _check_memory_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        """Fallback to in-memory rate limiting"""
        now = time.time()
        
        if key not in self.in_memory_cache:
            self.in_memory_cache[key] = []
        
        # Remove old entries outside the window
        request_times = self.in_memory_cache[key]
        request_times = [t for t in request_times if now - t < window_seconds]
        self.in_memory_cache[key] = request_times
        
        # Check limit
        if len(request_times) >= max_requests:
            return True  # Rate limited
        
        # Record this request
        request_times.append(now)
        return False


# Global rate limiter instance
_rate_limiter: Optional[RedisRateLimiter] = None


def get_rate_limiter() -> RedisRateLimiter:
    """Get or create global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RedisRateLimiter()
    return _rate_limiter


def rate_limit(
    max_requests: int = 10,
    window_seconds: int = 60,
    key_func: Optional[Callable[[Any], str]] = None,
):
    """
    Decorator for rate limiting API endpoints.
    
    Args:
        max_requests: Maximum allowed requests per window
        window_seconds: Time window in seconds
        key_func: Function to extract rate limit key from request context
                 (receives endpoint context, should return string key)
    
    Example:
        @rate_limit(max_requests=5, window_seconds=60, key_func=lambda ctx: ctx['user_id'])
        def send_invitation(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Default key function: try to extract user_id from kwargs
            if key_func:
                try:
                    key = key_func({**kwargs})  # Pass all kwargs to key_func
                except Exception:
                    key = "unknown"
            else:
                # Try to get user ID from current_user
                current_user = kwargs.get('current_user')
                if current_user and hasattr(current_user, 'id'):
                    key = f"user:{current_user.id}"
                else:
                    key = "unknown"
            
            # Check rate limit
            limiter = get_rate_limiter()
            if limiter.is_rate_limited(key, max_requests, window_seconds):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limited. Max {max_requests} requests per {window_seconds} seconds",
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ===== Specific Rate Limiters =====

def rate_limit_by_user(
    max_requests: int = 10,
    window_seconds: int = 60,
):
    """Rate limit by currently authenticated user"""
    def key_func(ctx):
        user_id = ctx.get('current_user')
        if user_id and hasattr(user_id, 'id'):
            return f"user:{user_id.id}"
        raise ValueError("No user in context")
    
    return rate_limit(
        max_requests=max_requests,
        window_seconds=window_seconds,
        key_func=key_func,
    )


def rate_limit_invite_endpoint(
    max_requests: int = 5,  # Max 5 invites per minute per user
    window_seconds: int = 60,
):
    """Specific rate limiter for invite endpoints"""
    def key_func(ctx):
        user_id = ctx.get('current_user')
        workspace_id = ctx.get('workspace_id')
        if user_id and hasattr(user_id, 'id'):
            # Rate limit per user per workspace
            return f"invite:{user_id.id}:{workspace_id}"
        raise ValueError("No user or workspace in context")
    
    return rate_limit(
        max_requests=max_requests,
        window_seconds=window_seconds,
        key_func=key_func,
    )
