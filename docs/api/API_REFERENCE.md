# PronaFlow API Documentation

Complete REST API documentation for PronaFlow backend.

## 📚 Available Versions

### Version 1.3 (Current) - February 3, 2026
- **[Full Documentation](API_DOCUMENTATION_V1.3.md)** - Complete API reference
- **Status**: ✅ Active
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**What's New in v1.3**:
- ✨ Added Module 8: Archive & Data Management endpoints
- ✨ Added Module 9: Reports & Analytics endpoints
- ✨ Added Module 10-12: Integration, Webhooks, and Plugins
- 🔧 Enhanced error handling with detailed error responses
- 🔧 Added pagination, filtering, and sorting patterns
- 🔧 Improved webhook delivery tracking
- 📖 Added comprehensive code examples (JS/TS, Python, cURL)
- 📖 Added best practices and security guidelines

## 🚀 Quick Start

### 1. Authentication
```bash
# Register
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!@#",
  "full_name": "John Doe"
}

# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!@#"
}
```

### 2. Use Access Token
```bash
# All subsequent requests
Authorization: Bearer {access_token}
```

### 3. Common Endpoints
```bash
# Get current user
GET /api/v1/auth/me

# List workspaces
GET /api/v1/workspaces

# List projects
GET /api/v1/projects?workspace_id={id}

# List tasks
GET /api/v1/tasks?project_id={id}
```

## 📋 API Modules

### Core Modules
1. **[Module 1: IAM](API_DOCUMENTATION_V1.3.md#module-1-identity--access-management-iam)** - Authentication & Authorization
2. **[Module 2: Workspaces](API_DOCUMENTATION_V1.3.md#module-2-workspace-management)** - Multi-tenant workspace management
3. **[Module 3: Projects](API_DOCUMENTATION_V1.3.md#module-3-project-lifecycle-management)** - Project lifecycle

### Execution & Collaboration
4. **[Module 4: Tasks](API_DOCUMENTATION_V1.3.md#module-4-task-execution--orchestration)** - Task management & execution
5. **[Module 5: Scheduling](API_DOCUMENTATION_V1.3.md#module-5-temporal-planning--scheduling)** - Temporal planning
6. **[Module 6: Collaboration](API_DOCUMENTATION_V1.3.md#module-6-unified-collaboration-hub)** - Notifications & comments

### Data & Analytics
7. **[Module 8: Archive](API_DOCUMENTATION_V1.3.md#module-8-archive--data-management)** - Data archiving & retention
8. **[Module 9: Reports](API_DOCUMENTATION_V1.3.md#module-9-reports--analytics)** - Analytics & reporting

### Integration & Extension
9. **[Module 10-12: Integration](API_DOCUMENTATION_V1.3.md#module-10-12-integration--webhooks)** - APIs, Webhooks, Plugins

### Business Operations
10. **[Module 13: Billing](API_DOCUMENTATION_V1.3.md#module-13-subscription--billing-management)** - Subscriptions & billing
11. **[Module 14: Admin](API_DOCUMENTATION_V1.3.md#module-14-system-administration)** - System administration
12. **[Module 15: Help Center](API_DOCUMENTATION_V1.3.md#module-15-help-center--knowledge-base)** - Knowledge base
13. **[Module 16: Onboarding](API_DOCUMENTATION_V1.3.md#module-16-user-onboarding--adoption)** - User onboarding

## 🔗 Interactive Documentation

### Swagger UI
Explore and test APIs interactively:
```
http://localhost:8000/docs
```

Features:
- Try out API calls directly
- See request/response schemas
- View authentication requirements
- Test with your own data

### ReDoc
Beautiful API documentation:
```
http://localhost:8000/redoc
```

Features:
- Clean, readable format
- Code samples in multiple languages
- Search functionality
- Download OpenAPI spec

### OpenAPI Schema
Download the OpenAPI specification:
```
http://localhost:8000/openapi.json
```

## 🛠️ Tools & SDKs

### Postman Collection
Import our Postman collection for easy testing:
- Download from `/docs/postman/pronaflow-api-v1.postman_collection.json`
- Import into Postman
- Set environment variables

### Code Examples
See [Testing & Examples](API_DOCUMENTATION_V1.3.md#testing--examples) for:
- cURL commands
- JavaScript/TypeScript (Fetch, Axios)
- Python (requests)
- Best practices

## 🔐 Authentication

### JWT Tokens
PronaFlow uses JWT (JSON Web Token) for authentication:

```typescript
// Login and store token
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { access_token } = await response.json();
localStorage.setItem('access_token', access_token);

// Use token in requests
const headers = {
  'Authorization': `Bearer ${access_token}`,
  'Content-Type': 'application/json'
};
```

### Token Expiration
- **Access Token**: 30 minutes
- **Refresh Token**: 7 days
- Implement token refresh before expiration

## 📊 Common Patterns

### Pagination
```
GET /api/v1/tasks?page=1&page_size=20
```

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

### Filtering & Sorting
```
GET /api/v1/tasks?status=active&sort=-created_at
```

### Error Handling
All errors follow consistent format:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "status_code": 422,
    "details": [...]
  }
}
```

## 🚦 Rate Limits

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Authentication | 5 attempts | 15 minutes |
| General API | 100 requests | 1 minute |
| Public endpoints | 30 requests | 1 minute |

Rate limit headers in every response:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642252800
```

## 🌐 Base URLs

### Development
```
http://localhost:8000
```

### Staging
```
https://api-staging.pronaflow.com
```

### Production
```
https://api.pronaflow.com
```

## 📞 Support

- **Technical Issues**: support@pronaflow.com
- **Bug Reports**: GitHub Issues
- **Feature Requests**: feedback.pronaflow.com
- **Documentation Updates**: Contribute via PR

## 📝 Changelog

### v1.3 - February 3, 2026
- Added Archive & Data Management endpoints
- Added Reports & Analytics endpoints
- Added Integration & Webhooks endpoints
- Enhanced error handling
- Added code examples for JS/TS and Python
- Improved documentation structure

### v1.2 - January 15, 2026
- Added Help Center endpoints
- Added Onboarding endpoints
- Enhanced workspace management
- Added MFA support

### v1.1 - December 1, 2025
- Added task dependencies
- Added file attachments
- Added time tracking
- Enhanced project management

### v1.0 - November 1, 2025
- Initial API release
- Core modules (IAM, Workspace, Project, Task)
- Basic authentication
- JWT token support

---

**Current Version**: 1.3  
**Last Updated**: February 3, 2026  
**Maintained by**: PronaFlow Development Team
