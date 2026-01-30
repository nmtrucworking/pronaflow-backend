"""
Entity Models for Functional Module 1: Identity and Access Management (IAM).
Prividers core user identity, roles, and permissions management.
Includes User, Role, Permission models with relationships.
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, Index, Table, Column, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin, SoftDeleteMixin
from app.db.enums import UserStatus, AuthProvider

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
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="User's full name."
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
    Tracks user sessions with device info, IP, location, and revocation status.
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
        nullable=False,
        index=True
    )
    token: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
        comment="JWT token for this session"
    )
    device_info: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True,
        comment="Browser/device info (e.g., Chrome on Windows 10)"
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), 
        nullable=True,
        comment="Client IP address"
    )
    geo_location: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True,
        comment="Estimated geographic location (city, country)"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="Full user agent string for device identification"
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        default=datetime.utcnow,
        comment="Last time this session was active"
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Timestamp when session was revoked/logged out"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])


class LoginAttempt(Base, TimestampMixin):
    """
    Track login attempts for brute-force protection.
    Stores failed login attempts per user/email.
    """
    __tablename__ = "login_attempts"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
        comment="Email attempted to login"
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IP address of login attempt"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User agent of login attempt"
    )
    success: Mapped[bool] = mapped_column(
        default=False,
        comment="Whether login attempt was successful"
    )
    reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Reason for failed attempt (e.g., 'Invalid password', 'Account locked')"
    )


class PasswordResetToken(Base, TimestampMixin):
    """
    One-time password reset tokens with expiration.
    """
    __tablename__ = "password_reset_tokens"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False,
        index=True
    )
    token: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
        comment="One-time reset token (hashed)"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Token expiration time (default: 15 minutes)"
    )
    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When token was used"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])


class EmailVerificationToken(Base, TimestampMixin):
    """
    One-time email verification tokens with expiration.
    """
    __tablename__ = "email_verification_tokens"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False,
        index=True
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Email to be verified"
    )
    token: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
        comment="One-time verification token (hashed)"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Token expiration time (default: 24 hours)"
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When email was verified"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])


class AuthProvider(Base, TimestampMixin):
    """
    OAuth2 Provider Configuration and User Linked Accounts.
    Tracks which OAuth providers are configured and which accounts users have linked.
    """
    __tablename__ = "oauth_providers"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False,
        index=True
    )
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="OAuth provider name (google, github, etc.)"
    )
    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="User ID from OAuth provider"
    )
    provider_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Email from OAuth provider"
    )
    access_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="OAuth access token (encrypted)"
    )
    refresh_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="OAuth refresh token (encrypted)"
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Token expiration time"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_oauth_provider_user', 'provider', 'provider_user_id', unique=True),
    )
