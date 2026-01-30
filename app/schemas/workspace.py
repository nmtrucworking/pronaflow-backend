"""
Pydantic schemas for Workspace-related API requests and responses.
Ref: docs/docs - PronaFlow React&FastAPI/02-Architeture/Entities/Workspace*.md
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, EmailStr


class WorkspaceRoleEnum(str, Enum):
    """Workspace role enumeration"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"
    GUEST = "guest"


# ===== Base Schemas =====

class WorkspaceBase(BaseModel):
    """Base schema for workspace data"""
    name: str = Field(..., min_length=1, max_length=50, description="Workspace name (Max 50 characters)")
    description: Optional[str] = Field(None, description="Optional workspace description")


class WorkspaceCreate(WorkspaceBase):
    """Schema for creating a new workspace"""
    pass


class WorkspaceUpdate(BaseModel):
    """Schema for updating workspace information"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Workspace name")
    description: Optional[str] = Field(None, description="Workspace description")
    status: Optional[str] = Field(None, description="Workspace status")


class WorkspaceResponse(WorkspaceBase):
    """Response schema for workspace (without members)"""
    id: UUID
    owner_id: UUID
    status: str
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Workspace Member Schemas =====

class WorkspaceMemberBase(BaseModel):
    """Base schema for workspace member data"""
    role: WorkspaceRoleEnum = Field(default=WorkspaceRoleEnum.MEMBER, description="Member role in workspace")


class WorkspaceMemberCreate(WorkspaceMemberBase):
    """Schema for adding a member to workspace"""
    user_id: UUID = Field(..., description="User ID to add as member")


class WorkspaceMemberUpdate(BaseModel):
    """Schema for updating workspace member"""
    role: Optional[WorkspaceRoleEnum] = Field(None, description="New role for member")
    is_active: Optional[bool] = Field(None, description="Active status of member")


class WorkspaceMemberResponse(WorkspaceMemberBase):
    """Response schema for workspace member"""
    id: UUID
    workspace_id: UUID
    user_id: UUID
    is_active: bool
    joined_at: datetime
    left_at: Optional[datetime]

    class Config:
        from_attributes = True


# ===== Workspace Invitation Schemas =====

class WorkspaceInvitationBase(BaseModel):
    """Base schema for workspace invitation"""
    email: EmailStr = Field(..., description="Email address of invited user")
    invited_role: WorkspaceRoleEnum = Field(default=WorkspaceRoleEnum.MEMBER, description="Role to assign")


class WorkspaceInvitationCreate(WorkspaceInvitationBase):
    """Schema for creating a workspace invitation"""
    pass


class WorkspaceInvitationAccept(BaseModel):
    """Schema for accepting workspace invitation"""
    token: str = Field(..., description="Invitation token")


class WorkspaceInvitationResponse(WorkspaceInvitationBase):
    """Response schema for workspace invitation"""
    id: UUID
    workspace_id: UUID
    invited_by: Optional[UUID]
    token_hash: str
    expires_at: datetime
    accepted_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Workspace Settings Schemas =====

class WorkspaceSettingBase(BaseModel):
    """Base schema for workspace settings"""
    timezone: Optional[str] = Field(None, description="Workspace timezone")
    work_days: Optional[str] = Field(None, description="Working days")
    work_hours: Optional[str] = Field(None, description="Working hours")
    logo_url: Optional[str] = Field(None, description="Logo URL")


class WorkspaceSettingCreate(WorkspaceSettingBase):
    """Schema for creating workspace settings"""
    pass


class WorkspaceSettingUpdate(WorkspaceSettingBase):
    """Schema for updating workspace settings"""
    pass


class WorkspaceSettingResponse(WorkspaceSettingBase):
    """Response schema for workspace settings"""
    workspace_id: UUID
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Access Log Schemas =====

class WorkspaceAccessLogResponse(BaseModel):
    """Response schema for workspace access log"""
    id: UUID
    user_id: UUID
    workspace_id: UUID
    created_at: datetime  # accessed_at maps to created_at

    class Config:
        from_attributes = True


# ===== Composite Schemas =====

class WorkspaceDetailResponse(WorkspaceResponse):
    """Extended response schema for workspace with members and settings"""
    members: List[WorkspaceMemberResponse] = []
    settings: Optional[WorkspaceSettingResponse] = None


class WorkspaceListResponse(BaseModel):
    """Response schema for workspace list"""
    total: int
    items: List[WorkspaceResponse]


class WorkspaceContextSwitch(BaseModel):
    """Schema for switching workspace context"""
    workspace_id: UUID = Field(..., description="Workspace ID to switch to")
