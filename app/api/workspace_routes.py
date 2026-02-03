"""
Workspace API Routes - Module 2
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.db.models.users import User
from app.schemas.workspace_schemas import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceDetailResponse,
    WorkspaceListResponse,
    WorkspaceMemberResponse,
    WorkspaceInvitationCreate,
    WorkspaceInvitationResponse,
    WorkspaceSettingsUpdate,
)
from app.services.workspace_service import WorkspaceService
from app.utils.exceptions import PronaFlowException
from app.utils.pagination import PaginationParams

router = APIRouter(prefix="/api/v1/workspaces", tags=["workspaces"])


# ==================== WORKSPACE CRUD ====================

@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create workspace",
    description="Create a new workspace. Current user becomes the owner."
)
def create_workspace(
    data: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new workspace."""
    try:
        service = WorkspaceService(db)
        workspace = service.create_workspace(
            user_id=current_user.id,
            name=data.name,
            description=data.description,
            avatar_url=data.avatar_url,
        )
        return workspace
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceDetailResponse,
    summary="Get workspace",
    description="Get workspace details. User must be a member."
)
def get_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get workspace details."""
    try:
        service = WorkspaceService(db)
        workspace = service.get_workspace(workspace_id, current_user.id)
        return workspace
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Update workspace",
    description="Update workspace details. Only owner can update."
)
def update_workspace(
    workspace_id: UUID,
    data: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update workspace."""
    try:
        service = WorkspaceService(db)
        workspace = service.update_workspace(
            workspace_id=workspace_id,
            user_id=current_user.id,
            name=data.name,
            description=data.description,
            avatar_url=data.avatar_url,
        )
        return workspace
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workspace",
    description="Delete workspace. Only owner can delete."
)
def delete_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete workspace."""
    try:
        service = WorkspaceService(db)
        service.delete_workspace(workspace_id, current_user.id)
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ==================== WORKSPACE QUERIES ====================

@router.get(
    "",
    response_model=WorkspaceListResponse,
    summary="List user workspaces",
    description="Get all workspaces for current user."
)
def list_workspaces(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user workspaces."""
    try:
        service = WorkspaceService(db)
        skip = (page - 1) * page_size
        workspaces, total = service.list_user_workspaces(
            current_user.id,
            skip=skip,
            limit=page_size
        )
        
        return WorkspaceListResponse(
            items=workspaces,
            total=total,
            page=page,
            page_size=page_size,
            has_next=skip + page_size < total,
            has_previous=page > 1,
        )
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "",
    response_model=WorkspaceListResponse,
    summary="Search workspaces",
    description="Search workspaces by name.",
)
def search_workspaces(
    query: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search workspaces."""
    try:
        service = WorkspaceService(db)
        skip = (page - 1) * page_size
        workspaces, total = service.search_workspaces(
            query=query,
            user_id=current_user.id,
            skip=skip,
            limit=page_size
        )
        
        return WorkspaceListResponse(
            items=workspaces,
            total=total,
            page=page,
            page_size=page_size,
            has_next=skip + page_size < total,
            has_previous=page > 1,
        )
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ==================== MEMBERS MANAGEMENT ====================

@router.get(
    "/{workspace_id}/members",
    response_model=list[WorkspaceMemberResponse],
    summary="Get workspace members",
    description="Get all members in workspace."
)
def get_members(
    workspace_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get workspace members."""
    try:
        service = WorkspaceService(db)
        skip = (page - 1) * page_size
        members, total = service.get_members(
            workspace_id,
            current_user.id,
            skip=skip,
            limit=page_size
        )
        return members
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add member",
    description="Add member to workspace. Admin role required."
)
def add_member(
    workspace_id: UUID,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add member to workspace."""
    try:
        service = WorkspaceService(db)
        member = service.add_member(
            workspace_id=workspace_id,
            user_id=current_user.id,
            member_user_id=UUID(data.get("user_id")),
            role=data.get("role", "member"),
        )
        return member
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete(
    "/{workspace_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove member",
    description="Remove member from workspace. Admin role required."
)
def remove_member(
    workspace_id: UUID,
    member_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove member from workspace."""
    try:
        service = WorkspaceService(db)
        service.remove_member(workspace_id, current_user.id, member_id)
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put(
    "/{workspace_id}/members/{member_id}/role",
    response_model=WorkspaceMemberResponse,
    summary="Update member role",
    description="Update member role. Admin role required."
)
def update_member_role(
    workspace_id: UUID,
    member_id: UUID,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update member role."""
    try:
        service = WorkspaceService(db)
        member = service.update_member_role(
            workspace_id=workspace_id,
            user_id=current_user.id,
            member_user_id=member_id,
            new_role=data.get("role"),
        )
        return member
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ==================== STATISTICS ====================

@router.get(
    "/{workspace_id}/stats",
    summary="Get workspace statistics",
    description="Get workspace statistics (projects, members, tasks)."
)
def get_stats(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get workspace statistics."""
    try:
        service = WorkspaceService(db)
        stats = service.get_stats(workspace_id, current_user.id)
        return stats
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
