"""
API Router initialization for v1 endpoints.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth

api_router = APIRouter(prefix="/api")

# Include endpoint routers
api_router.include_router(auth.router)
