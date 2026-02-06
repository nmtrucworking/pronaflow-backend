"""
Database module initialization.
Exports all core database components and models.
"""

# Core database components
from app.db.declarative_base import Base
from app.db.session import SessionLocal, engine, get_db

# All ORM models (automatically registered with Base.metadata)
from app.models import (
    User,
    Role,
    Permission,
    MFAConfig,
    MFABackupCode,
    AuthProvider,
    AuditLog,
    Session,
    Workspace,
    WorkspaceMember,
    WorkspaceInvitation,
    WorkspaceAccessLog,
    WorkspaceSetting,
    Project,
    Tag,
)

# Database utilities
from app.db.mixins import TimestampMixin, AuditMixin, SoftDeleteMixin
from app.db.enums import (
    UserStatus,
    AuthProvider as AuthProviderEnum,
    WorkspaceRole,
    ProjectStatus,
    ProjectGovernanceMode,
)

__all__ = [
    # Core
    "Base",
    "SessionLocal",
    "engine",
    "get_db",
    # Models
    "User",
    "Role",
    "Permission",
    "MFAConfig",
    "MFABackupCode",
    "AuthProvider",
    "AuditLog",
    "Session",
    "Workspace",
    "WorkspaceMember",
    "WorkspaceInvitation",
    "WorkspaceAccessLog",
    "WorkspaceSetting",
    "Project",
    "Tag",
    # Mixins
    "TimestampMixin",
    "AuditMixin",
    "SoftDeleteMixin",
    # Enums
    "UserStatus",
    "AuthProviderEnum",
    "WorkspaceRole",
    "ProjectStatus",
    "ProjectGovernanceMode",
]
