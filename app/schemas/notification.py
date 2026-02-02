"""
Pydantic schemas for Module 7: Event-Driven Notification System.

Schemas:
- NotificationCreate: Create notification
- NotificationRead: Read notification (with read/unread status)
- NotificationList: Paginated notification list
- NotificationTemplateBase: Notification template base
- NotificationTemplateCreate: Create template
- NotificationTemplateRead: Read template
- NotificationPreferenceCreate: Create user preferences
- NotificationPreferenceRead: Read user preferences
- WatcherCreate: Create watcher
- WatcherRead: Read watcher
- MarkAsReadRequest: Mark notification as read
- InteractionTrackingRequest: Track user interactions
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.db.enums import (
    NotificationTypeEnum, NotificationChannelEnum,
    NotificationPriorityEnum, NotificationStatusEnum,
    TemplateLocaleEnum
)


# ============ Notification Base Schemas ============

class NotificationBase(BaseModel):
    """Base schema for notifications."""
    title: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1)
    action_url: Optional[str] = None
    event_type: NotificationTypeEnum
    priority: NotificationPriorityEnum = NotificationPriorityEnum.MEDIUM
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""
    event_id: str = Field(..., description="Unique event ID for idempotency")
    recipient_id: str = Field(..., description="User ID of notification recipient")
    workspace_id: str = Field(..., description="Workspace context")
    channels_used: List[NotificationChannelEnum] = Field(
        default=[NotificationChannelEnum.IN_APP],
        description="Delivery channels"
    )
    scheduled_at: Optional[datetime] = None


class NotificationRead(NotificationBase):
    """Schema for reading a notification."""
    id: str
    recipient_id: str
    workspace_id: str
    event_id: str
    channels_used: List[NotificationChannelEnum]
    status: NotificationStatusEnum
    aggregation_group_id: Optional[str] = None
    aggregated_count: int = 1
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for notification list with pagination."""
    items: List[NotificationRead]
    total: int
    page: int
    page_size: int
    has_more: bool


class MarkAsReadRequest(BaseModel):
    """Schema for marking notification as read."""
    notification_id: str
    read: bool = True


class MarkMultipleAsReadRequest(BaseModel):
    """Schema for marking multiple notifications as read."""
    notification_ids: List[str]
    read: bool = True


# ============ Notification Template Schemas ============

class TemplateVariableDefine(BaseModel):
    """Template variable definition."""
    name: str = Field(..., description="Variable name (e.g., 'user_name')")
    type: str = Field(..., description="Variable type (string, number, date)")
    required: bool = True
    description: Optional[str] = None


class NotificationTemplateBase(BaseModel):
    """Base schema for notification templates."""
    template_key: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique template identifier (e.g., 'task_assigned')"
    )
    locale: TemplateLocaleEnum = TemplateLocaleEnum.EN
    subject: str = Field(..., description="Email subject template")
    body_template: str = Field(..., description="Template body (Mustache/Jinja2 format)")
    required_variables: List[TemplateVariableDefine] = Field(default_factory=list)
    email_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    priority: NotificationPriorityEnum = NotificationPriorityEnum.MEDIUM
    is_active: bool = True


class NotificationTemplateCreate(NotificationTemplateBase):
    """Schema for creating a notification template."""
    workspace_id: str = Field(..., description="Workspace context")


class NotificationTemplateRead(NotificationTemplateBase):
    """Schema for reading a notification template."""
    id: str
    workspace_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationTemplateListResponse(BaseModel):
    """Schema for template list with pagination."""
    items: List[NotificationTemplateRead]
    total: int
    page: int
    page_size: int


# ============ Notification Preference Schemas ============

class NotificationPreferenceBase(BaseModel):
    """Base schema for notification preferences."""
    notifications_enabled: bool = True
    email_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    enable_digest_batching: bool = True
    digest_frequency: str = "hourly"  # "realtime", "hourly", "daily", "weekly"
    unsubscribed_event_types: List[NotificationTypeEnum] = Field(default_factory=list)
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None  # "HH:MM" format
    quiet_hours_end: Optional[str] = None


class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Schema for creating notification preferences."""
    user_id: str = Field(..., description="User ID")
    workspace_id: str = Field(..., description="Workspace ID")


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences."""
    notifications_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    enable_digest_batching: Optional[bool] = None
    digest_frequency: Optional[str] = None
    unsubscribed_event_types: Optional[List[NotificationTypeEnum]] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class NotificationPreferenceRead(NotificationPreferenceBase):
    """Schema for reading notification preferences."""
    id: str
    user_id: str
    workspace_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Watcher Schemas ============

class WatcherBase(BaseModel):
    """Base schema for watchers."""
    entity_type: str = Field(..., description="Entity type: 'task', 'project', etc.")
    entity_id: str = Field(..., description="Entity ID to watch")
    is_watching: bool = True
    custom_channels: Optional[List[NotificationChannelEnum]] = None
    notify_on_types: Optional[List[NotificationTypeEnum]] = None


class WatcherCreate(WatcherBase):
    """Schema for creating a watcher."""
    user_id: str = Field(..., description="User ID")
    workspace_id: str = Field(..., description="Workspace ID")


class WatcherRead(WatcherBase):
    """Schema for reading a watcher."""
    id: str
    user_id: str
    workspace_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WatcherListResponse(BaseModel):
    """Schema for watcher list."""
    items: List[WatcherRead]
    total: int


class WatchToggleRequest(BaseModel):
    """Schema for toggling watch status."""
    entity_type: str = Field(..., description="Entity type")
    entity_id: str = Field(..., description="Entity ID")
    is_watching: bool = Field(..., description="Watch or unwatch")


# ============ Interaction Tracking Schemas ============

class InteractionLogBase(BaseModel):
    """Base schema for interaction logs."""
    interaction_type: str = Field(
        ...,
        description="Type of interaction: 'opened', 'clicked', 'read', 'approved', 'rejected'"
    )
    action_label: Optional[str] = None
    action_url_clicked: Optional[str] = None
    source_channel: NotificationChannelEnum
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class InteractionTrackingRequest(InteractionLogBase):
    """Schema for tracking user interactions."""
    notification_id: str = Field(..., description="Notification ID")


class InteractionLogRead(InteractionLogBase):
    """Schema for reading interaction logs."""
    id: str
    notification_id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class InteractionLogListResponse(BaseModel):
    """Schema for interaction log list."""
    items: List[InteractionLogRead]
    total: int
    page: int
    page_size: int


# ============ Event Schemas ============

class EventLogBase(BaseModel):
    """Base schema for event logs."""
    event_type: NotificationTypeEnum
    source_entity_type: str = Field(..., description="Entity type")
    source_entity_id: str = Field(..., description="Entity ID")
    event_payload: Dict[str, Any]
    triggered_by_user_id: Optional[str] = None


class EventLogCreate(EventLogBase):
    """Schema for creating event logs."""
    event_id: str = Field(..., description="Unique event ID for idempotency")
    workspace_id: str = Field(..., description="Workspace ID")


class EventLogRead(EventLogBase):
    """Schema for reading event logs."""
    id: str
    event_id: str
    workspace_id: str
    is_processed: bool
    processed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Aggregation & Batching Schemas ============

class AggregationRuleBase(BaseModel):
    """Base schema for aggregation rules."""
    entity_type: str = Field(..., description="Entity type to aggregate (task, project, etc.)")
    entity_id: str = Field(..., description="Entity ID")
    event_types: List[NotificationTypeEnum] = Field(
        default_factory=list,
        description="Event types to aggregate"
    )
    debounce_time_ms: int = Field(default=120000, description="Debounce time in milliseconds")
    max_aggregation_size: int = Field(default=10, description="Max events to aggregate")


class BatchingPreferenceBase(BaseModel):
    """Schema for batching preferences."""
    enabled: bool = True
    frequency: str = Field(default="hourly", description="Batching frequency")
    min_items: int = Field(default=2, description="Minimum items to trigger batch")
    max_items: int = Field(default=50, description="Maximum items per batch")


# ============ Statistics & Analytics Schemas ============

class NotificationStatistics(BaseModel):
    """Schema for notification statistics."""
    total_sent: int
    total_read: int
    open_rate: float  # Percentage (0-100)
    click_through_rate: float  # Percentage (0-100)
    top_event_types: Dict[str, int]  # Event type -> count
    top_channels: Dict[str, int]  # Channel -> count
    period: str = "all"  # "today", "week", "month", "all"


class ChannelStatistics(BaseModel):
    """Schema for channel-specific statistics."""
    channel: NotificationChannelEnum
    total_sent: int
    successful: int
    failed: int
    success_rate: float
    average_delivery_time_ms: int


# ============ System Error Response ============

class NotificationError(BaseModel):
    """Schema for notification errors."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    retry_count: Optional[int] = None
    next_retry_at: Optional[datetime] = None
