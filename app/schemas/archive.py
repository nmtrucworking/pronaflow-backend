"""
Pydantic schemas for Module 8: Data Archiving and Compliance.

Defines request/response models for archive management, trash bin operations,
data exports, retention policies, and audit logging.

Ref: Module 8 - Data Archiving and Compliance
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============ Archive Policy Schemas ============

class ArchivePolicyBase(BaseModel):
    """Base schema for archive policy configuration"""
    inactive_days: int = Field(180, ge=1, description="Days of inactivity before archiving")
    is_enabled: bool = Field(True, description="Whether auto-archiving is enabled")
    trash_retention_days: int = Field(30, ge=1, description="Days to keep deleted items")
    auto_purge_enabled: bool = Field(True, description="Whether auto-purge is enabled")
    export_link_expiry_hours: int = Field(24, ge=1, description="Hours until export link expires")
    max_export_file_size_mb: int = Field(500, ge=10, description="Max export file size in MB")
    notes: Optional[str] = Field(None, max_length=1000)


class ArchivePolicyCreate(ArchivePolicyBase):
    """Schema for creating archive policy"""
    workspace_id: str = Field(..., description="Workspace ID")


class ArchivePolicyUpdate(BaseModel):
    """Schema for updating archive policy"""
    inactive_days: Optional[int] = Field(None, ge=1)
    is_enabled: Optional[bool] = None
    trash_retention_days: Optional[int] = Field(None, ge=1)
    auto_purge_enabled: Optional[bool] = None
    export_link_expiry_hours: Optional[int] = Field(None, ge=1)
    max_export_file_size_mb: Optional[int] = Field(None, ge=10)
    notes: Optional[str] = Field(None, max_length=1000)


class ArchivePolicyRead(ArchivePolicyBase):
    """Schema for reading archive policy"""
    id: str
    workspace_id: str
    created_by_user_id: Optional[str]
    last_modified_by_user_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Deleted Item Schemas ============

class DeletedItemBase(BaseModel):
    """Base schema for deleted items"""
    entity_type: str = Field(..., description="Type of deleted entity: project, task, comment, file")
    deletion_reason: Optional[str] = Field(None, max_length=255)


class DeletedItemRead(DeletedItemBase):
    """Schema for reading deleted items (trash bin)"""
    id: str
    workspace_id: str
    entity_id: str
    deleted_by_user_id: Optional[str]
    deleted_at: datetime
    original_data: Dict[str, Any]
    is_restored: bool
    restored_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeletedItemListResponse(BaseModel):
    """Paginated response for deleted items list"""
    items: List[DeletedItemRead]
    total: int
    page: int
    page_size: int
    has_more: bool


class RestoreDeletedItemRequest(BaseModel):
    """Request to restore deleted item"""
    item_id: str = Field(..., description="Deleted item ID")


# ============ Archived Data Snapshot Schemas ============

class ArchivedSnapshotRead(BaseModel):
    """Schema for reading archived project snapshots"""
    id: str
    workspace_id: str
    project_id: str
    archived_at: datetime
    archived_by_user_id: Optional[str]
    project_data: Dict[str, Any]
    task_count: int
    total_time_logged: Optional[int]
    comment_count: int
    file_count: int
    archive_reason: Optional[str]
    storage_location: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArchivedSnapshotListResponse(BaseModel):
    """Paginated response for archived snapshots"""
    items: List[ArchivedSnapshotRead]
    total: int
    page: int
    page_size: int
    has_more: bool


# ============ Data Export Schemas ============

class DataExportRequestCreate(BaseModel):
    """Schema for requesting data export"""
    export_format: str = Field("json", description="json or csv")
    scope: str = Field("all", description="all, projects, or workspace")
    scope_id: Optional[str] = Field(None, description="Project ID if scope=projects")


class DataExportRequestRead(BaseModel):
    """Schema for reading export request status"""
    id: str
    workspace_id: str
    requested_by_user_id: str
    export_format: str
    scope: str
    status: str  # pending, processing, completed, failed
    progress_percent: int
    error_message: Optional[str]
    file_size_bytes: Optional[int]
    download_count: int
    expires_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class DataExportResponse(BaseModel):
    """Schema for download response"""
    export_id: str
    download_url: str
    expires_at: datetime
    file_size_bytes: Optional[int]
    format: str


class DataExportListResponse(BaseModel):
    """Paginated response for export requests"""
    items: List[DataExportRequestRead]
    total: int
    page: int
    page_size: int
    has_more: bool


# ============ Data Retention Policy Schemas ============

class RetentionPolicyBase(BaseModel):
    """Base schema for retention policy"""
    data_retention_type: str = Field(..., description="deleted_items, system_logs, or user_uploads")
    retention_days: int = Field(..., ge=1, description="Days to retain data")
    auto_purge_enabled: bool = Field(True, description="Whether auto-purge is enabled")


class RetentionPolicyRead(RetentionPolicyBase):
    """Schema for reading retention policy"""
    id: str
    workspace_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Audit Log Schemas ============

class AuditLogBase(BaseModel):
    """Base schema for audit logs"""
    action: str = Field(..., description="CREATE, READ, UPDATE, DELETE, EXPORT, ARCHIVE")
    resource_type: str = Field(..., description="project, task, file, user, etc")
    resource_id: str
    status_code: Optional[str] = Field(None, description="success, failure, error")
    error_message: Optional[str] = None


class AuditLogRead(AuditLogBase):
    """Schema for reading audit logs"""
    id: str
    workspace_id: str
    user_id: Optional[str]
    user_email: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    changes: Optional[Dict[str, Any]]
    logged_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Paginated response for audit logs"""
    items: List[AuditLogRead]
    total: int
    page: int
    page_size: int
    has_more: bool


class AuditLogQueryFilter(BaseModel):
    """Query filters for audit log search"""
    action: Optional[str] = None
    resource_type: Optional[str] = None
    user_id: Optional[str] = None
    status_code: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


# ============ Response Models ============

class ArchiveActionResponse(BaseModel):
    """Response for archive actions"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class BulkArchiveResponse(BaseModel):
    """Response for bulk archiving operations"""
    success: bool
    total_processed: int
    archived_count: int
    failed_count: int
    errors: List[Dict[str, str]] = []


class Statistics(BaseModel):
    """Archiving statistics"""
    active_items_count: int
    archived_items_count: int
    trash_bin_items_count: int
    total_storage_used_mb: float
    oldest_archive_date: Optional[datetime]
    upcoming_purge_count: int
