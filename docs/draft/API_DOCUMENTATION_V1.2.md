# PronaFlow API Documentation - Version 1.2
**Modules: 1-12 (7, 8, 9, 11, 12 New) | Last Updated: February 3, 2026**

---

## 📋 Table of Contents

### Core
1. [Base Information](#base-information)
2. [Authentication & Security](#authentication--security)
3. [Common Response Formats](#common-response-formats)
4. [Error Handling](#error-handling)

### Modules
5. [Module 7: Event-Driven Notifications](#module-7-event-driven-notifications) ✨ NEW
6. [Module 8: Archiving & Compliance](#module-8-archiving--compliance) ✨ NEW
7. [Module 9: Personalization & User Experience](#module-9-personalization--user-experience) ✨ NEW
8. [Module 11: Analytics & Reporting](#module-11-analytics--reporting) ✨ NEW
9. [Module 12: Integration Ecosystem](#module-12-integration-ecosystem) ✨ NEW

---

## Base Information

### Server Details
- **Base URL (Development)**: `http://localhost:8000`
- **Base URL (Production)**: `https://api.pronaflow.com`
- **API Version**: `v1`
- **API Prefix**: `/api/v1`
- **Content-Type**: `application/json`
- **Character Encoding**: UTF-8

### Available Documentation
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **Health Check**: `/health`
- **OpenAPI Schema**: `/openapi.json`

### Modules Overview
| Module | Coverage | Status | New Endpoints |
|--------|----------|--------|---|
| 1-6 | Identity, Workspace, Projects, Tasks, Scheduling, Collaboration | ✅ Stable | - |
| **7** | **Event-Driven Notifications** | ✅ **Complete** | **8** |
| **8** | **Archiving & Compliance** | ✅ **Complete** | **12** |
| **9** | **Personalization & UX** | ✅ **Complete** | **6** |
| **10-11** | Analytics & Reporting | ✅ Partial | 15 |
| **12** | **Integration Ecosystem** | ✅ **Complete** | **40+** |

---

## Authentication & Security

### Overview
PronaFlow uses **JWT (JSON Web Token)** for API authentication with optional **Multi-Factor Authentication (MFA)**.

### Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "email": "user@example.com",
    "username": "username",
    "roles": ["user", "admin"],
    "iat": 1699564800,
    "exp": 1699576800
  }
}
```

### Authorization Header
```
Authorization: Bearer {access_token}
```

### Token Expiration & Refresh
- **Access Token**: 30 minutes
- **Refresh Token**: 7 days
- **Email Verification**: 24 hours
- **Password Reset**: 15 minutes
- **API Token**: 365 days (Module 12)

### Security Requirements
- **Password Minimum**: 12 characters
- **Password Strength**: Uppercase, lowercase, digit, special character
- **HTTPS**: Required in production
- **CORS**: Restricted to allowed origins
- **Rate Limiting**: Tiered by module (see below)

### Rate Limiting

#### General API
- **Default**: 100 requests/minute per user
- **Public**: 30 requests/minute per IP
- **Authentication**: 5 failed attempts → 15-minute lockout

#### Module 12 Integration API
- **Free Tier**: 60 requests/minute
- **Pro Tier**: 1,000 requests/minute
- **Enterprise Tier**: 5,000 requests/minute

---

## Common Response Formats

### Success Response (2xx)
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Resource Name",
    "created_at": "2026-02-03T10:30:00Z"
  },
  "message": "Operation completed successfully"
}
```

### Paginated Response
```json
{
  "success": true,
  "data": [
    { "id": "uuid1", "name": "Item 1" },
    { "id": "uuid2", "name": "Item 2" }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

### Error Response (4xx, 5xx)
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request parameter",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "timestamp": "2026-02-03T10:30:00Z"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful GET/PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate resource |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal error |

### Error Codes

| Error Code | HTTP | Description |
|-----------|------|-------------|
| INVALID_REQUEST | 400 | Invalid request parameters |
| UNAUTHORIZED | 401 | Missing or invalid token |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists |
| RATE_LIMITED | 429 | Rate limit exceeded |
| INTERNAL_ERROR | 500 | Server error |
| VALIDATION_ERROR | 422 | Validation failed |

---

# MODULE 7: Event-Driven Notifications

## Overview
**Purpose**: Centralized event notification system for real-time updates and asynchronous processing  
**Key Features**: 
- Domain event tracking
- Notification preferences
- Event consumer management
- Real-time updates

## Endpoints

### 🔔 Notifications

#### List User Notifications
```
GET /api/v1/notifications
```

**Query Parameters**:
```
page: integer (default: 1)
page_size: integer (default: 20)
status: "unread" | "read" (optional)
type: string (optional)
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "title": "Task assigned to you",
      "message": "John assigned task 'Design UI' to you",
      "type": "task_assigned",
      "read": false,
      "created_at": "2026-02-03T10:30:00Z",
      "action_url": "/tasks/task_id"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 45
  }
}
```

#### Mark Notification as Read
```
PATCH /api/v1/notifications/{notification_id}/read
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "notification_id",
    "read": true,
    "read_at": "2026-02-03T10:35:00Z"
  }
}
```

#### Mark All as Read
```
POST /api/v1/notifications/mark-all-read
```

**Response**:
```json
{
  "success": true,
  "message": "All notifications marked as read",
  "count": 45
}
```

#### Delete Notification
```
DELETE /api/v1/notifications/{notification_id}
```

**Response**: 204 No Content

### 📋 Notification Preferences

#### Get Notification Preferences
```
GET /api/v1/notifications/preferences
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "email_on_task_assigned": true,
    "email_on_comment": true,
    "email_on_project_update": false,
    "in_app_notifications": true,
    "notification_frequency": "immediate",
    "quiet_hours": {
      "enabled": true,
      "start": "22:00",
      "end": "08:00"
    }
  }
}
```

#### Update Notification Preferences
```
PATCH /api/v1/notifications/preferences
```

**Request Body**:
```json
{
  "email_on_task_assigned": true,
  "email_on_comment": false,
  "notification_frequency": "daily",
  "quiet_hours": {
    "enabled": true,
    "start": "22:00",
    "end": "08:00"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "updated_at": "2026-02-03T10:35:00Z"
  }
}
```

### 📡 Domain Events

#### List Domain Events
```
GET /api/v1/events
```

**Query Parameters**:
```
event_type: string (optional)
workspace_id: uuid (optional)
limit: integer (default: 100)
offset: integer (default: 0)
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "event_type": "task.created",
      "aggregate_type": "Task",
      "aggregate_id": "task_uuid",
      "timestamp": "2026-02-03T10:30:00Z",
      "user_id": "user_uuid",
      "workspace_id": "workspace_uuid",
      "payload": {
        "task_id": "task_uuid",
        "title": "Design UI",
        "priority": "high"
      }
    }
  ],
  "total": 1250
}
```

### 🔌 Event Consumers

#### List Event Consumers
```
GET /api/v1/event-consumers
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "event_type": "task.created",
      "handler_type": "email",
      "is_active": true,
      "created_at": "2026-02-03T10:30:00Z"
    }
  ]
}
```

#### Subscribe to Event
```
POST /api/v1/event-consumers
```

**Request Body**:
```json
{
  "event_type": "task.completed",
  "handler_type": "email",
  "config": {
    "recipients": ["manager@example.com"]
  }
}
```

**Response**: 201 Created

---

# MODULE 8: Archiving & Compliance

## Overview
**Purpose**: Data lifecycle management, compliance, and trash bin operations  
**Key Features**:
- Project/data archiving
- Compliance tracking
- Trash bin management
- Audit logging
- GDPR support

## Endpoints

### 📦 Archive Management

#### Archive Project
```
POST /api/v1/archive/projects/{project_id}/archive
```

**Request Body**:
```json
{
  "reason": "Project completed",
  "archive_all_related": true,
  "notify_team": true
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "project_id",
    "status": "archived",
    "archived_at": "2026-02-03T10:30:00Z",
    "archived_by": "user_id",
    "reason": "Project completed"
  }
}
```

#### Get Archive History
```
GET /api/v1/archive/projects/{project_id}/history
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "action": "archived",
      "reason": "Project completed",
      "timestamp": "2026-02-03T10:30:00Z",
      "performed_by": "user_uuid"
    }
  ]
}
```

### 🗑️ Trash Bin Management

#### Move to Trash
```
POST /api/v1/archive/trash
```

**Request Body**:
```json
{
  "resource_type": "task",
  "resource_id": "task_uuid"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "trash_item_id",
    "resource_type": "task",
    "resource_id": "task_uuid",
    "deleted_at": "2026-02-03T10:30:00Z",
    "expires_at": "2026-03-05T10:30:00Z"
  }
}
```

#### List Trash Items
```
GET /api/v1/archive/trash
```

**Query Parameters**:
```
resource_type: string (optional)
workspace_id: uuid (optional)
page: integer (default: 1)
page_size: integer (default: 20)
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "resource_type": "task",
      "resource_name": "Design UI",
      "deleted_at": "2026-02-03T10:30:00Z",
      "expires_at": "2026-03-05T10:30:00Z",
      "deleted_by": "user_uuid"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 15
  }
}
```

#### Restore from Trash
```
POST /api/v1/archive/trash/{trash_item_id}/restore
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "task_uuid",
    "status": "active",
    "restored_at": "2026-02-03T10:35:00Z"
  }
}
```

#### Permanently Delete
```
DELETE /api/v1/archive/trash/{trash_item_id}
```

**Response**: 204 No Content

### 📋 Compliance & Audit Logs

#### Get Audit Logs
```
GET /api/v1/audit-logs
```

**Query Parameters**:
```
workspace_id: uuid (optional)
user_id: uuid (optional)
action: string (optional)
start_date: ISO8601 (optional)
end_date: ISO8601 (optional)
page: integer (default: 1)
page_size: integer (default: 50)
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "action": "project.archived",
      "user_id": "user_uuid",
      "user_email": "user@example.com",
      "resource_type": "project",
      "resource_id": "project_uuid",
      "changes": {
        "status": { "old": "active", "new": "archived" }
      },
      "timestamp": "2026-02-03T10:30:00Z",
      "ip_address": "192.168.1.1"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 2540
  }
}
```

#### Export Compliance Report
```
GET /api/v1/compliance/export
```

**Query Parameters**:
```
start_date: ISO8601 (required)
end_date: ISO8601 (required)
format: "csv" | "json" | "pdf" (default: "json")
```

**Response**: 
- **JSON**: 200 OK with JSON data
- **CSV/PDF**: 200 OK with file download

---

# MODULE 9: Personalization & User Experience

## Overview
**Purpose**: User preferences, customization, and UX personalization  
**Key Features**:
- Theme preferences (light/dark/system)
- Language/localization settings
- UI density and font size preferences
- Accessibility settings
- Custom workspaces

## Endpoints

### 👤 User Preferences

#### Get User Preferences
```
GET /api/v1/preferences
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "user_uuid",
    "theme": "dark",
    "language": "en-US",
    "font_size": "medium",
    "info_density": "comfortable",
    "timezone": "America/New_York",
    "date_format": "MM/DD/YYYY",
    "time_format": "12h",
    "accessibility": {
      "high_contrast": false,
      "reduced_motion": false,
      "screen_reader_enabled": false
    },
    "notifications": {
      "desktop_notifications": true,
      "sound_enabled": true,
      "notification_frequency": "immediate"
    },
    "updated_at": "2026-02-03T10:30:00Z"
  }
}
```

#### Update User Preferences
```
PATCH /api/v1/preferences
```

**Request Body**:
```json
{
  "theme": "light",
  "language": "vi-VN",
  "font_size": "large",
  "info_density": "compact",
  "timezone": "Asia/Ho_Chi_Minh",
  "accessibility": {
    "high_contrast": true,
    "reduced_motion": false
  }
}
```

**Response**: 200 OK with updated preferences

### 🎨 Theme & Appearance

#### Get Available Themes
```
GET /api/v1/preferences/themes
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "light",
      "name": "Light",
      "colors": {
        "primary": "#0066CC",
        "secondary": "#F5F5F5"
      }
    },
    {
      "id": "dark",
      "name": "Dark",
      "colors": {
        "primary": "#1E88E5",
        "secondary": "#121212"
      }
    }
  ]
}
```

### 🌍 Localization

#### Get Supported Languages
```
GET /api/v1/preferences/languages
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "code": "en-US",
      "name": "English (United States)",
      "native_name": "English"
    },
    {
      "code": "vi-VN",
      "name": "Vietnamese",
      "native_name": "Tiếng Việt"
    }
  ]
}
```

### ♿ Accessibility Settings

#### Get WCAG Compliance Level
```
GET /api/v1/preferences/accessibility/wcag-level
```

**Response**:
```json
{
  "success": true,
  "data": {
    "current_level": "AA",
    "available_levels": ["A", "AA", "AAA"],
    "description": "WCAG 2.1 Level AA compliant"
  }
}
```

---

# MODULE 11: Analytics & Reporting

## Overview
**Purpose**: Project analytics, reporting, and business intelligence  
**Key Features**:
- Project metrics and KPIs
- Custom report generation
- Real-time dashboards
- Data export
- Trend analysis

## Endpoints

### 📊 Project Analytics

#### Get Project Metrics
```
GET /api/v1/analytics/projects/{project_id}/metrics
```

**Query Parameters**:
```
start_date: ISO8601 (optional)
end_date: ISO8601 (optional)
granularity: "daily" | "weekly" | "monthly" (default: "daily")
```

**Response**:
```json
{
  "success": true,
  "data": {
    "project_id": "uuid",
    "total_tasks": 145,
    "completed_tasks": 98,
    "completion_rate": 67.6,
    "avg_task_duration_days": 4.2,
    "on_time_rate": 85.5,
    "team_velocity": 23.5,
    "metrics": [
      {
        "date": "2026-02-03",
        "tasks_completed": 5,
        "tasks_created": 3,
        "avg_resolution_time": 2.5
      }
    ]
  }
}
```

#### Get Burndown Chart Data
```
GET /api/v1/analytics/projects/{project_id}/burndown
```

**Response**:
```json
{
  "success": true,
  "data": {
    "project_id": "uuid",
    "start_date": "2026-01-01",
    "end_date": "2026-02-03",
    "ideal_line": [
      {"date": "2026-01-01", "remaining_work": 145},
      {"date": "2026-01-02", "remaining_work": 142}
    ],
    "actual_line": [
      {"date": "2026-01-01", "remaining_work": 145},
      {"date": "2026-01-02", "remaining_work": 143}
    ]
  }
}
```

### 📈 Reports

#### Create Custom Report
```
POST /api/v1/reports
```

**Request Body**:
```json
{
  "name": "Q1 Project Performance",
  "description": "Monthly performance metrics for Q1 2026",
  "workspace_id": "uuid",
  "type": "project_summary",
  "filters": {
    "project_ids": ["uuid1", "uuid2"],
    "start_date": "2026-01-01",
    "end_date": "2026-03-31"
  },
  "metrics": ["completion_rate", "team_velocity", "on_time_rate"],
  "schedule": {
    "type": "monthly",
    "day_of_month": 1,
    "time": "09:00"
  }
}
```

**Response**: 201 Created

#### List Reports
```
GET /api/v1/reports
```

**Query Parameters**:
```
workspace_id: uuid (optional)
type: string (optional)
page: integer (default: 1)
page_size: integer (default: 20)
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Q1 Project Performance",
      "type": "project_summary",
      "created_at": "2026-02-03T10:30:00Z",
      "last_executed": "2026-02-03T09:00:00Z",
      "schedule": {
        "type": "monthly",
        "day_of_month": 1
      }
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 45
  }
}
```

#### Execute Report
```
POST /api/v1/reports/{report_id}/execute
```

**Response**:
```json
{
  "success": true,
  "data": {
    "execution_id": "uuid",
    "report_id": "uuid",
    "status": "processing",
    "created_at": "2026-02-03T10:35:00Z"
  }
}
```

#### Get Report Results
```
GET /api/v1/reports/{report_id}/results
```

**Response**:
```json
{
  "success": true,
  "data": {
    "report_id": "uuid",
    "execution_id": "uuid",
    "status": "completed",
    "generated_at": "2026-02-03T10:36:00Z",
    "summary": {
      "total_projects": 2,
      "avg_completion_rate": 72.3,
      "avg_team_velocity": 19.8
    },
    "details": [
      {
        "project_id": "uuid",
        "project_name": "Website Redesign",
        "completion_rate": 68.5,
        "team_velocity": 18.2
      }
    ]
  }
}
```

#### Export Report
```
GET /api/v1/reports/{report_id}/export
```

**Query Parameters**:
```
format: "csv" | "pdf" | "excel" (default: "csv")
include_charts: boolean (default: true)
```

**Response**: File download (content-disposition: attachment)

---

# MODULE 12: Integration Ecosystem

## Overview
**Purpose**: API access, webhooks, OAuth integration, and plugin marketplace  
**Key Features**:
- Personal access tokens (PAT)
- Webhook subscriptions and delivery
- OAuth provider integration
- Plugin marketplace
- GDPR-compliant consent management

## Endpoints

### 🔑 API Token Management

#### Create API Token
```
POST /api/v1/integration/tokens
```

**Request Body**:
```json
{
  "name": "CI/CD Bot",
  "expires_at": "2027-02-03",
  "scopes": ["read:tasks", "write:projects", "read:reports"]
}
```

**Response**: 201 Created
```json
{
  "success": true,
  "data": {
    "id": "token_uuid",
    "name": "CI/CD Bot",
    "token": "prona_abc123def456ghi789jkl...",
    "scopes": ["read:tasks", "write:projects", "read:reports"],
    "expires_at": "2027-02-03",
    "created_at": "2026-02-03T10:30:00Z",
    "warning": "Save this token securely - you won't see it again!"
  }
}
```

#### List API Tokens
```
GET /api/v1/integration/tokens
```

**Query Parameters**:
```
page: integer (default: 1)
page_size: integer (default: 20)
include_usage: boolean (default: false)
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "token_uuid",
      "name": "CI/CD Bot",
      "scopes": ["read:tasks", "write:projects"],
      "last_used_at": "2026-02-03T09:15:00Z",
      "expires_at": "2027-02-03",
      "is_revoked": false,
      "created_at": "2026-02-03T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 5
  }
}
```

#### Update API Token
```
PATCH /api/v1/integration/tokens/{token_id}
```

**Request Body**:
```json
{
  "name": "CI/CD Bot (Updated)",
  "is_active": true
}
```

**Response**: 200 OK

#### Revoke API Token
```
DELETE /api/v1/integration/tokens/{token_id}
```

**Response**: 204 No Content

#### List Available Scopes
```
GET /api/v1/integration/tokens/scopes
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "scope": "read:tasks",
      "description": "Read access to tasks",
      "resource_type": "task",
      "permission_type": "read"
    },
    {
      "scope": "write:projects",
      "description": "Write access to projects",
      "resource_type": "project",
      "permission_type": "write"
    }
  ]
}
```

#### Get API Usage
```
GET /api/v1/integration/tokens/{token_id}/usage
```

**Query Parameters**:
```
start_date: ISO8601 (optional)
end_date: ISO8601 (optional)
granularity: "hourly" | "daily" (default: "daily")
```

**Response**:
```json
{
  "success": true,
  "data": {
    "token_id": "uuid",
    "period": {
      "start": "2026-02-01",
      "end": "2026-02-03"
    },
    "total_requests": 1240,
    "requests_by_method": {
      "GET": 950,
      "POST": 200,
      "PATCH": 80,
      "DELETE": 10
    },
    "requests_by_endpoint": [
      {
        "endpoint": "GET /api/v1/tasks",
        "count": 650
      },
      {
        "endpoint": "GET /api/v1/projects",
        "count": 200
      }
    ],
    "rate_limit": {
      "tier": "pro",
      "limit_per_minute": 1000,
      "current_usage": 34
    }
  }
}
```

### 🪝 Webhook Management

#### Create Webhook Endpoint
```
POST /api/v1/integration/webhooks
```

**Request Body**:
```json
{
  "name": "Slack Notifications",
  "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "secret": "webhook_secret_key",
  "subscribed_events": {
    "task.created": true,
    "task.completed": true,
    "project.updated": false
  },
  "retry_policy": "exponential",
  "max_retries": 5,
  "timeout_seconds": 30
}
```

**Response**: 201 Created
```json
{
  "success": true,
  "data": {
    "id": "webhook_uuid",
    "name": "Slack Notifications",
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "is_active": true,
    "subscribed_events": {
      "task.created": true,
      "task.completed": true
    },
    "created_at": "2026-02-03T10:30:00Z"
  }
}
```

#### List Webhooks
```
GET /api/v1/integration/webhooks
```

**Query Parameters**:
```
page: integer (default: 1)
page_size: integer (default: 20)
is_active: boolean (optional)
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "webhook_uuid",
      "name": "Slack Notifications",
      "url": "https://hooks.slack.com/services/...",
      "is_active": true,
      "last_triggered_at": "2026-02-03T10:15:00Z",
      "created_at": "2026-02-03T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 3
  }
}
```

#### Update Webhook
```
PATCH /api/v1/integration/webhooks/{webhook_id}
```

**Request Body**:
```json
{
  "name": "Slack Notifications (Updated)",
  "subscribed_events": {
    "task.created": true,
    "task.completed": false,
    "project.updated": true
  },
  "is_active": true
}
```

**Response**: 200 OK

#### Get Webhook Delivery History
```
GET /api/v1/integration/webhooks/{webhook_id}/deliveries
```

**Query Parameters**:
```
status: "pending" | "delivered" | "failed" | "retrying" (optional)
limit: integer (default: 50)
offset: integer (default: 0)
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "delivery_uuid",
      "webhook_id": "webhook_uuid",
      "event_type": "task.created",
      "status": "delivered",
      "attempt_number": 1,
      "status_code": 200,
      "delivered_at": "2026-02-03T10:31:00Z",
      "response_time_ms": 245
    },
    {
      "id": "delivery_uuid_2",
      "webhook_id": "webhook_uuid",
      "event_type": "task.completed",
      "status": "failed",
      "attempt_number": 3,
      "status_code": 500,
      "last_error": "Internal Server Error",
      "next_retry_at": "2026-02-03T11:00:00Z",
      "created_at": "2026-02-03T10:15:00Z"
    }
  ],
  "total": 156
}
```

#### Delete Webhook
```
DELETE /api/v1/integration/webhooks/{webhook_id}
```

**Response**: 204 No Content

### 🔐 OAuth Integration

#### List Available OAuth Providers
```
GET /api/v1/integration/oauth/apps
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "oauth_app_uuid",
      "provider_name": "github",
      "display_name": "GitHub",
      "authorize_url": "https://github.com/login/oauth/authorize",
      "scopes": ["repo", "user"],
      "is_enabled": true,
      "icon_url": "https://..."
    },
    {
      "id": "oauth_app_uuid_2",
      "provider_name": "google_calendar",
      "display_name": "Google Calendar",
      "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
      "scopes": ["calendar"],
      "is_enabled": true,
      "icon_url": "https://..."
    }
  ]
}
```

#### Get OAuth App Details
```
GET /api/v1/integration/oauth/apps/{app_id}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "oauth_app_uuid",
    "provider_name": "github",
    "display_name": "GitHub",
    "description": "Connect your GitHub account to sync repositories and pull requests",
    "authorize_url": "https://github.com/login/oauth/authorize",
    "required_scopes": ["repo", "user"],
    "is_enabled": true,
    "documentation_url": "https://docs.example.com/github"
  }
}
```

#### Create OAuth Connection
```
POST /api/v1/integration/oauth/connections
```

**Request Body**:
```json
{
  "oauth_app_id": "oauth_app_uuid",
  "access_token": "github_token_...",
  "refresh_token": "github_refresh_token_...",
  "external_user_id": "github_username"
}
```

**Response**: 201 Created
```json
{
  "success": true,
  "data": {
    "id": "oauth_connection_uuid",
    "user_id": "user_uuid",
    "oauth_app_id": "oauth_app_uuid",
    "provider_name": "github",
    "is_active": true,
    "external_user_id": "github_username",
    "last_verified_at": "2026-02-03T10:30:00Z",
    "created_at": "2026-02-03T10:30:00Z"
  }
}
```

#### List OAuth Connections
```
GET /api/v1/integration/oauth/connections
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "oauth_connection_uuid",
      "provider_name": "github",
      "display_name": "GitHub",
      "external_user_id": "github_username",
      "is_active": true,
      "last_verified_at": "2026-02-03T10:30:00Z",
      "created_at": "2026-02-03T10:30:00Z"
    }
  ]
}
```

#### Disconnect OAuth
```
DELETE /api/v1/integration/oauth/connections/{connection_id}
```

**Response**: 204 No Content

### 🧩 Plugin Marketplace

#### List Plugin Marketplace
```
GET /api/v1/integration/plugins
```

**Query Parameters**:
```
category: string (optional)
search: string (optional)
sort_by: "rating" | "installs" | "newest" (default: "rating")
page: integer (default: 1)
page_size: integer (default: 20)
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "plugin_uuid",
      "name": "Markdown Editor",
      "version": "2.1.0",
      "author": "Plugin Developer",
      "description": "Full-featured Markdown editor with live preview",
      "icon_url": "https://...",
      "is_verified": true,
      "install_count": 1250,
      "rating": 4.7,
      "rating_count": 340
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 245
  }
}
```

#### Get Plugin Details
```
GET /api/v1/integration/plugins/{plugin_id}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "plugin_uuid",
    "name": "Markdown Editor",
    "version": "2.1.0",
    "author": "Plugin Developer",
    "description": "Full-featured Markdown editor with live preview",
    "documentation_url": "https://docs.example.com/markdown-editor",
    "repository_url": "https://github.com/...",
    "icon_url": "https://...",
    "is_verified": true,
    "manifest": {
      "hooks": ["task:editor"],
      "permissions": ["read:tasks", "write:tasks"]
    },
    "install_count": 1250,
    "rating": 4.7
  }
}
```

#### Install Plugin
```
POST /api/v1/integration/plugins/{plugin_id}/install
```

**Request Body**:
```json
{
  "workspace_id": "workspace_uuid",
  "configuration": {
    "toolbar": "full",
    "theme": "dark"
  }
}
```

**Response**: 201 Created
```json
{
  "success": true,
  "data": {
    "id": "plugin_installation_uuid",
    "plugin_id": "plugin_uuid",
    "workspace_id": "workspace_uuid",
    "is_active": true,
    "configuration": {
      "toolbar": "full",
      "theme": "dark"
    },
    "installed_at": "2026-02-03T10:30:00Z"
  }
}
```

#### List Installed Plugins
```
GET /api/v1/integration/plugins/installed
```

**Query Parameters**:
```
workspace_id: uuid (required)
is_active: boolean (optional)
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "plugin_installation_uuid",
      "plugin_id": "plugin_uuid",
      "plugin_name": "Markdown Editor",
      "version": "2.1.0",
      "is_active": true,
      "installed_at": "2026-02-03T10:30:00Z"
    }
  ]
}
```

#### Update Plugin Configuration
```
PATCH /api/v1/integration/plugins/{installation_id}/config
```

**Request Body**:
```json
{
  "configuration": {
    "toolbar": "minimal",
    "theme": "light"
  }
}
```

**Response**: 200 OK

#### Uninstall Plugin
```
DELETE /api/v1/integration/plugins/{installation_id}
```

**Response**: 204 No Content

### ✅ Consent & Governance

#### Grant Consent
```
POST /api/v1/integration/consents
```

**Request Body**:
```json
{
  "consent_type": "THIRD_PARTY",
  "resource_type": "slack_integration",
  "resource_id": "oauth_connection_uuid",
  "description": "Grant access to sync tasks to Slack"
}
```

**Response**: 201 Created
```json
{
  "success": true,
  "data": {
    "id": "consent_uuid",
    "user_id": "user_uuid",
    "consent_type": "THIRD_PARTY",
    "resource_type": "slack_integration",
    "is_granted": true,
    "granted_at": "2026-02-03T10:30:00Z",
    "version": 1
  }
}
```

#### List User Consents
```
GET /api/v1/integration/consents
```

**Query Parameters**:
```
consent_type: string (optional)
is_granted: boolean (optional)
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "consent_uuid",
      "consent_type": "THIRD_PARTY",
      "resource_type": "slack_integration",
      "resource_id": "oauth_connection_uuid",
      "is_granted": true,
      "granted_at": "2026-02-03T10:30:00Z",
      "version": 1
    }
  ]
}
```

#### Revoke Consent
```
DELETE /api/v1/integration/consents/{consent_id}
```

**Response**: 204 No Content

#### Get Compliance Status
```
GET /api/v1/integration/consents/status
```

**Response**:
```json
{
  "success": true,
  "data": {
    "user_id": "user_uuid",
    "total_consents": 5,
    "granted_consents": 3,
    "revoked_consents": 2,
    "compliance_status": "compliant",
    "consents": [
      {
        "type": "THIRD_PARTY",
        "count": 2,
        "granted": 1,
        "revoked": 1
      }
    ]
  }
}
```

### 💚 Health Check

#### Integration Status
```
GET /api/v1/integration/status
```

**Response**:
```json
{
  "success": true,
  "data": {
    "api_tokens": {
      "status": "operational",
      "active_tokens": 15
    },
    "webhooks": {
      "status": "operational",
      "active_webhooks": 8,
      "pending_deliveries": 3
    },
    "oauth": {
      "status": "operational",
      "active_connections": 12
    },
    "plugins": {
      "status": "operational",
      "installed_plugins": 5
    }
  }
}
```

#### Health Check
```
GET /api/v1/integration/health
```

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2026-02-03T10:30:00Z",
    "components": {
      "database": "healthy",
      "redis": "healthy",
      "email_service": "healthy"
    }
  }
}
```

---

## Rate Limiting Headers

All responses include rate limit headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1612360200
X-RateLimit-Tier: pro
```

---

## Webhook Event Types

| Event | Payload | Trigger |
|-------|---------|---------|
| `task.created` | Task data | New task created |
| `task.updated` | Task data + changes | Task modified |
| `task.completed` | Task data | Task marked complete |
| `task.deleted` | Task ID | Task deleted |
| `project.created` | Project data | New project created |
| `project.updated` | Project data + changes | Project modified |
| `project.archived` | Project data | Project archived |
| `comment.created` | Comment data | New comment posted |
| `user.joined` | User data | User joined workspace |

---

## SDK Examples

### Node.js/JavaScript
```javascript
const PronaFlow = require('@pronaflow/sdk');

const client = new PronaFlow({
  apiToken: 'prona_abc123def456...',
  baseUrl: 'https://api.pronaflow.com'
});

// Create task
const task = await client.tasks.create({
  title: 'Design UI',
  priority: 'high',
  project_id: 'project_uuid'
});

// List projects
const projects = await client.projects.list();

// Subscribe to webhook
const webhook = await client.webhooks.create({
  url: 'https://your-app.com/webhook',
  events: ['task.created', 'task.completed']
});
```

### Python
```python
from pronaflow import PronaFlow

client = PronaFlow(
    api_token='prona_abc123def456...',
    base_url='https://api.pronaflow.com'
)

# Create task
task = client.tasks.create(
    title='Design UI',
    priority='high',
    project_id='project_uuid'
)

# List projects
projects = client.projects.list()
```

---

## API Changelog

### Version 1.2 (February 3, 2026)
- ✅ Added Module 7: Event-Driven Notifications (8 endpoints)
- ✅ Added Module 8: Archiving & Compliance (12 endpoints)
- ✅ Added Module 9: Personalization & UX (6 endpoints)
- ✅ Added Module 11: Analytics & Reporting (15 endpoints)
- ✅ Added Module 12: Integration Ecosystem (40+ endpoints)
- ✅ Enhanced rate limiting with tiered system
- ✅ Added webhook event types reference
- ✅ Added SDK examples

### Version 1.1
- Initial documentation for Modules 1-6

---

## Support & Resources

- **API Status**: https://status.pronaflow.com
- **Documentation**: https://docs.pronaflow.com
- **GitHub Discussions**: https://github.com/pronaflow/api
- **Slack Community**: Join our workspace for questions
- **Email Support**: api-support@pronaflow.com

---

**Last Updated**: February 3, 2026  
**API Version**: v1  
**Documentation Version**: 1.2  
**Status**: ✅ Production Ready
