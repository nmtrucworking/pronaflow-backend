"""
Extended Entity Models for Functional Module 3: Project Lifecycle Management.
Additional models for project templates, baselines, change requests, and archives.
Ref: docs/docs - PronaFlow React&FastAPI/02-Architeture/Entities/Project*.md
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Index, Table, Column, Boolean, Text, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin, AuditMixin
from app.db.enums import ChangeRequestStatus, ChangeRequestType

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.projects import Project
    from app.models.workspaces import Workspace


# ======= Association Tables =======
project_template_members_association = Table(
    'project_template_members_association',
    Base.metadata,
    Column('template_id', UUID(as_uuid=True), ForeignKey('project_templates.id'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
)


# ======= Entity Tables =======

class ProjectMember(Base, TimestampMixin):
    """
    ProjectMember Model - Phân quyền cấp dự án.
    Manages project-level role assignments (separate from workspace roles).
    Ref: Entities/ProjectMember.md
    """
    __tablename__ = "project_members"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key UUID for project member"
    )

    # Foreign Keys
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to project"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to user"
    )

    # Role Assignment
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Project-level role (e.g., LEAD, MEMBER, VIEWER)"
    )

    # Timing
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when user joined project"
    )

    # Relationships
    project: Mapped["Project"] = relationship(foreign_keys=[project_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    # Constraints
    __table_args__ = (
        Index('ix_project_members_project_user', 'project_id', 'user_id', unique=True),
        Index('ix_project_members_project_id', 'project_id'),
        Index('ix_project_members_user_id', 'user_id'),
    )


class ProjectTemplate(Base, AuditMixin):
    """
    ProjectTemplate Model - Chuẩn hóa khởi tạo dự án.
    Provides templates for standardizing project creation.
    Ref: Entities/ProjectTemplate.md
    """
    __tablename__ = "project_templates"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key UUID for project template"
    )

    # Foreign Key
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to workspace"
    )

    # Template Information
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Template name"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Template description"
    )

    # Global vs Workspace-specific
    is_global: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether template is globally available (admin only)"
    )

    # Template Configuration
    config: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Template configuration (task lists, roles, etc.)"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(foreign_keys=[workspace_id])

    # Indexes
    __table_args__ = (
        Index('ix_project_templates_workspace_id', 'workspace_id'),
        Index('ix_project_templates_is_global', 'is_global'),
    )


class ProjectBaseline(Base, AuditMixin):
    """
    ProjectBaseline Model - Chỉ bật khi governance_mode = STRICT.
    Creates snapshots of project state for change control.
    Ref: Entities/ProjectBaseline.md
    """
    __tablename__ = "project_baselines"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key UUID for project baseline"
    )

    # Foreign Key
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to project"
    )

    # Version Management
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Baseline version number"
    )

    snapshot_ref: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Reference to snapshot (file path, commit hash, etc.)"
    )

    # Active Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether this is the current active baseline"
    )

    # Snapshot Data
    snapshot_data: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Snapshot of project state at baseline creation"
    )

    # Relationships
    project: Mapped["Project"] = relationship(foreign_keys=[project_id])

    # Indexes
    __table_args__ = (
        Index('ix_project_baselines_project_id', 'project_id'),
        Index('ix_project_baselines_is_active', 'is_active'),
    )


class ProjectChangeRequest(Base, AuditMixin):
    """
    ProjectChangeRequest Model - Change control system for STRICT governance mode.
    Manages formal change requests in projects with strict governance.
    Ref: Entities/ProjectChangeRequest.md
    """
    __tablename__ = "project_change_requests"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key UUID for change request"
    )

    # Foreign Key
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to project"
    )

    # Change Request Information
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Change request title"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Detailed description of the change"
    )

    # Type
    type: Mapped[ChangeRequestType] = mapped_column(
        SQLEnum(ChangeRequestType),
        nullable=False,
        comment="Type of change request"
    )

    # Status
    status: Mapped[ChangeRequestStatus] = mapped_column(
        SQLEnum(ChangeRequestStatus),
        default=ChangeRequestStatus.PENDING,
        nullable=False,
        index=True,
        comment="Change request status"
    )

    # Impact Assessment
    impact_assessment: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Assessment of change impact"
    )

    # Approval
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        comment="User who approved the change"
    )

    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of approval"
    )

    # Relationships
    project: Mapped["Project"] = relationship(foreign_keys=[project_id])
    approver: Mapped[Optional["User"]] = relationship(foreign_keys=[approved_by])

    # Indexes
    __table_args__ = (
        Index('ix_project_change_requests_project_id', 'project_id'),
        Index('ix_project_change_requests_status', 'status'),
    )


class ProjectArchive(Base, AuditMixin):
    """
    ProjectArchive Model - Tracks archived projects and archival metadata.
    Records information about archived projects.
    Ref: Entities/ProjectArchive.md
    """
    __tablename__ = "project_archives"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key UUID for project archive"
    )

    # Foreign Key
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        comment="Reference to archived project"
    )

    # Archive Details
    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for archival"
    )

    archive_location: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Storage location of archived data"
    )

    # Relationships
    project: Mapped["Project"] = relationship(foreign_keys=[project_id])

    # Indexes
    __table_args__ = (
        Index('ix_project_archives_project_id', 'project_id'),
    )
