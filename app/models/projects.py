"""
Entity Models for Functional Module 3: Project Lifecycle Management.
Provides Project and related models for managing projects within workspaces.
Ref: docs/docs - PronaFlow React&FastAPI/02-Architeture/Entities/Project.md
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date

from sqlalchemy import String, DateTime, ForeignKey, Index, Table, Column, Date, Boolean, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin, SoftDeleteMixin
from app.db.enums import ProjectStatus, ProjectGovernanceMode, ProjectVisibility, ProjectPriority

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.workspaces import Workspace
    from app.models.collaboration import Note


# ======= Association Tables =======
project_members_association = Table(
    'project_members_association',
    Base.metadata,
    Column('project_id', UUID(as_uuid=True), ForeignKey('projects.id'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
)


# ======= Entity Tables =======

class Project(Base, TimestampMixin, SoftDeleteMixin):
    """
    Project Model - Central entity of Functional Module 3.
    Represents a project within a workspace.
    Ref: Entities/Project.md
    """
    __tablename__ = "projects"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for project"
    )

    # Foreign Keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to workspace"
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        comment="UUID of the project owner"
    )

    # Basic Information
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Project name (Max 100 characters)"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional project description"
    )

    # Project Configuration
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.NOT_STARTED,
        nullable=False,
        comment="Project status (NOT_STARTED / IN_PROGRESS / IN_REVIEW / DONE / CANCELLED)"
    )

    governance_mode: Mapped[ProjectGovernanceMode] = mapped_column(
        SQLEnum(ProjectGovernanceMode),
        default=ProjectGovernanceMode.SIMPLE,
        nullable=False,
        comment="Project governance mode (SIMPLE / STRICT)"
    )

    visibility: Mapped[ProjectVisibility] = mapped_column(
        SQLEnum(ProjectVisibility),
        default=ProjectVisibility.PRIVATE,
        nullable=False,
        comment="Project visibility (PUBLIC / PRIVATE)"
    )

    priority: Mapped[ProjectPriority] = mapped_column(
        SQLEnum(ProjectPriority),
        default=ProjectPriority.MEDIUM,
        nullable=False,
        comment="Project priority (CRITICAL / HIGH / MEDIUM / LOW)"
    )

    # Dates
    start_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Project start date"
    )

    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Project end date"
    )

    # Archive
    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when project was archived"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(foreign_keys=[workspace_id])
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id])
    members: Mapped[List["User"]] = relationship(secondary=project_members_association)
    notes: Mapped[List["Note"]] = relationship(back_populates="project", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_projects_workspace_id', 'workspace_id'),
        Index('ix_projects_owner_id', 'owner_id'),
        Index('ix_projects_name', 'name'),
        Index('ix_projects_status', 'status'),
        Index('ix_projects_is_deleted', 'is_deleted'),
    )
