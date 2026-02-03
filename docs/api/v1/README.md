# API V1 Endpoint Reference

Comprehensive reference for all API v1 endpoints organized by resource.

## Available Resources

- **Authentication** - User login, registration, token refresh
- **Workspaces** - Organization management
- **Projects** - Project lifecycle management
- **Tasks** - Task execution and management
- **Users** - User profiles and management
- **Reports** - Analytics and reporting
- **Admin** - System administration

## Base URL

```
/api/v1
```

## Common Query Parameters

- `limit` - Number of items to return (default: 20, max: 100)
- `offset` - Items to skip (default: 0)
- `sort` - Sort field (e.g., -created_at for descending)
- `filter` - Filter conditions (varies by resource)

## Response Format

All responses use standard JSON format with metadata.
