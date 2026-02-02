"""
Database models for Module 5: Temporal Planning and Scheduling.
Handles Gantt charts, task dependencies, baselines, SLA tracking, and resource planning.
Ref: docs/01-Requirements/Functional-Modules/5 - Temporal Planning and Scheduling.md
"""
import uuid
from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    Integer,
    Float,
    Numeric,
    ForeignKey,
    Index,
    CheckConstraint,
    UniqueConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin


class PlanState(Base, TimestampMixin):
    """
    Plan state machine for planning governance and approval workflow.
    Ref: Module 5 - Feature 2.11 - AC 1 - Plan State Machine
    """
    __tablename__ = "plan_states"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # State: Draft -> Submitted -> Approved -> Locked
    state = Column(String(50), nullable=False, default="DRAFT")
    
    # Approval tracking
    submitted_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    approved_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    locked_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True, comment="Approval notes or rejection reason")
    
    __table_args__ = (
        Index("ix_plan_states_project_id", "project_id"),
    )

    # Relationships
    project = relationship("Project", backref="plan_states")
    submitted_user = relationship("User", foreign_keys=[submitted_by], backref="plans_submitted")
    approved_user = relationship("User", foreign_keys=[approved_by], backref="plans_approved")
    locked_user = relationship("User", foreign_keys=[locked_by], backref="plans_locked")


class TaskBaseline(Base, TimestampMixin):
    """
    Baseline snapshot of task schedule for variance tracking.
    Ref: Module 5 - Feature 2.4 - AC 1 - Create Snapshot
    """
    __tablename__ = "task_baselines"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(PG_UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    baseline_version = Column(Integer, nullable=False, default=1, comment="Baseline version number (1, 2, ...)")
    
    # Snapshot of dates
    baseline_start = Column(DateTime(timezone=True), nullable=False, comment="Planned start date at baseline creation")
    baseline_end = Column(DateTime(timezone=True), nullable=False, comment="Planned end date at baseline creation")
    baseline_duration_hours = Column(Float, nullable=False, comment="Estimated hours at baseline creation")
    
    # For variance calculation
    actual_start = Column(DateTime(timezone=True), nullable=True, comment="Actual start date (when status -> IN_PROGRESS)")
    actual_end = Column(DateTime(timezone=True), nullable=True, comment="Actual end date (when status -> DONE)")
    actual_duration_hours = Column(Float, nullable=True, comment="Actual hours spent")
    
    # Variance metrics
    schedule_variance_days = Column(Float, nullable=True, comment="Difference between planned and actual start (days)")
    
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    __table_args__ = (
        Index("ix_task_baselines_task_id", "task_id"),
        Index("ix_task_baselines_baseline_version", "baseline_version"),
        UniqueConstraint("task_id", "baseline_version", name="uq_task_baselines_task_version"),
    )

    # Relationships
    task = relationship("Task", backref="baselines")
    creator = relationship("User", backref="created_baselines")


class TaskDependencySchedule(Base, TimestampMixin):
    """
    Extended scheduling information for task dependencies.
    Ref: Module 5 - Feature 2.2 - AC 4 - Lag & Lead Time Configuration
    """
    __tablename__ = "task_dependency_schedules"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dependency_id = Column(PG_UUID(as_uuid=True), ForeignKey("task_dependencies.id"), nullable=False)
    
    # Lag/Lead time configuration
    lag_days = Column(Integer, nullable=False, default=0, comment="Positive: lag time (wait), negative: lead time (early start)")
    
    # Scheduling flags
    is_auto_scheduled = Column(Boolean, nullable=False, default=True, comment="Auto-schedule this dependency (Ref: Feature 2.2 AC 3)")
    is_pinned = Column(Boolean, nullable=False, default=False, comment="Pinned (manually scheduled) - cannot be auto-adjusted")
    
    __table_args__ = (
        Index("ix_task_dependency_schedules_dependency_id", "dependency_id"),
        UniqueConstraint("dependency_id", name="uq_task_dependency_schedules_dependency"),
    )

    # Relationships
    dependency = relationship("TaskDependency", backref="schedule_config")


class SchedulingMode(Base, TimestampMixin):
    """
    Track whether a task is auto-scheduled or manually scheduled.
    Ref: Module 5 - Feature 2.2 - AC 3 - Scheduling Mode
    """
    __tablename__ = "scheduling_modes"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(PG_UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, unique=True)
    
    # Mode: Auto-scheduled (default) or Manually-scheduled (Pinned)
    mode = Column(String(50), nullable=False, default="AUTO", comment="AUTO or MANUAL")
    
    is_pinned = Column(Boolean, nullable=False, default=False, comment="Pinned to specific dates")
    
    __table_args__ = (
        Index("ix_scheduling_modes_task_id", "task_id"),
    )

    # Relationships
    task = relationship("Task", backref="scheduling_mode", uselist=False)


class SLAPolicy(Base, TimestampMixin):
    """
    SLA policy configuration by priority level.
    Ref: Module 5 - Feature 2.7 - AC 1 - SLA Definition
    """
    __tablename__ = "sla_policies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Priority level
    priority = Column(String(50), nullable=False, comment="CRITICAL, HIGH, MEDIUM, LOW")
    
    # SLA duration in business hours
    sla_hours = Column(Integer, nullable=False, comment="SLA target in working hours")
    warning_threshold_percent = Column(Integer, nullable=False, default=75, comment="Warn at X% of SLA time consumed")
    
    # Escalation rules
    enable_escalation = Column(Boolean, nullable=False, default=True)
    escalation_level_1_hours = Column(Integer, nullable=True, comment="Hours after breached for Level 1 escalation")
    escalation_level_2_hours = Column(Integer, nullable=True, comment="Hours after breached for Level 2 escalation")
    
    __table_args__ = (
        Index("ix_sla_policies_project_id", "project_id"),
        UniqueConstraint("project_id", "priority", name="uq_sla_policies_project_priority"),
    )

    # Relationships
    project = relationship("Project", backref="sla_policies")


class SLATracker(Base, TimestampMixin):
    """
    SLA tracking instance for each task.
    Ref: Module 5 - Feature 2.7 - AC 3 - Visual Warning
    """
    __tablename__ = "sla_trackers"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(PG_UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, unique=True)
    
    # SLA status: On Track, At Risk, Breached
    status = Column(String(50), nullable=False, default="ON_TRACK", comment="ON_TRACK, AT_RISK, BREACHED")
    
    # Timings
    sla_start_time = Column(DateTime(timezone=True), nullable=False, comment="When SLA timer started (task -> IN_PROGRESS)")
    sla_breach_time = Column(DateTime(timezone=True), nullable=True, comment="When SLA was breached (if any)")
    sla_deadline = Column(DateTime(timezone=True), nullable=False, comment="Calculated SLA deadline in business time")
    
    # Elapsed business time (in seconds, excluding non-working hours)
    elapsed_business_seconds = Column(Integer, nullable=False, default=0)
    paused_business_seconds = Column(Integer, nullable=False, default=0, comment="Total paused time (e.g., waiting for customer)")
    
    # Pause state tracking
    is_paused = Column(Boolean, nullable=False, default=False, comment="Is timer currently paused?")
    pause_reason = Column(String(255), nullable=True, comment="Why is timer paused? (e.g., Blocked, Waiting)")
    paused_at = Column(DateTime(timezone=True), nullable=True, comment="When was timer paused?")
    
    # Escalation tracking
    escalation_level_1_triggered = Column(Boolean, nullable=False, default=False)
    escalation_level_1_at = Column(DateTime(timezone=True), nullable=True)
    escalation_level_2_triggered = Column(Boolean, nullable=False, default=False)
    escalation_level_2_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index("ix_sla_trackers_task_id", "task_id"),
        Index("ix_sla_trackers_status", "status"),
    )

    # Relationships
    task = relationship("Task", backref="sla_tracker", uselist=False)


class WorkingHoursPolicy(Base, TimestampMixin):
    """
    Define working hours and non-working days for scheduling calculations.
    Ref: Module 5 - Business Rule 3.2 - Non-working Days
    """
    __tablename__ = "working_hours_policies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(PG_UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    
    # Working days: bitmask (0=Mon, 1=Tue, ..., 6=Sun)
    working_days_mask = Column(Integer, nullable=False, default=0b0111110, comment="Bitmask: 0=Mon...6=Sun. Default: Mon-Fri")
    
    # Working hours
    work_start_time = Column(String(8), nullable=False, default="09:00", comment="HH:MM format")
    work_end_time = Column(String(8), nullable=False, default="18:00", comment="HH:MM format")
    lunch_start_time = Column(String(8), nullable=True, default="12:00", comment="Optional lunch break start")
    lunch_end_time = Column(String(8), nullable=True, default="13:00", comment="Optional lunch break end")
    
    # Timezone for calculations
    timezone = Column(String(50), nullable=False, default="UTC", comment="Timezone for schedule calculations")
    
    __table_args__ = (
        Index("ix_working_hours_policies_workspace_id", "workspace_id"),
    )

    # Relationships
    workspace = relationship("Workspace", backref="working_hours_policies")


class HolidayCalendar(Base, TimestampMixin):
    """
    Holiday dates excluded from working hours.
    Ref: Module 5 - Business Rule 3.2 - Non-working Days
    """
    __tablename__ = "holiday_calendars"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(PG_UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    
    holiday_date = Column(DateTime(timezone=True), nullable=False, comment="Date of holiday")
    name = Column(String(255), nullable=False, comment="Holiday name (e.g., 'Christmas', 'Tet')")
    is_recurring = Column(Boolean, nullable=False, default=False, comment="Does it recur every year?")
    
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    __table_args__ = (
        Index("ix_holiday_calendars_workspace_id", "workspace_id"),
        Index("ix_holiday_calendars_holiday_date", "holiday_date"),
        UniqueConstraint("workspace_id", "holiday_date", name="uq_holiday_calendars_workspace_date"),
    )

    # Relationships
    workspace = relationship("Workspace", backref="holiday_calendars")
    creator = relationship("User", backref="created_holidays")


class PersonalException(Base, TimestampMixin):
    """
    Personal leave/vacation/sick days for team members.
    Ref: Module 5 - Feature 2.19 - AC 1 - Personal Exception Input
    """
    __tablename__ = "personal_exceptions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    exception_date = Column(DateTime(timezone=True), nullable=False, comment="Date of exception")
    exception_type = Column(String(50), nullable=False, comment="VACATION, SICK_LEAVE, HALF_DAY")
    
    notes = Column(Text, nullable=True)
    
    __table_args__ = (
        Index("ix_personal_exceptions_user_id", "user_id"),
        Index("ix_personal_exceptions_project_id", "project_id"),
        Index("ix_personal_exceptions_exception_date", "exception_date"),
    )

    # Relationships
    user = relationship("User", backref="personal_exceptions")
    project = relationship("Project", backref="personal_exceptions")


class PlanningScope(Base, TimestampMixin):
    """
    Control which tasks are included in planning scope (Gantt, CPM, auto-scheduling).
    Ref: Module 5 - Feature 2.9 - AC 1 - Scope Flag
    """
    __tablename__ = "planning_scopes"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(PG_UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, unique=True)
    
    # Include in planning scope?
    include_in_planning = Column(Boolean, nullable=False, default=True, comment="Include in Gantt, CPM, auto-scheduling")
    
    # Override parent scope?
    override_parent = Column(Boolean, nullable=False, default=False, comment="Override parent's scope setting?")
    
    __table_args__ = (
        Index("ix_planning_scopes_task_id", "task_id"),
    )

    # Relationships
    task = relationship("Task", backref="planning_scope", uselist=False)


class ResourceHistogram(Base, TimestampMixin):
    """
    Workload histogram data for resource balancing.
    Ref: Module 5 - Feature 2.5 - AC 1 - Resource Histogram
    """
    __tablename__ = "resource_histograms"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    histogram_date = Column(DateTime(timezone=True), nullable=False, comment="Date of histogram calculation")
    planned_hours = Column(Float, nullable=False, default=0.0, comment="Planned working hours for this date")
    
    is_overloaded = Column(Boolean, nullable=False, default=False, comment="Is > 8 hours planned?")
    overload_hours = Column(Float, nullable=False, default=0.0, comment="Excess hours over 8")
    
    __table_args__ = (
        Index("ix_resource_histograms_project_id", "project_id"),
        Index("ix_resource_histograms_user_id", "user_id"),
        Index("ix_resource_histograms_histogram_date", "histogram_date"),
    )

    # Relationships
    project = relationship("Project", backref="resource_histograms")
    user = relationship("User", backref="resource_histograms")


class SimulationSession(Base, TimestampMixin):
    """
    What-If simulation mode for planning changes.
    Ref: Module 5 - Feature 2.10 - AC 1 - Enter Simulation Mode
    """
    __tablename__ = "simulation_sessions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Session state
    is_active = Column(Boolean, nullable=False, default=True, comment="Is simulation still running?")
    
    # Impact snapshot
    delta_project_end_days = Column(Integer, nullable=True, comment="Project end date shift (days)")
    new_critical_path_count = Column(Integer, nullable=True, comment="Number of tasks newly on critical path")
    sla_at_risk_count = Column(Integer, nullable=True, comment="Tasks at risk of SLA breach")
    resource_overload_increase = Column(Integer, nullable=True, comment="Additional overload instances")
    
    # Session notes
    notes = Column(Text, nullable=True)
    
    __table_args__ = (
        Index("ix_simulation_sessions_project_id", "project_id"),
        Index("ix_simulation_sessions_is_active", "is_active"),
    )

    # Relationships
    project = relationship("Project", backref="simulation_sessions")
    creator = relationship("User", backref="created_simulations")


class CrossProjectDependency(Base, TimestampMixin):
    """
    Dependencies between tasks in different projects.
    Ref: Module 5 - Feature 2.18 - AC 1 - External Predecessor Selection
    """
    __tablename__ = "cross_project_dependencies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_task_id = Column(PG_UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, comment="Task in source project")
    source_project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    target_task_id = Column(PG_UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, comment="Task in target project")
    target_project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Dependency type (FS, SS, FF, SF)
    dependency_type = Column(String(10), nullable=False, default="FS", comment="FS, SS, FF, SF")
    
    # Status tracking
    is_broken = Column(Boolean, nullable=False, default=False, comment="Broken link? (e.g., source task deleted)")
    
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    __table_args__ = (
        Index("ix_cross_project_dependencies_source", "source_project_id", "source_task_id"),
        Index("ix_cross_project_dependencies_target", "target_project_id", "target_task_id"),
        UniqueConstraint("source_task_id", "target_task_id", name="uq_cross_project_dep_tasks"),
    )

    # Relationships
    source_task = relationship("Task", foreign_keys=[source_task_id], backref="external_successors")
    source_project = relationship("Project", foreign_keys=[source_project_id], backref="external_dependencies_source")
    
    target_task = relationship("Task", foreign_keys=[target_task_id], backref="external_predecessors")
    target_project = relationship("Project", foreign_keys=[target_project_id], backref="external_dependencies_target")
    
    creator = relationship("User", backref="created_cross_project_deps")


class PlanningAuditLog(Base, TimestampMixin):
    """
    Audit trail for planning changes.
    Ref: Module 5 - Business Rule 3.7 - Planning Audit Trail
    """
    __tablename__ = "planning_audit_logs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(PG_UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    
    # Change details
    change_type = Column(String(50), nullable=False, comment="START_DATE, END_DATE, DURATION, DEPENDENCY")
    old_value = Column(Text, nullable=True, comment="Previous value")
    new_value = Column(Text, nullable=False, comment="New value")
    reason = Column(Text, nullable=True, comment="Why was it changed?")
    
    changed_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    __table_args__ = (
        Index("ix_planning_audit_logs_task_id", "task_id"),
        Index("ix_planning_audit_logs_changed_by", "changed_by"),
        Index("ix_planning_audit_logs_change_type", "change_type"),
    )

    # Relationships
    task = relationship("Task", backref="planning_audit_logs")
    user = relationship("User", backref="planning_audit_logs")
