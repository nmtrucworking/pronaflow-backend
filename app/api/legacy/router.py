"""Legacy API router.

This router aggregates deprecated top-level route modules.
It is intentionally not included in app.main by default.
"""
from fastapi import APIRouter

from app.api.project_routes import router as project_router
from app.api.task_routes import router as task_router
from app.api.workspace_routes import router as workspace_router

legacy_api_router = APIRouter()
legacy_api_router.include_router(workspace_router)
legacy_api_router.include_router(project_router)
legacy_api_router.include_router(task_router)
