"""
Database models for Module 12: Integration Ecosystem.

Handles API access control, webhooks, OAuth connections, plugins, and governance.

Ref: Module 12 - Integration Ecosystem
"""
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text, JSON, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.db.mixins import TimestampMixin


class ApiToken(Base, TimestampMixin):
    """
    Personal Access Tokens (PAT) for API authentication.
    Users can create multiple tokens with different scopes and expiration dates.
    
    Ref: Module 12 - Feature 2.1 - AC 3 - Authentication via PAT
    """
    __tablename__ = "api_tokens"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    # Token info
    name = Column(String(255), nullable=False)  # User-friendly name
    token_hash = Column(String(255), nullable=False, unique=True)  # Hashed token (stored, not plaintext)
    
    # Token metadata
    is_active = Column(Boolean, nullable=False, default=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)  # NULL = never expires
    
    # Audit
    created_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Foreign keys
    user = relationship("User", foreign_keys=[user_id])
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    created_by = relationship("User", foreign_keys=[created_by_user_id], viewonly=True)
    revoked_by = relationship("User", foreign_keys=[revoked_by_user_id], viewonly=True)
    
    __table_args__ = (
        Index("ix_api_tokens_user_id", "user_id"),
        Index("ix_api_tokens_workspace_id", "workspace_id"),
        Index("ix_api_tokens_is_active", "is_active"),
    )


class ApiScope(Base):
    """
    API permission scopes.
    Defines granular permissions that can be granted to API tokens.
    
    Ref: Module 12 - Feature 2.1 - AC 3 - Scopes
    """
    __tablename__ = "api_scopes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Scope info
    scope_name = Column(String(100), nullable=False, unique=True)  # e.g., "read:tasks", "write:projects"
    description = Column(Text, nullable=True)
    
    # Scope category
    resource_type = Column(String(50), nullable=False)  # project, task, comment, file, workspace
    permission_type = Column(String(20), nullable=False)  # read, write, delete, admin
    
    # Metadata
    is_default = Column(Boolean, nullable=False, default=False)  # Include in new tokens by default
    is_deprecated = Column(Boolean, nullable=False, default=False)
    
    __table_args__ = (
        Index("ix_api_scopes_scope_name", "scope_name"),
        Index("ix_api_scopes_resource_type", "resource_type"),
    )


class ApiTokenScope(Base):
    """
    Junction table: Maps API tokens to scopes.
    Enables fine-grained permission control per token.
    
    Ref: Module 12 - Feature 2.1 - AC 3
    """
    __tablename__ = "api_token_scopes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    api_token_id = Column(String(36), ForeignKey("api_tokens.id", ondelete="CASCADE"), nullable=False)
    api_scope_id = Column(String(36), ForeignKey("api_scopes.id", ondelete="CASCADE"), nullable=False)
    
    # Foreign keys
    api_token = relationship("ApiToken")
    api_scope = relationship("ApiScope")
    
    __table_args__ = (
        UniqueConstraint('api_token_id', 'api_scope_id', name='uq_token_scope'),
        Index("ix_api_token_scopes_api_token_id", "api_token_id"),
    )


class ApiUsageLog(Base, TimestampMixin):
    """
    API usage tracking for rate limiting and audit logging.
    Logs each API request for analytics and compliance.
    
    Ref: Module 12 - Feature 3.1 - Rate Limiting
    """
    __tablename__ = "api_usage_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    api_token_id = Column(String(36), ForeignKey("api_tokens.id", ondelete="SET NULL"), nullable=True)
    
    # Request info
    method = Column(String(20), nullable=False)  # GET, POST, PATCH, DELETE
    endpoint = Column(String(500), nullable=False)  # /api/v1/projects, /api/v1/tasks
    
    # Response info
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=True)  # Response time in milliseconds
    
    # Rate limit tracking
    request_count_in_minute = Column(Integer, nullable=False, default=1)
    
    # Details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    logged_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign keys
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    api_token = relationship("ApiToken", foreign_keys=[api_token_id])
    
    __table_args__ = (
        Index("ix_api_usage_logs_workspace_id", "workspace_id"),
        Index("ix_api_usage_logs_api_token_id", "api_token_id"),
        Index("ix_api_usage_logs_logged_at", "logged_at"),
        Index("ix_api_usage_logs_status_code", "status_code"),
    )


class WebhookEndpoint(Base, TimestampMixin):
    """
    Webhook endpoint configuration per workspace.
    Stores the target URL and subscription preferences.
    
    Ref: Module 12 - Feature 2.2 - Outbound Webhooks
    """
    __tablename__ = "webhook_endpoints"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    # Webhook configuration
    name = Column(String(255), nullable=False)
    payload_url = Column(String(500), nullable=False)
    
    # Security
    secret_key = Column(String(255), nullable=False)  # For HMAC signature verification
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Retry configuration
    max_retries = Column(Integer, nullable=False, default=5)
    retry_backoff_seconds = Column(Integer, nullable=False, default=60)
    timeout_seconds = Column(Integer, nullable=False, default=30)
    
    # Metadata
    created_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    last_delivery_at = Column(DateTime, nullable=True)
    last_delivery_status = Column(String(50), nullable=True)  # success, failed, timeout
    
    # Foreign keys
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    created_by = relationship("User", foreign_keys=[created_by_user_id], viewonly=True)
    
    __table_args__ = (
        Index("ix_webhook_endpoints_workspace_id", "workspace_id"),
        Index("ix_webhook_endpoints_is_active", "is_active"),
    )


class WebhookEvent(Base):
    """
    Event types that webhook endpoints can subscribe to.
    Predefined list of system events.
    
    Ref: Module 12 - Feature 2.2 - AC 1 - Event Triggers
    """
    __tablename__ = "webhook_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    webhook_endpoint_id = Column(String(36), ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), nullable=False)
    
    # Event info
    event_type = Column(String(100), nullable=False)  # task.created, task.status_changed, comment.created
    is_subscribed = Column(Boolean, nullable=False, default=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign keys
    webhook_endpoint = relationship("WebhookEndpoint")
    
    __table_args__ = (
        UniqueConstraint('webhook_endpoint_id', 'event_type', name='uq_endpoint_event'),
        Index("ix_webhook_events_webhook_endpoint_id", "webhook_endpoint_id"),
    )


class WebhookDelivery(Base, TimestampMixin):
    """
    Webhook delivery history for reliability and debugging.
    Logs every webhook attempt with request/response details.
    
    Ref: Module 12 - Feature 2.2 - AC 2 - Delivery Reliability
    """
    __tablename__ = "webhook_deliveries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    webhook_endpoint_id = Column(String(36), ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), nullable=False)
    
    # Event info
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON, nullable=False)  # Full event payload
    
    # Delivery attempt
    attempt_number = Column(Integer, nullable=False, default=1)
    status_code = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, success, failed, timeout
    
    # Request/Response
    request_headers = Column(JSON, nullable=True)
    request_body = Column(JSON, nullable=True)
    response_headers = Column(JSON, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Retry info
    next_retry_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    
    # Timestamps
    delivered_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    webhook_endpoint = relationship("WebhookEndpoint")
    
    __table_args__ = (
        Index("ix_webhook_deliveries_webhook_endpoint_id", "webhook_endpoint_id"),
        Index("ix_webhook_deliveries_status", "status"),
        Index("ix_webhook_deliveries_delivered_at", "delivered_at"),
    )


class OAuthApp(Base, TimestampMixin):
    """
    OAuth applications for third-party connectors.
    Represents the connector (e.g., GitHub connector) itself.
    
    Ref: Module 12 - Feature 2.3 - Native Connectors
    """
    __tablename__ = "oauth_apps"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # App info
    name = Column(String(255), nullable=False, unique=True)  # github, google_calendar, slack
    display_name = Column(String(255), nullable=False)  # GitHub, Google Calendar, Slack
    description = Column(Text, nullable=True)
    
    # OAuth config
    client_id = Column(String(255), nullable=False)
    client_secret = Column(String(255), nullable=False)
    authorize_url = Column(String(500), nullable=False)
    token_url = Column(String(500), nullable=False)
    redirect_uri = Column(String(500), nullable=False)  # PronaFlow callback URL
    
    # Scope permissions
    required_scopes = Column(JSON, nullable=False)  # List of scopes to request
    
    # Status
    is_enabled = Column(Boolean, nullable=False, default=True)
    is_deprecated = Column(Boolean, nullable=False, default=False)
    
    # Metadata
    icon_url = Column(String(500), nullable=True)
    documentation_url = Column(String(500), nullable=True)
    
    __table_args__ = (
        Index("ix_oauth_apps_name", "name"),
    )


class OAuthConnection(Base, TimestampMixin):
    """
    OAuth connections between PronaFlow users and external services.
    Stores access tokens and connection metadata.
    
    Ref: Module 12 - Feature 2.3 - AC 1 - OAuth2 Authorization Flow
    """
    __tablename__ = "oauth_connections"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    oauth_app_id = Column(String(36), ForeignKey("oauth_apps.id", ondelete="CASCADE"), nullable=False)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    # Connection status
    is_active = Column(Boolean, nullable=False, default=True)
    is_sync_enabled = Column(Boolean, nullable=False, default=True)  # For bi-directional sync
    
    # Tokens
    access_token = Column(Text, nullable=False)  # Encrypted
    refresh_token = Column(Text, nullable=True)  # Encrypted
    token_expires_at = Column(DateTime, nullable=True)
    
    # External user info
    external_user_id = Column(String(255), nullable=False)
    external_user_email = Column(String(255), nullable=True)
    external_user_data = Column(JSON, nullable=True)  # Profile info from external service
    
    # Sync metadata
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(50), nullable=True)  # success, failed, partial
    sync_error = Column(Text, nullable=True)
    
    # Foreign keys
    user = relationship("User", foreign_keys=[user_id])
    oauth_app = relationship("OAuthApp", foreign_keys=[oauth_app_id])
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    
    __table_args__ = (
        UniqueConstraint('user_id', 'oauth_app_id', 'workspace_id', name='uq_user_app_workspace'),
        Index("ix_oauth_connections_user_id", "user_id"),
        Index("ix_oauth_connections_oauth_app_id", "oauth_app_id"),
        Index("ix_oauth_connections_workspace_id", "workspace_id"),
    )


class IntegrationBinding(Base, TimestampMixin):
    """
    Data mapping configuration for integrations.
    Maps fields between PronaFlow and external systems.
    
    Ref: Module 12 - Feature 2.3 - Bi-directional Sync
    """
    __tablename__ = "integration_bindings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    oauth_connection_id = Column(String(36), ForeignKey("oauth_connections.id", ondelete="CASCADE"), nullable=False)
    
    # Binding info
    local_resource_type = Column(String(50), nullable=False)  # task, project
    local_resource_id = Column(String(36), nullable=False)
    external_resource_type = Column(String(50), nullable=False)  # event, issue, calendar item
    external_resource_id = Column(String(255), nullable=False)
    
    # Field mapping
    field_mappings = Column(JSON, nullable=False)  # {local_field: external_field, ...}
    
    # Sync direction
    sync_direction = Column(String(20), nullable=False, default="bi")  # uni (one-way), bi (two-way)
    
    # Metadata
    created_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    last_synced_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    oauth_connection = relationship("OAuthConnection")
    created_by = relationship("User", foreign_keys=[created_by_user_id], viewonly=True)
    
    __table_args__ = (
        UniqueConstraint('oauth_connection_id', 'local_resource_type', 'local_resource_id', name='uq_connection_local_resource'),
        Index("ix_integration_bindings_oauth_connection_id", "oauth_connection_id"),
    )


class Plugin(Base, TimestampMixin):
    """
    Plugin definitions in the marketplace.
    Represents a plugin that can be installed into workspaces.
    
    Ref: Module 12 - Feature 2.4 - Plugin Architecture
    """
    __tablename__ = "plugins"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Plugin info
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    version = Column(String(50), nullable=False)
    
    # Plugin metadata
    developer_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    icon_url = Column(String(500), nullable=True)
    documentation_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    
    # Plugin code
    manifest = Column(JSON, nullable=False)  # manifest.json content
    bundle_url = Column(String(500), nullable=False)  # URL to plugin JS bundle
    
    # Permissions
    required_permissions = Column(JSON, nullable=False)  # List of requested permissions
    required_scopes = Column(JSON, nullable=False)  # API scopes needed
    
    # Status
    is_public = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_deprecated = Column(Boolean, nullable=False, default=False)
    
    # Ratings
    rating_avg = Column(Integer, nullable=True)  # 1-5 stars
    install_count = Column(Integer, nullable=False, default=0)
    
    # Foreign keys
    developer = relationship("User", foreign_keys=[developer_id], viewonly=True)
    
    __table_args__ = (
        Index("ix_plugins_name", "name"),
        Index("ix_plugins_is_public", "is_public"),
    )


class PluginInstallation(Base, TimestampMixin):
    """
    Plugin installations per workspace.
    Tracks which plugins are installed in which workspaces.
    
    Ref: Module 12 - Feature 2.4 - Plugin Architecture
    """
    __tablename__ = "plugin_installations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    plugin_id = Column(String(36), ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False)
    
    # Installation status
    is_enabled = Column(Boolean, nullable=False, default=True)
    
    # Configuration
    configuration = Column(JSON, nullable=True)  # Plugin-specific settings
    
    # Audit
    installed_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    uninstalled_at = Column(DateTime, nullable=True)
    
    # Metadata
    last_updated_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    plugin = relationship("Plugin", foreign_keys=[plugin_id])
    installed_by = relationship("User", foreign_keys=[installed_by_user_id], viewonly=True)
    
    __table_args__ = (
        UniqueConstraint('workspace_id', 'plugin_id', name='uq_workspace_plugin'),
        Index("ix_plugin_installations_workspace_id", "workspace_id"),
        Index("ix_plugin_installations_is_enabled", "is_enabled"),
    )


class ConsentGrant(Base, TimestampMixin):
    """
    User consent records for data sharing and privacy compliance.
    Tracks explicit user consent for third-party data access.
    
    Ref: Module 12 - Feature 3.2 - Data Security & Consent
    """
    __tablename__ = "consent_grants"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Consent type
    consent_type = Column(String(50), nullable=False)  # oauth_connection, plugin_installation, api_token
    
    # Entity reference
    entity_type = Column(String(50), nullable=False)  # oauth_app, plugin, integration
    entity_id = Column(String(36), nullable=False)
    
    # Consent details
    requested_permissions = Column(JSON, nullable=False)  # Permissions requested
    granted_permissions = Column(JSON, nullable=False)  # Permissions actually granted
    
    # Revocation
    is_active = Column(Boolean, nullable=False, default=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Audit
    granted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
    
    # Foreign keys
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        UniqueConstraint('user_id', 'consent_type', 'entity_type', 'entity_id', name='uq_user_consent'),
        Index("ix_consent_grants_user_id", "user_id"),
        Index("ix_consent_grants_consent_type", "consent_type"),
    )
