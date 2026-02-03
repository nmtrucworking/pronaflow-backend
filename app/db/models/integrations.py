"""
Entity Models for Functional Module 10-12: API Integration, Authentication Tokens, and Webhooks.
Provides ApiToken, WebhookEndpoint, WebhookEvent, IntegrationBinding models.
Ref: docs/docs - PronaFlow React&FastAPI/02-Architeture/Entities/ApiToken*.md
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Index, Table, Column, Boolean, Text, Integer, Enum as SQLEnum, UniqueConstraint
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


class ApiTokenScope(Base):
    """
    ApiTokenScope Model - Junction table for API tokens and scopes.
    Maps API tokens to their assigned scopes for permission control.
    Ref: Module 12 - Feature 2.1 - AC 3
    """
    __tablename__ = "api_token_scopes"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for token-scope mapping"
    )

    # Foreign Keys
    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("api_tokens.id", ondelete="CASCADE"),
        nullable=False,
        comment="API token reference"
    )

    scope_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("api_scopes.id", ondelete="CASCADE"),
        nullable=False,
        comment="API scope reference"
    )

    # Indexes and Constraints
    __table_args__ = (
        UniqueConstraint('token_id', 'scope_id', name='uq_token_scope'),
        Index("ix_api_token_scopes_token_id", "token_id"),
        Index("ix_api_token_scopes_scope_id", "scope_id"),
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


class ApiUsageLog(Base, TimestampMixin):
    """
    ApiUsageLog Model - Tracks API usage for rate limiting and analytics.
    Records each API request for quota management and monitoring.
    Ref: Module 12 - Feature 2.1 - Rate Limiting
    """
    __tablename__ = "api_usage_logs"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for usage log entry"
    )

    # Foreign Keys
    api_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('api_tokens.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="API token used for the request"
    )

    # Request Details
    method: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="HTTP method (GET, POST, PATCH, DELETE)"
    )

    endpoint: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="API endpoint path"
    )

    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="HTTP response status code"
    )

    response_time_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Response time in milliseconds"
    )

    # Indexes
    __table_args__ = (
        Index('ix_api_usage_logs_api_token_id', 'api_token_id'),
        Index('ix_api_usage_logs_created_at', 'created_at'),
    )


class OAuthApp(Base, TimestampMixin):
    """
    OAuthApp Model - OAuth provider applications.
    Defines external services that can be integrated via OAuth (GitHub, Google, Slack, etc.).
    Ref: Module 12 - Feature 3 - OAuth
    """
    __tablename__ = "oauth_apps"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for OAuth app"
    )

    # OAuth App Details
    provider_name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="OAuth provider name (github, google_calendar, slack, etc.)"
    )

    client_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="OAuth client ID"
    )

    client_secret: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="OAuth client secret (should be encrypted)"
    )

    authorize_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="OAuth authorization endpoint URL"
    )

    token_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="OAuth token endpoint URL"
    )

    scopes: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="OAuth scopes required by PronaFlow"
    )

    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether OAuth app is enabled for use"
    )

    # Relationships
    connections: Mapped[List["OAuthConnection"]] = relationship(back_populates="oauth_app", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_oauth_apps_provider_name', 'provider_name'),
        Index('ix_oauth_apps_is_enabled', 'is_enabled'),
    )


class OAuthConnection(Base, TimestampMixin):
    """
    OAuthConnection Model - User OAuth connections to external services.
    Stores user's OAuth tokens and connection details.
    Ref: Module 12 - Feature 3 - AC 2
    """
    __tablename__ = "oauth_connections"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for OAuth connection"
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="User who owns the connection"
    )

    oauth_app_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('oauth_apps.id', ondelete='RESTRICT'),
        nullable=False,
        comment="OAuth app being connected"
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Workspace context"
    )

    # OAuth Tokens
    access_token: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="OAuth access token (should be encrypted)"
    )

    refresh_token: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="OAuth refresh token (should be encrypted)"
    )

    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Token expiration timestamp"
    )

    # Connection Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether connection is active"
    )

    last_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last time token was verified as valid"
    )

    external_user_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="External service user ID"
    )

    # Relationships
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    oauth_app: Mapped["OAuthApp"] = relationship(back_populates="connections", foreign_keys=[oauth_app_id])
    workspace: Mapped["Workspace"] = relationship(foreign_keys=[workspace_id])
    bindings: Mapped[List["IntegrationBinding"]] = relationship(back_populates="oauth_connection")

    # Indexes
    __table_args__ = (
        Index('ix_oauth_connections_user_id', 'user_id'),
        Index('ix_oauth_connections_workspace_id', 'workspace_id'),
        Index('ix_oauth_connections_is_active', 'is_active'),
    )


class Plugin(Base, TimestampMixin):
    """
    Plugin Model - Plugin marketplace entries.
    Defines available plugins that can be installed in workspaces.
    Ref: Module 12 - Feature 5 - Plugin Marketplace
    """
    __tablename__ = "plugins"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for plugin"
    )

    # Plugin Metadata
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Plugin name"
    )

    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Current plugin version (semantic versioning)"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Plugin description"
    )

    author: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Plugin author/developer"
    )

    # Plugin Details
    manifest: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Plugin manifest (metadata, hooks, permissions)"
    )

    repository_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Git repository URL"
    )

    documentation_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Documentation URL"
    )

    icon_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Plugin icon URL"
    )

    # Marketplace Status
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether plugin is verified by PronaFlow team"
    )

    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether plugin is available in marketplace"
    )

    # Relationships
    installations: Mapped[List["PluginInstallation"]] = relationship(back_populates="plugin", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_plugins_name', 'name'),
        Index('ix_plugins_is_enabled', 'is_enabled'),
    )


class PluginInstallation(Base, TimestampMixin):
    """
    PluginInstallation Model - Plugin installations per workspace.
    Tracks which plugins are installed in which workspaces.
    Ref: Module 12 - Feature 5 - AC 2
    """
    __tablename__ = "plugin_installations"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for plugin installation"
    )

    # Foreign Keys
    plugin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('plugins.id', ondelete='CASCADE'),
        nullable=False,
        comment="Plugin being installed"
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Workspace where plugin is installed"
    )

    installed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        comment="User who installed the plugin"
    )

    # Installation Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether plugin is active"
    )

    configuration: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Plugin-specific configuration"
    )

    # Plugin State
    last_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Last error message if plugin failed"
    )

    # Relationships
    plugin: Mapped["Plugin"] = relationship(back_populates="installations", foreign_keys=[plugin_id])
    workspace: Mapped["Workspace"] = relationship(foreign_keys=[workspace_id])
    installer: Mapped["User"] = relationship(foreign_keys=[installed_by])

    # Indexes
    __table_args__ = (
        Index('ix_plugin_installations_workspace_id', 'workspace_id'),
        Index('ix_plugin_installations_is_active', 'is_active'),
    )


class ConsentGrant(Base, TimestampMixin):
    """
    ConsentGrant Model - User consent records for privacy compliance.
    Tracks user consent for data usage, integrations, and third-party services.
    Ref: Module 12 - Feature 6 - Governance & Compliance
    """
    __tablename__ = "consent_grants"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for consent grant"
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="User who granted consent"
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Workspace context"
    )

    # Consent Details
    consent_type: Mapped[str] = mapped_column(
        SQLEnum('DATA_USAGE', 'THIRD_PARTY', 'ANALYTICS', 'MARKETING', name='consent_type'),
        nullable=False,
        comment="Type of consent (data_usage, third_party_integration, analytics, marketing)"
    )

    resource_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Specific resource (e.g., 'slack_integration', 'google_analytics')"
    )

    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID of the specific resource if applicable"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable description of what's being consented to"
    )

    # Consent Status
    is_granted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether user granted consent"
    )

    granted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When consent was granted"
    )

    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When consent was revoked"
    )

    # Compliance
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Consent policy version (for tracking changes)"
    )

    # Relationships
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    workspace: Mapped["Workspace"] = relationship(foreign_keys=[workspace_id])

    # Indexes
    __table_args__ = (
        Index('ix_consent_grants_user_id', 'user_id'),
        Index('ix_consent_grants_workspace_id', 'workspace_id'),
        Index('ix_consent_grants_consent_type', 'consent_type'),
        Index('ix_consent_grants_is_granted', 'is_granted'),
    )
