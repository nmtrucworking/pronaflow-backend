"""
Pydantic schemas for scheduling and planning module.
Implements schemas for Functional Module 5: Temporal Planning and Scheduling.
Ref: docs/01-Requirements/Functional-Modules/5 - Temporal Planning and Scheduling.md
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.db.enums import (
    PlanStateEnum,
    SchedulingModeEnum,
    DependencyTypeEnum,
    SLAStatusEnum,
    PersonalExceptionType,
    ZoomLevel,
    ResourceLevelingStrategy,
)


# ===== Plan State Schemas =====

class PlanStateBase(BaseModel):
    """Base schema for plan state"""
    state: PlanStateEnum = Field(default=PlanStateEnum.DRAFT, description="Plan state")


class PlanStateResponse(PlanStateBase):
    """Response schema for plan state"""
    id: UUID
    project_id: UUID
    submitted_by: Optional[UUID]
    submitted_at: Optional[datetime]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    locked_by: Optional[UUID]
    locked_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Task Baseline Schemas =====

class TaskBaselineCreate(BaseModel):
    """
    Schema for creating task baseline.
    Ref: Module 5 - Feature 2.4 - AC 1 - Create Snapshot
    """
    task_id: UUID = Field(..., description="Task ID")
    baseline_version: int = Field(default=1, ge=1, description="Baseline version")


class TaskBaselineResponse(BaseModel):
    """Response schema for task baseline"""
    id: UUID
    task_id: UUID
    baseline_version: int
    
    baseline_start: datetime
    baseline_end: datetime
    baseline_duration_hours: float
    
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    actual_duration_hours: Optional[float]
    
    schedule_variance_days: Optional[float]
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Scheduling Mode Schemas =====

class SchedulingModeCreate(BaseModel):
    """
    Schema for setting task scheduling mode.
    Ref: Module 5 - Feature 2.2 - AC 3 - Scheduling Mode
    """
    task_id: UUID = Field(..., description="Task ID")
    mode: SchedulingModeEnum = Field(default=SchedulingModeEnum.AUTO, description="AUTO or MANUAL")
    is_pinned: bool = Field(default=False, description="Pinned (manually scheduled)?")


class SchedulingModeUpdate(BaseModel):
    """Schema for updating scheduling mode"""
    mode: Optional[SchedulingModeEnum]
    is_pinned: Optional[bool]


class SchedulingModeResponse(BaseModel):
    """Response schema for scheduling mode"""
    id: UUID
    task_id: UUID
    mode: SchedulingModeEnum
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Dependency Schedule Schemas =====

class TaskDependencyScheduleCreate(BaseModel):
    """
    Schema for configuring lag/lead time on dependencies.
    Ref: Module 5 - Feature 2.2 - AC 4 - Lag & Lead Time
    """
    dependency_id: UUID = Field(..., description="Task dependency ID")
    lag_days: int = Field(default=0, description="Lag (positive) or lead (negative) time in days")


class TaskDependencyScheduleUpdate(BaseModel):
    """Schema for updating dependency schedule"""
    lag_days: Optional[int]
    is_auto_scheduled: Optional[bool]
    is_pinned: Optional[bool]


class TaskDependencyScheduleResponse(BaseModel):
    """Response schema for dependency schedule"""
    id: UUID
    dependency_id: UUID
    lag_days: int
    is_auto_scheduled: bool
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== SLA Policy Schemas =====

class SLAPolicyCreate(BaseModel):
    """
    Schema for creating SLA policy.
    Ref: Module 5 - Feature 2.7 - AC 1 - SLA Definition
    """
    project_id: UUID = Field(..., description="Project ID")
    priority: str = Field(..., description="CRITICAL, HIGH, MEDIUM, LOW")
    sla_hours: int = Field(..., ge=1, description="SLA target in working hours")
    warning_threshold_percent: int = Field(default=75, ge=1, le=100, description="Warning threshold (%)")
    enable_escalation: bool = Field(default=True, description="Enable escalation?")
    escalation_level_1_hours: Optional[int] = Field(None, ge=1, description="Hours after breach for L1")
    escalation_level_2_hours: Optional[int] = Field(None, ge=1, description="Hours after breach for L2")


class SLAPolicyUpdate(BaseModel):
    """Schema for updating SLA policy"""
    sla_hours: Optional[int]
    warning_threshold_percent: Optional[int]
    enable_escalation: Optional[bool]
    escalation_level_1_hours: Optional[int]
    escalation_level_2_hours: Optional[int]


class SLAPolicyResponse(BaseModel):
    """Response schema for SLA policy"""
    id: UUID
    project_id: UUID
    priority: str
    sla_hours: int
    warning_threshold_percent: int
    enable_escalation: bool
    escalation_level_1_hours: Optional[int]
    escalation_level_2_hours: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== SLA Tracker Schemas =====

class SLATrackerResponse(BaseModel):
    """Response schema for SLA tracker"""
    id: UUID
    task_id: UUID
    status: SLAStatusEnum
    
    sla_start_time: datetime
    sla_breach_time: Optional[datetime]
    sla_deadline: datetime
    
    elapsed_business_seconds: int
    paused_business_seconds: int
    is_paused: bool
    pause_reason: Optional[str]
    
    escalation_level_1_triggered: bool
    escalation_level_1_at: Optional[datetime]
    escalation_level_2_triggered: bool
    escalation_level_2_at: Optional[datetime]
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Working Hours Policy Schemas =====

class WorkingHoursPolicyCreate(BaseModel):
    """
    Schema for creating working hours policy.
    Ref: Module 5 - Business Rule 3.2
    """
    workspace_id: UUID = Field(..., description="Workspace ID")
    working_days_mask: int = Field(default=0b0111110, description="Bitmask: 0=Mon...6=Sun")
    work_start_time: str = Field(default="09:00", description="HH:MM format")
    work_end_time: str = Field(default="18:00", description="HH:MM format")
    lunch_start_time: Optional[str] = Field(None, description="Lunch break start")
    lunch_end_time: Optional[str] = Field(None, description="Lunch break end")
    timezone: str = Field(default="UTC", description="Timezone for calculations")


class WorkingHoursPolicyUpdate(BaseModel):
    """Schema for updating working hours policy"""
    working_days_mask: Optional[int]
    work_start_time: Optional[str]
    work_end_time: Optional[str]
    lunch_start_time: Optional[str]
    lunch_end_time: Optional[str]
    timezone: Optional[str]


class WorkingHoursPolicyResponse(BaseModel):
    """Response schema for working hours policy"""
    id: UUID
    workspace_id: UUID
    working_days_mask: int
    work_start_time: str
    work_end_time: str
    lunch_start_time: Optional[str]
    lunch_end_time: Optional[str]
    timezone: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Holiday Calendar Schemas =====

class HolidayCalendarCreate(BaseModel):
    """Schema for creating holiday entry"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    holiday_date: datetime = Field(..., description="Date of holiday")
    name: str = Field(..., max_length=255, description="Holiday name")
    is_recurring: bool = Field(default=False, description="Recurs yearly?")


class HolidayCalendarResponse(BaseModel):
    """Response schema for holiday calendar"""
    id: UUID
    workspace_id: UUID
    holiday_date: datetime
    name: str
    is_recurring: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Personal Exception Schemas =====

class PersonalExceptionCreate(BaseModel):
    """
    Schema for creating personal exception.
    Ref: Module 5 - Feature 2.19 - AC 1
    """
    user_id: UUID = Field(..., description="User ID")
    project_id: UUID = Field(..., description="Project ID")
    exception_date: datetime = Field(..., description="Exception date")
    exception_type: PersonalExceptionType = Field(..., description="Type of exception")
    notes: Optional[str] = Field(None, description="Notes")


class PersonalExceptionResponse(BaseModel):
    """Response schema for personal exception"""
    id: UUID
    user_id: UUID
    project_id: UUID
    exception_date: datetime
    exception_type: PersonalExceptionType
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Planning Scope Schemas =====

class PlanningScopeCreate(BaseModel):
    """
    Schema for setting planning scope.
    Ref: Module 5 - Feature 2.9 - AC 1
    """
    task_id: UUID = Field(..., description="Task ID")
    include_in_planning: bool = Field(default=True, description="Include in planning scope?")
    override_parent: bool = Field(default=False, description="Override parent scope?")


class PlanningScopeUpdate(BaseModel):
    """Schema for updating planning scope"""
    include_in_planning: Optional[bool]
    override_parent: Optional[bool]


class PlanningScopeResponse(BaseModel):
    """Response schema for planning scope"""
    id: UUID
    task_id: UUID
    include_in_planning: bool
    override_parent: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Resource Histogram Schemas =====

class ResourceHistogramResponse(BaseModel):
    """Response schema for resource histogram"""
    id: UUID
    project_id: UUID
    user_id: UUID
    histogram_date: datetime
    planned_hours: float
    is_overloaded: bool
    overload_hours: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Simulation Session Schemas =====

class SimulationSessionStart(BaseModel):
    """Schema for starting simulation mode"""
    project_id: UUID = Field(..., description="Project ID")
    notes: Optional[str] = Field(None, description="Simulation notes")


class SimulationSessionUpdate(BaseModel):
    """Schema for updating simulation session"""
    notes: Optional[str]


class SimulationSessionApply(BaseModel):
    """Schema for applying simulation changes"""
    save_as_baseline: bool = Field(default=False, description="Save as new baseline?")


class SimulationSessionResponse(BaseModel):
    """Response schema for simulation session"""
    id: UUID
    project_id: UUID
    created_by: UUID
    is_active: bool
    
    delta_project_end_days: Optional[int]
    new_critical_path_count: Optional[int]
    sla_at_risk_count: Optional[int]
    resource_overload_increase: Optional[int]
    
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Cross-Project Dependency Schemas =====

class CrossProjectDependencyCreate(BaseModel):
    """
    Schema for creating cross-project dependency.
    Ref: Module 5 - Feature 2.18 - AC 1
    """
    source_task_id: UUID = Field(..., description="Source task ID")
    source_project_id: UUID = Field(..., description="Source project ID")
    target_task_id: UUID = Field(..., description="Target task ID")
    target_project_id: UUID = Field(..., description="Target project ID")
    dependency_type: DependencyTypeEnum = Field(default=DependencyTypeEnum.FS, description="FS, SS, FF, SF")


class CrossProjectDependencyResponse(BaseModel):
    """Response schema for cross-project dependency"""
    id: UUID
    source_task_id: UUID
    source_project_id: UUID
    target_task_id: UUID
    target_project_id: UUID
    dependency_type: DependencyTypeEnum
    is_broken: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Planning Audit Log Schemas =====

class PlanningAuditLogResponse(BaseModel):
    """Response schema for planning audit log"""
    id: UUID
    task_id: UUID
    change_type: str
    old_value: Optional[str]
    new_value: str
    reason: Optional[str]
    changed_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Composite/Complex Schemas =====

class GanttChartFilter(BaseModel):
    """Schema for filtering Gantt chart data"""
    project_id: UUID = Field(..., description="Project ID")
    zoom_level: ZoomLevel = Field(default=ZoomLevel.MONTH, description="Zoom level")
    start_date: Optional[datetime] = Field(None, description="Filter start date")
    end_date: Optional[datetime] = Field(None, description="Filter end date")
    include_milestones: bool = Field(default=True, description="Include milestones?")
    show_critical_path: bool = Field(default=False, description="Highlight critical path?")
    show_baseline: bool = Field(default=False, description="Show baseline comparison?")


class CriticalPathAnalysisResponse(BaseModel):
    """Response schema for critical path analysis"""
    total_float_hours: float = Field(..., description="Total float (slack) in hours")
    critical_task_ids: List[UUID] = Field(..., description="Task IDs on critical path")
    project_end_date: datetime = Field(..., description="Calculated project end date")
    updated_at: datetime


class ImpactAnalysisResponse(BaseModel):
    """
    Response schema for change impact analysis.
    Ref: Module 5 - Feature 2.12 - AC 2
    """
    delta_project_end_days: int = Field(..., description="Project end date shift")
    affected_task_ids: List[UUID] = Field(..., description="Tasks impacted by change")
    new_critical_path_count: int = Field(..., description="Number of critical path changes")
    sla_at_risk_count: int = Field(..., description="Tasks at SLA risk")
    resource_overload_increase: int = Field(..., description="Additional resource overloads")


class ResourceLevelingRequest(BaseModel):
    """Schema for resource leveling request"""
    project_id: UUID = Field(..., description="Project ID")
    strategy: ResourceLevelingStrategy = Field(default=ResourceLevelingStrategy.WITHIN_SLACK)
    preview_only: bool = Field(default=True, description="Preview without applying?")


class ResourceLevelingResponse(BaseModel):
    """Response schema for resource leveling"""
    tasks_to_move: List[UUID] = Field(..., description="Tasks that will be rescheduled")
    conflict_reduction_percent: float = Field(..., description="Estimated conflict reduction (%)")
    project_end_date_delta_days: int = Field(..., description="Project end date change")
    affected_resources: List[UUID] = Field(..., description="Affected resource IDs")
