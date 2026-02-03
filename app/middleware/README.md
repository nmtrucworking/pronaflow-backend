# Middleware

This directory contains custom FastAPI middleware.

## Purpose
- Request/response processing
- Authentication and authorization
- Logging and monitoring
- Error handling

## Example
```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Process request
        response = await call_next(request)
        # Process response
        return response
```
