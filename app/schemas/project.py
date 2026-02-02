"""
Pydantic schemas for Project-related API requests and responses.
Implements schemas for Functional Module 3: Project Lifecycle Management.
Ref: docs/01-Requirements/Functional-Modules/3 - Project Lifecycle Management.md
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.db.enums import (
    ProjectStatus,
    ProjectGovernanceMode,
    ProjectVisibility,
    ProjectRole,
    ProjectPriority,
    ChangeRequestStatus,
    ChangeRequestType,
    ProjectHealthStatus,
)


# ===== Project Base Schemas =====

class ProjectBase(BaseModel):
    """Base schema for project data"""
    name: str = Field(..., min_length=1, max_length=100, description="Project name (Max 100 characters)")
    description: Optional[str] = Field(None, description="Optional project description")
    start_date: Optional[date] = Field(None, description="Project start date")
    end_date: Optional[date] = Field(None, description="Project end date")
    
    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Validate that end_date >= start_date if both are provided"""
        if v is not None and info.data.get('start_date') is not None:
            if v < info.data['start_date']:
                raise ValueError('end_date must be >= start_date')
        return v


class ProjectCreate(ProjectBase):
    """
    Schema for creating a new project.
    Ref: Module 3 - Feature 2.1 - AC 1
    """
    workspace_id: UUID = Field(..., description="Workspace ID where project will be created")
    governance_mode: Optional[ProjectGovernanceMode] = Field(
        default=ProjectGovernanceMode.SIMPLE,
        description="Governance mode (SIMPLE or STRICT)"
    )
    visibility: Optional[ProjectVisibility] = Field(
        default=ProjectVisibility.PRIVATE,
        description="Project visibility"
    )
    priority: Optional[ProjectPriority] = Field(
        default=ProjectPriority.MEDIUM,
        description="Project priority"
    )


class ProjectUpdate(BaseModel):
    """
    Schema for updating project information.
    Ref: Module 3 - Feature 2.1 - AC 2
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    priority: Optional[ProjectPriority] = None
    
    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Validate that end_date >= start_date if both are provided"""
        if v is not None and info.data.get('start_date') is not None:
            if v < info.data['start_date']:
                raise ValueError('end_date must be >= start_date')
        return v


class ProjectStatusUpdate(BaseModel):
    """
    Schema for updating project status.
    Ref: Module 3 - Feature 2.2
    """
    status: ProjectStatus = Field(..., description="New project status")
    cancellation_reason: Optional[str] = Field(
        None,
        description="Required when transitioning to CANCELLED status"
    )
    
    @field_validator('cancellation_reason')
    @classmethod
    def validate_cancellation_reason(cls, v, info):
        """Require cancellation_reason when status is CANCELLED"""
        status = info.data.get('status')
        if status == ProjectStatus.CANCELLED and not v:
            raise ValueError('cancellation_reason is required when status is CANCELLED')
        return v


class ProjectResponse(ProjectBase):
    """Response schema for project"""
    id: UUID
    workspace_id: UUID
    owner_id: UUID
    status: ProjectStatus
    governance_mode: ProjectGovernanceMode
    visibility: ProjectVisibility
    priority: ProjectPriority
    is_deleted: bool
    deleted_at: Optional[datetime]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response with relationships"""
    member_count: Optional[int] = Field(None, description="Number of project members")
    task_count: Optional[int] = Field(None, description="Number of tasks")
    health_status: Optional[ProjectHealthStatus] = Field(None, description="Project health indicator")


class ProjectListResponse(BaseModel):
    """Paginated list of projects"""
    total: int
    items: List[ProjectResponse]


# ===== Project Member Schemas =====

class ProjectMemberBase(BaseModel):
    """Base schema for project member"""
    role: ProjectRole = Field(default=ProjectRole.MEMBER, description="Project role")


class ProjectMemberCreate(ProjectMemberBase):
    """
    Schema for adding a member to project.
    Ref: Module 3 - Feature 2.3 - AC 1
    """
    user_id: UUID = Field(..., description="User ID to add as project member")


class ProjectMemberUpdate(BaseModel):
    """Schema for updating project member role"""
    role: ProjectRole = Field(..., description="New role for member")


class ProjectMemberResponse(ProjectMemberBase):
    """Response schema for project member"""
    id: UUID
    project_id: UUID
    user_id: UUID
    joined_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Project Template Schemas =====

class ProjectTemplateBase(BaseModel):
    """Base schema for project template"""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: Optional[str] = Field(None, description="Template description")


class ProjectTemplateCreate(ProjectTemplateBase):
    """
    Schema for creating project template.
    Ref: Module 3 - Feature 2.6 - AC 1
    """
    workspace_id: UUID = Field(..., description="Workspace ID")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Template configuration (task lists, settings, etc.)"
    )
    is_global: bool = Field(default=False, description="Global template (admin only)")


class ProjectTemplateUpdate(BaseModel):
    """Schema for updating project template"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ProjectTemplateResponse(ProjectTemplateBase):
    """Response schema for project template"""
    id: UUID
    workspace_id: UUID
    is_global: bool
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]

    class Config:
        from_attributes = True


class ProjectFromTemplateCreate(BaseModel):
    """
    Schema for creating project from template.
    Ref: Module 3 - Feature 2.6 - AC 2
    """
    template_id: UUID = Field(..., description="Template ID to use")
    workspace_id: UUID = Field(..., description="Workspace ID")
    name: str = Field(..., min_length=1, max_length=100, description="New project name")
    start_date: Optional[date] = Field(None, description="Project start date for date remapping")
    copy_members: bool = Field(default=False, description="Copy template members to project")


# ===== Project Baseline Schemas =====

class ProjectBaselineBase(BaseModel):
    """Base schema for project baseline"""
    version: int = Field(..., description="Baseline version number")
    snapshot_ref: str = Field(..., description="Reference to snapshot")


class ProjectBaselineCreate(ProjectBaselineBase):
    """
    Schema for creating project baseline.
    Ref: Module 3 - Feature 2.13
    """
    project_id: UUID = Field(..., description="Project ID")
    snapshot_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot of project state"
    )


class ProjectBaselineResponse(ProjectBaselineBase):
    """Response schema for project baseline"""
    id: UUID
    project_id: UUID
    is_active: bool
    snapshot_data: Dict[str, Any]
    created_at: datetime
    created_by: Optional[UUID]

    class Config:
        from_attributes = True


# ===== Change Request Schemas =====

class ChangeRequestBase(BaseModel):
    """Base schema for change request"""
    title: str = Field(..., min_length=1, max_length=255, description="Change request title")
    description: Optional[str] = Field(None, description="Detailed description")


class ChangeRequestCreate(ChangeRequestBase):
    """
    Schema for creating change request.
    Ref: Module 3 - Feature 2.11 - AC 1
    """
    project_id: UUID = Field(..., description="Project ID")
    type: ChangeRequestType = Field(..., description="Type of change")
    impact_assessment: Optional[str] = Field(None, description="Impact assessment")


class ChangeRequestUpdate(BaseModel):
    """Schema for updating change request"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    impact_assessment: Optional[str] = None


class ChangeRequestApprove(BaseModel):
    """
    Schema for approving/rejecting change request.
    Ref: Module 3 - Feature 2.11 - AC 2
    """
    status: ChangeRequestStatus = Field(
        ...,
        description="Approval decision (APPROVED or REJECTED)"
    )
    reason: Optional[str] = Field(None, description="Reason for decision")


class ChangeRequestResponse(ChangeRequestBase):
    """Response schema for change request"""
    id: UUID
    project_id: UUID
    type: ChangeRequestType
    status: ChangeRequestStatus
    impact_assessment: Optional[str]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]

    class Config:
        from_attributes = True


# ===== Project Archive Schemas =====

class ProjectArchiveCreate(BaseModel):
    """
    Schema for archiving project.
    Ref: Module 3 - Feature 2.5 & 2.12
    """
    project_id: UUID = Field(..., description="Project ID to archive")
    reason: Optional[str] = Field(None, description="Reason for archival")
    archive_location: Optional[str] = Field(None, description="Storage location")


class ProjectArchiveResponse(BaseModel):
    """Response schema for project archive"""
    id: UUID
    project_id: UUID
    reason: Optional[str]
    archive_location: Optional[str]
    created_at: datetime
    created_by: Optional[UUID]

    class Config:
        from_attributes = True


# ===== Project Clone/Duplicate Schemas =====

class ProjectClone(BaseModel):
    """
    Schema for cloning/duplicating project.
    Ref: Module 3 - Feature 2.1 - AC 3
    """
    name: str = Field(..., min_length=1, max_length=100, description="Name for cloned project")
    copy_structure: bool = Field(default=True, description="Copy task lists and settings")
    copy_tasks: bool = Field(default=False, description="Copy tasks (usually not selected)")
    copy_members: bool = Field(default=False, description="Copy project members")


# ===== Project Health & Metrics Schemas =====

class ProjectHealthUpdate(BaseModel):
    """
    Schema for updating project health (manual override).
    Ref: Module 3 - Feature 2.10 - AC 3
    """
    health_status: ProjectHealthStatus = Field(..., description="Health status")
    reason: str = Field(..., min_length=1, description="Reason for manual override (required)")


class ProjectMetricsResponse(BaseModel):
    """Response schema for project metrics"""
    project_id: UUID
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    completion_percentage: float
    health_status: ProjectHealthStatus
    schedule_health: Optional[str]
    resource_health: Optional[str]
    budget_health: Optional[str]
