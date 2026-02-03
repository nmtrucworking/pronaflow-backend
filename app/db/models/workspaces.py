"""
Entity Models for Functional Module 2: Multi-tenancy Workspace Governance.
Provides Workspace, WorkspaceMember, WorkspaceInvitation, WorkspaceAccessLog, and WorkspaceSetting models.
Ref: docs/docs - PronaFlow React&FastAPI/02-Architeture/Entities/Workspace*.md
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Index, Table, Column, Boolean, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin, SoftDeleteMixin
from app.db.enums import WorkspaceRole

if TYPE_CHECKING:
    from app.db.models.users import User


# ======= Association Tables =======
workspace_members_association = Table(
    'workspace_members_association',
    Base.metadata,
    Column('workspace_id', UUID(as_uuid=True), ForeignKey('workspaces.id'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
)


# ======= Entity Tables =======

class Workspace(Base, TimestampMixin, SoftDeleteMixin):
    """
    Workspace Model - Tenant Logic (Container cao nhất).
    Represents a workspace/organization in the multi-tenancy system.
    Ref: Entities/Workspace.md
    """
    __tablename__ = "workspaces"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for workspace"
    )

    # Basic Information
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Workspace name (Max 50 characters)"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional workspace description"
    )

    # Owner Information
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        comment="UUID of the workspace owner"
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default='ACTIVE',
        nullable=False,
        comment="Workspace status (ACTIVE / SOFT_DELETED)"
    )

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="owned_workspaces", foreign_keys=[owner_id])
    members: Mapped[List["WorkspaceMember"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    invitations: Mapped[List["WorkspaceInvitation"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    access_logs: Mapped[List["WorkspaceAccessLog"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    settings: Mapped[Optional["WorkspaceSetting"]] = relationship(back_populates="workspace", cascade="all, delete-orphan", uselist=False)
    subscription: Mapped[Optional["WorkspaceSubscription"]] = relationship(back_populates="workspace", uselist=False)

    # Indexes
    __table_args__ = (
        Index('ix_workspaces_owner_id', 'owner_id'),
        Index('ix_workspaces_name', 'name'),
        Index('ix_workspaces_is_deleted', 'is_deleted'),
    )


class WorkspaceMember(Base, TimestampMixin):
    """
    WorkspaceMember Model - Bảng trung tâm của Multi-tenancy (User ↔ Workspace).
    Manages the relationship between Users and Workspaces with role assignment.
    Ref: Entities/WorkspaceMember.md
    """
    __tablename__ = "workspace_members"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key UUID for workspace member"
    )

    # Foreign Keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to workspace"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to user"
    )

    # Role
    role: Mapped[WorkspaceRole] = mapped_column(
        SQLEnum(WorkspaceRole),
        default=WorkspaceRole.MEMBER,
        nullable=False,
        comment="Role within workspace (OWNER / ADMIN / MEMBER / VIEWER / GUEST)"
    )

    # Status Fields
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether member is active in workspace"
    )

    left_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when member left workspace (nullable)"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="workspace_memberships")

    # Constraints
    # (workspace_id, user_id) UNIQUE - enforced at DB level
    __table_args__ = (
        Index('ix_workspace_members_workspace_user', 'workspace_id', 'user_id', unique=True),
        Index('ix_workspace_members_workspace_id', 'workspace_id'),
        Index('ix_workspace_members_user_id', 'user_id'),
        Index('ix_workspace_members_is_active', 'is_active'),
    )


class WorkspaceInvitation(Base, TimestampMixin):
    """
    WorkspaceInvitation Model - Invitation + Magic Link.
    Manages workspace invitations sent via email with token-based acceptance.
    Ref: Entities/WorkspaceInvitation.md
    """
    __tablename__ = "workspace_invitations"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key UUID for invitation"
    )

    # Foreign Keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to workspace being invited to"
    )

    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        comment="UUID of user who sent the invitation"
    )

    # Invitation Details
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Email address of invited user"
    )

    invited_role: Mapped[WorkspaceRole] = mapped_column(
        SQLEnum(WorkspaceRole),
        default=WorkspaceRole.MEMBER,
        nullable=False,
        comment="Role to be assigned (ADMIN / MEMBER / VIEWER)"
    )

    # Token Management
    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Hash of invitation token for security"
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Expiration timestamp (+48h from creation)"
    )

    # Acceptance Status
    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when invitation was accepted (nullable)"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="invitations")
    invited_by_user: Mapped[Optional["User"]] = relationship(foreign_keys=[invited_by])

    # Indexes
    __table_args__ = (
        Index('ix_workspace_invitations_workspace_id', 'workspace_id'),
        Index('ix_workspace_invitations_email', 'email'),
        Index('ix_workspace_invitations_token_hash', 'token_hash'),
    )


class WorkspaceAccessLog(Base, TimestampMixin):
    """
    WorkspaceAccessLog Model - Phục vụ Context Switching & Audit.
    Tracks access and context switches for audit purposes.
    Ref: Entities/WorkspaceAccessLog.md
    """
    __tablename__ = "workspace_access_logs"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key UUID for access log"
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to user"
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to workspace"
    )

    # Access timestamp is in created_at from TimestampMixin
    # accessed_at is mapped to created_at field

    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="access_logs")
    user: Mapped["User"] = relationship()

    # Indexes
    __table_args__ = (
        Index('ix_workspace_access_logs_user_id', 'user_id'),
        Index('ix_workspace_access_logs_workspace_id', 'workspace_id'),
        Index('ix_workspace_access_logs_created_at', 'created_at'),
    )


class WorkspaceSetting(Base, TimestampMixin):
    """
    WorkspaceSetting Model - Ngữ cảnh chung cho toàn bộ workspace.
    Stores workspace-wide configuration settings.
    Ref: Entities/WorkspaceSetting.md
    """
    __tablename__ = "workspace_settings"

    # Primary Key & Foreign Key (1:1 relationship)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        primary_key=True,
        comment="Reference to workspace (PK and FK)"
    )

    # Configuration Fields
    timezone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Workspace timezone (e.g., 'UTC', 'Asia/Ho_Chi_Minh')"
    )

    work_days: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Working days (e.g., 'Mon,Tue,Wed,Thu,Fri')"
    )

    work_hours: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Working hours (e.g., '{start: 09:00, end: 18:00}')"
    )

    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL to workspace logo"
    )

    # Relationship
    workspace: Mapped["Workspace"] = relationship(back_populates="settings")
