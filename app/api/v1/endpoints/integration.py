"""
API endpoints for Module 12: Integration Ecosystem.

RESTful endpoints for API tokens, webhooks, OAuth, plugins, and governance.

Ref: Module 12 - Integration Ecosystem
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
from typing import Optional

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.users import User
from app.models.integration import ApiToken, WebhookEndpoint, OAuthConnection, IntegrationBinding, Plugin, PluginInstallation, ConsentGrant
from app.models.integrations import ApiUsageLog
from app.schemas.integration import (
    ApiTokenCreate, ApiTokenUpdate, ApiTokenRead, ApiTokenCreateResponse, ApiTokenListResponse,
    ApiScopeListResponse,
    ApiUsageLogListResponse,
    WebhookEndpointCreate, WebhookEndpointUpdate, WebhookEndpointRead, WebhookEndpointListResponse,
    OAuthAppListResponse,
    OAuthConnectionCreate, OAuthConnectionUpdate, OAuthConnectionRead, OAuthConnectionListResponse,
    IntegrationBindingCreate, IntegrationBindingRead, IntegrationBindingListResponse,
    PluginCreate, PluginUpdate, PluginRead, PluginListResponse,
    PluginInstallationCreate, PluginInstallationUpdate, PluginInstallationRead, PluginInstallationListResponse,
    ConsentGrantCreate, ConsentGrantRead, ConsentGrantListResponse,
    IntegrationStatusResponse, HealthCheckResponse
)
from app.services.integration import (
    ApiTokenService, WebhookService, OAuthService, PluginService, ConsentService
)


router = APIRouter(prefix="/api/v1/integration", tags=["integration"])


# ============ API Token Endpoints ============

@router.post("/tokens", response_model=ApiTokenCreateResponse)
def create_api_token(
    workspace_id: str = Query(..., description="Workspace ID"),
    token_data: ApiTokenCreate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API token for the current user.
    
    Ref: Module 12 - Feature 2.1 - AC 3
    """
    token_service = ApiTokenService(db)
    return token_service.create_api_token(
        current_user.id,
        workspace_id,
        token_data
    )


@router.get("/tokens", response_model=ApiTokenListResponse)
def list_api_tokens(
    workspace_id: str = Query(..., description="Workspace ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List API tokens for the current user.
    
    Ref: Module 12 - Feature 2.1
    """
    query = db.query(ApiToken).filter(
        and_(ApiToken.user_id == current_user.id, ApiToken.workspace_id == workspace_id)
    ).order_by(desc(ApiToken.created_at))
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return ApiTokenListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.patch("/tokens/{token_id}")
def update_api_token(
    token_id: str,
    token_update: ApiTokenUpdate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update API token settings.
    """
    token = db.query(ApiToken).filter(
        and_(ApiToken.id == token_id, ApiToken.user_id == current_user.id)
    ).first()
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    if token_update.name:
        token.name = token_update.name
    if token_update.is_active is not None:
        token.is_active = token_update.is_active
    
    db.commit()
    return token


@router.delete("/tokens/{token_id}")
def revoke_api_token(
    token_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke an API token.
    
    Ref: Module 12 - Feature 2.1 - AC 3 - Revocation
    """
    token_service = ApiTokenService(db)
    success = token_service.revoke_token(token_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Token not found")
    
    return {"message": "Token revoked successfully"}


# ============ API Scope Endpoints ============

@router.get("/scopes", response_model=ApiScopeListResponse)
def list_api_scopes(
    db: Session = Depends(get_db)
):
    """
    List available API scopes.
    
    Ref: Module 12 - Feature 2.1 - AC 3 - Scopes
    """
    scopes = db.query(ApiScope).filter(ApiScope.is_deprecated == False).all()
    
    return ApiScopeListResponse(
        items=scopes,
        total=len(scopes)
    )


# ============ API Usage Log Endpoints ============

@router.get("/usage-logs", response_model=ApiUsageLogListResponse)
def get_api_usage_logs(
    workspace_id: str = Query(..., description="Workspace ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get API usage logs for rate limiting analysis.
    
    Ref: Module 12 - Feature 3.1 - Rate Limiting
    """
    query = db.query(ApiUsageLog).filter(
        ApiUsageLog.workspace_id == workspace_id
    ).order_by(desc(ApiUsageLog.logged_at))
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return ApiUsageLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


# ============ Webhook Endpoint Endpoints ============

@router.post("/webhooks", response_model=WebhookEndpointRead)
def create_webhook_endpoint(
    workspace_id: str = Query(..., description="Workspace ID"),
    webhook_data: WebhookEndpointCreate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create webhook endpoint.
    
    Ref: Module 12 - Feature 2.2 - AC 1
    """
    webhook_service = WebhookService(db)
    return webhook_service.create_webhook_endpoint(
        workspace_id,
        current_user.id,
        webhook_data
    )


@router.get("/webhooks", response_model=WebhookEndpointListResponse)
def list_webhook_endpoints(
    workspace_id: str = Query(..., description="Workspace ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List webhook endpoints for workspace.
    
    Ref: Module 12 - Feature 2.2
    """
    query = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.workspace_id == workspace_id
    ).order_by(desc(WebhookEndpoint.created_at))
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return WebhookEndpointListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.patch("/webhooks/{endpoint_id}", response_model=WebhookEndpointRead)
def update_webhook_endpoint(
    endpoint_id: str,
    endpoint_update: WebhookEndpointUpdate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update webhook endpoint configuration.
    """
    endpoint = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.id == endpoint_id
    ).first()
    
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    if endpoint_update.name:
        endpoint.name = endpoint_update.name
    if endpoint_update.payload_url:
        endpoint.payload_url = str(endpoint_update.payload_url)
    if endpoint_update.is_active is not None:
        endpoint.is_active = endpoint_update.is_active
    if endpoint_update.max_retries:
        endpoint.max_retries = endpoint_update.max_retries
    if endpoint_update.timeout_seconds:
        endpoint.timeout_seconds = endpoint_update.timeout_seconds
    
    db.commit()
    return endpoint


# ============ OAuth App Endpoints ============

@router.get("/oauth/apps", response_model=OAuthAppListResponse)
def list_oauth_apps(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List available OAuth apps (native connectors).
    
    Ref: Module 12 - Feature 2.3
    """
    query = db.query(OAuthApp).filter(
        and_(OAuthApp.is_enabled == True, OAuthApp.is_deprecated == False)
    ).order_by(OAuthApp.display_name)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return OAuthAppListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


# ============ OAuth Connection Endpoints ============

@router.post("/oauth/connections", response_model=OAuthConnectionRead)
def create_oauth_connection(
    workspace_id: str = Query(..., description="Workspace ID"),
    connection_data: OAuthConnectionCreate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create OAuth connection (initiate OAuth flow).
    
    Ref: Module 12 - Feature 2.3 - AC 1
    """
    oauth_service = OAuthService(db)
    return oauth_service.create_oauth_connection(
        current_user.id,
        workspace_id,
        connection_data
    )


@router.get("/oauth/connections", response_model=OAuthConnectionListResponse)
def list_oauth_connections(
    workspace_id: str = Query(..., description="Workspace ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List OAuth connections for current user.
    
    Ref: Module 12 - Feature 2.3
    """
    query = db.query(OAuthConnection).filter(
        and_(OAuthConnection.user_id == current_user.id, OAuthConnection.workspace_id == workspace_id)
    ).order_by(desc(OAuthConnection.created_at))
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return OAuthConnectionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.delete("/oauth/connections/{connection_id}")
def revoke_oauth_connection(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke OAuth connection.
    
    Ref: Module 12 - Feature 3.2 - Revocation
    """
    connection = db.query(OAuthConnection).filter(
        and_(OAuthConnection.id == connection_id, OAuthConnection.user_id == current_user.id)
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    connection.is_active = False
    db.commit()
    
    return {"message": "Connection revoked successfully"}


# ============ Integration Binding Endpoints ============

@router.post("/bindings", response_model=IntegrationBindingRead)
def create_integration_binding(
    binding_data: IntegrationBindingCreate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create integration binding for bi-directional sync.
    
    Ref: Module 12 - Feature 2.3 - AC 2
    """
    oauth_service = OAuthService(db)
    return oauth_service.create_integration_binding(
        binding_data.oauth_connection_id,
        binding_data
    )


@router.get("/bindings", response_model=IntegrationBindingListResponse)
def list_integration_bindings(
    workspace_id: str = Query(..., description="Workspace ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List integration bindings.
    """
    query = db.query(IntegrationBinding).join(
        OAuthConnection,
        IntegrationBinding.oauth_connection_id == OAuthConnection.id
    ).filter(
        and_(OAuthConnection.workspace_id == workspace_id, OAuthConnection.user_id == current_user.id)
    ).order_by(desc(IntegrationBinding.created_at))
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return IntegrationBindingListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


# ============ Plugin Endpoints ============

@router.get("/plugins", response_model=PluginListResponse)
def list_plugins(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List available plugins in marketplace.
    
    Ref: Module 12 - Feature 2.4
    """
    query = db.query(Plugin).filter(
        and_(Plugin.is_public == True, Plugin.is_deprecated == False)
    ).order_by(desc(Plugin.install_count))
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PluginListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/plugins/{plugin_id}", response_model=PluginRead)
def get_plugin_detail(
    plugin_id: str,
    db: Session = Depends(get_db)
):
    """
    Get plugin details.
    """
    plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
    
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    return plugin


# ============ Plugin Installation Endpoints ============

@router.post("/plugins/install", response_model=PluginInstallationRead)
def install_plugin(
    workspace_id: str = Query(..., description="Workspace ID"),
    installation_data: PluginInstallationCreate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Install plugin into workspace.
    
    Ref: Module 12 - Feature 2.4 - Plugin Architecture
    """
    plugin_service = PluginService(db)
    return plugin_service.install_plugin(
        workspace_id,
        installation_data.plugin_id,
        current_user.id,
        installation_data.configuration
    )


@router.get("/plugins/installed", response_model=PluginInstallationListResponse)
def list_installed_plugins(
    workspace_id: str = Query(..., description="Workspace ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List plugins installed in workspace.
    """
    query = db.query(PluginInstallation).filter(
        PluginInstallation.workspace_id == workspace_id
    ).order_by(desc(PluginInstallation.created_at))
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PluginInstallationListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.patch("/plugins/install/{installation_id}", response_model=PluginInstallationRead)
def update_plugin_installation(
    installation_id: str,
    update_data: PluginInstallationUpdate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update plugin installation settings.
    """
    installation = db.query(PluginInstallation).filter(
        PluginInstallation.id == installation_id
    ).first()
    
    if not installation:
        raise HTTPException(status_code=404, detail="Installation not found")
    
    if update_data.is_enabled is not None:
        installation.is_enabled = update_data.is_enabled
    if update_data.configuration:
        installation.configuration = update_data.configuration
    
    installation.last_updated_at = datetime.utcnow()
    db.commit()
    
    return installation


@router.delete("/plugins/install/{installation_id}")
def uninstall_plugin(
    installation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uninstall plugin from workspace.
    """
    plugin_service = PluginService(db)
    success = plugin_service.uninstall_plugin(installation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Installation not found")
    
    return {"message": "Plugin uninstalled successfully"}


# ============ Consent Grant Endpoints ============

@router.get("/consents", response_model=ConsentGrantListResponse)
def list_consents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's consent grants.
    
    Ref: Module 12 - Feature 3.2 - Data Security & Consent
    """
    query = db.query(ConsentGrant).filter(
        ConsentGrant.user_id == current_user.id
    ).order_by(desc(ConsentGrant.granted_at))
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return ConsentGrantListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.delete("/consents/{consent_id}")
def revoke_consent(
    consent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke user consent.
    
    Ref: Module 12 - Feature 3.2 - Revocation
    """
    consent = db.query(ConsentGrant).filter(
        and_(ConsentGrant.id == consent_id, ConsentGrant.user_id == current_user.id)
    ).first()
    
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    
    consent_service = ConsentService(db)
    consent_service.revoke_consent(consent_id)
    
    return {"message": "Consent revoked successfully"}


# ============ Status & Health Check Endpoints ============

@router.get("/status", response_model=IntegrationStatusResponse)
def get_integration_status(
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get integration ecosystem status.
    """
    api_tokens_count = db.query(ApiToken).filter(
        and_(ApiToken.workspace_id == workspace_id, ApiToken.is_active == True)
    ).count()
    
    active_webhooks = db.query(WebhookEndpoint).filter(
        and_(WebhookEndpoint.workspace_id == workspace_id, WebhookEndpoint.is_active == True)
    ).count()
    
    oauth_connections = db.query(OAuthConnection).filter(
        and_(OAuthConnection.workspace_id == workspace_id, OAuthConnection.is_active == True)
    ).count()
    
    plugins_installed = db.query(PluginInstallation).filter(
        and_(PluginInstallation.workspace_id == workspace_id, PluginInstallation.is_enabled == True)
    ).count()
    
    return IntegrationStatusResponse(
        api_tokens_count=api_tokens_count,
        active_webhooks_count=active_webhooks,
        oauth_connections_count=oauth_connections,
        installed_plugins_count=plugins_installed,
        api_requests_today=0,  # To be calculated from logs
        rate_limit_remaining=0,
        rate_limit_reset_at=datetime.utcnow()
    )


@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Health check for integration ecosystem.
    """
    return HealthCheckResponse(
        api_available=True,
        webhooks_processing=True,
        oauth_status="healthy",
        plugins_loaded=db.query(Plugin).filter(Plugin.is_public == True).count(),
        last_check_at=datetime.utcnow()
    )
