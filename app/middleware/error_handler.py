"""
Error Handler Middleware for PronaFlow API
"""
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException
from app.utils.exceptions import PronaFlowException

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling."""
    
    async def dispatch(self, request: Request, call_next):
        """
        Handle errors and return consistent error responses.
        
        Args:
            request: HTTP request
            call_next: Next middleware/route
            
        Returns:
            HTTP response
        """
        try:
            response = await call_next(request)
            return response
            
        except PronaFlowException as exc:
            # Handle custom application exceptions
            logger.warning(
                f"PronaFlow Exception: {exc.code} - {exc.message}",
                extra={
                    "code": exc.code,
                    "status_code": exc.status_code,
                }
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                    }
                }
            )
            
        except HTTPException as exc:
            # Handle Starlette HTTP exceptions
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": "HTTP_ERROR",
                        "message": exc.detail,
                    }
                }
            )
            
        except Exception as exc:
            # Handle unexpected exceptions
            logger.error(
                f"Unexpected error: {type(exc).__name__}",
                exc_info=True,
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                    }
                }
            )
