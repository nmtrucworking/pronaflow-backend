"""
Project API Routes - Module 3
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.project_schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectStatsResponse,
    ProjectSearchResponse,
)
from app.services.project_service import ProjectService
from app.utils.exceptions import PronaFlowException

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


# ==================== PROJECT CRUD ====================

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
    description="Create a new project in workspace."
)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new project."""
    try:
        service = ProjectService(db)
        project = service.create_project(
            workspace_id=data.workspace_id,
            user_id=current_user.id,
            name=data.name,
            description=data.description,
            color=data.color,
        )
        return project
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Get project",
    description="Get project details."
)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project details."""
    try:
        service = ProjectService(db)
        project = service.get_project(project_id, current_user.id)
        return project
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Update project details. Only owner can update."
)
def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project."""
    try:
        service = ProjectService(db)
        project = service.update_project(
            project_id=project_id,
            user_id=current_user.id,
            name=data.name,
            description=data.description,
            color=data.color,
        )
        return project
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Delete project. Only owner can delete."
)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete project."""
    try:
        service = ProjectService(db)
        service.delete_project(project_id, current_user.id)
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ==================== PROJECT QUERIES ====================

@router.get(
    "/workspace/{workspace_id}",
    response_model=ProjectListResponse,
    summary="List workspace projects",
    description="Get all projects in workspace."
)
def list_workspace_projects(
    workspace_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List workspace projects."""
    try:
        service = ProjectService(db)
        skip = (page - 1) * page_size
        projects, total = service.list_workspace_projects(
            workspace_id,
            current_user.id,
            skip=skip,
            limit=page_size
        )
        
        return ProjectListResponse(
            items=projects,
            total=total,
            page=page,
            page_size=page_size,
            has_next=skip + page_size < total,
            has_previous=page > 1,
        )
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/user/mine",
    response_model=ProjectListResponse,
    summary="List user projects",
    description="Get all projects owned by current user."
)
def list_user_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user projects."""
    try:
        service = ProjectService(db)
        skip = (page - 1) * page_size
        projects, total = service.list_user_projects(
            current_user.id,
            skip=skip,
            limit=page_size
        )
        
        return ProjectListResponse(
            items=projects,
            total=total,
            page=page,
            page_size=page_size,
            has_next=skip + page_size < total,
            has_previous=page > 1,
        )
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/search/{workspace_id}",
    response_model=ProjectSearchResponse,
    summary="Search projects",
    description="Search projects in workspace."
)
def search_projects(
    workspace_id: UUID,
    query: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search projects."""
    try:
        service = ProjectService(db)
        skip = (page - 1) * page_size
        projects, total = service.search_projects(
            workspace_id,
            query,
            current_user.id,
            skip=skip,
            limit=page_size
        )
        
        return ProjectSearchResponse(
            items=projects,
            total=total,
            page=page,
            page_size=page_size,
            has_next=skip + page_size < total,
            has_previous=page > 1,
        )
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ==================== STATUS MANAGEMENT ====================

@router.put(
    "/{project_id}/status",
    response_model=ProjectResponse,
    summary="Update project status",
    description="Update project status. Only owner can update."
)
def update_status(
    project_id: UUID,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project status."""
    try:
        service = ProjectService(db)
        project = service.update_status(
            project_id,
            current_user.id,
            data.get("status")
        )
        return project
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ==================== STATISTICS ====================

@router.get(
    "/{project_id}/stats",
    response_model=ProjectStatsResponse,
    summary="Get project statistics",
    description="Get project task statistics."
)
def get_stats(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project statistics."""
    try:
        service = ProjectService(db)
        stats = service.get_stats(project_id, current_user.id)
        return stats
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
