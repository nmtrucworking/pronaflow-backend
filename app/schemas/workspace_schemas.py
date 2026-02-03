"""
Pydantic schemas for Workspace API
Request/Response models for workspace operations
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
import uuid
from app.db.enums import WorkspaceRole


# ==================== WORKSPACE SCHEMAS ====================

class WorkspaceBase(BaseModel):
    """Base workspace schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Workspace name")
    description: Optional[str] = Field(None, max_length=1000, description="Workspace description")


class WorkspaceCreate(WorkspaceBase):
    """Schema for creating a workspace."""
    pass


class WorkspaceUpdate(BaseModel):
    """Schema for updating a workspace."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)


class WorkspaceResponse(WorkspaceBase):
    """Schema for workspace response."""
    id: uuid.UUID
    owner_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkspaceDetailResponse(WorkspaceResponse):
    """Detailed workspace response with members count."""
    member_count: int = Field(description="Number of workspace members")
    
    class Config:
        from_attributes = True


# ==================== WORKSPACE MEMBER SCHEMAS ====================

class WorkspaceMemberBase(BaseModel):
    """Base workspace member schema."""
    user_id: uuid.UUID = Field(..., description="User ID")
    role: WorkspaceRole = Field(default=WorkspaceRole.MEMBER, description="Member role")


class WorkspaceMemberCreate(WorkspaceMemberBase):
    """Schema for adding a member to workspace."""
    pass


class WorkspaceMemberUpdate(BaseModel):
    """Schema for updating member role."""
    role: WorkspaceRole = Field(..., description="New role")


class WorkspaceMemberResponse(WorkspaceMemberBase):
    """Schema for workspace member response."""
    id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class WorkspaceMemberDetailResponse(WorkspaceMemberResponse):
    """Detailed member response with user info."""
    user_email: str
    user_name: str
    
    class Config:
        from_attributes = True


# ==================== WORKSPACE INVITATION SCHEMAS ====================

class WorkspaceInvitationCreate(BaseModel):
    """Schema for creating workspace invitation."""
    email: EmailStr = Field(..., description="Email to invite")
    role: WorkspaceRole = Field(default=WorkspaceRole.MEMBER)


class WorkspaceInvitationResponse(BaseModel):
    """Schema for invitation response."""
    id: uuid.UUID
    workspace_id: uuid.UUID
    email: str
    role: WorkspaceRole
    status: str
    created_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True


# ==================== WORKSPACE SETTINGS SCHEMAS ====================

class WorkspaceSettingsBase(BaseModel):
    """Base workspace settings schema."""
    enable_public_access: bool = Field(default=False)
    allow_guest_access: bool = Field(default=False)
    auto_archive_inactive_days: Optional[int] = Field(None, ge=7, le=365)


class WorkspaceSettingsUpdate(WorkspaceSettingsBase):
    """Schema for updating workspace settings."""
    pass


class WorkspaceSettingsResponse(WorkspaceSettingsBase):
    """Schema for settings response."""
    id: uuid.UUID
    workspace_id: uuid.UUID
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== LIST/PAGINATION SCHEMAS ====================

class WorkspaceListResponse(BaseModel):
    """Paginated workspace list response."""
    items: List[WorkspaceResponse]
    total: int
    skip: int
    limit: int
    page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class WorkspaceMemberListResponse(BaseModel):
    """Paginated member list response."""
    items: List[WorkspaceMemberDetailResponse]
    total: int
    skip: int
    limit: int
    page: int
    total_pages: int
    has_next: bool
    has_previous: bool
