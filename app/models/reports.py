"""
Entity Models for Functional Module 9: Reports & Analytics.
Provides ReportDefinition, ReportExecution, MetricSnapshot, KPI models.
Ref: docs/docs - PronaFlow React&FastAPI/02-Architeture/Entities/Report*.md
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Index, Table, Column, Boolean, Text, Integer, Float, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.workspaces import Workspace
    from app.models.projects import Project


# ======= Entity Tables =======

class ReportDefinition(Base, TimestampMixin):
    """
    ReportDefinition Model - Define custom reports and dashboards.
    Stores report templates and configurations.
    Ref: Entities/ReportDefinition.md
    """
    __tablename__ = "report_definitions"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for report definition"
    )

    # Foreign Keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to workspace"
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        comment="User who created the report"
    )

    # Report Information
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Report name"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Report description"
    )

    # Report Configuration
    report_type: Mapped[str] = mapped_column(
        SQLEnum('DASHBOARD', 'TABLE', 'CHART', 'EXPORT', name='report_type'),
        default='DASHBOARD',
        nullable=False,
        comment="Type of report"
    )

    filters: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Report filters and query parameters"
    )

    metrics: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Metrics to include in report"
    )

    visualization_config: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Visualization settings (colors, layout, etc.)"
    )

    # Scheduling
    is_scheduled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether report is scheduled for generation"
    )

    schedule_frequency: Mapped[Optional[str]] = mapped_column(
        SQLEnum('DAILY', 'WEEKLY', 'MONTHLY', name='schedule_frequency'),
        nullable=True,
        comment="Report generation frequency (if scheduled)"
    )

    next_execution_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Next scheduled execution time"
    )

    # Sharing
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether report is publicly accessible"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(foreign_keys=[workspace_id])
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    executions: Mapped[List["ReportExecution"]] = relationship(back_populates="definition", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_report_definitions_workspace_id', 'workspace_id'),
        Index('ix_report_definitions_is_scheduled', 'is_scheduled'),
    )


class ReportExecution(Base, TimestampMixin):
    """
    ReportExecution Model - Track report executions and results.
    Records each time a report is generated.
    Ref: Entities/ReportExecution.md
    """
    __tablename__ = "report_executions"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for report execution"
    )

    # Foreign Keys
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('report_definitions.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to report definition"
    )

    triggered_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        comment="User who triggered the report execution"
    )

    # Execution Status
    status: Mapped[str] = mapped_column(
        SQLEnum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='execution_status'),
        default='PENDING',
        nullable=False,
        index=True,
        comment="Execution status"
    )

    # Results
    result_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Generated report data (JSON)"
    )

    # Metadata
    execution_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Execution time in milliseconds"
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if execution failed"
    )

    # Download/Export
    export_format: Mapped[Optional[str]] = mapped_column(
        SQLEnum('PDF', 'EXCEL', 'CSV', 'JSON', name='export_format'),
        nullable=True,
        comment="Export format if applicable"
    )

    export_file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Path to exported file"
    )

    # Relationships
    definition: Mapped["ReportDefinition"] = relationship(back_populates="executions", foreign_keys=[report_id])
    triggered_by_user: Mapped["User"] = relationship(foreign_keys=[triggered_by])

    # Indexes
    __table_args__ = (
        Index('ix_report_executions_report_id', 'report_id'),
        Index('ix_report_executions_status', 'status'),
        Index('ix_report_executions_created_at', 'created_at'),
    )


class MetricSnapshot(Base, TimestampMixin):
    """
    MetricSnapshot Model - Point-in-time snapshots of metrics.
    Records metric values at specific points in time for trend analysis.
    Ref: Entities/MetricSnapshot.md
    """
    __tablename__ = "metric_snapshots"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for metric snapshot"
    )

    # Foreign Keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to workspace"
    )

    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=True,
        comment="Optional reference to project (if project-specific)"
    )

    # Metric Information
    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Name of the metric (e.g., 'tasks_completed', 'velocity')"
    )

    metric_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Numeric value of the metric"
    )

    # Additional Data
    meta: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Additional metric metadata"
    )

    # Time Window
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Start of measurement period"
    )

    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="End of measurement period"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(foreign_keys=[workspace_id])
    project: Mapped[Optional["Project"]] = relationship(foreign_keys=[project_id])

    # Indexes
    __table_args__ = (
        Index('ix_metric_snapshots_workspace_id', 'workspace_id'),
        Index('ix_metric_snapshots_metric_name', 'metric_name'),
        Index('ix_metric_snapshots_period_start', 'period_start'),
    )


class KPI(Base, TimestampMixin):
    """
    KPI Model - Key Performance Indicators.
    Defines and tracks KPIs for workspaces and projects.
    Ref: Entities/KPI.md
    """
    __tablename__ = "kpis"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for KPI"
    )

    # Foreign Keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to workspace"
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        comment="User who created the KPI"
    )

    # KPI Definition
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="KPI name"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="KPI description"
    )

    # Measurement
    metric_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Key to identify the underlying metric"
    )

    target_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Target value for the KPI"
    )

    current_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Current value of the KPI"
    )

    # Status
    status: Mapped[str] = mapped_column(
        SQLEnum('ON_TRACK', 'AT_RISK', 'OFF_TRACK', name='kpi_status'),
        default='ON_TRACK',
        nullable=False,
        comment="KPI status based on current value vs target"
    )

    # Timeline
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="KPI tracking start date"
    )

    end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="KPI tracking end date"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(foreign_keys=[workspace_id])
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])

    # Indexes
    __table_args__ = (
        Index('ix_kpis_workspace_id', 'workspace_id'),
        Index('ix_kpis_metric_key', 'metric_key'),
    )
