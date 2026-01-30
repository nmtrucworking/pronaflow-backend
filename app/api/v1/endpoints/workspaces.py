"""
API endpoints for Workspace management.
Provides REST API for workspace CRUD, member management, and invitations.
Ref: docs/docs - PronaFlow React&FastAPI/01-Requirements/Functional-Modules/2 - Multi-tenancy Workspace Governance.md
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.db.models.users import User
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceDetailResponse,
    WorkspaceListResponse,
    WorkspaceMemberResponse,
    WorkspaceMemberCreate,
    WorkspaceMemberUpdate,
    WorkspaceInvitationCreate,
    WorkspaceInvitationResponse,
    WorkspaceInvitationAccept,
    WorkspaceAccessLogResponse,
    WorkspaceSettingResponse,
    WorkspaceSettingUpdate,
    WorkspaceContextSwitch,
)
from app.services.workspace import (
    WorkspaceService,
    WorkspaceMemberService,
    WorkspaceInvitationService,
    WorkspaceAccessLogService,
    WorkspaceSettingService,
)

router = APIRouter(prefix="/v1/workspaces", tags=["workspaces"])


# ===== Workspace CRUD Operations =====

@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new workspace",
)
def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new workspace.
    
    **AC 1 - Khởi tạo thành công:**
    - User inputs Workspace Name (Required, Max 50 chars) and Description (Optional)
    - System creates new Workspace record
    - Assigns current user as Owner
    - Auto-switches context to new workspace
    """
    workspace = WorkspaceService.create_workspace(db, workspace_data, current_user.id)

    # Log access (context switch to new workspace)
    WorkspaceAccessLogService.log_access(db, workspace.id, current_user.id)

    return workspace


@router.get(
    "",
    response_model=WorkspaceListResponse,
    summary="List user workspaces",
)
def list_workspaces(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all workspaces for the current user.
    Returns only active workspaces where user is a member.
    """
    workspaces, total = WorkspaceService.list_user_workspaces(
        db, current_user.id, skip, limit
    )

    return WorkspaceListResponse(total=total, items=workspaces)


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceDetailResponse,
    summary="Get workspace details",
)
def get_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a workspace including members and settings.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check if user is member
    member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not member or not member.is_active:
        raise HTTPException(
            status_code=403, detail="Not a member of this workspace"
        )

    return workspace


@router.put(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Update workspace",
)
def update_workspace(
    workspace_id: UUID,
    update_data: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update workspace information.
    Only workspace owner or admin can update.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check authorization
    member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    updated = WorkspaceService.update_workspace(db, workspace_id, update_data)
    return updated


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workspace",
)
def delete_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Soft delete a workspace.
    Only workspace owner can delete.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check authorization - only owner
    if workspace.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can delete workspace")

    WorkspaceService.delete_workspace(db, workspace_id)


# ===== Workspace Member Operations =====

@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add workspace member",
)
def add_member(
    workspace_id: UUID,
    member_data: WorkspaceMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a member to workspace.
    Only admin or owner can add members.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check authorization
    current_member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not current_member or current_member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    member = WorkspaceMemberService.add_member(db, workspace_id, member_data)
    if not member:
        raise HTTPException(status_code=400, detail="User not found or already member")

    return member


@router.get(
    "/{workspace_id}/members",
    response_model=List[WorkspaceMemberResponse],
    summary="List workspace members",
)
def list_members(
    workspace_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all members of a workspace.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check if user is member
    member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not member or not member.is_active:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")

    members, _ = WorkspaceMemberService.list_members(db, workspace_id, skip, limit)
    return members


@router.put(
    "/{workspace_id}/members/{user_id}",
    response_model=WorkspaceMemberResponse,
    summary="Update member role/status",
)
def update_member(
    workspace_id: UUID,
    user_id: UUID,
    update_data: WorkspaceMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a member's role or active status.
    Only admin or owner can update.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check authorization
    current_member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not current_member or current_member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    member = WorkspaceMemberService.update_member(db, workspace_id, user_id, update_data)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    return member


@router.delete(
    "/{workspace_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove workspace member",
)
def remove_member(
    workspace_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove a member from workspace.
    Only admin or owner can remove.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check authorization
    current_member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not current_member or current_member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    success = WorkspaceMemberService.remove_member(db, workspace_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")


# ===== Workspace Invitation Operations =====

@router.post(
    "/{workspace_id}/invitations",
    response_model=WorkspaceInvitationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send workspace invitation",
)
def send_invitation(
    workspace_id: UUID,
    invitation_data: WorkspaceInvitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send an invitation to join workspace via email.
    Invitation expires after 48 hours.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check authorization
    current_member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not current_member or current_member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    invitation = WorkspaceInvitationService.create_invitation(
        db, workspace_id, current_user.id, invitation_data
    )

    # TODO: Send invitation email with magic link
    # email_service.send_invitation(invitation.email, invitation.token, workspace.name)

    return invitation


@router.get(
    "/{workspace_id}/invitations",
    response_model=List[WorkspaceInvitationResponse],
    summary="List pending invitations",
)
def list_invitations(
    workspace_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List pending invitations for a workspace.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check authorization
    current_member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not current_member or current_member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    invitations, _ = WorkspaceInvitationService.list_pending_invitations(
        db, workspace_id, skip, limit
    )
    return invitations


@router.delete(
    "/{workspace_id}/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel invitation",
)
def cancel_invitation(
    workspace_id: UUID,
    invitation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancel a pending invitation.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check authorization
    current_member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not current_member or current_member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    success = WorkspaceInvitationService.cancel_invitation(db, invitation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Invitation not found or already accepted")


# ===== Workspace Settings Operations =====

@router.get(
    "/{workspace_id}/settings",
    response_model=WorkspaceSettingResponse,
    summary="Get workspace settings",
)
def get_settings(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get workspace configuration settings.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check if user is member
    member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not member or not member.is_active:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")

    settings = WorkspaceSettingService.get_settings(db, workspace_id)
    if not settings:
        raise HTTPException(status_code=404, detail="Workspace settings not found")

    return settings


@router.put(
    "/{workspace_id}/settings",
    response_model=WorkspaceSettingResponse,
    summary="Update workspace settings",
)
def update_settings(
    workspace_id: UUID,
    update_data: WorkspaceSettingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update workspace configuration settings.
    Only admin or owner can update.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check authorization
    current_member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not current_member or current_member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    settings = WorkspaceSettingService.update_settings(db, workspace_id, update_data)
    if not settings:
        raise HTTPException(status_code=404, detail="Workspace settings not found")

    return settings


# ===== Workspace Context Switch =====

@router.post(
    "/{workspace_id}/access",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Switch workspace context",
)
def switch_context(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Log user's access to workspace (context switch).
    Used for tracking workspace navigation and audit logging.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check if user is active member
    member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not member or not member.is_active:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")

    WorkspaceAccessLogService.log_access(db, workspace_id, current_user.id)


# ===== Workspace Access History =====

@router.get(
    "/{workspace_id}/access-logs",
    response_model=List[WorkspaceAccessLogResponse],
    summary="Get access logs",
)
def get_access_logs(
    workspace_id: UUID,
    user_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get workspace access history for audit purposes.
    Only admin or owner can view.
    """
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check authorization
    current_member = WorkspaceMemberService.get_member(db, workspace_id, current_user.id)
    if not current_member or current_member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    logs, _ = WorkspaceAccessLogService.get_access_history(
        db, workspace_id, user_id, skip, limit
    )
    return logs
