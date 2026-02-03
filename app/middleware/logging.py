"""
Logging Middleware for PronaFlow API
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and log details.
        
        Args:
            request: HTTP request
            call_next: Next middleware/route
            
        Returns:
            HTTP response
        """
        # Start timer
        start_time = time.time()
        
        # Get request details
        method = request.method
        path = request.url.path
        query_string = request.url.query
        
        # Log request
        logger.info(
            f"REQUEST | {method} {path}",
            extra={
                "method": method,
                "path": path,
                "query_string": query_string,
                "client": request.client.host if request.client else "unknown",
            }
        )
        
        try:
            # Call next middleware/route
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"RESPONSE | {method} {path} | {response.status_code} | {duration:.3f}s",
                extra={
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration": duration,
                }
            )
            
            # Add timing header
            response.headers["X-Process-Time"] = str(duration)
            
            return response
            
        except Exception as exc:
            # Log error
            duration = time.time() - start_time
            logger.error(
                f"ERROR | {method} {path} | {duration:.3f}s",
                exc_info=True,
                extra={
                    "method": method,
                    "path": path,
                    "duration": duration,
                }
            )
            raise
