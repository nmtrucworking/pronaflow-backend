"""
Service layer for Module 12: Integration Ecosystem.

Implements business logic for API tokens, webhooks, OAuth, plugins, and governance.

Ref: Module 12 - Integration Ecosystem
"""
import hashlib
import secrets
import json
import hmac
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.integration import (
    ApiToken, ApiScope, ApiTokenScope,
    WebhookEndpoint, WebhookEvent, WebhookDelivery,
    OAuthApp, OAuthConnection, IntegrationBinding,
    Plugin, PluginInstallation, ConsentGrant
)
from app.models.integrations import ApiUsageLog
from app.schemas.integration import (
    ApiTokenCreate, ApiTokenUpdate, ApiTokenCreateResponse,
    WebhookEndpointCreate, WebhookEndpointUpdate,
    OAuthConnectionCreate, OAuthConnectionUpdate,
    IntegrationBindingCreate,
    PluginCreate, PluginInstallationCreate, PluginInstallationUpdate,
    ConsentGrantCreate
)


class ApiTokenService:
    """
    Service for API token management.
    Handles token creation, validation, revocation, and usage tracking.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_api_token(
        self,
        user_id: str,
        workspace_id: str,
        token_data: ApiTokenCreate
    ) -> ApiTokenCreateResponse:
        """
        Create a new API token.
        
        Ref: Module 12 - Feature 2.1 - AC 3
        """
        # Generate token
        token = self._generate_token()
        token_hash = self._hash_token(token)
        
        # Create token record
        expires_at = token_data.expires_at or (datetime.utcnow() + timedelta(days=365))
        
        api_token = ApiToken(
            id=str(uuid4()),
            user_id=user_id,
            workspace_id=workspace_id,
            name=token_data.name,
            token_hash=token_hash,
            is_active=True,
            expires_at=expires_at,
            created_by_user_id=user_id
        )
        
        self.db.add(api_token)
        self.db.flush()
        
        # Add scopes
        if token_data.scopes:
            for scope_name in token_data.scopes:
                scope = self.db.query(ApiScope).filter(
                    ApiScope.scope_name == scope_name
                ).first()
                
                if scope:
                    token_scope = ApiTokenScope(
                        id=str(uuid4()),
                        api_token_id=api_token.id,
                        api_scope_id=scope.id
                    )
                    self.db.add(token_scope)
        
        self.db.commit()
        
        return ApiTokenCreateResponse(
            id=api_token.id,
            name=api_token.name,
            token=token,  # Only shown once
            scopes=token_data.scopes,
            expires_at=api_token.expires_at,
            created_at=api_token.created_at
        )
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate API token and return token info with scopes.
        
        Ref: Module 12 - Feature 2.1 - AC 3
        """
        token_hash = self._hash_token(token)
        
        api_token = self.db.query(ApiToken).filter(
            and_(
                ApiToken.token_hash == token_hash,
                ApiToken.is_active == True,
                or_(
                    ApiToken.expires_at.is_(None),
                    ApiToken.expires_at > datetime.utcnow()
                )
            )
        ).first()
        
        if not api_token:
            return None
        
        # Get scopes
        scopes = self.db.query(ApiScope).join(
            ApiTokenScope,
            ApiTokenScope.api_scope_id == ApiScope.id
        ).filter(
            ApiTokenScope.api_token_id == api_token.id
        ).all()
        
        return {
            "user_id": api_token.user_id,
            "workspace_id": api_token.workspace_id,
            "token_id": api_token.id,
            "scopes": [s.scope_name for s in scopes]
        }
    
    def revoke_token(self, token_id: str, user_id: str) -> bool:
        """
        Revoke an API token.
        
        Ref: Module 12 - Feature 2.1 - AC 3
        """
        token = self.db.query(ApiToken).filter(
            and_(
                ApiToken.id == token_id,
                ApiToken.user_id == user_id
            )
        ).first()
        
        if not token:
            return False
        
        token.is_active = False
        token.revoked_at = datetime.utcnow()
        token.revoked_by_user_id = user_id
        
        self.db.commit()
        return True
    
    def log_usage(
        self,
        workspace_id: str,
        token_id: Optional[str],
        method: str,
        endpoint: str,
        status_code: int,
        response_time_ms: Optional[int],
        ip_address: Optional[str],
        error_message: Optional[str] = None
    ):
        """
        Log API usage for rate limiting and analytics.
        
        Ref: Module 12 - Feature 3.1 - Rate Limiting
        """
        usage_log = ApiUsageLog(
            id=str(uuid4()),
            workspace_id=workspace_id,
            api_token_id=token_id,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            response_time_ms=response_time_ms,
            ip_address=ip_address,
            error_message=error_message,
            logged_at=datetime.utcnow()
        )
        
        self.db.add(usage_log)
        self.db.commit()
    
    def check_rate_limit(
        self,
        workspace_id: str,
        token_id: str,
        limit: int = 1000
    ) -> tuple[bool, int]:
        """
        Check if token has exceeded rate limit.
        
        Ref: Module 12 - Feature 3.1
        """
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        
        count = self.db.query(ApiUsageLog).filter(
            and_(
                ApiUsageLog.api_token_id == token_id,
                ApiUsageLog.logged_at >= one_minute_ago
            )
        ).count()
        
        remaining = max(0, limit - count)
        return (count < limit, remaining)
    
    @staticmethod
    def _generate_token() -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()


class WebhookService:
    """
    Service for webhook management.
    Handles webhook endpoint configuration, event subscriptions, and delivery.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_webhook_endpoint(
        self,
        workspace_id: str,
        user_id: str,
        endpoint_data: WebhookEndpointCreate
    ):
        """
        Create webhook endpoint.
        
        Ref: Module 12 - Feature 2.2 - AC 1
        """
        secret_key = secrets.token_urlsafe(32)
        
        webhook = WebhookEndpoint(
            id=str(uuid4()),
            workspace_id=workspace_id,
            name=endpoint_data.name,
            payload_url=str(endpoint_data.payload_url),
            secret_key=secret_key,
            is_active=True,
            max_retries=endpoint_data.max_retries,
            timeout_seconds=endpoint_data.timeout_seconds,
            created_by_user_id=user_id
        )
        
        self.db.add(webhook)
        self.db.flush()
        
        # Subscribe to events
        if hasattr(endpoint_data, 'event_types') and endpoint_data.event_types:
            for event_type in endpoint_data.event_types:
                event = WebhookEvent(
                    id=str(uuid4()),
                    webhook_endpoint_id=webhook.id,
                    event_type=event_type,
                    is_subscribed=True
                )
                self.db.add(event)
        
        self.db.commit()
        return webhook
    
    def log_webhook_delivery(
        self,
        webhook_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        status: str = "pending",
        status_code: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        error: Optional[str] = None
    ) -> str:
        """
        Log webhook delivery attempt.
        
        Ref: Module 12 - Feature 2.2 - AC 2
        """
        delivery = WebhookDelivery(
            id=str(uuid4()),
            webhook_endpoint_id=webhook_id,
            event_type=event_type,
            event_data=event_data,
            attempt_number=1,
            status=status,
            status_code=status_code,
            response_time_ms=response_time_ms,
            last_error=error
        )
        
        self.db.add(delivery)
        self.db.commit()
        return delivery.id
    
    def schedule_retry(self, delivery_id: str, retry_after_seconds: int):
        """
        Schedule webhook retry.
        
        Ref: Module 12 - Feature 2.2 - AC 2 - Retry Mechanism
        """
        delivery = self.db.query(WebhookDelivery).filter(
            WebhookDelivery.id == delivery_id
        ).first()
        
        if delivery and delivery.attempt_number < 5:
            delivery.attempt_number += 1
            delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=retry_after_seconds)
            self.db.commit()
    
    def generate_hmac_signature(self, webhook_secret: str, payload: Dict[str, Any]) -> str:
        """
        Generate HMAC signature for webhook payload.
        
        Ref: Module 12 - Feature 2.2 - Security
        """
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            webhook_secret.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"


class OAuthService:
    """
    Service for OAuth connections and native connectors.
    Handles OAuth flow, token storage, and bi-directional sync.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_oauth_connection(
        self,
        user_id: str,
        workspace_id: str,
        connection_data: OAuthConnectionCreate
    ):
        """
        Create OAuth connection.
        
        Ref: Module 12 - Feature 2.3 - AC 1
        """
        connection = OAuthConnection(
            id=str(uuid4()),
            user_id=user_id,
            oauth_app_id=connection_data.oauth_app_id,
            workspace_id=workspace_id,
            is_active=True,
            is_sync_enabled=connection_data.is_sync_enabled,
            access_token="",  # Will be set after OAuth callback
            external_user_id=""
        )
        
        self.db.add(connection)
        self.db.commit()
        return connection
    
    def update_access_token(
        self,
        connection_id: str,
        access_token: str,
        refresh_token: Optional[str],
        external_user_id: str,
        external_user_email: Optional[str],
        token_expires_in: Optional[int] = None
    ):
        """
        Update OAuth access token after successful authentication.
        
        Ref: Module 12 - Feature 2.3 - AC 1
        """
        connection = self.db.query(OAuthConnection).filter(
            OAuthConnection.id == connection_id
        ).first()
        
        if connection:
            connection.access_token = access_token
            connection.refresh_token = refresh_token
            connection.external_user_id = external_user_id
            connection.external_user_email = external_user_email
            
            if token_expires_in:
                connection.token_expires_at = datetime.utcnow() + timedelta(seconds=token_expires_in)
            
            connection.is_active = True
            self.db.commit()
        
        return connection
    
    def create_integration_binding(
        self,
        connection_id: str,
        binding_data: IntegrationBindingCreate
    ):
        """
        Create data mapping for bi-directional sync.
        
        Ref: Module 12 - Feature 2.3 - AC 2
        """
        binding = IntegrationBinding(
            id=str(uuid4()),
            oauth_connection_id=connection_id,
            local_resource_type=binding_data.local_resource_type,
            local_resource_id=binding_data.local_resource_id,
            external_resource_type=binding_data.external_resource_type,
            external_resource_id=binding_data.external_resource_id,
            field_mappings=binding_data.field_mappings,
            sync_direction=binding_data.sync_direction
        )
        
        self.db.add(binding)
        self.db.commit()
        return binding


class PluginService:
    """
    Service for plugin management.
    Handles plugin marketplace and workspace installations.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_plugin(self, plugin_data: PluginCreate):
        """
        Create new plugin.
        
        Ref: Module 12 - Feature 2.4 - AC 1
        """
        plugin = Plugin(
            id=str(uuid4()),
            name=plugin_data.name,
            display_name=plugin_data.display_name,
            description=plugin_data.description,
            version=plugin_data.version,
            manifest=plugin_data.manifest,
            bundle_url=plugin_data.bundle_url,
            required_permissions=plugin_data.required_permissions,
            required_scopes=plugin_data.required_scopes,
            icon_url=plugin_data.icon_url,
            documentation_url=plugin_data.documentation_url,
            github_url=plugin_data.github_url,
            is_public=False
        )
        
        self.db.add(plugin)
        self.db.commit()
        return plugin
    
    def install_plugin(
        self,
        workspace_id: str,
        plugin_id: str,
        user_id: str,
        configuration: Optional[Dict[str, Any]] = None
    ):
        """
        Install plugin into workspace.
        
        Ref: Module 12 - Feature 2.4 - Plugin Architecture
        """
        installation = PluginInstallation(
            id=str(uuid4()),
            workspace_id=workspace_id,
            plugin_id=plugin_id,
            is_enabled=True,
            configuration=configuration,
            installed_by_user_id=user_id
        )
        
        self.db.add(installation)
        
        # Update install count
        plugin = self.db.query(Plugin).filter(Plugin.id == plugin_id).first()
        if plugin:
            plugin.install_count += 1
        
        self.db.commit()
        return installation
    
    def uninstall_plugin(self, installation_id: str):
        """
        Uninstall plugin from workspace.
        """
        installation = self.db.query(PluginInstallation).filter(
            PluginInstallation.id == installation_id
        ).first()
        
        if installation:
            plugin = installation.plugin
            plugin.install_count = max(0, plugin.install_count - 1)
            
            self.db.delete(installation)
            self.db.commit()
            return True
        
        return False


class ConsentService:
    """
    Service for consent management and privacy compliance.
    Tracks user consent for third-party data access.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def grant_consent(
        self,
        user_id: str,
        consent_data: ConsentGrantCreate
    ):
        """
        Record user consent grant.
        
        Ref: Module 12 - Feature 3.2 - Data Security & Consent
        """
        consent = ConsentGrant(
            id=str(uuid4()),
            user_id=user_id,
            consent_type=consent_data.consent_type,
            entity_type=consent_data.entity_type,
            entity_id=consent_data.entity_id,
            requested_permissions=consent_data.requested_permissions,
            granted_permissions=consent_data.granted_permissions,
            is_active=True,
            granted_at=datetime.utcnow()
        )
        
        self.db.add(consent)
        self.db.commit()
        return consent
    
    def revoke_consent(self, consent_id: str) -> bool:
        """
        Revoke user consent.
        
        Ref: Module 12 - Feature 3.2 - Revocation
        """
        consent = self.db.query(ConsentGrant).filter(
            ConsentGrant.id == consent_id
        ).first()
        
        if consent:
            consent.is_active = False
            consent.revoked_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
