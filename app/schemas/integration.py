"""
Pydantic schemas for Module 12: Integration Ecosystem.

Defines request/response models for API tokens, webhooks, OAuth, plugins, and governance.

Ref: Module 12 - Integration Ecosystem
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


# ============ API Token Schemas ============

class ApiTokenBase(BaseModel):
    """Base schema for API token"""
    name: str = Field(..., description="User-friendly name for the token")
    expires_at: Optional[datetime] = Field(None, description="Token expiration date (null = never expires)")


class ApiTokenCreate(ApiTokenBase):
    """Schema for creating API token"""
    scopes: List[str] = Field(default_factory=list, description="List of scope names (e.g., ['read:tasks', 'write:projects'])")


class ApiTokenUpdate(BaseModel):
    """Schema for updating API token"""
    name: Optional[str] = None
    is_active: Optional[bool] = None


class ApiTokenRead(ApiTokenBase):
    """Schema for reading API token"""
    id: str
    user_id: str
    workspace_id: str
    token_hash: str
    is_active: bool
    last_used_at: Optional[datetime]
    revoked_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApiTokenCreateResponse(BaseModel):
    """Response with actual token (only shown once on creation)"""
    id: str
    name: str
    token: str = Field(..., description="ACTUAL TOKEN (shown only once, save securely)")
    scopes: List[str]
    expires_at: Optional[datetime]
    created_at: datetime


class ApiTokenListResponse(BaseModel):
    """Paginated response for API tokens"""
    items: List[ApiTokenRead]
    total: int
    page: int
    page_size: int


# ============ API Scope Schemas ============

class ApiScopeBase(BaseModel):
    """Base schema for API scope"""
    scope_name: str = Field(..., description="Scope identifier (e.g., 'read:tasks')")
    description: Optional[str] = None
    resource_type: str = Field(..., description="Resource type (project, task, comment, file, workspace)")
    permission_type: str = Field(..., description="Permission type (read, write, delete, admin)")


class ApiScopeRead(ApiScopeBase):
    """Schema for reading API scope"""
    id: str
    is_default: bool
    is_deprecated: bool
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ApiScopeListResponse(BaseModel):
    """Response for API scopes list"""
    items: List[ApiScopeRead]
    total: int


# ============ API Usage Log Schemas ============

class ApiUsageLogRead(BaseModel):
    """Schema for reading API usage log"""
    id: str
    workspace_id: str
    api_token_id: Optional[str]
    method: str
    endpoint: str
    status_code: int
    response_time_ms: Optional[int]
    ip_address: Optional[str]
    logged_at: datetime
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class ApiUsageLogListResponse(BaseModel):
    """Paginated response for API usage logs"""
    items: List[ApiUsageLogRead]
    total: int
    page: int
    page_size: int


# ============ Webhook Endpoint Schemas ============

class WebhookEndpointBase(BaseModel):
    """Base schema for webhook endpoint"""
    name: str = Field(..., description="Friendly name for the webhook")
    payload_url: HttpUrl = Field(..., description="Target URL to send webhooks")
    max_retries: int = Field(default=5, description="Max retry attempts")
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")


class WebhookEndpointCreate(WebhookEndpointBase):
    """Schema for creating webhook endpoint"""
    event_types: List[str] = Field(default_factory=list, description="Events to subscribe to")


class WebhookEndpointUpdate(BaseModel):
    """Schema for updating webhook endpoint"""
    name: Optional[str] = None
    payload_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    max_retries: Optional[int] = None
    timeout_seconds: Optional[int] = None


class WebhookEndpointRead(WebhookEndpointBase):
    """Schema for reading webhook endpoint"""
    id: str
    workspace_id: str
    is_active: bool
    last_delivery_at: Optional[datetime]
    last_delivery_status: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WebhookEndpointListResponse(BaseModel):
    """Paginated response for webhook endpoints"""
    items: List[WebhookEndpointRead]
    total: int
    page: int
    page_size: int


# ============ Webhook Event Schemas ============

class WebhookEventRead(BaseModel):
    """Schema for reading webhook event subscription"""
    id: str
    webhook_endpoint_id: str
    event_type: str
    is_subscribed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Webhook Delivery Schemas ============

class WebhookDeliveryRead(BaseModel):
    """Schema for reading webhook delivery history"""
    id: str
    webhook_endpoint_id: str
    event_type: str
    attempt_number: int
    status: str
    status_code: Optional[int]
    response_time_ms: Optional[int]
    last_error: Optional[str]
    delivered_at: Optional[datetime]
    next_retry_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebhookDeliveryListResponse(BaseModel):
    """Paginated response for webhook deliveries"""
    items: List[WebhookDeliveryRead]
    total: int
    page: int
    page_size: int


# ============ OAuth App Schemas ============

class OAuthAppRead(BaseModel):
    """Schema for reading OAuth app"""
    id: str
    name: str
    display_name: str
    description: Optional[str]
    version: str
    icon_url: Optional[str]
    documentation_url: Optional[str]
    is_enabled: bool
    is_verified: bool
    is_deprecated: bool
    required_scopes: List[str]
    rating_avg: Optional[int]
    install_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class OAuthAppListResponse(BaseModel):
    """Response for OAuth apps list"""
    items: List[OAuthAppRead]
    total: int
    page: int
    page_size: int


# ============ OAuth Connection Schemas ============

class OAuthConnectionBase(BaseModel):
    """Base schema for OAuth connection"""
    is_sync_enabled: bool = Field(default=True, description="Enable bi-directional sync")


class OAuthConnectionCreate(OAuthConnectionBase):
    """Schema for creating OAuth connection"""
    oauth_app_id: str = Field(..., description="OAuth app to connect")
    authorization_code: str = Field(..., description="Code from OAuth provider")


class OAuthConnectionUpdate(BaseModel):
    """Schema for updating OAuth connection"""
    is_active: Optional[bool] = None
    is_sync_enabled: Optional[bool] = None


class OAuthConnectionRead(OAuthConnectionBase):
    """Schema for reading OAuth connection"""
    id: str
    user_id: str
    oauth_app_id: str
    workspace_id: str
    is_active: bool
    last_sync_at: Optional[datetime]
    last_sync_status: Optional[str]
    external_user_email: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OAuthConnectionListResponse(BaseModel):
    """Paginated response for OAuth connections"""
    items: List[OAuthConnectionRead]
    total: int
    page: int
    page_size: int


# ============ Integration Binding Schemas ============

class IntegrationBindingBase(BaseModel):
    """Base schema for integration binding"""
    local_resource_type: str = Field(..., description="PronaFlow resource type (task, project)")
    local_resource_id: str = Field(..., description="PronaFlow resource ID")
    external_resource_type: str = Field(..., description="External resource type (event, issue, calendar item)")
    external_resource_id: str = Field(..., description="External resource ID")
    field_mappings: Dict[str, str] = Field(..., description="Field mapping {local_field: external_field}")
    sync_direction: str = Field(default="bi", description="uni or bi")


class IntegrationBindingCreate(IntegrationBindingBase):
    """Schema for creating integration binding"""
    oauth_connection_id: str = Field(..., description="OAuth connection to use")


class IntegrationBindingRead(IntegrationBindingBase):
    """Schema for reading integration binding"""
    id: str
    oauth_connection_id: str
    last_synced_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IntegrationBindingListResponse(BaseModel):
    """Paginated response for integration bindings"""
    items: List[IntegrationBindingRead]
    total: int
    page: int
    page_size: int


# ============ Plugin Schemas ============

class PluginBase(BaseModel):
    """Base schema for plugin"""
    name: str = Field(..., description="Unique plugin name")
    display_name: str = Field(..., description="User-friendly name")
    description: str = Field(..., description="Plugin description")
    version: str = Field(..., description="Semantic version (e.g., 1.0.0)")


class PluginCreate(PluginBase):
    """Schema for creating plugin"""
    manifest: Dict[str, Any] = Field(..., description="manifest.json content")
    bundle_url: str = Field(..., description="URL to plugin JS bundle")
    required_permissions: List[str] = Field(default_factory=list, description="Required permissions")
    required_scopes: List[str] = Field(default_factory=list, description="Required API scopes")
    icon_url: Optional[str] = None
    documentation_url: Optional[str] = None
    github_url: Optional[str] = None


class PluginUpdate(BaseModel):
    """Schema for updating plugin"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    is_public: Optional[bool] = None
    is_deprecated: Optional[bool] = None


class PluginRead(PluginBase):
    """Schema for reading plugin"""
    id: str
    is_public: bool
    is_verified: bool
    is_deprecated: bool
    icon_url: Optional[str]
    documentation_url: Optional[str]
    rating_avg: Optional[int]
    install_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PluginListResponse(BaseModel):
    """Response for plugins list"""
    items: List[PluginRead]
    total: int
    page: int
    page_size: int


# ============ Plugin Installation Schemas ============

class PluginInstallationBase(BaseModel):
    """Base schema for plugin installation"""
    plugin_id: str = Field(..., description="Plugin to install")


class PluginInstallationCreate(PluginInstallationBase):
    """Schema for creating plugin installation"""
    configuration: Optional[Dict[str, Any]] = None


class PluginInstallationUpdate(BaseModel):
    """Schema for updating plugin installation"""
    is_enabled: Optional[bool] = None
    configuration: Optional[Dict[str, Any]] = None


class PluginInstallationRead(PluginInstallationBase):
    """Schema for reading plugin installation"""
    id: str
    workspace_id: str
    is_enabled: bool
    configuration: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PluginInstallationListResponse(BaseModel):
    """Paginated response for plugin installations"""
    items: List[PluginInstallationRead]
    total: int
    page: int
    page_size: int


# ============ Consent Grant Schemas ============

class ConsentGrantBase(BaseModel):
    """Base schema for consent grant"""
    consent_type: str = Field(..., description="oauth_connection, plugin_installation, api_token")
    entity_type: str = Field(..., description="oauth_app, plugin, integration")
    entity_id: str = Field(..., description="ID of the entity")
    requested_permissions: List[str] = Field(..., description="Requested permissions")
    granted_permissions: List[str] = Field(..., description="Actually granted permissions")


class ConsentGrantCreate(ConsentGrantBase):
    """Schema for creating consent grant"""
    pass


class ConsentGrantRead(ConsentGrantBase):
    """Schema for reading consent grant"""
    id: str
    user_id: str
    is_active: bool
    revoked_at: Optional[datetime]
    granted_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConsentGrantListResponse(BaseModel):
    """Paginated response for consent grants"""
    items: List[ConsentGrantRead]
    total: int
    page: int
    page_size: int


# ============ Composite Response Schemas ============

class IntegrationStatusResponse(BaseModel):
    """Integration status overview"""
    api_tokens_count: int
    active_webhooks_count: int
    oauth_connections_count: int
    installed_plugins_count: int
    api_requests_today: int
    rate_limit_remaining: int
    rate_limit_reset_at: datetime


class HealthCheckResponse(BaseModel):
    """Health check for integrations"""
    api_available: bool
    webhooks_processing: bool
    oauth_status: str  # healthy, degraded, down
    plugins_loaded: int
    last_check_at: datetime
