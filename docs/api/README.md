# API V1 Endpoints Documentation

This directory contains endpoint documentation organized by module and resource.

## Structure

- **auth/** - Authentication endpoints
- **workspaces/** - Workspace management
- **projects/** - Project management
- **tasks/** - Task and execution endpoints
- **reports/** - Reporting and analytics
- **admin/** - Administrative endpoints

## General Guidelines

- All endpoints require authentication (except public endpoints)
- Use Bearer tokens in Authorization header
- All timestamps are in ISO 8601 format
- Pagination uses limit/offset pattern
- Errors use consistent error response format

## Rate Limits

- Default: 100 requests/minute
- Auth: 5 failed attempts → 15-minute lockout
- Public: 30 requests/minute
