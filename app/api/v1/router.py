"""
API Router initialization for v1 endpoints.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, workspaces, admin, projects

api_router = APIRouter(prefix="/api")

# Include endpoint routers
api_router.include_router(auth.router)
api_router.include_router(workspaces.router)
api_router.include_router(projects.router)
api_router.include_router(admin.router)
