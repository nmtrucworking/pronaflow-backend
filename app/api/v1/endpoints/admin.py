"""
Admin API endpoints for System Administration.
Provides admin-only endpoints for managing workspaces and system operations.
Ref: Module 2 - System Admin Governance
"""
from typing import List
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.db.models.users import User
from app.schemas.workspace import (
    WorkspaceResponse,
    WorkspaceListResponse,
)
from app.services.workspace import WorkspaceService
from app.repositories.workspace_repository import WorkspaceRepository


router = APIRouter(prefix="/v1/admin", tags=["admin"])


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to verify user is system admin.
    In production, check against a proper admin role or permission.
    """
    # TODO: Implement proper admin role checking
    # For now, check if user has admin flag or specific role
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


# ===== Admin Workspace Management =====

@router.get(
    "/workspaces/deleted",
    response_model=WorkspaceListResponse,
    summary="List deleted workspaces (Admin only)",
)
def list_deleted_workspaces(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    older_than_days: int = Query(None, ge=1, description="Filter workspaces deleted more than X days ago"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    List all soft-deleted workspaces.
    
    **Module 2 - AC 2: System Admin Governance**
    - System admin can view all deleted workspaces
    - Can filter by deletion date
    - Used for restore or cleanup operations
    
    **Admin Only:** This endpoint requires system administrator privileges
    """
    workspace_repo = WorkspaceRepository(db)
    workspaces, total = workspace_repo.list_deleted(
        skip=skip,
        limit=limit,
        older_than_days=older_than_days
    )
    
    return WorkspaceListResponse(total=total, items=workspaces)


@router.post(
    "/workspaces/{workspace_id}/restore",
    response_model=WorkspaceResponse,
    summary="Restore deleted workspace (Admin only)",
)
def restore_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    Restore a soft-deleted workspace.
    
    **Module 2 - AC 2: Restore Capability**
    - Admin can search workspace by ID or Name
    - Restore button reinstates access for owner and members
    - Workspace becomes active again
    
    **Admin Only:** This endpoint requires system administrator privileges
    """
    workspace_repo = WorkspaceRepository(db)
    
    # Get workspace including deleted ones
    workspace = workspace_repo.get_by_id(workspace_id, include_deleted=True)
    
    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )
    
    if not workspace.is_deleted:
        raise HTTPException(
            status_code=400,
            detail="Workspace is not deleted"
        )
    
    # Restore workspace
    restored = workspace_repo.restore(workspace)
    db.commit()
    db.refresh(restored)
    
    return restored


@router.delete(
    "/workspaces/{workspace_id}/hard-delete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Permanently delete workspace (Admin only)",
)
def hard_delete_workspace(
    workspace_id: UUID,
    confirm: bool = Query(..., description="Confirmation flag to prevent accidental deletion"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    Permanently delete a workspace from database.
    
    **Module 2 - AC 1: Auto-Purge Policy**
    - Manual trigger for hard deletion
    - Removes workspace and all related data permanently
    - Cannot be undone
    
    **Admin Only:** This endpoint requires system administrator privileges
    **Warning:** This operation is irreversible!
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required for hard deletion"
        )
    
    workspace_repo = WorkspaceRepository(db)
    
    # Get workspace including deleted ones
    workspace = workspace_repo.get_by_id(workspace_id, include_deleted=True)
    
    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )
    
    # Hard delete
    success = workspace_repo.hard_delete(workspace_id)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete workspace"
        )
    
    db.commit()


@router.post(
    "/workspaces/cleanup",
    summary="Cleanup old deleted workspaces (Admin only)",
)
def cleanup_old_workspaces(
    days: int = Query(30, ge=1, description="Delete workspaces older than X days"),
    dry_run: bool = Query(True, description="If true, only return count without deleting"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    Cleanup (hard delete) workspaces that have been soft-deleted for more than X days.
    
    **Module 2 - AC 1: Auto-Purge Policy**
    - Implements the 30-day auto-purge policy
    - Can be run manually or scheduled
    - Dry-run mode to preview what will be deleted
    
    **Admin Only:** This endpoint requires system administrator privileges
    """
    workspace_repo = WorkspaceRepository(db)
    
    # Get workspaces to be deleted
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    workspaces, total = workspace_repo.list_deleted(older_than_days=days, limit=1000)
    
    if dry_run:
        return {
            "dry_run": True,
            "workspaces_to_delete": total,
            "cutoff_date": cutoff_date.isoformat(),
            "message": f"Would delete {total} workspaces deleted before {cutoff_date.date()}"
        }
    
    # Hard delete all old workspaces
    deleted_count = 0
    for workspace in workspaces:
        success = workspace_repo.hard_delete(workspace.id)
        if success:
            deleted_count += 1
    
    db.commit()
    
    return {
        "dry_run": False,
        "deleted_count": deleted_count,
        "cutoff_date": cutoff_date.isoformat(),
        "message": f"Successfully deleted {deleted_count} workspaces"
    }


# ===== Admin User Management =====

@router.get(
    "/users/{user_id}/workspaces",
    response_model=WorkspaceListResponse,
    summary="List all workspaces for a user (Admin only)",
)
def list_user_workspaces_admin(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_inactive: bool = Query(False, description="Include inactive memberships"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    List all workspaces for a specific user (admin view).
    
    **Admin Only:** This endpoint requires system administrator privileges
    """
    workspaces, total = WorkspaceService.list_user_workspaces(
        db, user_id, skip, limit
    )
    
    return WorkspaceListResponse(total=total, items=workspaces)
