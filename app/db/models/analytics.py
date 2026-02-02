"""
Analytics and Reporting Models for Module 11.
Implements Descriptive Analytics and Diagnostic Analytics capabilities.

Models:
- SprintMetric: Real-time burn-down, burn-up, and scope tracking
- VelocityMetric: Sprint velocity history for planning
- ResourceAllocation: Resource capacity tracking
- TimeEntry: Individual time logging (timer + manual)
- Timesheet: Weekly/monthly timesheet aggregation with approval workflow
- CustomReport: User-defined report configurations (drag-drop)
- ReportSchedule: Automated report generation scheduling

Ref: Module 11 - Advanced Analytics and Reporting
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, UniqueConstraint, Index, Enum, DECIMAL
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.enums import (
    AnalyticsTypeEnum, ReportFormatEnum, TimesheetStatusEnum,
    BillableStatusEnum, ReportScheduleFrequencyEnum
)


class MetricSnapshot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Performance metrics snapshot for historical tracking.
    
    Stores EVM calculations (CPI, SPI) at point-in-time for trend analysis.
    Used for dashboards and historical reporting.
    
    Ref: Module 11 - EVM Calculations, Section 4.1
    """
    __tablename__ = "metric_snapshots"

    # Foreign Keys
    project_id = Column(String, ForeignKey("project.id"), nullable=False)
    sprint_id = Column(String, ForeignKey("sprint.id"), nullable=True)
    recorded_by = Column(String, ForeignKey("user.id"), nullable=True)

    # Snapshot timestamp (when this metric was recorded)
    snapshot_date = Column(DateTime, nullable=False)

    # EVM Metrics (from earned value calculation)
    planned_value = Column(DECIMAL(10, 2), nullable=False)  # PV
    earned_value = Column(DECIMAL(10, 2), nullable=False)   # EV
    actual_cost = Column(DECIMAL(10, 2), nullable=False)    # AC

    # Calculated indices
    cost_performance_index = Column(Float, nullable=False)  # CPI = EV/AC
    schedule_performance_index = Column(Float, nullable=False)  # SPI = EV/PV

    # Variances
    cost_variance = Column(DECIMAL(10, 2), nullable=False)  # CV = EV - AC
    schedule_variance = Column(DECIMAL(10, 2), nullable=False)  # SV = EV - PV

    # Project health at this point
    progress_percentage = Column(Float, nullable=False, default=0)
    on_track = Column(Boolean, nullable=False, default=True)
    health_status = Column(String(20), nullable=False, default="GREEN")  # GREEN, AMBER, RED

    # Metadata
    notes = Column(Text, nullable=True)

    # Indexes
    __table_args__ = (
        Index("ix_metric_snapshot_project", "project_id"),
        Index("ix_metric_snapshot_sprint", "sprint_id"),
        Index("ix_metric_snapshot_date", "snapshot_date"),
        Index("ix_metric_snapshot_project_date", "project_id", "snapshot_date"),
    )


class KPI(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Key Performance Indicators per project/sprint.
    
    Defines target KPIs and tracks actual values.
    Used for performance monitoring and SLA tracking.
    
    Ref: Module 11 - Metrics Definition
    """
    __tablename__ = "kpis"

    # Foreign Keys
    project_id = Column(String, ForeignKey("project.id"), nullable=False)
    sprint_id = Column(String, ForeignKey("sprint.id"), nullable=True)
    created_by = Column(String, ForeignKey("user.id"), nullable=False)

    # KPI Definition
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # KPI Type
    kpi_type = Column(String(50), nullable=False)  # velocity, cycle_time, defect_rate, etc.
    unit = Column(String(50), nullable=False)  # points, days, %, hours
    
    # Target & Actual
    target_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)  # Real-time value
    
    # Status
    status = Column(String(20), nullable=False, default="ON_TRACK")  # ON_TRACK, AT_RISK, OFF_TRACK
    achieved = Column(Boolean, nullable=False, default=False)
    
    # Thresholds for status
    green_threshold = Column(Float, nullable=True)  # Good performance threshold
    amber_threshold = Column(Float, nullable=True)  # Warning threshold
    red_threshold = Column(Float, nullable=True)    # Critical threshold
    
    # Timeline
    start_date = Column(DateTime, nullable=False)
    target_date = Column(DateTime, nullable=False)
    
    # Weight (for composite scoring)
    weight = Column(Float, nullable=False, default=1.0)  # Importance multiplier

    # Indexes
    __table_args__ = (
        Index("ix_kpi_project", "project_id"),
        Index("ix_kpi_sprint", "sprint_id"),
        Index("ix_kpi_status", "status"),
    )


class TimesheetApproval(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Timesheet approval workflow tracking (separate from Timesheet entity).
    
    Tracks approval status, approver, and rejection reasons.
    Provides audit trail for compliance.
    
    Ref: Module 11 - Feature 2.3 AC 3 - Timesheet Approval Workflow
    """
    __tablename__ = "timesheet_approvals"

    # Foreign Keys
    timesheet_id = Column(String, ForeignKey("timesheets.id"), nullable=False, unique=True)
    approver_id = Column(String, ForeignKey("user.id"), nullable=True)
    rejected_by = Column(String, ForeignKey("user.id"), nullable=True)

    # Approval status
    status = Column(Enum(TimesheetStatusEnum), nullable=False, default=TimesheetStatusEnum.DRAFT)

    # Approval tracking
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)

    # Approval notes
    approval_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Validation results
    validation_passed = Column(Boolean, nullable=False, default=False)
    validation_errors = Column(JSON, nullable=True)  # [{field, error}]

    # Compliance flags
    is_compliant = Column(Boolean, nullable=False, default=True)
    requires_escalation = Column(Boolean, nullable=False, default=False)

    # Audit trail
    approval_notes_history = Column(JSON, nullable=True)  # Full history of changes

    # Indexes
    __table_args__ = (
        Index("ix_timesheet_approval_status", "status"),
        Index("ix_timesheet_approval_approver", "approver_id"),
    )


class ReportPermission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Granular access control for custom reports.
    
    Defines which users can VIEW, EDIT, or SHARE specific reports.
    Implements data visibility rules and security policies.
    
    Ref: Module 11 - Section 3.1 - Data Visibility & Security
    """
    __tablename__ = "report_permissions"

    # Foreign Keys
    report_id = Column(String, ForeignKey("custom_reports.id"), nullable=False)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    granted_by = Column(String, ForeignKey("user.id"), nullable=False)

    # Permission level
    permission_level = Column(String(20), nullable=False)  # VIEW, EDIT, SHARE, ADMIN
    
    # Scope (optional - restrict data visibility)
    scope_type = Column(String(50), nullable=True)  # PROJECT, WORKSPACE, TEAM, PERSONAL
    scope_id = Column(String, nullable=True)

    # Validity
    is_active = Column(Boolean, nullable=False, default=True)
    granted_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # Time-limited access

    # Audit
    grant_reason = Column(Text, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by = Column(String, ForeignKey("user.id"), nullable=True)

    # Constraints
    __table_args__ = (
        Index("ix_report_permission_report", "report_id"),
        Index("ix_report_permission_user", "user_id"),
        Index("ix_report_permission_active", "is_active"),
        UniqueConstraint("report_id", "user_id", name="uq_report_permission_per_user"),
    )



class SprintMetric(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Real-time sprint performance metrics tracking.
    
    Tracks:
    - Burn-down: Ideal vs Actual remaining work
    - Burn-up: Completed work + scope creep
    - Scope changes (new tasks added during sprint)
    - Sprint progress (days elapsed)
    
    Ref: Module 11 - Feature 2.1 - Agile Performance Metrics AC 1-2
    """
    __tablename__ = "sprint_metrics"

    # Foreign Keys
    sprint_id = Column(String, ForeignKey("sprint.id"), nullable=False)
    project_id = Column(String, ForeignKey("project.id"), nullable=False)

    # Core Metrics
    total_story_points = Column(Integer, nullable=False, default=0)
    initial_story_points = Column(Integer, nullable=False, default=0)  # Planned Value
    completed_story_points = Column(Integer, nullable=False, default=0)  # Earned Value
    remaining_story_points = Column(Integer, nullable=False, default=0)
    
    # Scope Creep Tracking
    added_story_points = Column(Integer, nullable=False, default=0)
    removed_story_points = Column(Integer, nullable=False, default=0)
    
    # Timeline
    sprint_start_date = Column(DateTime, nullable=False)
    sprint_end_date = Column(DateTime, nullable=False)
    days_elapsed = Column(Integer, nullable=False, default=0)
    total_sprint_days = Column(Integer, nullable=False, default=14)
    
    # Earned Value Metrics (EVM)
    planned_value = Column(DECIMAL(10, 2), nullable=False, default=0)  # Planned Cost
    earned_value = Column(DECIMAL(10, 2), nullable=False, default=0)  # Completed Value
    actual_cost = Column(DECIMAL(10, 2), nullable=False, default=0)   # Actual Hours * Rate
    
    # Performance Indices
    # CPI = EV / AC (1.0 = on budget, >1 = under budget, <1 = over budget)
    cost_performance_index = Column(Float, nullable=True)
    # SPI = EV / PV (1.0 = on schedule, >1 = ahead, <1 = behind)
    schedule_performance_index = Column(Float, nullable=True)
    
    # On-track Indicator
    is_on_track = Column(Boolean, nullable=False, default=True)
    risk_level = Column(String(20), nullable=False, default="LOW")  # LOW, MEDIUM, HIGH
    
    # Metadata
    last_updated_by = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # Indexes
    __table_args__ = (
        Index("ix_sprint_metric_sprint", "sprint_id"),
        Index("ix_sprint_metric_project", "project_id"),
        Index("ix_sprint_metric_dates", "sprint_start_date", "sprint_end_date"),
    )


class VelocityMetric(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Historical sprint velocity tracking.
    
    Stores:
    - Commitment (planned story points)
    - Completed (actual story points)
    - Average velocity (3-sprint moving average)
    
    Used for capacity planning and forecasting.
    
    Ref: Module 11 - Feature 2.1 - Agile Performance Metrics AC 2
    """
    __tablename__ = "velocity_metrics"

    # Foreign Keys
    sprint_id = Column(String, ForeignKey("sprint.id"), nullable=False, unique=True)
    project_id = Column(String, ForeignKey("project.id"), nullable=False)

    # Velocity Data
    commitment = Column(Integer, nullable=False)  # Planned story points
    completed = Column(Integer, nullable=False)   # Actual story points
    velocity = Column(Float, nullable=False)      # Completed / Commitment ratio
    
    # Team Capacity Planning
    team_size = Column(Integer, nullable=False)
    avg_velocity_3_sprints = Column(Float, nullable=True)  # 3-sprint average
    avg_velocity_6_sprints = Column(Float, nullable=True)  # 6-sprint average
    trend = Column(String(20), nullable=False, default="STABLE")  # INCREASING, STABLE, DECREASING
    
    sprint_number = Column(Integer, nullable=False)
    sprint_start_date = Column(DateTime, nullable=False)
    sprint_end_date = Column(DateTime, nullable=False)

    # Indexes
    __table_args__ = (
        Index("ix_velocity_metric_project", "project_id"),
        Index("ix_velocity_metric_sprint_number", "project_id", "sprint_number"),
    )


class ResourceAllocation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Resource capacity and utilization tracking.
    
    Tracks:
    - Team member capacity (working hours/day)
    - Assigned hours
    - Utilization percentage (Assigned / Capacity)
    - Overload/Underutilization status
    
    Used for heatmap visualization.
    
    Ref: Module 11 - Feature 2.2 - Resource Utilization Heatmap
    """
    __tablename__ = "resource_allocations"

    # Foreign Keys
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    project_id = Column(String, ForeignKey("project.id"), nullable=False)

    # Capacity Data
    working_capacity_hours = Column(Float, nullable=False, default=8.0)  # Hours/day
    assigned_hours = Column(Float, nullable=False, default=0)
    utilization_percentage = Column(Float, nullable=False, default=0)  # 0-100%
    
    # Heatmap Color Coding (AC 1)
    # GREEN: 70-90%, RED: >100%, GREY: <50%
    capacity_status = Column(String(20), nullable=False, default="GREY")
    
    # Tracking Date
    allocation_date = Column(DateTime, nullable=False)
    
    # Metrics
    is_overloaded = Column(Boolean, nullable=False, default=False)  # > 100%
    is_underutilized = Column(Boolean, nullable=False, default=False)  # < 50%
    
    # Detailed Breakdown
    in_progress_hours = Column(Float, nullable=False, default=0)
    completed_hours = Column(Float, nullable=False, default=0)
    blocked_hours = Column(Float, nullable=False, default=0)

    # Indexes
    __table_args__ = (
        Index("ix_resource_alloc_user", "user_id"),
        Index("ix_resource_alloc_project", "project_id"),
        Index("ix_resource_alloc_date", "allocation_date"),
        Index("ix_resource_alloc_user_date", "user_id", "allocation_date"),
    )


class TimeEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Individual time tracking entry.
    
    Features:
    - Timer mode (Start/Stop with auto calculation)
    - Manual entry mode (hh:mm:ss input)
    - Edit history tracking
    - Billable vs Non-billable classification
    - Task/Project association
    
    Validations (Business Rules):
    - No future logging (except leave requests)
    - Daily log max 24h (hard limit)
    - Warning if daily log > 12h (soft warning)
    
    Ref: Module 11 - Feature 2.3 - Time Tracking & Timesheets AC 1-2
    """
    __tablename__ = "time_entries"

    # Foreign Keys
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    task_id = Column(String, ForeignKey("task.id"), nullable=True)  # Optional
    project_id = Column(String, ForeignKey("project.id"), nullable=False)

    # Time Data
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_seconds = Column(Integer, nullable=False)  # Total seconds
    duration_hours = Column(Float, nullable=False)  # Calculated hours
    
    # Entry Type
    entry_type = Column(String(20), nullable=False, default="TIMER")  # TIMER or MANUAL
    
    # Billable Classification (AC 2)
    is_billable = Column(Boolean, nullable=False, default=True)
    billable_status = Column(Enum(BillableStatusEnum), nullable=False, default=BillableStatusEnum.NON_BILLABLE)
    hourly_rate = Column(DECIMAL(10, 2), nullable=True)
    billable_amount = Column(DECIMAL(10, 2), nullable=True)  # hours * rate
    
    # Classification
    category = Column(String(100), nullable=True)  # Work, Meeting, Training, etc.
    description = Column(Text, nullable=True)
    
    # Validation Flags
    daily_warning_exceeded = Column(Boolean, nullable=False, default=False)  # > 12h
    daily_max_exceeded = Column(Boolean, nullable=False, default=False)  # > 24h
    
    # Audit Trail
    edit_count = Column(Integer, nullable=False, default=0)
    edit_history = Column(JSON, nullable=True)  # [{timestamp, user_id, old_value, new_value}]
    manually_edited = Column(Boolean, nullable=False, default=False)
    edit_reason = Column(Text, nullable=True)

    # Indexes
    __table_args__ = (
        Index("ix_time_entry_user", "user_id"),
        Index("ix_time_entry_task", "task_id"),
        Index("ix_time_entry_project", "project_id"),
        Index("ix_time_entry_date", "start_time"),
        Index("ix_time_entry_billable", "is_billable"),
        Index("ix_time_entry_user_date", "user_id", "start_time"),
    )


class Timesheet(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Weekly/Monthly timesheet aggregation with approval workflow.
    
    Features:
    - Aggregates time entries for a period
    - Approval workflow (DRAFT → SUBMITTED → APPROVED/REJECTED)
    - Total hours, billable hours, costs
    - Rejection reason tracking
    
    Ref: Module 11 - Feature 2.3 AC 3 - Timesheet Approval Workflow
    """
    __tablename__ = "timesheets"

    # Foreign Keys
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    project_id = Column(String, ForeignKey("project.id"), nullable=False)
    approved_by = Column(String, ForeignKey("user.id"), nullable=True)

    # Period
    period_start_date = Column(DateTime, nullable=False)
    period_end_date = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False, default="WEEKLY")  # WEEKLY, MONTHLY
    
    # Time Summary
    total_hours = Column(Float, nullable=False, default=0)
    billable_hours = Column(Float, nullable=False, default=0)
    non_billable_hours = Column(Float, nullable=False, default=0)
    
    # Cost Summary
    total_cost = Column(DECIMAL(10, 2), nullable=False, default=0)
    billable_amount = Column(DECIMAL(10, 2), nullable=False, default=0)
    
    # Time Entries Reference
    time_entries_count = Column(Integer, nullable=False, default=0)
    time_entries_json = Column(JSON, nullable=True)  # Embedded entries summary
    
    # Approval Workflow
    status = Column(Enum(TimesheetStatusEnum), nullable=False, default=TimesheetStatusEnum.DRAFT)
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Indexes
    __table_args__ = (
        Index("ix_timesheet_user", "user_id"),
        Index("ix_timesheet_project", "project_id"),
        Index("ix_timesheet_period", "period_start_date", "period_end_date"),
        Index("ix_timesheet_status", "status"),
        Index("ix_timesheet_user_status", "user_id", "status"),
    )


class CustomReport(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    User-defined custom report configurations.
    
    Features:
    - Drag-drop interface configuration
    - Dimension selection (Project, Assignee, Tag, Priority, Month)
    - Metric selection (Count, Sum, Average)
    - Advanced filtering (AND/OR logic)
    - Export formats (PDF, CSV, XLSX)
    
    Ref: Module 11 - Feature 2.4 - Custom Report Builder AC 1-2
    """
    __tablename__ = "custom_reports"

    # Foreign Keys
    created_by = Column(String, ForeignKey("user.id"), nullable=False)
    project_id = Column(String, ForeignKey("project.id"), nullable=False)

    # Report Configuration
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Drag-drop Configuration
    dimensions = Column(JSON, nullable=False)  # ["project", "assignee", "tag"]
    metrics = Column(JSON, nullable=False)     # ["count_tasks", "sum_hours", "avg_cycle_time"]
    filters = Column(JSON, nullable=True)      # [{field, operator, value}] with AND/OR logic
    
    # Report Type & Display
    report_type = Column(Enum(AnalyticsTypeEnum), nullable=False, default=AnalyticsTypeEnum.CUSTOM_REPORT)
    visualization_type = Column(String(50), nullable=False, default="TABLE")  # TABLE, CHART, HEATMAP
    sort_by = Column(JSON, nullable=True)  # [{field, direction}]
    
    # Access Control
    is_public = Column(Boolean, nullable=False, default=False)
    shared_with_users = Column(JSON, nullable=True)  # [user_ids]
    
    # Metadata
    last_run_at = Column(DateTime, nullable=True)
    last_run_result_size = Column(Integer, nullable=True)
    is_template = Column(Boolean, nullable=False, default=False)

    # Indexes
    __table_args__ = (
        Index("ix_custom_report_creator", "created_by"),
        Index("ix_custom_report_project", "project_id"),
    )


class ReportSchedule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Automated report generation scheduling.
    
    Features:
    - Schedule frequency (Daily, Weekly, Monthly, Quarterly, Annually)
    - Recipient email lists
    - Export format selection
    - Automated email delivery
    
    Ref: Module 11 - Feature 2.4 - Custom Report Builder (Scheduling)
    """
    __tablename__ = "report_schedules"

    # Foreign Keys
    custom_report_id = Column(String, ForeignKey("custom_reports.id"), nullable=False)
    created_by = Column(String, ForeignKey("user.id"), nullable=False)
    project_id = Column(String, ForeignKey("project.id"), nullable=False)

    # Schedule Configuration
    frequency = Column(Enum(ReportScheduleFrequencyEnum), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timing
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # Null = indefinite
    next_run_at = Column(DateTime, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    
    # Execution Days (for weekly)
    execution_days = Column(JSON, nullable=True)  # [1,3,5] = Mon, Wed, Fri
    execution_time = Column(String(5), nullable=True)  # "09:00" in HH:MM format
    
    # Recipients & Format
    recipient_emails = Column(JSON, nullable=False)  # [email1, email2]
    export_format = Column(Enum(ReportFormatEnum), nullable=False, default=ReportFormatEnum.PDF)
    include_charts = Column(Boolean, nullable=False, default=True)
    
    # Status Tracking
    total_runs = Column(Integer, nullable=False, default=0)
    success_runs = Column(Integer, nullable=False, default=0)
    failed_runs = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)

    # Indexes
    __table_args__ = (
        Index("ix_report_schedule_report", "custom_report_id"),
        Index("ix_report_schedule_creator", "created_by"),
        Index("ix_report_schedule_next_run", "next_run_at"),
    )
