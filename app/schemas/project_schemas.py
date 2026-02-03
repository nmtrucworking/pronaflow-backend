"""
Pydantic schemas for Project API
Request/Response models for project operations
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date
import uuid
from app.db.enums import ProjectStatus, ProjectVisibility, ProjectGovernanceMode, ProjectPriority


# ==================== PROJECT SCHEMAS ====================

class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    visibility: ProjectVisibility = Field(default=ProjectVisibility.PRIVATE)
    governance_mode: ProjectGovernanceMode = Field(default=ProjectGovernanceMode.SIMPLE)


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    workspace_id: uuid.UUID = Field(..., description="Workspace ID")


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[ProjectStatus] = None
    visibility: Optional[ProjectVisibility] = None
    governance_mode: Optional[ProjectGovernanceMode] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: uuid.UUID
    workspace_id: uuid.UUID
    owner_id: uuid.UUID
    status: ProjectStatus
    start_date: Optional[date]
    end_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response with statistics."""
    task_count: int = Field(description="Total number of tasks")
    completed_task_count: int = Field(description="Number of completed tasks")
    member_count: int = Field(description="Number of project members")
    
    class Config:
        from_attributes = True


# ==================== PROJECT MEMBER SCHEMAS ====================

class ProjectMemberResponse(BaseModel):
    """Schema for project member."""
    id: uuid.UUID
    user_id: uuid.UUID
    user_email: str
    user_name: str
    role: str
    joined_at: datetime
    
    class Config:
        from_attributes = True


class ProjectMemberListResponse(BaseModel):
    """Paginated project member list."""
    items: List[ProjectMemberResponse]
    total: int
    skip: int
    limit: int


# ==================== PROJECT STATISTICS SCHEMAS ====================

class ProjectStatsResponse(BaseModel):
    """Schema for project statistics."""
    total_tasks: int
    todo: int
    in_progress: int
    in_review: int
    done: int
    completion_percentage: float
    overdue_count: int
    total_members: int


# ==================== LIST/PAGINATION SCHEMAS ====================

class ProjectListResponse(BaseModel):
    """Paginated project list response."""
    items: List[ProjectResponse]
    total: int
    skip: int
    limit: int
    page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ProjectSearchResponse(BaseModel):
    """Project search results."""
    items: List[ProjectResponse]
    query: str
    total: int
    
    class Config:
        from_attributes = True
