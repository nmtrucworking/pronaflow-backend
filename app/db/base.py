"""
Central registry for all database models and metadata.
This module imports all ORM models to ensure they are registered with SQLAlchemy.
Used by Alembic for automatic migration generation.
"""

from app.db.declarative_base import Base

# Import all models - ensures they are registered with Base.metadata for Alembic
from app.db.models import (
    # Module 1: Identity & Access Management (IAM)
    User,
    Role,
    Permission,
    MFAConfig,
    MFABackupCode,
    AuthProvider,
    AuditLog,
    Session,
    # Module 2: Multi-tenancy Workspace Governance
    Workspace,
    WorkspaceMember,
    WorkspaceInvitation,
    WorkspaceAccessLog,
    WorkspaceSetting,
    # Module 3: Project Lifecycle Management
    Project,
    # Module 4 & 15: Tag & Categorization System
    Tag,
)

__all__ = [
    "Base",
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
]
