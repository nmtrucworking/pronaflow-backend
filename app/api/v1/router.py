"""
API Router initialization for v1 endpoints.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, workspaces, admin, projects, tasks, scheduling, collaboration, notifications, archive, personalization

api_router = APIRouter(prefix="/api")

# Include endpoint routers
api_router.include_router(auth.router)
api_router.include_router(workspaces.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(scheduling.router)
api_router.include_router(collaboration.router)
api_router.include_router(notifications.router)
api_router.include_router(archive.router)
api_router.include_router(personalization.router)
api_router.include_router(admin.router)
