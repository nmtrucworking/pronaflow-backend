"""
Entity Models for Functional Module 1: Identity and Access Management (IAM).
Prividers core user identity, roles, and permissions management.
Includes User, Role, Permission models with relationships.
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, Index, Table, Column, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin, SoftDeleteMixin
from app.db.enums import UserStatus

if TYPE_CHECKING:
    from app.db.models.workspaces import Workspace, WorkspaceMember

# ======= Association Tables =======
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True)
)

# 1st Entity: User
class User(Base, TimestampMixin, SoftDeleteMixin):
    """
    Model Authentication and User Identity.
    Args:
        Base (_type_): _description_
        AuditMixin (_type_): _description_
        SoftDeleteMixin (_type_): _description_
    """
    __tablename__ = "users"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key UUID for the user."
    )

    # Authentication Fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False, # Required for login
        comment="User's email address."
    )
    username: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False, # Optional based on auth provider
        comment="User's username."
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=True, 
        comment="Hashed password for local authentication."
    )

    status: Mapped[UserStatus] = mapped_column(
        default=UserStatus.PENDING
    )
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    # Relationships
    roles: Mapped[List["Role"]] = relationship(secondary=user_roles, back_populates="users")
    owned_workspaces: Mapped[List["Workspace"]] = relationship(back_populates="owner")
    workspace_memberships: Mapped[List["WorkspaceMember"]] = relationship(back_populates="user")
    

class Role(Base):
    """
    Summary-func: Định nghĩa vai trò hệ thống (RBAC).
    Ref: Entities/Roles.md.
    """
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, default=uuid.uuid4
    )
    role_name: Mapped[str] = mapped_column(
        String(50), unique=True, 
        nullable=False
    )
    hierarchy_level: Mapped[int] = mapped_column(
        Integer, default=0
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        secondary=user_roles, 
        back_populates="roles"
    )
    permissions: Mapped[List["Permission"]] = relationship(
        secondary=role_permissions, 
        back_populates="roles"
    )

class Permission(Base):
    """
    Summary-func: Quyền hạn chi tiết (Fine-grained permissions).
    Ref: Entities/Permissions.md.
    """
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    roles: Mapped[List["Role"]] = relationship(secondary=role_permissions, back_populates="permissions")

class MFAConfig(Base):
    """
    MFA Configuration for Users.
    Ref: Entities/MFAConfig.md
    """
    __tablename__ = "mfa_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    secret_key: Mapped[str] = mapped_column(String(255), nullable=False)
    enabled: Mapped[bool] = mapped_column(default=False)

class MFABackupCode(Base):
    """
    MFA Backup Codes for Users.
    Ref: Entities/MFABackupCode.md
    """
    __tablename__ = "mfa_backup_codes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    mfa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('mfa_configs.id'), nullable=False)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class AuthProvider(Base, TimestampMixin):
    """
    Supported Authentication Providers.
    Ref: Entities/AuthProvider.md
    """
    __tablename__ = "auth_providers"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

class AuditLog(Base, TimestampMixin):
    """
    Audit Logs for tracking user actions.
    Ref: Entities/AuditLogs.md
    """
    __tablename__ = "audit_logs"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey('users.id'), 
        nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

class Session(Base, TimestampMixin):
    """
    Session Model - Login Sessions for Users.
    Ref: Entities/Session.md
    """
    __tablename__ = "sessions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey('users.id'), 
        nullable=False
    )
    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    geo_location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_current: Mapped[bool] = mapped_column(default=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship(foreign_keys=[user_id])