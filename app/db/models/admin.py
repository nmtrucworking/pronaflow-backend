"""
Database models for System Administration (Module 14)

Core Principles:
- Separation of Duties (SoD)
- Least Privilege
- Audit-first / Write-protected logs
- Admin ≠ User
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    String, Text, Boolean, DateTime, Integer, JSON, Enum,
    ForeignKey, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base_class import Base


class AdminUser(Base):
    """
    Admin identity - separate from regular User
    Admin ≠ User principle
    """
    __tablename__ = "admin_users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Identity
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Profile
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)
    department: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Security
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    
    # Metadata
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default=dict)
    
    # Relationships
    roles = relationship("AdminUserRole", back_populates="admin_user", cascade="all, delete-orphan")
    audit_logs = relationship("AdminAuditLog", back_populates="admin_user", foreign_keys="AdminAuditLog.admin_user_id")
    created_incidents = relationship("SecurityIncident", back_populates="assigned_to", foreign_keys="SecurityIncident.assigned_to_id")
    change_requests = relationship("ChangeRequest", back_populates="requester", foreign_keys="ChangeRequest.requester_id")
    approved_changes = relationship("ChangeRequest", back_populates="approver", foreign_keys="ChangeRequest.approved_by_id")
    access_reviews = relationship("AccessReview", back_populates="reviewer")
    
    __table_args__ = (
        Index("idx_admin_user_active", "is_active"),
        Index("idx_admin_user_locked", "is_locked"),
    )


class AdminRole(Base):
    """
    18 specialized admin roles for Enterprise
    """
    __tablename__ = "admin_roles"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Identity
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Category: technical, security, business, audit
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Security
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_mfa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_session_duration: Mapped[int] = mapped_column(Integer, default=28800, nullable=False)  # 8 hours
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Metadata
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default=dict)
    
    # Relationships
    permissions = relationship("AdminRolePermission", back_populates="role", cascade="all, delete-orphan")
    user_assignments = relationship("AdminUserRole", back_populates="role", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_admin_role_category", "category"),
        Index("idx_admin_role_active", "is_active"),
        CheckConstraint(
            "category IN ('technical', 'security', 'business', 'audit')",
            name="ck_admin_role_category"
        ),
    )


class AdminPermission(Base):
    """
    Granular permissions for admin operations
    """
    __tablename__ = "admin_permissions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Identity
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Scope
    resource: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g., "users", "billing", "security"
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "read", "write", "delete", "execute"
    
    # Security
    is_dangerous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Requires extra approval
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Metadata
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default=dict)
    
    # Relationships
    role_assignments = relationship("AdminRolePermission", back_populates="permission", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_admin_permission_resource", "resource"),
        UniqueConstraint("resource", "action", name="uq_admin_permission_resource_action"),
    )


class AdminRolePermission(Base):
    """
    Many-to-many: Role → Permission
    """
    __tablename__ = "admin_role_permissions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    role_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_roles.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_permissions.id", ondelete="CASCADE"), nullable=False)
    
    # Audit
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    granted_by_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    
    # Relationships
    role = relationship("AdminRole", back_populates="permissions")
    permission = relationship("AdminPermission", back_populates="role_assignments")
    
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
        Index("idx_role_permission_role", "role_id"),
        Index("idx_role_permission_permission", "permission_id"),
    )


class AdminUserRole(Base):
    """
    Many-to-many: AdminUser → AdminRole
    Time-bound assignments for least privilege
    """
    __tablename__ = "admin_user_roles"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    admin_user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_roles.id", ondelete="CASCADE"), nullable=False)
    
    # Time-bound assignment
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))  # NULL = permanent
    
    # Approval
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    approval_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # Audit
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    assigned_by_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    revoked_by_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    
    # Relationships
    admin_user = relationship("AdminUser", back_populates="roles", foreign_keys=[admin_user_id])
    role = relationship("AdminRole", back_populates="user_assignments")
    
    __table_args__ = (
        UniqueConstraint("admin_user_id", "role_id", name="uq_admin_user_role"),
        Index("idx_admin_user_role_user", "admin_user_id"),
        Index("idx_admin_user_role_role", "role_id"),
        Index("idx_admin_user_role_valid", "valid_from", "valid_until"),
    )


class SystemConfig(Base):
    """
    System-wide configuration (key-value store)
    Immutable audit trail for changes
    """
    __tablename__ = "system_configs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Config
    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)  # string, integer, boolean, json
    
    # Metadata
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # security, performance, billing, etc.
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_editable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Version control
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    previous_value: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    
    __table_args__ = (
        Index("idx_system_config_category", "category"),
        Index("idx_system_config_sensitive", "is_sensitive"),
    )


class FeatureFlag(Base):
    """
    Feature control: Kill switch / Gradual rollout
    """
    __tablename__ = "feature_flags"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Identity
    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # State
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rollout_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    
    # Targeting
    target_workspaces: Mapped[Optional[list]] = mapped_column(JSONB)  # List of workspace IDs
    target_users: Mapped[Optional[list]] = mapped_column(JSONB)  # List of user IDs
    targeting_rules: Mapped[Optional[dict]] = mapped_column(JSONB)  # Complex targeting logic
    
    # Lifecycle
    environment: Mapped[str] = mapped_column(String(50), default="production", nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    
    # Metadata
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default=dict)
    
    __table_args__ = (
        Index("idx_feature_flag_enabled", "is_enabled"),
        Index("idx_feature_flag_environment", "environment"),
        CheckConstraint(
            "rollout_percentage >= 0 AND rollout_percentage <= 100",
            name="ck_feature_flag_rollout"
        ),
    )


class AdminAuditLog(Base):
    """
    Immutable audit trail for all admin operations
    Write-protected logs
    """
    __tablename__ = "admin_audit_logs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Actor
    admin_user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False)
    
    # Action
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g., "user.delete", "config.update"
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True))
    
    # Context
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 compatible
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    session_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Details
    changes: Mapped[Optional[dict]] = mapped_column(JSONB)  # Before/after state
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default=dict)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # success, failed, denied
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamp (immutable)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    admin_user = relationship("AdminUser", back_populates="audit_logs", foreign_keys=[admin_user_id])
    
    __table_args__ = (
        Index("idx_audit_log_admin_user", "admin_user_id"),
        Index("idx_audit_log_action", "action"),
        Index("idx_audit_log_resource", "resource_type", "resource_id"),
        Index("idx_audit_log_created_at", "created_at"),
        Index("idx_audit_log_status", "status"),
    )


class SecurityIncident(Base):
    """
    Security events and incidents
    """
    __tablename__ = "security_incidents"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Identity
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Classification
    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # critical, high, medium, low
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # fraud, abuse, breach, etc.
    
    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # open, investigating, resolved, closed
    
    # Assignment
    assigned_to_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    
    # Context
    affected_user_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True))
    affected_workspace_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    
    # Evidence
    evidence: Mapped[Optional[dict]] = mapped_column(JSONB)
    actions_taken: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Resolution
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    reported_by_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    
    # Metadata
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default=dict)
    
    # Relationships
    assigned_to = relationship("AdminUser", back_populates="created_incidents", foreign_keys=[assigned_to_id])
    
    __table_args__ = (
        Index("idx_security_incident_severity", "severity"),
        Index("idx_security_incident_status", "status"),
        Index("idx_security_incident_category", "category"),
        Index("idx_security_incident_assigned", "assigned_to_id"),
        CheckConstraint(
            "severity IN ('critical', 'high', 'medium', 'low')",
            name="ck_security_incident_severity"
        ),
        CheckConstraint(
            "status IN ('open', 'investigating', 'resolved', 'closed')",
            name="ck_security_incident_status"
        ),
    )


class ChangeRequest(Base):
    """
    Release / Change management
    """
    __tablename__ = "change_requests"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Identity
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    change_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # release, config, hotfix, rollback
    
    # Impact
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # critical, high, medium, low
    affected_systems: Mapped[list] = mapped_column(JSONB, nullable=False)
    rollback_plan: Mapped[Optional[str]] = mapped_column(Text)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # draft, pending, approved, rejected, deployed, rolled_back
    
    # Schedule
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    deployed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Approval
    approved_by_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    approval_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Results
    deployment_notes: Mapped[Optional[str]] = mapped_column(Text)
    was_successful: Mapped[Optional[bool]] = mapped_column(Boolean)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    requester_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False)
    
    # Metadata
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default=dict)
    
    # Relationships
    requester = relationship("AdminUser", back_populates="change_requests", foreign_keys=[requester_id])
    approver = relationship("AdminUser", back_populates="approved_changes", foreign_keys=[approved_by_id])
    
    __table_args__ = (
        Index("idx_change_request_type", "change_type"),
        Index("idx_change_request_risk", "risk_level"),
        Index("idx_change_request_status", "status"),
        Index("idx_change_request_scheduled", "scheduled_at"),
        CheckConstraint(
            "risk_level IN ('critical', 'high', 'medium', 'low')",
            name="ck_change_request_risk"
        ),
        CheckConstraint(
            "status IN ('draft', 'pending', 'approved', 'rejected', 'deployed', 'rolled_back')",
            name="ck_change_request_status"
        ),
    )


class AccessReview(Base):
    """
    Periodic access review for compliance
    """
    __tablename__ = "access_reviews"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Review cycle
    review_period: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "2026-Q1"
    review_type: Mapped[str] = mapped_column(String(50), nullable=False)  # quarterly, annual, ad-hoc
    
    # Scope
    admin_user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False)
    roles_reviewed: Mapped[list] = mapped_column(JSONB, nullable=False)  # List of role IDs
    
    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # pending, approved, revoked
    
    # Review
    reviewer_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    review_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Decision
    decision: Mapped[Optional[str]] = mapped_column(String(50))  # approve_all, revoke_some, revoke_all
    revoked_roles: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Metadata
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default=dict)
    
    # Relationships
    reviewer = relationship("AdminUser", back_populates="access_reviews", foreign_keys=[reviewer_id])
    
    __table_args__ = (
        Index("idx_access_review_period", "review_period"),
        Index("idx_access_review_status", "status"),
        Index("idx_access_review_admin_user", "admin_user_id"),
        Index("idx_access_review_reviewer", "reviewer_id"),
        CheckConstraint(
            "status IN ('pending', 'approved', 'revoked')",
            name="ck_access_review_status"
        ),
    )
