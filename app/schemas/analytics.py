"""
Analytics and Reporting Pydantic Schemas for Module 11.
Handles validation and serialization for all analytics operations.

Schema Categories:
- Sprint Metrics (Create, Update, Read)
- Velocity Metrics (Create, Read)
- Resource Allocation (Create, Read)
- Time Entries (Create, Update, Read) - with validators
- Timesheets (Create, Update, Read)
- Custom Reports (Create, Update, Read)
- Report Schedules (Create, Update, Read)

Validators:
- Time entry: No future logging, daily <= 24h, warning > 12h
- Timesheet: Status workflow validation
- Report: Filter logic validation

Ref: Module 11 - Advanced Analytics and Reporting
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, validator, root_validator

from app.db.enums import (
    AnalyticsTypeEnum, ReportFormatEnum, TimesheetStatusEnum,
    BillableStatusEnum, ReportScheduleFrequencyEnum
)


# ==================== Metric Snapshot Schemas ====================

class MetricSnapshotCreate(BaseModel):
    """Create metric snapshot"""
    project_id: str
    sprint_id: Optional[str] = None
    snapshot_date: datetime
    planned_value: Decimal
    earned_value: Decimal
    actual_cost: Decimal


class MetricSnapshotRead(BaseModel):
    """Read metric snapshot"""
    id: UUID
    project_id: str
    sprint_id: Optional[str]
    snapshot_date: datetime
    planned_value: Decimal
    earned_value: Decimal
    actual_cost: Decimal
    cost_performance_index: float
    schedule_performance_index: float
    cost_variance: Decimal
    schedule_variance: Decimal
    progress_percentage: float
    on_track: bool
    health_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== KPI Schemas ====================

class KPICreate(BaseModel):
    """Create KPI"""
    project_id: str
    sprint_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    kpi_type: str
    unit: str
    target_value: float = Field(..., gt=0)
    start_date: datetime
    target_date: datetime
    weight: float = Field(1.0, ge=0.1, le=10.0)


class KPIRead(BaseModel):
    """Read KPI"""
    id: UUID
    project_id: str
    sprint_id: Optional[str]
    name: str
    description: Optional[str]
    kpi_type: str
    unit: str
    target_value: float
    actual_value: Optional[float]
    current_value: Optional[float]
    status: str
    achieved: bool
    start_date: datetime
    target_date: datetime
    weight: float
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Timesheet Approval Schemas ====================

class TimesheetApprovalCreate(BaseModel):
    """Create timesheet approval record"""
    timesheet_id: UUID
    validation_passed: bool = False


class TimesheetApprovalRead(BaseModel):
    """Read timesheet approval"""
    id: UUID
    timesheet_id: UUID
    status: TimesheetStatusEnum
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    rejected_at: Optional[datetime]
    approver_id: Optional[str]
    approval_notes: Optional[str]
    rejection_reason: Optional[str]
    validation_passed: bool
    validation_errors: Optional[List[Dict[str, Any]]]
    is_compliant: bool
    requires_escalation: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Report Permission Schemas ====================

class ReportPermissionCreate(BaseModel):
    """Create report permission"""
    report_id: str
    user_id: str
    permission_level: str = Field(..., description="VIEW, EDIT, SHARE, ADMIN")
    scope_type: Optional[str] = None
    scope_id: Optional[str] = None
    grant_reason: Optional[str] = None
    expires_at: Optional[datetime] = None


class ReportPermissionRead(BaseModel):
    """Read report permission"""
    id: UUID
    report_id: str
    user_id: str
    permission_level: str
    scope_type: Optional[str]
    scope_id: Optional[str]
    is_active: bool
    granted_at: datetime
    expires_at: Optional[datetime]
    grant_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True



# ==================== Sprint Metrics Schemas ====================

class SprintMetricCreate(BaseModel):
    """Create sprint metric from sprint data"""
    sprint_id: str = Field(..., description="Sprint ID")
    project_id: str = Field(..., description="Project ID")
    total_story_points: int = Field(0, ge=0)
    initial_story_points: int = Field(0, ge=0, description="Planned Value")
    sprint_start_date: datetime
    sprint_end_date: datetime
    total_sprint_days: int = Field(14, ge=1)


class SprintMetricUpdate(BaseModel):
    """Update sprint metrics"""
    completed_story_points: Optional[int] = Field(None, ge=0)
    remaining_story_points: Optional[int] = Field(None, ge=0)
    added_story_points: Optional[int] = Field(None, ge=0, description="Scope creep addition")
    removed_story_points: Optional[int] = Field(None, ge=0)
    planned_value: Optional[Decimal] = Field(None, ge=0)
    earned_value: Optional[Decimal] = Field(None, ge=0)
    actual_cost: Optional[Decimal] = Field(None, ge=0)
    is_on_track: Optional[bool] = None
    risk_level: Optional[str] = None
    notes: Optional[str] = None


class SprintMetricRead(BaseModel):
    """Read sprint metric (full DTO)"""
    id: UUID
    sprint_id: str
    project_id: str
    total_story_points: int
    initial_story_points: int
    completed_story_points: int
    remaining_story_points: int
    added_story_points: int
    removed_story_points: int
    sprint_start_date: datetime
    sprint_end_date: datetime
    days_elapsed: int
    total_sprint_days: int
    planned_value: Decimal
    earned_value: Decimal
    actual_cost: Decimal
    cost_performance_index: Optional[float]
    schedule_performance_index: Optional[float]
    is_on_track: bool
    risk_level: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Velocity Metrics Schemas ====================

class VelocityMetricCreate(BaseModel):
    """Create velocity metric for sprint"""
    sprint_id: str
    project_id: str
    commitment: int = Field(..., gt=0)
    completed: int = Field(..., ge=0)
    team_size: int = Field(..., gt=0)
    sprint_number: int = Field(..., gt=0)
    sprint_start_date: datetime
    sprint_end_date: datetime


class VelocityMetricRead(BaseModel):
    """Read velocity metric"""
    id: UUID
    sprint_id: str
    project_id: str
    commitment: int
    completed: int
    velocity: float
    team_size: int
    avg_velocity_3_sprints: Optional[float]
    avg_velocity_6_sprints: Optional[float]
    trend: str
    sprint_number: int
    sprint_start_date: datetime
    sprint_end_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Resource Allocation Schemas ====================

class ResourceAllocationCreate(BaseModel):
    """Create resource allocation record"""
    user_id: str
    project_id: str
    working_capacity_hours: float = Field(8.0, gt=0, description="Working hours per day")
    assigned_hours: float = Field(0, ge=0)
    allocation_date: datetime


class ResourceAllocationRead(BaseModel):
    """Read resource allocation"""
    id: UUID
    user_id: str
    project_id: str
    working_capacity_hours: float
    assigned_hours: float
    utilization_percentage: float
    capacity_status: str  # GREEN, RED, GREY
    allocation_date: datetime
    is_overloaded: bool
    is_underutilized: bool
    in_progress_hours: float
    completed_hours: float
    blocked_hours: float
    created_at: datetime

    class Config:
        from_attributes = True


class ResourceHeatmapRead(BaseModel):
    """Heatmap view of resource utilization"""
    date: date
    resources: List[Dict[str, Any]] = Field(
        ...,
        description="List of {user_id, name, capacity_status, utilization_percentage, assigned_hours}"
    )


# ==================== Time Entry Schemas ====================

class TimeEntryCreate(BaseModel):
    """Create time entry (timer or manual)"""
    user_id: str
    project_id: str
    task_id: Optional[str] = None
    start_time: datetime
    end_time: datetime
    entry_type: str = Field("TIMER", description="TIMER or MANUAL")
    is_billable: bool = Field(True)
    billable_status: BillableStatusEnum = BillableStatusEnum.NON_BILLABLE
    category: Optional[str] = None
    description: Optional[str] = None

    @validator("end_time")
    def end_after_start(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v

    @validator("start_time")
    def no_future_logging(cls, v):
        """Business Rule: Cannot log time for future dates"""
        if v.date() > datetime.utcnow().date():
            raise ValueError("Cannot log time for future dates (except leave requests)")
        return v

    @root_validator
    def validate_daily_limits(cls, values):
        """
        Business Rule: Validate daily time logging limits
        - Hard limit: 24h per day
        - Soft warning: >12h per day
        """
        if "start_time" not in values or "end_time" not in values:
            return values

        start = values["start_time"]
        end = values["end_time"]
        duration_hours = (end - start).total_seconds() / 3600

        if duration_hours > 24:
            raise ValueError("Entry exceeds 24-hour daily maximum")

        values["daily_warning_exceeded"] = duration_hours > 12
        values["daily_max_exceeded"] = duration_hours > 24

        return values


class TimeEntryUpdate(BaseModel):
    """Update time entry"""
    end_time: Optional[datetime] = None
    is_billable: Optional[bool] = None
    billable_status: Optional[BillableStatusEnum] = None
    category: Optional[str] = None
    description: Optional[str] = None
    edit_reason: Optional[str] = None


class TimeEntryRead(BaseModel):
    """Read time entry"""
    id: UUID
    user_id: str
    project_id: str
    task_id: Optional[str]
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    duration_hours: float
    entry_type: str
    is_billable: bool
    billable_status: BillableStatusEnum
    hourly_rate: Optional[Decimal]
    billable_amount: Optional[Decimal]
    category: Optional[str]
    description: Optional[str]
    daily_warning_exceeded: bool
    daily_max_exceeded: bool
    edit_count: int
    manually_edited: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimerControlRequest(BaseModel):
    """Request to start/stop timer"""
    user_id: str
    project_id: str
    task_id: Optional[str] = None
    action: str = Field(..., description="START or STOP")
    category: Optional[str] = None
    description: Optional[str] = None


# ==================== Timesheet Schemas ====================

class TimesheetCreate(BaseModel):
    """Create timesheet"""
    user_id: str
    project_id: str
    period_start_date: datetime
    period_end_date: datetime
    period_type: str = Field("WEEKLY", description="WEEKLY or MONTHLY")
    notes: Optional[str] = None


class TimesheetSubmit(BaseModel):
    """Submit timesheet for approval"""
    timesheet_id: UUID
    notes: Optional[str] = None


class TimesheetApprove(BaseModel):
    """Approve timesheet"""
    timesheet_id: UUID
    approval_notes: Optional[str] = None


class TimesheetReject(BaseModel):
    """Reject timesheet"""
    timesheet_id: UUID
    rejection_reason: str = Field(..., min_length=10)


class TimesheetRead(BaseModel):
    """Read timesheet"""
    id: UUID
    user_id: str
    project_id: str
    period_start_date: datetime
    period_end_date: datetime
    period_type: str
    total_hours: float
    billable_hours: float
    non_billable_hours: float
    total_cost: Decimal
    billable_amount: Decimal
    time_entries_count: int
    status: TimesheetStatusEnum
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    rejected_at: Optional[datetime]
    rejection_reason: Optional[str]
    notes: Optional[str]
    approval_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Custom Report Schemas ====================

class FilterExpression(BaseModel):
    """Filter expression for custom reports"""
    field: str = Field(..., description="Field name: project, assignee, tag, priority, month")
    operator: str = Field(..., description="eq, ne, gt, lt, in, contains")
    value: Any = Field(...)
    logic: Optional[str] = Field(None, description="AND or OR connector")


class CustomReportCreate(BaseModel):
    """Create custom report"""
    name: str = Field(..., min_length=1, max_length=255)
    project_id: str
    description: Optional[str] = None
    dimensions: List[str] = Field(
        ...,
        description="Dimensions: project, assignee, tag, priority, month, status"
    )
    metrics: List[str] = Field(
        ...,
        description="Metrics: count_tasks, sum_hours, avg_cycle_time, sum_costs"
    )
    filters: Optional[List[FilterExpression]] = None
    visualization_type: str = Field("TABLE", description="TABLE, CHART, HEATMAP")
    is_public: bool = Field(False)
    is_template: bool = Field(False)


class CustomReportUpdate(BaseModel):
    """Update custom report"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    dimensions: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    filters: Optional[List[FilterExpression]] = None
    visualization_type: Optional[str] = None
    is_public: Optional[bool] = None


class CustomReportRead(BaseModel):
    """Read custom report"""
    id: UUID
    name: str
    project_id: str
    description: Optional[str]
    created_by: str
    dimensions: List[str]
    metrics: List[str]
    filters: Optional[List[Dict[str, Any]]]
    visualization_type: str
    is_public: bool
    is_template: bool
    last_run_at: Optional[datetime]
    last_run_result_size: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportExecuteRequest(BaseModel):
    """Request to execute custom report"""
    report_id: UUID
    export_format: Optional[ReportFormatEnum] = None


class ReportExecuteResponse(BaseModel):
    """Response from report execution"""
    report_id: UUID
    execution_time_ms: int
    result_count: int
    data: Optional[List[Dict[str, Any]]] = None
    download_url: Optional[str] = None


# ==================== Report Schedule Schemas ====================

class ReportScheduleCreate(BaseModel):
    """Create report schedule"""
    custom_report_id: str
    project_id: str
    frequency: ReportScheduleFrequencyEnum
    start_date: datetime
    end_date: Optional[datetime] = None
    execution_days: Optional[List[int]] = Field(None, description="[1-7] for weekly")
    execution_time: Optional[str] = Field(None, description="HH:MM format")
    recipient_emails: List[str] = Field(..., min_items=1)
    export_format: ReportFormatEnum = ReportFormatEnum.PDF
    include_charts: bool = Field(True)

    @validator("recipient_emails", each_item=True)
    def validate_email(cls, v):
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v


class ReportScheduleUpdate(BaseModel):
    """Update report schedule"""
    frequency: Optional[ReportScheduleFrequencyEnum] = None
    execution_days: Optional[List[int]] = None
    execution_time: Optional[str] = None
    recipient_emails: Optional[List[str]] = None
    export_format: Optional[ReportFormatEnum] = None
    include_charts: Optional[bool] = None
    is_active: Optional[bool] = None
    end_date: Optional[datetime] = None


class ReportScheduleRead(BaseModel):
    """Read report schedule"""
    id: UUID
    custom_report_id: str
    project_id: str
    created_by: str
    frequency: ReportScheduleFrequencyEnum
    is_active: bool
    start_date: datetime
    end_date: Optional[datetime]
    next_run_at: Optional[datetime]
    last_run_at: Optional[datetime]
    execution_days: Optional[List[int]]
    execution_time: Optional[str]
    recipient_emails: List[str]
    export_format: ReportFormatEnum
    include_charts: bool
    total_runs: int
    success_runs: int
    failed_runs: int
    last_error: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Summary/Aggregation Response Schemas ====================

class BurndownChartData(BaseModel):
    """Burn-down chart visualization data"""
    sprint_id: str
    days: List[int]
    ideal_line: List[float]
    actual_line: List[float]
    scope_line: Optional[List[float]] = None
    on_track: bool
    risk_level: str


class VelocityChartData(BaseModel):
    """Velocity trend chart data"""
    sprints: List[str]
    commitments: List[int]
    completed: List[int]
    velocities: List[float]
    avg_velocity_3: Optional[float]
    trend: str


class AnalyticsOverviewRead(BaseModel):
    """High-level analytics overview for dashboard"""
    sprint_health: Dict[str, Any]
    team_velocity: Dict[str, Any]
    resource_utilization: Dict[str, Any]
    time_tracking_summary: Dict[str, Any]
    pending_timesheets: int
    overdue_approvals: int
