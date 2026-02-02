# PronaFlow API Documentation - Version 1.2 Index

**Version**: 1.2  
**Release Date**: February 3, 2026  
**Status**: ✅ Production Ready  
**Coverage**: All 12 Modules (Modules 7, 8, 9, 11, 12 New)

---

## 📚 Documentation Files

### Primary Documentation

#### 1. **API_DOCUMENTATION_V1.2.md** ⭐ START HERE
**Comprehensive API Reference**
- Complete endpoint documentation for all modules
- Request/response examples for each endpoint
- Query parameters and filters
- Rate limiting specifications
- Webhook event types reference
- SDK usage examples (Node.js, Python)
- 10,000+ words, 90+ endpoints documented

**Modules Covered**:
- ✅ Modules 1-6: Identity, Workspace, Projects, Tasks, Scheduling, Collaboration
- ✅ Module 7: Event-Driven Notifications (8 endpoints)
- ✅ Module 8: Archiving & Compliance (12 endpoints)
- ✅ Module 9: Personalization & UX (6 endpoints)
- ✅ Module 11: Analytics & Reporting (15 endpoints)
- ✅ Module 12: Integration Ecosystem (40+ endpoints)

#### 2. **API_DOCUMENTATION_V1.2_RELEASE_NOTES.md**
**Release Information & Summary**
- What's new in v1.2
- Complete endpoint summary table
- Key features overview
- Usage examples and quick starts
- Breaking changes (none)
- Deprecations (none)
- Migration guide
- Support resources

---

## 🔍 Quick Navigation

### By Use Case

**Authentication & Authorization**
- See: API_DOCUMENTATION_V1.2.md → Authentication & Security
- Token structure, expiration, refresh
- Rate limiting details
- MFA support

**Creating & Managing Tasks**
- See: Modules 1-6 sections (existing documentation)
- GET /api/v1/tasks
- POST /api/v1/tasks
- PATCH /api/v1/tasks/{id}

**Real-Time Notifications** (NEW)
- See: Module 7 - Event-Driven Notifications
- GET /api/v1/notifications
- PATCH /api/v1/notifications/{id}/read
- GET /api/v1/notifications/preferences

**Archiving & Compliance** (NEW)
- See: Module 8 - Archiving & Compliance
- POST /api/v1/archive/projects/{id}/archive
- POST /api/v1/archive/trash
- GET /api/v1/audit-logs

**User Preferences** (NEW)
- See: Module 9 - Personalization & UX
- GET /api/v1/preferences
- PATCH /api/v1/preferences
- GET /api/v1/preferences/themes

**Analytics & Reports** (NEW)
- See: Module 11 - Analytics & Reporting
- GET /api/v1/analytics/projects/{id}/metrics
- POST /api/v1/reports
- GET /api/v1/reports/{id}/results

**API Integrations** (NEW)
- See: Module 12 - Integration Ecosystem
- Personal Access Tokens: POST /api/v1/integration/tokens
- Webhooks: POST /api/v1/integration/webhooks
- OAuth: POST /api/v1/integration/oauth/connections
- Plugins: GET /api/v1/integration/plugins

---

## 📊 Documentation Statistics

| Metric | Count |
|--------|-------|
| **Total Endpoints** | 90+ |
| **Total Modules** | 12 |
| **New Modules** | 5 |
| **New Endpoints** | 45+ |
| **Code Examples** | 30+ |
| **Tables** | 25+ |
| **Words** | 10,000+ |

---

## 🚀 Getting Started

### 1. Read the Overview
Start with **API_DOCUMENTATION_V1.2_RELEASE_NOTES.md** for:
- What's new in v1.2
- Quick endpoint summary
- Key features overview

### 2. Deep Dive by Module
For each module you need:
- Understand the purpose and key features
- Review available endpoints
- See request/response examples
- Test with Swagger UI or Postman

### 3. Integration Guide
Pick your use case:
- **Notifications**: Module 7
- **Archiving**: Module 8
- **Personalization**: Module 9
- **Analytics**: Module 11
- **External Integrations**: Module 12

### 4. Test Your Endpoints
- **Swagger UI**: https://api.pronaflow.com/docs
- **Postman**: Import collection from API_DOCUMENTATION_V1.2.md
- **cURL**: Use examples provided in each section

---

## 📋 Module Overview

### Modules 1-6 (Stable)
- Identity & Access Management (IAM)
- Workspace Management
- Project Lifecycle Management
- Task Execution & Orchestration
- Temporal Planning & Scheduling
- Unified Collaboration Hub

**Status**: ✅ Fully Documented (v1.0 & v1.1)  
**Endpoints**: 45+  
**Breaking Changes**: None

### Module 7: Event-Driven Notifications ✨ NEW
**Purpose**: Centralized notification system with real-time updates  
**Endpoints**: 8 (notifications, preferences, events, consumers)  
**Key Features**: 
- In-app notification delivery
- Email notifications
- User preferences (quiet hours, frequency)
- Domain event tracking
- Event consumer subscriptions

### Module 8: Archiving & Compliance ✨ NEW
**Purpose**: Data lifecycle management and GDPR compliance  
**Endpoints**: 12 (archive, trash, audit logs, compliance)  
**Key Features**:
- Project archiving with audit trail
- Trash bin (30-day retention)
- 7-year audit logs for compliance
- Compliance report export
- GDPR data handling

### Module 9: Personalization & UX ✨ NEW
**Purpose**: User preferences and customization  
**Endpoints**: 6 (preferences, themes, languages, accessibility)  
**Key Features**:
- Theme selection (light/dark/system)
- Language/localization (en-US, vi-VN)
- Font size & info density settings
- Accessibility features (WCAG AA/AAA)
- High contrast mode

### Module 11: Analytics & Reporting ✨ NEW
**Purpose**: Project metrics, KPIs, and custom reports  
**Endpoints**: 15 (metrics, burndown, reports, export)  
**Key Features**:
- Real-time project metrics
- Burndown chart data
- Custom report creation
- Scheduled report generation
- Export in multiple formats (CSV, PDF, Excel)

### Module 12: Integration Ecosystem ✨ NEW
**Purpose**: External service integration and extensibility  
**Endpoints**: 40+ (tokens, webhooks, OAuth, bindings, plugins, consent)  
**Key Features**:
- Personal Access Tokens (PAT) with scopes
- Webhook subscriptions with HMAC signatures
- OAuth 2.0 integration (GitHub, Google, Slack, etc.)
- Bi-directional data sync
- Plugin marketplace with verification
- GDPR-compliant consent management

---

## 🔐 Security & Authentication

All endpoints require:
- **JWT Bearer Token** in Authorization header: `Authorization: Bearer {token}`
- **Valid access_token** from login endpoint
- **Scope permissions** for restricted operations (Module 12)

Rate Limiting:
- **General API**: 100 req/min (user), 30 req/min (public)
- **Module 12 API**: Free 60, Pro 1000, Enterprise 5000 req/min

---

## 📖 How to Use This Documentation

### For API Developers
1. Open **API_DOCUMENTATION_V1.2.md**
2. Find your module in the table of contents
3. Review endpoint descriptions
4. Check request/response examples
5. Test with Swagger UI at `/docs`

### For DevOps/Integration
1. Read **Module 12: Integration Ecosystem** first
2. API Tokens for programmatic access
3. Webhooks for event subscriptions
4. Plugins for extensibility

### For Frontend Developers
1. Module 7: Notifications for UI updates
2. Module 9: Preferences for customization
3. Module 11: Analytics for dashboards
4. Module 12: OAuth for external logins

### For Business/Product
1. Module 8: Archiving & Compliance for GDPR
2. Module 11: Analytics & Reporting for insights
3. Module 12: Integration Ecosystem for partnerships

---

## 🛠️ Common Tasks

### Creating an API Token (Module 12)
```
POST /api/v1/integration/tokens
{
  "name": "CI/CD Bot",
  "scopes": ["read:tasks", "write:projects"],
  "expires_at": "2027-02-03"
}
```
See: Module 12 → API Token Management

### Setting Up Webhooks (Module 12)
```
POST /api/v1/integration/webhooks
{
  "name": "Slack Notifications",
  "url": "https://hooks.slack.com/...",
  "subscribed_events": {"task.created": true}
}
```
See: Module 12 → Webhook Management

### Getting Project Metrics (Module 11)
```
GET /api/v1/analytics/projects/{id}/metrics
```
See: Module 11 → Project Analytics

### Managing Notifications (Module 7)
```
GET /api/v1/notifications
PATCH /api/v1/notifications/{id}/read
```
See: Module 7 → Notifications

### Archiving Data (Module 8)
```
POST /api/v1/archive/projects/{id}/archive
GET /api/v1/audit-logs
```
See: Module 8 → Archive Management

---

## 🐛 Troubleshooting

### Documentation Issues
- **Endpoint not working?** Check request format in examples
- **Authentication failed?** Verify token is valid and not expired
- **Rate limited?** Check X-RateLimit headers in response
- **Webhook not delivering?** See Module 12 webhook delivery history

### Getting Help
- **Swagger UI**: https://api.pronaflow.com/docs
- **Status Page**: https://status.pronaflow.com
- **Email**: api-support@pronaflow.com
- **GitHub Issues**: https://github.com/pronaflow/api/issues

---

## 📱 SDK Examples

### Node.js
```javascript
const PronaFlow = require('@pronaflow/sdk');
const client = new PronaFlow({ apiToken: 'prona_...' });

const tasks = await client.tasks.list();
const token = await client.integration.createToken({
  name: 'CI Bot',
  scopes: ['read:tasks']
});
```

### Python
```python
from pronaflow import PronaFlow
client = PronaFlow(api_token='prona_...')

tasks = client.tasks.list()
token = client.integration.create_token(
    name='CI Bot',
    scopes=['read:tasks']
)
```

---

## 📊 Version History

| Version | Date | Modules | Status |
|---------|------|---------|--------|
| **1.2** | Feb 3, 2026 | 1-12 (7,8,9,11,12 new) | ✅ Current |
| 1.1 | Jan 15, 2026 | 1-6 | ✅ Stable |
| 1.0 | Dec 1, 2025 | 1-6 | ✅ Archived |

---

## ✅ Checklist

Before going to production:
- [ ] Read API_DOCUMENTATION_V1.2.md
- [ ] Review authentication section
- [ ] Test endpoints in Swagger UI
- [ ] Generate API token for your application
- [ ] Set up webhooks if needed
- [ ] Review rate limiting for your use case
- [ ] Configure error handling
- [ ] Test in staging environment

---

## 📚 Additional Resources

| Resource | Link |
|----------|------|
| **Main Docs** | API_DOCUMENTATION_V1.2.md |
| **Release Notes** | API_DOCUMENTATION_V1.2_RELEASE_NOTES.md |
| **Swagger UI** | https://api.pronaflow.com/docs |
| **API Status** | https://status.pronaflow.com |
| **GitHub** | https://github.com/pronaflow/api |
| **Support** | api-support@pronaflow.com |

---

**Last Updated**: February 3, 2026  
**Documentation Version**: 1.2  
**Status**: ✅ Production Ready

Start with **API_DOCUMENTATION_V1.2.md** for complete endpoint reference!
