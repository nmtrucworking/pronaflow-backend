"""
Database models for Module 8: Data Archiving and Compliance.

Handles automated archiving strategies, trash bin management, data exports,
retention policies, and audit logging for GDPR compliance.

Ref: Module 8 - Data Archiving and Compliance
"""
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text, JSON, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.db.mixins import TimestampMixin


class ArchivePolicy(Base, TimestampMixin):
    """
    Archive policy configuration per workspace.
    Defines rules for automatic archiving, retention periods, and compliance settings.
    
    Ref: Module 8 - Feature 2.1 - Automated Archiving Strategy
    """
    __tablename__ = "archive_policies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    # Archive settings
    inactive_days = Column(Integer, nullable=False, default=180)  # Days before archiving (AC 1)
    is_enabled = Column(Boolean, nullable=False, default=True)
    
    # Trash bin settings
    trash_retention_days = Column(Integer, nullable=False, default=30)  # Auto-purge after 30 days
    auto_purge_enabled = Column(Boolean, nullable=False, default=True)
    
    # Export settings
    export_link_expiry_hours = Column(Integer, nullable=False, default=24)
    max_export_file_size_mb = Column(Integer, nullable=False, default=500)
    
    # Metadata
    created_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    last_modified_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Foreign keys
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    created_by = relationship("User", foreign_keys=[created_by_user_id], viewonly=True)
    last_modified_by = relationship("User", foreign_keys=[last_modified_by_user_id], viewonly=True)
    
    __table_args__ = (
        UniqueConstraint("workspace_id", name="uq_archive_policy_per_workspace"),
        Index("ix_archive_policies_workspace_id", "workspace_id"),
    )


class DeletedItem(Base, TimestampMixin):
    """
    Soft-deleted items in trash bin.
    Tracks deleted projects, tasks, comments, and files with restoration capability.
    
    Ref: Module 8 - Feature 2.2 - Trash Bin & Soft Delete
    """
    __tablename__ = "deleted_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    # Soft delete tracking
    entity_type = Column(String(50), nullable=False)  # "project", "task", "comment", "file"
    entity_id = Column(String(36), nullable=False)
    deleted_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    deleted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Data snapshot for restoration
    original_data = Column(JSON, nullable=False)  # Original entity data before deletion
    deletion_reason = Column(String(255), nullable=True)  # User-provided reason
    
    # Restoration tracking
    restored_at = Column(DateTime, nullable=True)
    restored_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_restored = Column(Boolean, nullable=False, default=False)
    
    # Foreign keys
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    deleted_by = relationship("User", foreign_keys=[deleted_by_user_id], viewonly=True)
    restored_by = relationship("User", foreign_keys=[restored_by_user_id], viewonly=True)
    
    __table_args__ = (
        Index("ix_deleted_items_workspace_id", "workspace_id"),
        Index("ix_deleted_items_entity_type", "entity_type"),
        Index("ix_deleted_items_deleted_at", "deleted_at"),
        Index("ix_deleted_items_is_restored", "is_restored"),
    )


class ArchivedDataSnapshot(Base, TimestampMixin):
    """
    Snapshots of archived projects with read-only data.
    Stores archived project state for historical reference and audit trails.
    
    Ref: Module 8 - Feature 2.1 - AC 2 - State Transition & Immutability
    """
    __tablename__ = "archived_snapshots"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    # Archive reference
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    archived_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    archived_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Snapshot data
    project_data = Column(JSON, nullable=False)  # Full project state at archival time
    task_count = Column(Integer, nullable=False, default=0)
    total_time_logged = Column(Integer, nullable=True)  # Total hours/minutes
    comment_count = Column(Integer, nullable=False, default=0)
    file_count = Column(Integer, nullable=False, default=0)
    
    # Metadata
    archive_reason = Column(String(255), nullable=True)
    storage_location = Column(String(255), nullable=True)  # Path to cold storage (S3/archive DB)
    
    # Foreign keys
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    archived_by = relationship("User", foreign_keys=[archived_by_user_id], viewonly=True)
    
    __table_args__ = (
        Index("ix_archived_snapshots_workspace_id", "workspace_id"),
        Index("ix_archived_snapshots_project_id", "project_id"),
        Index("ix_archived_snapshots_archived_at", "archived_at"),
    )


class DataExportRequest(Base, TimestampMixin):
    """
    Asynchronous data export requests for GDPR compliance.
    Tracks export status, download links, and expiration.
    
    Ref: Module 8 - Feature 2.3 - Data Export & Portability (AC 1)
    """
    __tablename__ = "data_export_requests"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    # Request info
    requested_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    export_format = Column(String(20), nullable=False, default="json")  # json, csv
    scope = Column(String(50), nullable=False)  # "all", "projects", "workspace"
    scope_id = Column(String(36), nullable=True)  # Project ID if scope="projects"
    
    # Status tracking
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    progress_percent = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    
    # Export output
    file_size_bytes = Column(Integer, nullable=True)
    file_path = Column(String(500), nullable=True)  # S3 key or local file path
    download_token = Column(String(255), nullable=True)  # Secure token for download link
    download_count = Column(Integer, nullable=False, default=0)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)  # Link expires after 24 hours
    completed_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    requested_by = relationship("User", foreign_keys=[requested_by_user_id], viewonly=True)
    
    __table_args__ = (
        Index("ix_data_export_requests_workspace_id", "workspace_id"),
        Index("ix_data_export_requests_requested_by_user_id", "requested_by_user_id"),
        Index("ix_data_export_requests_status", "status"),
        Index("ix_data_export_requests_expires_at", "expires_at"),
    )


class DataRetentionLog(Base, TimestampMixin):
    """
    Audit log for retention policy enforcement.
    Tracks data purge events, archival events, and retention rule applications.
    
    Ref: Module 8 - Section 3.2 - Data Retention Policy
    """
    __tablename__ = "data_retention_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    # Retention action
    action_type = Column(String(50), nullable=False)  # "archive", "soft_delete", "hard_delete", "export"
    data_retention_type = Column(String(50), nullable=False)  # deleted_items, system_logs, user_uploads
    
    # Entity info
    entity_type = Column(String(50), nullable=False)  # project, task, comment, file
    entity_id = Column(String(36), nullable=False)
    entity_count = Column(Integer, nullable=False, default=1)  # Batch operations
    
    # Policy details
    retention_days = Column(Integer, nullable=True)
    executed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    executed_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Metadata
    details = Column(JSON, nullable=True)  # Additional context
    rows_affected = Column(Integer, nullable=False, default=0)
    
    # Foreign keys
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    executed_by = relationship("User", foreign_keys=[executed_by_user_id], viewonly=True)
    
    __table_args__ = (
        Index("ix_data_retention_logs_workspace_id", "workspace_id"),
        Index("ix_data_retention_logs_action_type", "action_type"),
        Index("ix_data_retention_logs_executed_at", "executed_at"),
    )


class AuditLog(Base, TimestampMixin):
    """
    Comprehensive audit trail for compliance and forensic analysis.
    Logs all significant system actions including data access, modifications, and deletions.
    
    Ref: Module 8 - Section 3.2 - Data Retention Policy (90-day retention)
    """
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    # Action tracking
    action = Column(String(100), nullable=False)  # CREATE, READ, UPDATE, DELETE, EXPORT, ARCHIVE
    resource_type = Column(String(50), nullable=False)  # project, task, file, user, etc.
    resource_id = Column(String(36), nullable=False)
    
    # User info
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_email = Column(String(255), nullable=True)  # For deleted users
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Change details
    changes = Column(JSON, nullable=True)  # {field: {old: value, new: value}}
    status_code = Column(String(20), nullable=True)  # success, failure, error
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    logged_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign keys
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    user = relationship("User", foreign_keys=[user_id], viewonly=True)
    
    __table_args__ = (
        Index("ix_audit_logs_workspace_id", "workspace_id"),
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_resource_type", "resource_type"),
        Index("ix_audit_logs_logged_at", "logged_at"),
    )
