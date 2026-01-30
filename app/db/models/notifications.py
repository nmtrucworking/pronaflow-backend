"""
Entity Models for Functional Module 6: Notifications & Events.
Provides Notification, NotificationTemplate, DomainEvent, EventConsumer models.
Ref: docs/docs - PronaFlow React&FastAPI/02-Architeture/Entities/Notification*.md
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Index, Table, Column, Boolean, Text, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.users import User


# ======= Entity Tables =======

class Notification(Base, TimestampMixin):
    """
    Notification Model - User notifications for events.
    Ref: Entities/Notification.md
    """
    __tablename__ = "notifications"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for notification"
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Notification receiver"
    )

    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('domain_events.id', ondelete='SET NULL'),
        nullable=True,
        comment="Reference to domain event"
    )

    # Content
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Notification title (rendered)"
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Notification content (rendered HTML/JSON)"
    )

    # Priority
    priority: Mapped[str] = mapped_column(
        SQLEnum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='notification_priority'),
        default='MEDIUM',
        nullable=False,
        comment="Notification priority level"
    )

    # Status
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether notification has been read"
    )

    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when notification was read"
    )

    # Expiration
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="TTL - when notification expires and can be deleted"
    )

    # Relationships
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    event: Mapped[Optional["DomainEvent"]] = relationship(foreign_keys=[event_id])

    # Indexes
    __table_args__ = (
        Index('ix_notifications_user_id', 'user_id'),
        Index('ix_notifications_is_read', 'is_read'),
        Index('ix_notifications_created_at', 'created_at'),
    )


class NotificationTemplate(Base, TimestampMixin):
    """
    NotificationTemplate Model - Templates for rendering notifications.
    """
    __tablename__ = "notification_templates"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for notification template"
    )

    # Template Information
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="Template name (e.g., 'task_assigned', 'comment_added')"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Template description"
    )

    # Content Templates
    title_template: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Title template with placeholders (e.g., 'Task {task_title} assigned to you')"
    )

    content_template: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Content template with placeholders (rich-text HTML/JSON)"
    )

    # Metadata
    variables: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Available variables for substitution"
    )

    # Relationships
    notifications: Mapped[List["Notification"]] = relationship(foreign_keys="Notification.event_id")


class DomainEvent(Base, TimestampMixin):
    """
    DomainEvent Model - System-wide domain events.
    Tracks significant events in the system (task created, user invited, etc.)
    Ref: Entities/DomainEvent.md
    """
    __tablename__ = "domain_events"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for domain event"
    )

    # Event Information
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of event (e.g., 'task.created', 'user.invited')"
    )

    aggregate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="ID of the aggregate root that triggered the event"
    )

    aggregate_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Type of aggregate (e.g., 'Task', 'User')"
    )

    # Event Payload
    payload: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Event data payload"
    )

    # Metadata
    meta: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Additional metadata (user_id, ip_address, etc.)"
    )

    # Published Flag
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether event has been published to consumers"
    )

    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when event was published"
    )

    # Relationships
    notifications: Mapped[List["Notification"]] = relationship(back_populates="event", foreign_keys="Notification.event_id")
    consumer_events: Mapped[List["EventConsumer"]] = relationship(back_populates="event", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_domain_events_event_type', 'event_type'),
        Index('ix_domain_events_aggregate_id', 'aggregate_id'),
        Index('ix_domain_events_is_published', 'is_published'),
    )


class EventConsumer(Base, TimestampMixin):
    """
    EventConsumer Model - Tracks which consumers have processed events.
    Used for event sourcing and pub/sub patterns.
    Ref: Entities/EventConsumer.md
    """
    __tablename__ = "event_consumers"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for event consumer"
    )

    # Foreign Keys
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('domain_events.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to domain event"
    )

    # Consumer Information
    consumer_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Name of the consumer service/handler"
    )

    # Processing Status
    status: Mapped[str] = mapped_column(
        SQLEnum('PENDING', 'PROCESSING', 'SUCCEEDED', 'FAILED', name='event_consumer_status'),
        default='PENDING',
        nullable=False,
        index=True,
        comment="Processing status"
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of retry attempts"
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if processing failed"
    )

    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when event was processed"
    )

    # Relationships
    event: Mapped["DomainEvent"] = relationship(back_populates="consumer_events", foreign_keys=[event_id])

    # Indexes
    __table_args__ = (
        Index('ix_event_consumers_event_id', 'event_id'),
        Index('ix_event_consumers_consumer_name', 'consumer_name'),
        Index('ix_event_consumers_status', 'status'),
    )


class NotificationPreference(Base, TimestampMixin):
    """
    NotificationPreference Model - User notification preferences.
    Tracks which types of notifications users want to receive.
    """
    __tablename__ = "notification_preferences"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for notification preference"
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        comment="Reference to user"
    )

    # Notification Settings
    notify_task_assigned: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Notify when task is assigned"
    )

    notify_task_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Notify when task is completed"
    )

    notify_comment_reply: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Notify on comment replies"
    )

    notify_mention: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Notify when mentioned"
    )

    notify_workspace_update: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Notify on workspace updates"
    )

    # Channel Preferences
    email_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Enable email notifications"
    )

    in_app_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Enable in-app notifications"
    )

    # Relationships
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
