"""
Integration Guide - How to register routes in FastAPI app

This file shows how to integrate the Phase 2.3 routes into the main application.
"""

# Add to app/main.py or the FastAPI application factory:

from fastapi import FastAPI
from app.api import workspace_routes, project_routes, task_routes

def create_app():
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="PronaFlow API",
        version="1.2.0",
        description="Workspace, Project & Task Management System"
    )
    
    # ==================== MIDDLEWARE ====================
    
    # Add middleware in this order:
    # 1. Logging middleware (first to log all requests)
    from app.middleware.logging import LoggingMiddleware
    app.add_middleware(LoggingMiddleware)
    
    # 2. Error handler middleware (catches exceptions)
    from app.middleware.error_handler import ErrorHandlerMiddleware
    app.add_middleware(ErrorHandlerMiddleware)
    
    # 3. CORS middleware (if needed for frontend)
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # ==================== DEPENDENCY OVERRIDES ====================
    
    from app.core.dependencies import get_db, get_current_user
    
    # Override dependencies if using test fixtures:
    # from tests.conftest import override_get_db
    # app.dependency_overrides[get_db] = override_get_db
    
    # ==================== ROUTE REGISTRATION ====================
    
    # Register all API routes (Phase 2.3)
    app.include_router(workspace_routes.router)
    app.include_router(project_routes.router)
    app.include_router(task_routes.router)
    
    # Register other modules as they're implemented:
    # app.include_router(comment_routes.router)      # Phase 3
    # app.include_router(notification_routes.router) # Phase 3
    # app.include_router(activity_routes.router)     # Phase 3
    # ... more routes ...
    
    # ==================== HEALTH CHECK ENDPOINT ====================
    
    @app.get("/health", tags=["System"])
    async def health_check():
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy",
            "version": "1.2.0",
            "service": "PronaFlow API"
        }
    
    @app.get("/api/v1", tags=["System"])
    async def api_info():
        """API information endpoint."""
        return {
            "version": "1.2.0",
            "modules": {
                "core": ["Workspace", "Project", "Task"],
                "advanced": ["Comments", "Notifications", "Activities", "Reports"],
                "integration": ["Webhooks", "Integrations", "Analytics"]
            },
            "endpoints": {
                "workspaces": "/api/v1/workspaces",
                "projects": "/api/v1/projects",
                "tasks": "/api/v1/tasks"
            }
        }
    
    # ==================== EXCEPTION HANDLERS ====================
    
    from fastapi import Request
    from fastapi.responses import JSONResponse
    from app.utils.exceptions import PronaFlowException
    
    @app.exception_handler(PronaFlowException)
    async def pronaflow_exception_handler(request: Request, exc: PronaFlowException):
        """Handle PronaFlow custom exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": exc.error_code,
                "path": str(request.url.path),
            }
        )
    
    # ==================== STARTUP/SHUTDOWN ====================
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize application on startup."""
        print("🚀 PronaFlow API starting up...")
        # Initialize database connection pool
        # Initialize cache
        # Initialize external services
        print("✅ PronaFlow API ready to accept requests")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Clean up resources on shutdown."""
        print("🛑 PronaFlow API shutting down...")
        # Close database connections
        # Flush caches
        # Close external service connections
        print("✅ PronaFlow API shut down successfully")
    
    return app


# ==================== RUNNING THE APPLICATION ====================

# Option 1: Using uvicorn (production)
if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=4,
        log_level="info",
        access_log=True,
    )


# Option 2: Using FastAPI CLI (development)
# fastapi dev app/main.py


# Option 3: Docker
# docker run -p 8000:8000 pronaflow-backend:latest


# ==================== API DOCUMENTATION ====================

"""
Once the app is running, you can access:

1. OpenAPI (Swagger UI):
   http://localhost:8000/docs

2. ReDoc:
   http://localhost:8000/redoc

3. OpenAPI JSON:
   http://localhost:8000/openapi.json

4. Health Check:
   http://localhost:8000/health

5. API Info:
   http://localhost:8000/api/v1
"""


# ==================== TESTING THE API ====================

"""
Example requests using curl:

1. Create Workspace:
   curl -X POST http://localhost:8000/api/v1/workspaces \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"name": "My Workspace"}'

2. List Workspaces:
   curl -X GET "http://localhost:8000/api/v1/workspaces?page=1&page_size=20" \
     -H "Authorization: Bearer YOUR_TOKEN"

3. Create Project:
   curl -X POST http://localhost:8000/api/v1/projects \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"workspace_id": "uuid-here", "name": "Project Name"}'

4. Create Task:
   curl -X POST http://localhost:8000/api/v1/tasks \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"project_id": "uuid", "task_list_id": "uuid", "title": "Task Title"}'
"""


# ==================== ENVIRONMENT VARIABLES ====================

"""
Required in .env file:

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/pronaflow

# JWT Token
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Server
DEBUG=True
WORKERS=4

# Logging
LOG_LEVEL=INFO
"""
