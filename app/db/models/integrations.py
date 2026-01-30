"""
Entity Models for Functional Module 10-12: API Integration, Authentication Tokens, and Webhooks.
Provides ApiToken, WebhookEndpoint, WebhookEvent, IntegrationBinding models.
Ref: docs/docs - PronaFlow React&FastAPI/02-Architeture/Entities/ApiToken*.md
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Index, Table, Column, Boolean, Text, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.users import User
    from app.db.models.workspaces import Workspace


# ======= Entity Tables =======

class ApiToken(Base, TimestampMixin):
    """
    ApiToken Model - API authentication tokens for users/bots.
    Manages API access tokens for programmatic access.
    Ref: Entities/ApiToken.md
    """
    __tablename__ = "api_tokens"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for API token"
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Token owner"
    )

    # Token Information
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Token name (e.g., 'CI Bot', 'Mobile App')"
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="Hashed token (never store plaintext)"
    )

    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of last use"
    )

    # Expiration
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Token expiration date (nullable = no expiration)"
    )

    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when token was revoked"
    )

    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether token is revoked"
    )

    # Relationships
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    scopes: Mapped[List["ApiScope"]] = relationship(secondary="api_token_scopes", back_populates="tokens")

    # Indexes
    __table_args__ = (
        Index('ix_api_tokens_user_id', 'user_id'),
        Index('ix_api_tokens_is_revoked', 'is_revoked'),
    )


class ApiScope(Base, TimestampMixin):
    """
    ApiScope Model - OAuth-like scopes for API tokens.
    Defines fine-grained permissions for API tokens.
    Ref: Entities/ApiScope.md
    """
    __tablename__ = "api_scopes"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for API scope"
    )

    # Scope Information
    scope: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Scope identifier (e.g., 'tasks:read', 'tasks:write', 'projects:read')"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Scope description"
    )

    # Relationships
    tokens: Mapped[List["ApiToken"]] = relationship(secondary="api_token_scopes", back_populates="scopes")


# Association table for many-to-many relationship between ApiToken and ApiScope
api_token_scopes = Table(
    'api_token_scopes',
    Base.metadata,
    Column('token_id', UUID(as_uuid=True), ForeignKey('api_tokens.id'), primary_key=True),
    Column('scope_id', UUID(as_uuid=True), ForeignKey('api_scopes.id'), primary_key=True),
)


class WebhookEndpoint(Base, TimestampMixin):
    """
    WebhookEndpoint Model - Webhook configuration for external integrations.
    Manages webhook endpoints that receive event notifications.
    Ref: Entities/WebhookEndpoint.md
    """
    __tablename__ = "webhook_endpoints"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for webhook endpoint"
    )

    # Foreign Keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to workspace"
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        comment="User who created the webhook"
    )

    # Webhook Configuration
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Webhook name"
    )

    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Target URL to deliver events"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether webhook is active"
    )

    secret: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Secret key for HMAC signature verification"
    )

    # Subscribed Events
    subscribed_events: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="JSON object with subscribed event types as keys (e.g., {'task.created': true, 'task.updated': true})"
    )

    # Delivery Settings
    retry_policy: Mapped[str] = mapped_column(
        SQLEnum('EXPONENTIAL', 'LINEAR', 'NO_RETRY', name='retry_policy'),
        default='EXPONENTIAL',
        nullable=False,
        comment="Retry strategy for failed deliveries"
    )

    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
        comment="Maximum number of delivery retries"
    )

    timeout_seconds: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
        comment="Request timeout in seconds"
    )

    # Statistics
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of last event delivery"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(foreign_keys=[workspace_id])
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    deliveries: Mapped[List["WebhookDelivery"]] = relationship(back_populates="endpoint", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_webhook_endpoints_workspace_id', 'workspace_id'),
        Index('ix_webhook_endpoints_is_active', 'is_active'),
    )


class WebhookEvent(Base, TimestampMixin):
    """
    WebhookEvent Model - Events that can be subscribed to via webhooks.
    Defines available webhook event types.
    Ref: Entities/WebhookEvent.md
    """
    __tablename__ = "webhook_events"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for webhook event"
    )

    # Event Information
    event_type: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Event type (e.g., 'task.created', 'project.updated')"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Event description"
    )

    payload_schema: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="JSON Schema for event payload"
    )

    # Relationships
    deliveries: Mapped[List["WebhookDelivery"]] = relationship(back_populates="event")


class WebhookDelivery(Base, TimestampMixin):
    """
    WebhookDelivery Model - Records of webhook event deliveries.
    Tracks each attempt to deliver an event to a webhook endpoint.
    Ref: Entities/WebhookDelivery.md
    """
    __tablename__ = "webhook_deliveries"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for webhook delivery"
    )

    # Foreign Keys
    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('webhook_endpoints.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to webhook endpoint"
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('webhook_events.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
        comment="Reference to webhook event type"
    )

    domain_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('domain_events.id', ondelete='SET NULL'),
        nullable=True,
        comment="Reference to domain event that triggered delivery"
    )

    # Delivery Status
    status: Mapped[str] = mapped_column(
        SQLEnum('PENDING', 'DELIVERED', 'FAILED', 'RETRYING', name='webhook_delivery_status'),
        default='PENDING',
        nullable=False,
        index=True,
        comment="Delivery status"
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of delivery attempts"
    )

    # Response Information
    response_status_code: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="HTTP response status code"
    )

    response_body: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="HTTP response body (truncated)"
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if delivery failed"
    )

    # Timing
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Scheduled time for next retry"
    )

    # Relationships
    endpoint: Mapped["WebhookEndpoint"] = relationship(back_populates="deliveries", foreign_keys=[endpoint_id])
    event: Mapped["WebhookEvent"] = relationship(back_populates="deliveries", foreign_keys=[event_id])

    # Indexes
    __table_args__ = (
        Index('ix_webhook_deliveries_endpoint_id', 'endpoint_id'),
        Index('ix_webhook_deliveries_status', 'status'),
        Index('ix_webhook_deliveries_created_at', 'created_at'),
    )


class IntegrationBinding(Base, TimestampMixin):
    """
    IntegrationBinding Model - External service integrations (Slack, GitHub, etc.).
    Manages connections to external services.
    Ref: Entities/IntegrationBinding.md
    """
    __tablename__ = "integration_bindings"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for integration binding"
    )

    # Foreign Keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to workspace"
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        comment="User who created the integration"
    )

    # Integration Information
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Integration provider (e.g., 'slack', 'github', 'jira')"
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Integration name/identifier"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether integration is active"
    )

    # Credentials (encrypted)
    credentials: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Encrypted credentials/tokens (should be encrypted in app layer)"
    )

    # Configuration
    config: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Integration-specific configuration"
    )

    # Status
    status: Mapped[str] = mapped_column(
        SQLEnum('ACTIVE', 'INACTIVE', 'ERROR', name='integration_status'),
        default='ACTIVE',
        nullable=False,
        comment="Integration status"
    )

    last_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Last error message"
    )

    last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of last successful sync"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(foreign_keys=[workspace_id])
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])

    # Indexes
    __table_args__ = (
        Index('ix_integration_bindings_workspace_id', 'workspace_id'),
        Index('ix_integration_bindings_provider', 'provider'),
        Index('ix_integration_bindings_is_active', 'is_active'),
    )
