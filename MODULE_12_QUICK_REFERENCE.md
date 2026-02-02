# Module 12: Integration Ecosystem - Quick Reference Guide

## At a Glance

**Module 12** provides an extensible ecosystem for integrating PronaFlow with external services through APIs, webhooks, OAuth, and plugins.

| Feature | Status | Endpoints | Entities |
|---------|--------|-----------|----------|
| API Access (Tokens & Scopes) | ✅ Complete | 7 | 3 |
| Rate Limiting | ✅ Complete | 2 | 1 |
| Webhooks | ✅ Complete | 4 | 3 |
| OAuth Integration | ✅ Complete | 7 | 2 |
| Data Sync Bindings | ✅ Complete | 5 | 1 |
| Plugin Marketplace | ✅ Complete | 6 | 2 |
| Consent & Governance | ✅ Complete | 4 | 1 |
| **Total** | **✅ Complete** | **40+** | **13** |

---

## Core Entities

### API Access Layer
```
ApiToken ──────┬──────> User
               └──────> ApiScope (many-to-many via ApiTokenScope)

ApiTokenScope (junction table)
```

**Use Case**: User creates personal access token to authenticate API requests
```bash
POST /v1/integration/tokens
{
  "name": "CI Bot Token",
  "expires_at": "2025-12-31",
  "scopes": ["read:tasks", "write:projects"]
}
```

### Rate Limiting
```
ApiUsageLog ──> ApiToken ──> User
```

**Use Case**: Enforce API quota (60 req/min free, 1000 req/min pro)
```python
rate_limit = check_rate_limit(token_id)
if not rate_limit.is_allowed:
    raise RateLimitExceeded()
```

### Webhook Layer
```
WebhookEndpoint ──────┬──────> Workspace
                      └──────> WebhookDelivery ──> WebhookEvent

WebhookEvent (defines available events)
```

**Use Case**: Notify external service when task is created
```bash
POST /v1/integration/webhooks
{
  "url": "https://example.com/webhook",
  "secret": "secret_key",
  "events": {
    "task.created": true,
    "task.updated": true
  },
  "retry_policy": "EXPONENTIAL"
}
```

### OAuth Integration
```
OAuthApp ──> OAuthConnection ──┬──> User
             └──> IntegrationBinding ──> Workspace

IntegrationBinding (field mapping)
```

**Use Case**: Connect to GitHub to sync pull requests
```bash
POST /v1/integration/oauth/connections
{
  "oauth_app_id": "github",
  "access_token": "github_token..."
}
```

### Plugin System
```
Plugin ──> PluginInstallation ──┬──> Workspace
           └──> User (installer)
```

**Use Case**: Install markdown editor plugin in workspace
```bash
POST /v1/integration/plugins/markdown-editor/install
{
  "workspace_id": "ws123",
  "configuration": {
    "toolbar": "full",
    "theme": "dark"
  }
}
```

### Governance & Compliance
```
ConsentGrant ──┬──> User
               └──> Workspace
```

**Use Case**: Track GDPR consent for Slack integration
```bash
POST /v1/integration/consents
{
  "consent_type": "THIRD_PARTY",
  "resource_type": "slack_integration",
  "resource_id": "slack_conn_123",
  "description": "Grant access to sync tasks to Slack"
}
```

---

## API Endpoints Quick Reference

### 🔑 API Tokens
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v1/integration/tokens` | Create new token |
| GET | `/v1/integration/tokens` | List user's tokens |
| PATCH | `/v1/integration/tokens/{id}` | Update token (name, active status) |
| DELETE | `/v1/integration/tokens/{id}` | Revoke token |
| GET | `/v1/integration/tokens/scopes` | List available scopes |
| GET | `/v1/integration/tokens/{id}/scopes` | Get token's scopes |
| GET | `/v1/integration/tokens/usage-logs` | API usage analytics |

### 🪝 Webhooks
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v1/integration/webhooks` | Create webhook endpoint |
| GET | `/v1/integration/webhooks` | List workspace webhooks |
| PATCH | `/v1/integration/webhooks/{id}` | Update webhook config |
| GET | `/v1/integration/webhooks/{id}/deliveries` | View delivery history |

### 🔐 OAuth
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/v1/integration/oauth/apps` | List available OAuth providers |
| GET | `/v1/integration/oauth/apps/{id}` | Get provider details |
| POST | `/v1/integration/oauth/connections` | Connect to external service |
| GET | `/v1/integration/oauth/connections` | List user's connections |
| GET | `/v1/integration/oauth/connections/{id}` | Get connection details |
| DELETE | `/v1/integration/oauth/connections/{id}` | Disconnect |
| POST | `/v1/integration/oauth/callback` | OAuth callback handler |

### 🔗 Data Sync Bindings
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v1/integration/bindings` | Create field mapping |
| GET | `/v1/integration/bindings` | List bindings |
| PATCH | `/v1/integration/bindings/{id}` | Update mapping |
| DELETE | `/v1/integration/bindings/{id}` | Remove binding |
| POST | `/v1/integration/bindings/{id}/sync` | Trigger sync |

### 🧩 Plugins
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/v1/integration/plugins` | Plugin marketplace |
| GET | `/v1/integration/plugins/{id}` | Plugin details |
| POST | `/v1/integration/plugins/{id}/install` | Install plugin |
| GET | `/v1/integration/plugins/installed` | List installed plugins |
| PATCH | `/v1/integration/plugins/{id}/config` | Update configuration |
| DELETE | `/v1/integration/plugins/{id}/uninstall` | Uninstall |

### ✅ Consent & Compliance
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/v1/integration/consents` | List consents |
| POST | `/v1/integration/consents` | Grant consent |
| DELETE | `/v1/integration/consents/{id}` | Revoke consent |
| GET | `/v1/integration/consents/status` | Compliance status |

### 📊 Health & Status
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/v1/integration/status` | Integration status |
| GET | `/v1/integration/health` | Health check |

---

## Configuration

### Environment Variables

```bash
# API Token Settings
API_TOKEN_EXPIRY_DAYS=365
API_TOKEN_HASH_ALGORITHM=sha256

# Rate Limiting (requests per minute)
RATE_LIMIT_TIER_FREE_REQ_PER_MIN=60
RATE_LIMIT_TIER_PRO_REQ_PER_MIN=1000
RATE_LIMIT_TIER_ENTERPRISE_REQ_PER_MIN=5000
RATE_LIMIT_WINDOW_SECONDS=60

# Webhook Settings
WEBHOOK_MAX_RETRIES=5
WEBHOOK_RETRY_BACKOFF_SECONDS=60
WEBHOOK_TIMEOUT_SECONDS=30
WEBHOOK_MAX_PAYLOAD_SIZE_KB=1024
WEBHOOK_DELIVERY_TTL_HOURS=24

# OAuth Settings
OAUTH_TOKEN_EXPIRY_MINUTES=60
OAUTH_REFRESH_TOKEN_EXPIRY_DAYS=30
OAUTH_AUTHORIZATION_CODE_EXPIRY_MINUTES=10
OAUTH_REDIRECT_URI_BASE=http://localhost:3000

# Plugin Settings
PLUGIN_MAX_SIZE_MB=50
PLUGIN_MAX_INSTALLABLE_PER_WORKSPACE=100
PLUGIN_EXECUTION_TIMEOUT_SECONDS=30

# Consent & Governance
CONSENT_POLICY_VERSION=1
CONSENT_AUDIT_LOG_RETENTION_DAYS=2555  # 7 years for GDPR
```

---

## Code Examples

### Creating an API Token
```python
# Service
from app.services.integration import ApiTokenService

service = ApiTokenService(db)
response = service.create_api_token(
    user_id=current_user.id,
    workspace_id=workspace_id,
    token_data=ApiTokenCreate(
        name="CI/CD Bot",
        expires_at=datetime(2026, 12, 31),
        scopes=["read:tasks", "write:projects"]
    )
)
print(f"Token: {response.token}")  # Only shown once!
```

### Setting Up a Webhook
```python
from app.services.integration import WebhookService

service = WebhookService(db)
webhook = service.create_webhook_endpoint(
    workspace_id=workspace_id,
    endpoint_data=WebhookEndpointCreate(
        name="Slack Integration",
        url="https://hooks.slack.com/services/...",
        secret="webhook_secret",
        subscribed_events={
            "task.created": True,
            "task.completed": True
        },
        retry_policy="EXPONENTIAL"
    )
)
```

### Connecting OAuth
```python
from app.services.integration import OAuthService

service = OAuthService(db)
connection = service.create_oauth_connection(
    user_id=current_user.id,
    workspace_id=workspace_id,
    oauth_app_id="github",
    access_token=github_token
)
```

### Managing Consent (GDPR)
```python
from app.services.integration import ConsentService

service = ConsentService(db)

# Grant consent
consent = service.grant_consent(
    user_id=user_id,
    consent_type="THIRD_PARTY",
    resource_type="slack_integration",
    resource_id="slack_123"
)

# Revoke consent
service.revoke_consent(consent_id=consent.id)

# Check compliance
status = service.get_user_consent_status(user_id)
```

---

## Security Best Practices

### 1️⃣ API Token Management
- ✅ Never log actual token value (use token hash)
- ✅ Implement token rotation schedule
- ✅ Revoke immediately if compromised
- ✅ Use shortest expiration needed

### 2️⃣ Webhook Security
- ✅ Always verify HMAC signature
- ✅ Validate webhook URL before registration
- ✅ Implement timeout to prevent hangs
- ✅ Retry failed deliveries with backoff

### 3️⃣ OAuth Security
- ✅ Store tokens encrypted at rest
- ✅ Refresh tokens before expiry
- ✅ Validate OAuth scope requests
- ✅ Implement PKCE for mobile clients

### 4️⃣ GDPR Compliance
- ✅ Obtain explicit consent before processing
- ✅ Track all consent grant/revoke events
- ✅ Retain audit logs for 7 years
- ✅ Allow one-click consent revocation

---

## Troubleshooting

### Webhook Not Delivering
1. Check endpoint is active: `GET /v1/integration/webhooks/{id}`
2. Verify URL is accessible and returns 2xx status
3. Check delivery history: `GET /v1/integration/webhooks/{id}/deliveries`
4. Review error message in webhook_deliveries table

### OAuth Token Expired
1. Check token_expires_at: `GET /v1/integration/oauth/connections/{id}`
2. Automatic refresh on next API call (if refresh_token available)
3. Manual refresh: Update refresh_token in OAuthConnection table

### Rate Limit Hit
1. Check current usage: `GET /v1/integration/tokens/usage-logs`
2. Plan optimization to reduce API calls
3. Upgrade to higher tier (Pro: 1000 req/min, Enterprise: 5000 req/min)

### Plugin Installation Failed
1. Check plugin manifest for required permissions
2. Verify workspace has capacity (max 100 plugins)
3. Check plugin file size (max 50 MB)
4. Review plugin_installations.error field

---

## Database Schema Highlights

### Key Indexes for Performance
```sql
-- Token validation (most frequent query)
CREATE INDEX ix_api_tokens_token_hash ON api_tokens(token_hash);
CREATE INDEX ix_api_tokens_user_id ON api_tokens(user_id);

-- Webhook delivery status
CREATE INDEX ix_webhook_deliveries_status ON webhook_deliveries(status);
CREATE INDEX ix_webhook_deliveries_created_at ON webhook_deliveries(created_at);

-- OAuth connection lookup
CREATE INDEX ix_oauth_connections_user_id ON oauth_connections(user_id);
CREATE INDEX ix_oauth_connections_workspace_id ON oauth_connections(workspace_id);

-- Consent tracking (GDPR)
CREATE INDEX ix_consent_grants_user_id ON consent_grants(user_id);
CREATE INDEX ix_consent_grants_consent_type ON consent_grants(consent_type);
```

### Cascading Delete Behavior
- Delete User → Deletes all ApiTokens, OAuthConnections, PluginInstallations
- Delete Workspace → Deletes all WebhookEndpoints, Integrations, PluginInstallations
- Delete Plugin → Deletes all PluginInstallations
- Delete OAuthApp → Deletes all OAuthConnections and IntegrationBindings

---

## Next Steps

1. **Deploy**: Run `alembic upgrade head` to create all tables
2. **Configure**: Set environment variables for rate limits and timeouts
3. **Populate OAuth**: Add GitHub, Google, Slack app configurations
4. **Initialize Scopes**: Load standard API scopes (read:*, write:*, admin:*)
5. **Test**: Create test token and verify rate limiting works
6. **Monitor**: Setup alerts for webhook delivery failures

---

**Status**: ✅ Production Ready  
**Last Updated**: 2024  
**Maintained By**: Development Team
