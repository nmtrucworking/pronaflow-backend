# PronaFlow API Documentation - Version 1.3
**Modules: 1-16 | Last Updated: February 3, 2026**

---

## 📋 Table of Contents
1. [Base Information](#base-information)
2. [Authentication & Security](#authentication--security)
3. [Common Patterns](#common-patterns)
4. [Module 1: Identity & Access Management (IAM)](#module-1-identity--access-management-iam)
5. [Module 2: Workspace Management](#module-2-workspace-management)
6. [Module 3: Project Lifecycle Management](#module-3-project-lifecycle-management)
7. [Module 4: Task Execution & Orchestration](#module-4-task-execution--orchestration)
8. [Module 5: Temporal Planning & Scheduling](#module-5-temporal-planning--scheduling)
9. [Module 6: Unified Collaboration Hub](#module-6-unified-collaboration-hub)
10. [Module 8: Archive & Data Management](#module-8-archive--data-management)
11. [Module 9: Reports & Analytics](#module-9-reports--analytics)
12. [Module 10-12: Integration & Webhooks](#module-10-12-integration--webhooks)
13. [Module 13: Subscription & Billing Management](#module-13-subscription--billing-management)
14. [Module 14: System Administration](#module-14-system-administration)
15. [Module 15: Help Center & Knowledge Base](#module-15-help-center--knowledge-base)
16. [Module 16: User Onboarding & Adoption](#module-16-user-onboarding--adoption)
17. [Common Response Formats](#common-response-formats)
18. [Error Handling](#error-handling)
19. [Rate Limiting & Quotas](#rate-limiting--quotas)
20. [Webhooks](#webhooks)
21. [Testing & Examples](#testing--examples)

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

### Environment Configuration
Create `.env` file in project root:
```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/pronaflow
SECRET_KEY=your-secret-key-change-in-production
DEBUG=False
APP_VERSION=1.0.0
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## Authentication & Security

### Overview
PronaFlow uses **JWT (JSON Web Token)** for API authentication with optional **Multi-Factor Authentication (MFA)**.

### Token Structure
```
Header: {
  "alg": "HS256",
  "typ": "JWT"
}

Payload: {
  "sub": "user_id",
  "email": "user@example.com",
  "username": "username",
  "roles": ["user", "admin"],
  "iat": 1699564800,
  "exp": 1699576800
}

Signature: HMACSHA256(...)
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

### Security Requirements
- **Password Minimum**: 12 characters
- **Password Strength**: Uppercase, lowercase, digit, special character
- **HTTPS**: Required in production
- **CORS**: Restricted to allowed origins

### Rate Limiting
- **General**: 100 requests/minute per IP
- **Authentication**: 5 failed attempts → 15-minute lockout
- **Public Endpoints**: 30 requests/minute

---

## Common Patterns

### Pagination
All list endpoints support pagination using query parameters:

**Query Parameters**:
```
?page=1              # Page number (default: 1)
&page_size=20        # Items per page (default: 20, max: 100)
```

**Response Format**:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### Filtering
Use query parameters for filtering:

```
?status=active                    # Filter by status
&created_after=2024-01-01        # Date range
&created_before=2024-12-31
&search=keyword                   # Search in text fields
&tag=urgent                       # Filter by tags
```

### Sorting
Use `sort` parameter with field name and direction:

```
?sort=created_at                 # Ascending
?sort=-created_at                # Descending (prefix with -)
?sort=priority,-created_at       # Multiple fields
```

### Field Selection
Select specific fields to reduce payload size:

```
?fields=id,name,status           # Only include specified fields
?exclude=description,metadata    # Exclude specific fields
```

### Expansion
Include related resources in response:

```
?expand=creator,assignees        # Include related objects
?expand=project.workspace        # Nested expansion
```

### Date/Time Format
All timestamps use **ISO 8601** format:
```
2024-01-15T10:30:00Z             # UTC timezone
2024-01-15T10:30:00+07:00        # With timezone offset
```

### Bulk Operations
Some endpoints support bulk operations:

**Request**:
```json
{
  "ids": ["id1", "id2", "id3"],
  "action": "update",
  "data": {
    "status": "completed"
  }
}
```

**Response**:
```json
{
  "success_count": 2,
  "failed_count": 1,
  "results": [
    {"id": "id1", "status": "success"},
    {"id": "id2", "status": "success"},
    {"id": "id3", "status": "failed", "error": "Permission denied"}
  ]
}
```

---

## Module 1: Identity & Access Management (IAM)

### Overview
Handles user registration, authentication, session management, and multi-factor authentication.

### Endpoints

#### User Registration
```
POST /api/v1/auth/register
```
**Description**: Register a new user account

**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!@#",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "status": "pending_verification",
  "email_verified_at": null,
  "created_at": "2024-01-15T10:30:00Z",
  "roles": []
}
```

**Errors**:
- `400`: Email already exists / Invalid password strength
- `422`: Validation error

---

#### User Login
```
POST /api/v1/auth/login
```
**Description**: Login with email and password

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!@#"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "johndoe",
    "roles": ["user"]
  },
  "mfa_required": false
}
```

**Errors**:
- `401`: Invalid credentials
- `403`: Account locked (too many attempts)
- `403`: Email not verified

---

#### Verify Email
```
POST /api/v1/auth/verify-email
```
**Description**: Verify email with token from verification email

**Request Body**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "message": "Email verified successfully"
}
```

---

#### Resend Verification Email
```
POST /api/v1/auth/resend-verification
```
**Description**: Resend email verification link

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "message": "Verification email sent"
}
```

---

#### Get Current User
```
GET /api/v1/auth/me
```
**Description**: Get current authenticated user info

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "status": "active",
  "email_verified_at": "2024-01-15T10:35:00Z",
  "mfa_enabled": false,
  "roles": ["user"],
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors**:
- `401`: Unauthorized / Invalid token
- `404`: User not found

---

#### Logout
```
POST /api/v1/auth/logout
```
**Description**: Logout current session

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

---

#### Multi-Factor Authentication (MFA)

##### Enable MFA
```
POST /api/v1/auth/mfa/enable
```
**Description**: Enable multi-factor authentication

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "secret": "JBSWY3DPEBLW64TMMQ======",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHQAAAB0CAY...",
  "backup_codes": [
    "12345678",
    "87654321",
    "11223344",
    "55667788",
    "99887766"
  ]
}
```

---

##### Confirm MFA
```
POST /api/v1/auth/mfa/confirm
```
**Description**: Confirm MFA setup with TOTP code

**Request Body**:
```json
{
  "totp_code": "123456"
}
```

**Response** (200 OK):
```json
{
  "message": "MFA enabled successfully",
  "mfa_enabled": true
}
```

---

##### Verify MFA Code (Login)
```
POST /api/v1/auth/mfa/verify
```
**Description**: Verify TOTP code during login

**Request Body**:
```json
{
  "email": "user@example.com",
  "totp_code": "123456"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

##### Disable MFA
```
POST /api/v1/auth/mfa/disable
```
**Description**: Disable multi-factor authentication

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "password": "SecurePass123!@#"
}
```

**Response** (200 OK):
```json
{
  "message": "MFA disabled successfully"
}
```

---

##### Get Backup Codes
```
GET /api/v1/auth/mfa/backup-codes
```
**Description**: Get MFA backup codes

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "backup_codes": [
    "12345678",
    "87654321",
    "11223344",
    "55667788",
    "99887766"
  ]
}
```

---

#### Session Management

##### Get All Sessions
```
GET /api/v1/auth/sessions
```
**Description**: Get list of all active sessions for current user

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440001",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "ip_address": "192.168.1.100",
      "device": "Chrome on Windows",
      "location": "Ho Chi Minh, Vietnam",
      "created_at": "2024-01-15T10:30:00Z",
      "last_activity": "2024-01-15T11:20:00Z",
      "is_current": true
    }
  ],
  "total": 1
}
```

---

##### Revoke Session
```
POST /api/v1/auth/sessions/revoke
```
**Description**: Revoke a specific session

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Response** (200 OK):
```json
{
  "message": "Session revoked successfully"
}
```

---

##### Revoke All Sessions
```
POST /api/v1/auth/sessions/revoke-all
```
**Description**: Revoke all sessions except current

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "message": "All sessions revoked successfully",
  "revoked_count": 5
}
```

---

#### Password Management

##### Request Password Reset
```
POST /api/v1/auth/password-reset
```
**Description**: Request password reset email

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "message": "Password reset email sent"
}
```

---

##### Confirm Password Reset
```
POST /api/v1/auth/password-reset/confirm
```
**Description**: Confirm password reset with token

**Request Body**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "new_password": "NewSecurePass123!@#"
}
```

**Response** (200 OK):
```json
{
  "message": "Password reset successfully"
}
```

---

##### Change Password
```
POST /api/v1/auth/password-change
```
**Description**: Change password for authenticated user

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "current_password": "SecurePass123!@#",
  "new_password": "NewSecurePass123!@#"
}
```

**Response** (200 OK):
```json
{
  "message": "Password changed successfully"
}
```

---

## Module 2: Workspace Management

### Overview
Manages workspaces, team members, invitations, and workspace settings.

### Endpoints

#### Create Workspace
```
POST /api/v1/workspaces
```
**Description**: Create a new workspace

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "name": "My Team",
  "description": "Our development team workspace",
  "workspace_type": "team",
  "logo_url": "https://example.com/logo.png"
}
```

**Response** (201 Created):
```json
{
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Team",
  "description": "Our development team workspace",
  "workspace_type": "team",
  "owner_id": "550e8400-e29b-41d4-a716-446655440001",
  "members_count": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

#### List Workspaces
```
GET /api/v1/workspaces
```
**Description**: List all workspaces for current user

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `sort_by`: Sort field (name, created_at, updated_at)
- `sort_order`: asc or desc

**Response** (200 OK):
```json
{
  "workspaces": [
    {
      "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "My Team",
      "description": "Our development team workspace",
      "workspace_type": "team",
      "owner_id": "550e8400-e29b-41d4-a716-446655440001",
      "members_count": 5,
      "role": "owner",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

---

#### Get Workspace
```
GET /api/v1/workspaces/{id}
```
**Description**: Get workspace details

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Workspace ID

**Response** (200 OK):
```json
{
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Team",
  "description": "Our development team workspace",
  "workspace_type": "team",
  "owner_id": "550e8400-e29b-41d4-a716-446655440001",
  "members_count": 5,
  "role": "owner",
  "settings": {
    "allow_public_access": false,
    "allow_member_invitations": true
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

#### Update Workspace
```
PUT /api/v1/workspaces/{id}
```
**Description**: Update workspace details

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Workspace ID

**Request Body**:
```json
{
  "name": "Updated Team Name",
  "description": "Updated description",
  "logo_url": "https://example.com/new-logo.png"
}
```

**Response** (200 OK):
```json
{
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Team Name",
  "description": "Updated description",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Errors**:
- `403`: Not owner or admin
- `404`: Workspace not found

---

#### Delete Workspace
```
DELETE /api/v1/workspaces/{id}
```
**Description**: Soft delete workspace (can be restored)

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Workspace ID

**Response** (200 OK):
```json
{
  "message": "Workspace deleted successfully"
}
```

**Errors**:
- `403`: Not owner
- `404`: Workspace not found

---

#### List Workspace Members
```
GET /api/v1/workspaces/{id}/members
```
**Description**: Get list of workspace members

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Workspace ID

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `role`: Filter by role (owner, admin, member)

**Response** (200 OK):
```json
{
  "members": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440001",
      "username": "johndoe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "role": "owner",
      "joined_at": "2024-01-15T10:30:00Z",
      "last_activity": "2024-01-15T11:20:00Z"
    },
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440002",
      "username": "janedoe",
      "email": "jane@example.com",
      "full_name": "Jane Doe",
      "role": "member",
      "joined_at": "2024-01-15T10:35:00Z",
      "last_activity": "2024-01-15T11:10:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 2,
    "total_pages": 1
  }
}
```

---

#### Add Workspace Member
```
POST /api/v1/workspaces/{id}/members
```
**Description**: Add a new member to workspace

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Workspace ID

**Request Body**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "role": "member"
}
```

**Response** (201 Created):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "username": "janedoe",
  "email": "jane@example.com",
  "role": "member",
  "joined_at": "2024-01-15T11:30:00Z"
}
```

**Errors**:
- `403`: Not owner or admin
- `409`: User already member

---

#### Update Member Role
```
PUT /api/v1/workspaces/{id}/members/{user_id}
```
**Description**: Update member role

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Workspace ID
- `user_id`: User ID

**Request Body**:
```json
{
  "role": "admin"
}
```

**Response** (200 OK):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "role": "admin",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

---

#### Remove Member
```
DELETE /api/v1/workspaces/{id}/members/{user_id}
```
**Description**: Remove member from workspace

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Workspace ID
- `user_id`: User ID

**Response** (200 OK):
```json
{
  "message": "Member removed successfully"
}
```

---

#### Send Invitation
```
POST /api/v1/workspaces/{id}/invitations
```
**Description**: Send invitation to join workspace

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Workspace ID

**Request Body**:
```json
{
  "email": "newuser@example.com",
  "role": "member",
  "message": "Welcome to our team!"
}
```

**Response** (201 Created):
```json
{
  "invitation_id": "550e8400-e29b-41d4-a716-446655440003",
  "email": "newuser@example.com",
  "status": "pending",
  "role": "member",
  "created_at": "2024-01-15T11:50:00Z",
  "expires_at": "2024-02-15T11:50:00Z"
}
```

---

#### List Workspace Invitations
```
GET /api/v1/workspaces/{id}/invitations
```
**Description**: Get list of pending invitations

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Workspace ID

**Query Parameters**:
- `status`: pending, accepted, rejected

**Response** (200 OK):
```json
{
  "invitations": [
    {
      "invitation_id": "550e8400-e29b-41d4-a716-446655440003",
      "email": "newuser@example.com",
      "status": "pending",
      "role": "member",
      "created_at": "2024-01-15T11:50:00Z",
      "expires_at": "2024-02-15T11:50:00Z"
    }
  ]
}
```

---

#### Accept Workspace Invitation
```
POST /api/v1/workspaces/invitations/accept
```
**Description**: Accept workspace invitation

**Query Parameters**:
- `token`: Invitation token (from email link)

**Response** (200 OK):
```json
{
  "message": "Invitation accepted successfully",
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "workspace_name": "My Team"
}
```

---

#### Cancel Invitation
```
DELETE /api/v1/workspaces/{id}/invitations/{inv_id}
```
**Description**: Cancel pending invitation

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Workspace ID
- `inv_id`: Invitation ID

**Response** (200 OK):
```json
{
  "message": "Invitation cancelled"
}
```

---

#### Get Last Accessed Workspace
```
GET /api/v1/workspaces/me/last-accessed
```
**Description**: Get user's last accessed workspace

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Team",
  "accessed_at": "2024-01-15T11:50:00Z"
}
```

---

#### Get Workspace Settings
```
GET /api/v1/workspaces/{id}/settings
```
**Description**: Get workspace settings

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Workspace ID

**Response** (200 OK):
```json
{
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "settings": {
    "allow_public_access": false,
    "allow_member_invitations": true,
    "default_task_status": "todo",
    "timezone": "Asia/Ho_Chi_Minh"
  }
}
```

---

#### Update Workspace Settings
```
PUT /api/v1/workspaces/{id}/settings
```
**Description**: Update workspace settings

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "allow_public_access": true,
  "default_task_status": "todo",
  "timezone": "Asia/Ho_Chi_Minh"
}
```

**Response** (200 OK):
```json
{
  "message": "Settings updated successfully"
}
```

---

## Module 3: Project Lifecycle Management

### Overview
Manages projects, templates, baselines, change requests, and project health metrics.

### Endpoints

#### Create Project
```
POST /api/v1/projects
```
**Description**: Create a new project

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Website Redesign",
  "description": "Complete redesign of company website",
  "project_type": "web_development",
  "start_date": "2024-02-01",
  "end_date": "2024-06-30",
  "budget": 50000,
  "risk_level": "medium"
}
```

**Response** (201 Created):
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Website Redesign",
  "description": "Complete redesign of company website",
  "project_type": "web_development",
  "status": "active",
  "start_date": "2024-02-01",
  "end_date": "2024-06-30",
  "budget": 50000,
  "risk_level": "medium",
  "owner_id": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2024-01-15T12:00:00Z"
}
```

---

#### List Projects
```
GET /api/v1/projects
```
**Description**: List projects with filters

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `workspace_id`: Filter by workspace (required in some cases)
- `status`: active, completed, archived, cancelled
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `sort_by`: name, created_at, start_date, end_date

**Response** (200 OK):
```json
{
  "projects": [
    {
      "project_id": "550e8400-e29b-41d4-a716-446655440010",
      "name": "Website Redesign",
      "status": "active",
      "owner_id": "550e8400-e29b-41d4-a716-446655440001",
      "start_date": "2024-02-01",
      "end_date": "2024-06-30",
      "progress": 35,
      "members_count": 5,
      "created_at": "2024-01-15T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 10,
    "total_pages": 1
  }
}
```

---

#### Get Project Details
```
GET /api/v1/projects/{id}
```
**Description**: Get project full details

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Project ID

**Response** (200 OK):
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "name": "Website Redesign",
  "description": "Complete redesign of company website",
  "project_type": "web_development",
  "status": "active",
  "start_date": "2024-02-01",
  "end_date": "2024-06-30",
  "budget": 50000,
  "spent": 15000,
  "risk_level": "medium",
  "owner_id": "550e8400-e29b-41d4-a716-446655440001",
  "members_count": 5,
  "tasks_count": 25,
  "tasks_completed": 8,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

---

#### Update Project
```
PATCH /api/v1/projects/{id}
```
**Description**: Update project details

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "name": "Website Redesign v2",
  "description": "Updated description",
  "end_date": "2024-07-31",
  "budget": 60000
}
```

**Response** (200 OK):
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "name": "Website Redesign v2",
  "updated_at": "2024-01-15T12:15:00Z"
}
```

---

#### Update Project Status
```
PATCH /api/v1/projects/{id}/status
```
**Description**: Update project status

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "status": "completed",
  "completion_date": "2024-06-30"
}
```

**Response** (200 OK):
```json
{
  "status": "completed",
  "completion_date": "2024-06-30"
}
```

---

#### Delete Project
```
DELETE /api/v1/projects/{id}
```
**Description**: Soft delete project

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "message": "Project deleted successfully"
}
```

---

#### Clone Project
```
POST /api/v1/projects/{id}/clone
```
**Description**: Clone project with all templates

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "new_name": "Website Redesign - Phase 2",
  "copy_tasks": true,
  "copy_members": false
}
```

**Response** (201 Created):
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440011",
  "name": "Website Redesign - Phase 2",
  "message": "Project cloned successfully"
}
```

---

#### Project Members Management

##### List Project Members
```
GET /api/v1/projects/{id}/members
```

**Response** (200 OK):
```json
{
  "members": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440001",
      "username": "johndoe",
      "email": "john@example.com",
      "role": "owner",
      "joined_at": "2024-01-15T12:00:00Z"
    }
  ]
}
```

---

##### Add Project Member
```
POST /api/v1/projects/{id}/members
```

**Request Body**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "role": "member"
}
```

**Response** (201 Created):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "role": "member",
  "joined_at": "2024-01-15T12:20:00Z"
}
```

---

##### Update Member Role
```
PATCH /api/v1/projects/{id}/members/{user_id}
```

**Request Body**:
```json
{
  "role": "admin"
}
```

**Response** (200 OK):
```json
{
  "role": "admin"
}
```

---

##### Remove Member
```
DELETE /api/v1/projects/{id}/members/{user_id}
```

**Response** (200 OK):
```json
{
  "message": "Member removed from project"
}
```

---

#### Project Templates

##### Create Template
```
POST /api/v1/projects/templates
```

**Request Body**:
```json
{
  "name": "Web Development Template",
  "description": "Standard template for web development projects",
  "structure": {
    "phases": [
      {
        "name": "Planning",
        "duration_days": 10
      }
    ]
  }
}
```

**Response** (201 Created):
```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440020",
  "name": "Web Development Template",
  "created_at": "2024-01-15T12:30:00Z"
}
```

---

##### List Templates
```
GET /api/v1/projects/templates
```

**Response** (200 OK):
```json
{
  "templates": [
    {
      "template_id": "550e8400-e29b-41d4-a716-446655440020",
      "name": "Web Development Template",
      "description": "Standard template for web development projects",
      "created_at": "2024-01-15T12:30:00Z"
    }
  ]
}
```

---

##### Create Project from Template
```
POST /api/v1/projects/from-template
```

**Request Body**:
```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440020",
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_name": "New Web Development Project",
  "start_date": "2024-02-15"
}
```

**Response** (201 Created):
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440012",
  "name": "New Web Development Project",
  "message": "Project created from template"
}
```

---

#### Change Requests

##### Create Change Request
```
POST /api/v1/projects/{id}/change-requests
```

**Request Body**:
```json
{
  "title": "Update project timeline",
  "description": "Need to extend deadline by 2 weeks",
  "scope": "timeline_change",
  "impact_analysis": "Low impact - affects only deadline",
  "requested_changes": {
    "end_date": "2024-07-14"
  }
}
```

**Response** (201 Created):
```json
{
  "change_request_id": "550e8400-e29b-41d4-a716-446655440030",
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "status": "pending",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2024-01-15T13:00:00Z"
}
```

---

##### List Change Requests
```
GET /api/v1/projects/{id}/change-requests
```

**Query Parameters**:
- `status`: pending, approved, rejected

**Response** (200 OK):
```json
{
  "change_requests": [
    {
      "change_request_id": "550e8400-e29b-41d4-a716-446655440030",
      "status": "pending",
      "title": "Update project timeline",
      "created_by": "johndoe",
      "created_at": "2024-01-15T13:00:00Z"
    }
  ]
}
```

---

##### Approve/Reject Change Request
```
PATCH /api/v1/projects/{id}/change-requests/{cr_id}/approve
```

**Request Body**:
```json
{
  "approved": true,
  "reviewer_notes": "Changes are acceptable"
}
```

**Response** (200 OK):
```json
{
  "change_request_id": "550e8400-e29b-41d4-a716-446655440030",
  "status": "approved",
  "approved_at": "2024-01-15T13:15:00Z"
}
```

---

#### Project Metrics & Health
```
GET /api/v1/projects/{id}/metrics
```

**Response** (200 OK):
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "health_status": "amber",
  "metrics": {
    "schedule_health": {
      "status": "amber",
      "progress": 35,
      "on_track": true
    },
    "budget_health": {
      "status": "green",
      "spent_percentage": 30,
      "spent": 15000
    },
    "resource_health": {
      "status": "green",
      "utilization": 75
    }
  }
}
```

---

## Module 4: Task Execution & Orchestration

### Overview
Manages tasks, subtasks, task lists, dependencies, comments, and time tracking.

### Endpoints

#### Create Task List
```
POST /api/v1/tasks/lists
```
**Description**: Create a new task list

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "name": "Frontend Tasks",
  "description": "All frontend development tasks",
  "order": 1
}
```

**Response** (201 Created):
```json
{
  "task_list_id": "550e8400-e29b-41d4-a716-446655440040",
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "name": "Frontend Tasks",
  "description": "All frontend development tasks",
  "order": 1,
  "tasks_count": 0,
  "created_at": "2024-01-15T13:30:00Z"
}
```

---

#### List Task Lists
```
GET /api/v1/tasks/lists
```
**Description**: List all task lists

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `project_id`: Filter by project (required)
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

**Response** (200 OK):
```json
{
  "task_lists": [
    {
      "task_list_id": "550e8400-e29b-41d4-a716-446655440040",
      "project_id": "550e8400-e29b-41d4-a716-446655440010",
      "name": "Frontend Tasks",
      "tasks_count": 5,
      "completed_count": 2,
      "order": 1,
      "created_at": "2024-01-15T13:30:00Z"
    }
  ]
}
```

---

#### Get Task List
```
GET /api/v1/tasks/lists/{list_id}
```

**Response** (200 OK):
```json
{
  "task_list_id": "550e8400-e29b-41d4-a716-446655440040",
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "name": "Frontend Tasks",
  "description": "All frontend development tasks",
  "tasks_count": 5,
  "completed_count": 2,
  "created_at": "2024-01-15T13:30:00Z"
}
```

---

#### Update Task List
```
PATCH /api/v1/tasks/lists/{list_id}
```

**Request Body**:
```json
{
  "name": "Updated Frontend Tasks",
  "description": "Updated description"
}
```

**Response** (200 OK):
```json
{
  "task_list_id": "550e8400-e29b-41d4-a716-446655440040",
  "name": "Updated Frontend Tasks",
  "updated_at": "2024-01-15T13:45:00Z"
}
```

---

#### Delete Task List
```
DELETE /api/v1/tasks/lists/{list_id}
```

**Query Parameters**:
- `force`: true to force delete with tasks

**Response** (200 OK):
```json
{
  "message": "Task list deleted successfully"
}
```

---

#### Create Task
```
POST /api/v1/tasks
```
**Description**: Create a new task

**Request Body**:
```json
{
  "task_list_id": "550e8400-e29b-41d4-a716-446655440040",
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "title": "Design homepage mockup",
  "description": "Create high-fidelity mockup for homepage",
  "status": "todo",
  "priority": "high",
  "assigned_to": "550e8400-e29b-41d4-a716-446655440002",
  "due_date": "2024-02-15",
  "estimated_hours": 8,
  "tags": ["design", "frontend"]
}
```

**Response** (201 Created):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440050",
  "task_list_id": "550e8400-e29b-41d4-a716-446655440040",
  "title": "Design homepage mockup",
  "status": "todo",
  "priority": "high",
  "assigned_to": "550e8400-e29b-41d4-a716-446655440002",
  "due_date": "2024-02-15",
  "estimated_hours": 8,
  "actual_hours": 0,
  "created_at": "2024-01-15T14:00:00Z"
}
```

---

#### List Tasks
```
GET /api/v1/tasks
```
**Description**: List tasks with filters

**Query Parameters**:
- `project_id`: Filter by project
- `task_list_id`: Filter by task list
- `status`: todo, in_progress, in_review, completed
- `priority`: low, medium, high, critical
- `assigned_to`: Filter by assignee
- `due_date_from`: Start date filter
- `due_date_to`: End date filter
- `page`: Page number
- `page_size`: Items per page
- `sort_by`: title, due_date, priority, created_at

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440050",
      "title": "Design homepage mockup",
      "status": "todo",
      "priority": "high",
      "assigned_to": "janedoe",
      "due_date": "2024-02-15",
      "estimated_hours": 8,
      "progress": 0,
      "created_at": "2024-01-15T14:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 15,
    "total_pages": 1
  }
}
```

---

#### Get Task Details
```
GET /api/v1/tasks/{task_id}
```

**Response** (200 OK):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440050",
  "task_list_id": "550e8400-e29b-41d4-a716-446655440040",
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "title": "Design homepage mockup",
  "description": "Create high-fidelity mockup for homepage",
  "status": "todo",
  "priority": "high",
  "assigned_to": "550e8400-e29b-41d4-a716-446655440002",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "due_date": "2024-02-15",
  "estimated_hours": 8,
  "actual_hours": 0,
  "progress": 0,
  "tags": ["design", "frontend"],
  "dependencies": [],
  "subtasks_count": 0,
  "comments_count": 0,
  "created_at": "2024-01-15T14:00:00Z",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

---

#### Update Task
```
PATCH /api/v1/tasks/{task_id}
```

**Request Body**:
```json
{
  "title": "Design homepage mockup - Updated",
  "description": "Create high-fidelity mockup for homepage with dark mode support",
  "priority": "critical",
  "due_date": "2024-02-14",
  "estimated_hours": 12
}
```

**Response** (200 OK):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440050",
  "title": "Design homepage mockup - Updated",
  "updated_at": "2024-01-15T14:15:00Z"
}
```

---

#### Update Task Status
```
PATCH /api/v1/tasks/{task_id}/status
```

**Request Body**:
```json
{
  "status": "in_progress",
  "started_at": "2024-01-15T14:30:00Z"
}
```

**Response** (200 OK):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440050",
  "status": "in_progress",
  "started_at": "2024-01-15T14:30:00Z"
}
```

---

#### Delete Task
```
DELETE /api/v1/tasks/{task_id}
```

**Response** (200 OK):
```json
{
  "message": "Task deleted successfully"
}
```

---

#### Move Task
```
POST /api/v1/tasks/{task_id}/move
```

**Request Body**:
```json
{
  "task_list_id": "550e8400-e29b-41d4-a716-446655440041",
  "position": 1
}
```

**Response** (200 OK):
```json
{
  "message": "Task moved successfully"
}
```

---

#### Subtasks

##### Create Subtask
```
POST /api/v1/tasks/{task_id}/subtasks
```

**Request Body**:
```json
{
  "title": "Create wireframes",
  "description": "Create low-fidelity wireframes",
  "status": "todo",
  "assigned_to": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Response** (201 Created):
```json
{
  "subtask_id": "550e8400-e29b-41d4-a716-446655440060",
  "task_id": "550e8400-e29b-41d4-a716-446655440050",
  "title": "Create wireframes",
  "status": "todo",
  "created_at": "2024-01-15T14:45:00Z"
}
```

---

##### List Subtasks
```
GET /api/v1/tasks/{task_id}/subtasks
```

**Response** (200 OK):
```json
{
  "subtasks": [
    {
      "subtask_id": "550e8400-e29b-41d4-a716-446655440060",
      "title": "Create wireframes",
      "status": "todo",
      "assigned_to": "janedoe"
    }
  ]
}
```

---

#### Task Comments

##### Create Comment
```
POST /api/v1/tasks/{task_id}/comments
```

**Request Body**:
```json
{
  "content": "Started working on the design",
  "mentions": ["user_id1", "user_id2"]
}
```

**Response** (201 Created):
```json
{
  "comment_id": "550e8400-e29b-41d4-a716-446655440070",
  "task_id": "550e8400-e29b-41d4-a716-446655440050",
  "content": "Started working on the design",
  "author": "johndoe",
  "created_at": "2024-01-15T15:00:00Z"
}
```

---

##### List Comments
```
GET /api/v1/tasks/{task_id}/comments
```

**Response** (200 OK):
```json
{
  "comments": [
    {
      "comment_id": "550e8400-e29b-41d4-a716-446655440070",
      "content": "Started working on the design",
      "author": "johndoe",
      "created_at": "2024-01-15T15:00:00Z"
    }
  ]
}
```

---

#### Task Attachments

##### Upload File
```
POST /api/v1/tasks/{task_id}/files
```

**Request Body** (multipart/form-data):
```
file: <binary_data>
```

**Response** (201 Created):
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440080",
  "filename": "mockup.png",
  "size": 1024000,
  "url": "https://api.pronaflow.com/files/550e8400-e29b-41d4-a716-446655440080",
  "uploaded_by": "johndoe",
  "uploaded_at": "2024-01-15T15:15:00Z"
}
```

---

#### Time Tracking

##### Log Time Entry
```
POST /api/v1/tasks/{task_id}/time-entries
```

**Request Body**:
```json
{
  "hours": 2.5,
  "date": "2024-01-15",
  "description": "Worked on design mockup",
  "billable": true
}
```

**Response** (201 Created):
```json
{
  "entry_id": "550e8400-e29b-41d4-a716-446655440090",
  "task_id": "550e8400-e29b-41d4-a716-446655440050",
  "hours": 2.5,
  "date": "2024-01-15",
  "logged_by": "johndoe",
  "created_at": "2024-01-15T15:30:00Z"
}
```

---

## Module 5: Temporal Planning & Scheduling

### Overview
Manages project scheduling, baselines, SLA policies, critical paths, and resource leveling.

### Endpoints

#### Plan State Management

##### Get Plan State
```
GET /api/v1/scheduling/plans/{project_id}/state
```

**Response** (200 OK):
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "state": "planning",
  "last_updated": "2024-01-15T16:00:00Z",
  "can_execute": false,
  "warnings": []
}
```

---

##### Submit Plan
```
POST /api/v1/scheduling/plans/{project_id}/submit
```

**Response** (200 OK):
```json
{
  "state": "submitted",
  "submitted_at": "2024-01-15T16:15:00Z"
}
```

---

#### Task Baselines

##### Create Task Baseline
```
POST /api/v1/scheduling/baselines
```

**Request Body**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440050",
  "baseline_start": "2024-02-01",
  "baseline_end": "2024-02-15",
  "baseline_duration_days": 14
}
```

**Response** (201 Created):
```json
{
  "baseline_id": "550e8400-e29b-41d4-a716-446655440100",
  "task_id": "550e8400-e29b-41d4-a716-446655440050",
  "baseline_start": "2024-02-01",
  "baseline_end": "2024-02-15",
  "created_at": "2024-01-15T16:30:00Z"
}
```

---

#### Scheduling Modes

##### Set Scheduling Mode
```
POST /api/v1/scheduling/scheduling-modes
```

**Request Body**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440050",
  "mode": "asap"
}
```

**Response** (201 Created):
```json
{
  "mode_id": "550e8400-e29b-41d4-a716-446655440110",
  "task_id": "550e8400-e29b-41d4-a716-446655440050",
  "mode": "asap"
}
```

---

#### SLA Management

##### Create SLA Policy
```
POST /api/v1/scheduling/sla-policies
```

**Request Body**:
```json
{
  "name": "Critical Priority SLA",
  "priority_level": "critical",
  "response_time_hours": 1,
  "resolution_time_hours": 4
}
```

**Response** (201 Created):
```json
{
  "policy_id": "550e8400-e29b-41d4-a716-446655440120",
  "name": "Critical Priority SLA",
  "response_time_hours": 1,
  "resolution_time_hours": 4,
  "created_at": "2024-01-15T16:45:00Z"
}
```

---

#### Critical Path Analysis

##### Get Critical Path
```
GET /api/v1/scheduling/critical-path/{project_id}
```

**Response** (200 OK):
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "critical_path": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440050",
      "title": "Design homepage mockup",
      "start_date": "2024-02-01",
      "end_date": "2024-02-15",
      "slack": 0
    }
  ],
  "project_completion_date": "2024-06-30"
}
```

---

#### Impact Analysis

##### Perform Impact Analysis
```
POST /api/v1/scheduling/impact-analysis/{task_id}
```

**Request Body**:
```json
{
  "proposed_end_date": "2024-02-20"
}
```

**Response** (200 OK):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440050",
  "impacts": [
    {
      "affected_task_id": "550e8400-e29b-41d4-a716-446655440051",
      "impact_type": "delayed_start",
      "days_delayed": 5
    }
  ]
}
```

---

#### Resource Leveling

##### Perform Resource Leveling
```
POST /api/v1/scheduling/resource-leveling
```

**Request Body**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "preserve_critical_path": true
}
```

**Response** (200 OK):
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "tasks_rescheduled": 5,
  "new_completion_date": "2024-07-05"
}
```

---

## Module 6: Unified Collaboration Hub

### Overview
Manages notes, approvals, public sharing, mentions, and real-time presence.

### Endpoints

#### Notes & Documentation

##### Create Note
```
POST /api/v1/collaboration/notes
```

**Request Body**:
```json
{
  "resource_type": "project",
  "resource_id": "550e8400-e29b-41d4-a716-446655440010",
  "title": "Project Implementation Plan",
  "content": "# Implementation Plan\n\n## Phase 1\nDevelopment setup and architecture",
  "is_template": false
}
```

**Response** (201 Created):
```json
{
  "note_id": "550e8400-e29b-41d4-a716-446655440130",
  "resource_type": "project",
  "resource_id": "550e8400-e29b-41d4-a716-446655440010",
  "title": "Project Implementation Plan",
  "author": "johndoe",
  "created_at": "2024-01-15T17:00:00Z",
  "updated_at": "2024-01-15T17:00:00Z"
}
```

---

##### Get Note
```
GET /api/v1/collaboration/notes/{note_id}
```

**Response** (200 OK):
```json
{
  "note_id": "550e8400-e29b-41d4-a716-446655440130",
  "title": "Project Implementation Plan",
  "content": "# Implementation Plan\n\n## Phase 1\nDevelopment setup and architecture",
  "author": "johndoe",
  "created_at": "2024-01-15T17:00:00Z",
  "versions": 2
}
```

---

##### Update Note
```
PUT /api/v1/collaboration/notes/{note_id}
```

**Request Body**:
```json
{
  "title": "Project Implementation Plan - Updated",
  "content": "# Implementation Plan\n\n## Phase 1\nDevelopment setup and architecture\n\n## Phase 2\nFeature development"
}
```

**Response** (200 OK):
```json
{
  "note_id": "550e8400-e29b-41d4-a716-446655440130",
  "title": "Project Implementation Plan - Updated",
  "updated_at": "2024-01-15T17:15:00Z",
  "version": 2
}
```

---

#### Approvals

##### Request Approval
```
POST /api/v1/collaboration/approvals
```

**Request Body**:
```json
{
  "resource_type": "change_request",
  "resource_id": "550e8400-e29b-41d4-a716-446655440030",
  "title": "Approve Project Timeline Change",
  "description": "Please review and approve the timeline extension",
  "approvers": ["550e8400-e29b-41d4-a716-446655440001"],
  "due_date": "2024-01-20"
}
```

**Response** (201 Created):
```json
{
  "approval_id": "550e8400-e29b-41d4-a716-446655440140",
  "status": "pending",
  "created_by": "johndoe",
  "created_at": "2024-01-15T17:30:00Z"
}
```

---

##### Get Approval
```
GET /api/v1/collaboration/approvals/{id}
```

**Response** (200 OK):
```json
{
  "approval_id": "550e8400-e29b-41d4-a716-446655440140",
  "title": "Approve Project Timeline Change",
  "status": "pending",
  "approvers": [
    {
      "approver_id": "550e8400-e29b-41d4-a716-446655440001",
      "username": "manager",
      "status": "pending",
      "responded_at": null
    }
  ],
  "created_at": "2024-01-15T17:30:00Z"
}
```

---

##### Update Approval Status
```
PUT /api/v1/collaboration/approvals/{id}
```

**Request Body**:
```json
{
  "status": "approved",
  "approver_notes": "Timeline change is acceptable"
}
```

**Response** (200 OK):
```json
{
  "approval_id": "550e8400-e29b-41d4-a716-446655440140",
  "status": "approved",
  "updated_at": "2024-01-15T17:45:00Z"
}
```

---

#### Public Links & Sharing

##### Create Public Link
```
POST /api/v1/collaboration/public-links
```

**Request Body**:
```json
{
  "resource_type": "project",
  "resource_id": "550e8400-e29b-41d4-a716-446655440010",
  "title": "Project Overview",
  "access_level": "view",
  "expires_at": "2024-02-15",
  "password": "optional_password"
}
```

**Response** (201 Created):
```json
{
  "link_id": "550e8400-e29b-41d4-a716-446655440150",
  "token": "abc123xyz789",
  "url": "https://pronaflow.com/share/abc123xyz789",
  "access_level": "view",
  "created_at": "2024-01-15T18:00:00Z"
}
```

---

##### Access Public Link
```
GET /api/v1/collaboration/public-links/{token}
```

**Response** (200 OK):
```json
{
  "resource_type": "project",
  "resource_id": "550e8400-e29b-41d4-a716-446655440010",
  "title": "Project Overview",
  "data": {
    "project_id": "550e8400-e29b-41d4-a716-446655440010",
    "name": "Website Redesign",
    "status": "active"
  }
}
```

---

##### Revoke Public Link
```
PUT /api/v1/collaboration/public-links/{id}/revoke
```

**Response** (200 OK):
```json
{
  "message": "Public link revoked"
}
```

---

#### User Mentions

##### Get User Mentions
```
GET /api/v1/collaboration/mentions
```

**Query Parameters**:
- `unread_only`: true to get only unread mentions

**Response** (200 OK):
```json
{
  "mentions": [
    {
      "mention_id": "550e8400-e29b-41d4-a716-446655440160",
      "mentioned_in": "comment",
      "resource_type": "task",
      "resource_id": "550e8400-e29b-41d4-a716-446655440050",
      "mentioned_by": "johndoe",
      "context": "Please review this design @janedoe",
      "created_at": "2024-01-15T18:15:00Z",
      "read": false
    }
  ]
}
```

---

##### Mark Mention as Read
```
PUT /api/v1/collaboration/mentions/{id}/read
```

**Response** (200 OK):
```json
{
  "mention_id": "550e8400-e29b-41d4-a716-446655440160",
  "read": true
}
```

---

#### User Presence

##### Update Presence
```
POST /api/v1/collaboration/presence
```

**Request Body**:
```json
{
  "resource_type": "project",
  "resource_id": "550e8400-e29b-41d4-a716-446655440010",
  "status": "online"
}
```

**Response** (200 OK):
```json
{
  "presence_id": "550e8400-e29b-41d4-a716-446655440170",
  "status": "online",
  "updated_at": "2024-01-15T18:30:00Z"
}
```

---

##### Get Active Users
```
GET /api/v1/collaboration/presence/{resource_type}/{resource_id}
```

**Response** (200 OK):
```json
{
  "active_users": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440001",
      "username": "johndoe",
      "status": "online",
      "updated_at": "2024-01-15T18:30:00Z"
    }
  ]
}
```

---

#### Search

##### Search Content
```
GET /api/v1/collaboration/search
```

**Query Parameters**:
- `q`: Search query (required)
- `resource_types`: Filter by resource types (comma-separated)
- `page`: Page number
- `page_size`: Items per page

**Response** (200 OK):
```json
{
  "results": [
    {
      "resource_type": "note",
      "resource_id": "550e8400-e29b-41d4-a716-446655440130",
      "title": "Project Implementation Plan",
      "snippet": "...Development setup and architecture...",
      "relevance": 0.95
    }
  ],
  "total": 5,
  "query": "Implementation"
}
```

---

## Common Response Formats

### Success Response
```json
{
  "data": {
    "id": "...",
    "name": "...",
    ...
  },
  "meta": {
    "timestamp": "2024-01-15T18:30:00Z",
    "version": "1.0"
  }
}
```

### List Response
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  },
  "meta": {
    "timestamp": "2024-01-15T18:30:00Z"
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request parameters",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "meta": {
    "timestamp": "2024-01-15T18:30:00Z",
    "request_id": "req_123456"
  }
}
```

---

## Error Handling

---

## Module 13: Subscription & Billing Management

**Base Path:** `/api/subscription`

### Plans
- `GET /api/subscription/plans`
- `POST /api/subscription/plans`
- `GET /api/subscription/plans/{plan_id}`
- `PATCH /api/subscription/plans/{plan_id}`

### Workspace Subscriptions
- `GET /api/subscription/workspaces/{workspace_id}/subscription`
- `POST /api/subscription/workspaces/{workspace_id}/subscription`
- `POST /api/subscription/workspaces/{workspace_id}/subscription/upgrade`
- `POST /api/subscription/workspaces/{workspace_id}/subscription/cancel`

### Usage
- `GET /api/subscription/workspaces/{workspace_id}/usage`
- `GET /api/subscription/workspaces/{workspace_id}/usage/summary`

### Clients (Freelancer)
- `GET /api/subscription/workspaces/{workspace_id}/clients`
- `POST /api/subscription/workspaces/{workspace_id}/clients`
- `GET /api/subscription/clients/{client_id}`
- `PATCH /api/subscription/clients/{client_id}`
- `DELETE /api/subscription/clients/{client_id}`

### Freelancer Invoices
- `GET /api/subscription/workspaces/{workspace_id}/invoices`
- `POST /api/subscription/workspaces/{workspace_id}/invoices`
- `GET /api/subscription/invoices/{invoice_id}`
- `PATCH /api/subscription/invoices/{invoice_id}/status`
- `POST /api/subscription/invoices/{invoice_id}/generate-pdf`

---

## Module 14: System Administration

**Base Path:** `/api/admin-system`

### Admin Users & Roles
- `POST /api/admin-system/users`
- `GET /api/admin-system/users`
- `GET /api/admin-system/users/{admin_user_id}`
- `PATCH /api/admin-system/users/{admin_user_id}`
- `POST /api/admin-system/users/{admin_user_id}/lock`
- `POST /api/admin-system/users/{admin_user_id}/unlock`

- `POST /api/admin-system/roles`
- `GET /api/admin-system/roles`
- `GET /api/admin-system/roles/{role_id}`
- `PATCH /api/admin-system/roles/{role_id}`
- `GET /api/admin-system/roles/{role_id}/permissions`
- `POST /api/admin-system/roles/{role_id}/permissions`

- `POST /api/admin-system/permissions`
- `GET /api/admin-system/permissions`
- `PATCH /api/admin-system/permissions/{permission_id}`

### Role Assignments
- `POST /api/admin-system/users/{admin_user_id}/roles`
- `POST /api/admin-system/role-assignments/{assignment_id}/approve`
- `DELETE /api/admin-system/role-assignments/{assignment_id}`
- `GET /api/admin-system/users/{admin_user_id}/roles`

### System Config & Feature Flags
- `POST /api/admin-system/config`
- `GET /api/admin-system/config`
- `GET /api/admin-system/config/{key}`
- `PATCH /api/admin-system/config/{key}`

- `POST /api/admin-system/feature-flags`
- `GET /api/admin-system/feature-flags`
- `GET /api/admin-system/feature-flags/{key}`
- `PATCH /api/admin-system/feature-flags/{key}`
- `GET /api/admin-system/feature-flags/{key}/check/{user_id}`

### Audit, Security, Change, Review
- `POST /api/admin-system/audit-logs`
- `GET /api/admin-system/audit-logs`
- `POST /api/admin-system/security-incidents`
- `GET /api/admin-system/security-incidents`
- `GET /api/admin-system/security-incidents/{incident_id}`
- `PATCH /api/admin-system/security-incidents/{incident_id}`

- `POST /api/admin-system/change-requests`
- `GET /api/admin-system/change-requests`
- `GET /api/admin-system/change-requests/{change_id}`
- `PATCH /api/admin-system/change-requests/{change_id}`
- `POST /api/admin-system/change-requests/{change_id}/approve`

- `POST /api/admin-system/access-reviews`
- `GET /api/admin-system/access-reviews`
- `GET /api/admin-system/access-reviews/{review_id}`
- `POST /api/admin-system/access-reviews/{review_id}/complete`

- `GET /api/admin-system/stats`

---

## Module 15: Help Center & Knowledge Base

**Base Path:** `/api/help-center`

### Categories & Articles
- `POST /api/help-center/categories`
- `GET /api/help-center/categories`
- `PATCH /api/help-center/categories/{category_id}`

- `POST /api/help-center/articles`
- `GET /api/help-center/articles`
- `GET /api/help-center/articles/{article_id}`
- `PATCH /api/help-center/articles/{article_id}`

### Versioning & Localization
- `POST /api/help-center/articles/{article_id}/versions`
- `POST /api/help-center/versions/{version_id}/translations`
- `GET /api/help-center/articles/{article_id}/reader`

### Contextual Help & Visibility
- `POST /api/help-center/route-mappings`
- `GET /api/help-center/route-mappings`
- `GET /api/help-center/contextual`
- `POST /api/help-center/articles/{article_id}/visibility`

### Feedback & Search
- `POST /api/help-center/articles/{article_id}/feedback`
- `GET /api/help-center/search`
- `POST /api/help-center/search/failed`

---

## Module 16: User Onboarding & Adoption

**Base Path:** `/api/onboarding`

### Survey & Persona
- `POST /api/onboarding/surveys`
- `GET /api/onboarding/surveys`
- `POST /api/onboarding/surveys/{survey_id}/questions`
- `POST /api/onboarding/responses`
- `POST /api/onboarding/persona`

### Flow & Status
- `POST /api/onboarding/flows`
- `POST /api/onboarding/flows/{flow_id}/steps`
- `GET /api/onboarding/status`
- `PATCH /api/onboarding/status`

### Tours
- `POST /api/onboarding/tours`
- `POST /api/onboarding/tours/{tour_id}/steps`

### Checklist & Rewards
- `POST /api/onboarding/checklists`
- `POST /api/onboarding/checklists/{checklist_id}/items`
- `PATCH /api/onboarding/checklist-progress`
- `POST /api/onboarding/rewards`

### Feature Beacons
- `POST /api/onboarding/beacons`
- `GET /api/onboarding/beacons`
- `POST /api/onboarding/beacons/{beacon_id}/dismiss`

---

## Module 8: Archive & Data Management

### Overview
Manage data archiving, retention policies, and data restoration.

### Endpoints

#### Archive Project
```
POST /api/v1/projects/{id}/archive
```
**Description**: Archive a project with all related data

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Project ID

**Request Body**:
```json
{
  "reason": "Project completed",
  "retention_days": 365,
  "include_tasks": true,
  "include_files": true
}
```

**Response** (200 OK):
```json
{
  "archive_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "550e8400-e29b-41d4-a716-446655440001",
  "archived_at": "2024-01-15T10:30:00Z",
  "expires_at": "2025-01-15T10:30:00Z",
  "size_bytes": 15728640,
  "items_count": 150
}
```

---

#### List Archives
```
GET /api/v1/archives
```
**Description**: List all archives in workspace

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `workspace_id`: Filter by workspace
- `type`: project, task, workspace
- `status`: active, expired, restored
- `page`, `page_size`: Pagination

**Response** (200 OK):
```json
{
  "archives": [
    {
      "archive_id": "550e8400-e29b-41d4-a716-446655440000",
      "type": "project",
      "name": "Old Project",
      "archived_at": "2024-01-15T10:30:00Z",
      "expires_at": "2025-01-15T10:30:00Z",
      "size_bytes": 15728640,
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1
  }
}
```

---

#### Restore Archive
```
POST /api/v1/archives/{id}/restore
```
**Description**: Restore archived data

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Archive ID

**Request Body**:
```json
{
  "restore_to_workspace": "550e8400-e29b-41d4-a716-446655440002",
  "restore_tasks": true,
  "restore_files": true
}
```

**Response** (200 OK):
```json
{
  "message": "Archive restored successfully",
  "restored_project_id": "550e8400-e29b-41d4-a716-446655440003",
  "restored_items": 150
}
```

---

#### Delete Archive
```
DELETE /api/v1/archives/{id}
```
**Description**: Permanently delete archived data

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Archive ID

**Response** (200 OK):
```json
{
  "message": "Archive deleted successfully"
}
```

---

## Module 9: Reports & Analytics

### Overview
Generate reports, view analytics, and track KPIs.

### Endpoints

#### Get Dashboard Stats
```
GET /api/v1/analytics/dashboard
```
**Description**: Get overview dashboard statistics

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `workspace_id`: Workspace ID
- `date_from`: Start date (ISO 8601)
- `date_to`: End date (ISO 8601)

**Response** (200 OK):
```json
{
  "summary": {
    "total_projects": 45,
    "active_projects": 12,
    "total_tasks": 567,
    "completed_tasks": 423,
    "overdue_tasks": 15,
    "team_members": 25
  },
  "charts": {
    "tasks_by_status": {
      "todo": 89,
      "in_progress": 45,
      "completed": 423,
      "blocked": 10
    },
    "tasks_completion_trend": [
      {"date": "2024-01-01", "completed": 12},
      {"date": "2024-01-02", "completed": 15}
    ]
  },
  "period": {
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-31T23:59:59Z"
  }
}
```

---

#### Generate Custom Report
```
POST /api/v1/reports/generate
```
**Description**: Generate custom report

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "name": "Monthly Progress Report",
  "type": "project_status",
  "filters": {
    "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
    "date_from": "2024-01-01",
    "date_to": "2024-01-31",
    "project_ids": ["id1", "id2"]
  },
  "format": "pdf",
  "include_charts": true
}
```

**Response** (201 Created):
```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "estimated_completion": "2024-01-15T10:35:00Z"
}
```

---

#### Get Report Status
```
GET /api/v1/reports/{id}
```
**Description**: Get report generation status

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Report ID

**Response** (200 OK):
```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Monthly Progress Report",
  "status": "completed",
  "format": "pdf",
  "file_url": "https://storage.pronaflow.com/reports/abc123.pdf",
  "file_size": 2048576,
  "generated_at": "2024-01-15T10:32:00Z",
  "expires_at": "2024-02-15T10:32:00Z"
}
```

---

#### Download Report
```
GET /api/v1/reports/{id}/download
```
**Description**: Download generated report

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Report ID

**Response**: Binary file (PDF/Excel/CSV)

---

#### List KPIs
```
GET /api/v1/analytics/kpis
```
**Description**: Get configured KPIs and their current values

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `workspace_id`: Workspace ID

**Response** (200 OK):
```json
{
  "kpis": [
    {
      "kpi_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Task Completion Rate",
      "description": "Percentage of tasks completed on time",
      "current_value": 85.5,
      "target_value": 90.0,
      "unit": "percentage",
      "trend": "up",
      "last_updated": "2024-01-15T10:30:00Z"
    },
    {
      "kpi_id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Average Task Duration",
      "description": "Average time to complete tasks",
      "current_value": 3.2,
      "target_value": 3.0,
      "unit": "days",
      "trend": "down",
      "last_updated": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## Module 10-12: Integration & Webhooks

### Overview
Manage API tokens, webhooks, OAuth integrations, and plugins.

### API Tokens

#### Create API Token
```
POST /api/v1/tokens
```
**Description**: Create a new API token

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "name": "CI/CD Integration",
  "scopes": ["tasks:read", "tasks:write", "projects:read"],
  "expires_in_days": 90
}
```

**Response** (201 Created):
```json
{
  "token_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "CI/CD Integration",
  "token": "pnf_live_1234567890abcdef",
  "scopes": ["tasks:read", "tasks:write", "projects:read"],
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-04-15T10:30:00Z"
}
```

**Note**: Token value is only shown once. Store it securely.

---

#### List API Tokens
```
GET /api/v1/tokens
```
**Description**: List all API tokens

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "tokens": [
    {
      "token_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "CI/CD Integration",
      "scopes": ["tasks:read", "tasks:write"],
      "last_used": "2024-01-15T09:00:00Z",
      "created_at": "2024-01-15T10:30:00Z",
      "expires_at": "2024-04-15T10:30:00Z",
      "status": "active"
    }
  ]
}
```

---

#### Revoke API Token
```
DELETE /api/v1/tokens/{id}
```
**Description**: Revoke an API token

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Token ID

**Response** (200 OK):
```json
{
  "message": "Token revoked successfully"
}
```

---

### Webhooks

#### Create Webhook
```
POST /api/v1/webhooks
```
**Description**: Create a webhook endpoint

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "url": "https://myapp.com/webhooks/pronaflow",
  "events": ["task.created", "task.updated", "task.completed"],
  "secret": "webhook_secret_key",
  "active": true,
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response** (201 Created):
```json
{
  "webhook_id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://myapp.com/webhooks/pronaflow",
  "events": ["task.created", "task.updated", "task.completed"],
  "secret": "webhook_secret_key",
  "active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### List Webhooks
```
GET /api/v1/webhooks
```
**Description**: List all webhooks

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `workspace_id`: Filter by workspace

**Response** (200 OK):
```json
{
  "webhooks": [
    {
      "webhook_id": "550e8400-e29b-41d4-a716-446655440000",
      "url": "https://myapp.com/webhooks/pronaflow",
      "events": ["task.created", "task.updated"],
      "active": true,
      "last_delivery": "2024-01-15T10:25:00Z",
      "success_rate": 98.5,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

#### Test Webhook
```
POST /api/v1/webhooks/{id}/test
```
**Description**: Send test event to webhook

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Webhook ID

**Response** (200 OK):
```json
{
  "delivery_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "success",
  "response_code": 200,
  "response_time_ms": 145
}
```

---

#### Get Webhook Deliveries
```
GET /api/v1/webhooks/{id}/deliveries
```
**Description**: Get webhook delivery history

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Webhook ID

**Query Parameters**:
- `page`, `page_size`: Pagination
- `status`: success, failed

**Response** (200 OK):
```json
{
  "deliveries": [
    {
      "delivery_id": "550e8400-e29b-41d4-a716-446655440001",
      "event": "task.created",
      "status": "success",
      "response_code": 200,
      "response_time_ms": 145,
      "attempts": 1,
      "delivered_at": "2024-01-15T10:25:00Z"
    },
    {
      "delivery_id": "550e8400-e29b-41d4-a716-446655440002",
      "event": "task.updated",
      "status": "failed",
      "response_code": 500,
      "response_time_ms": 2000,
      "attempts": 3,
      "last_attempt_at": "2024-01-15T10:28:00Z",
      "error": "Internal Server Error"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 2
  }
}
```

---

#### Delete Webhook
```
DELETE /api/v1/webhooks/{id}
```
**Description**: Delete a webhook

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `id`: Webhook ID

**Response** (200 OK):
```json
{
  "message": "Webhook deleted successfully"
}
```

---

### OAuth Integrations

#### List Available Integrations
```
GET /api/v1/integrations/available
```
**Description**: List available third-party integrations

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "integrations": [
    {
      "integration_id": "slack",
      "name": "Slack",
      "description": "Connect your workspace to Slack",
      "logo_url": "https://cdn.pronaflow.com/integrations/slack.png",
      "supported_features": ["notifications", "task_creation"],
      "oauth_required": true
    },
    {
      "integration_id": "github",
      "name": "GitHub",
      "description": "Link GitHub issues and pull requests",
      "logo_url": "https://cdn.pronaflow.com/integrations/github.png",
      "supported_features": ["issue_sync", "pr_tracking"],
      "oauth_required": true
    }
  ]
}
```

---

#### Connect Integration
```
POST /api/v1/integrations/{integration_id}/connect
```
**Description**: Initiate OAuth flow for integration

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `integration_id`: Integration identifier (e.g., slack, github)

**Request Body**:
```json
{
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "redirect_uri": "https://app.pronaflow.com/integrations/callback"
}
```

**Response** (200 OK):
```json
{
  "authorization_url": "https://slack.com/oauth/v2/authorize?client_id=...&state=...",
  "state": "random_state_token"
}
```

---

#### List Connected Integrations
```
GET /api/v1/integrations
```
**Description**: List connected integrations

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `workspace_id`: Workspace ID

**Response** (200 OK):
```json
{
  "integrations": [
    {
      "connection_id": "550e8400-e29b-41d4-a716-446655440000",
      "integration_id": "slack",
      "name": "Slack",
      "connected_at": "2024-01-15T10:30:00Z",
      "status": "active",
      "settings": {
        "channel": "#general",
        "notify_on": ["task.created", "task.completed"]
      }
    }
  ]
}
```

---

#### Disconnect Integration
```
DELETE /api/v1/integrations/{connection_id}
```
**Description**: Disconnect an integration

**Headers**: 
```
Authorization: Bearer {access_token}
```

**Path Parameters**:
- `connection_id`: Connection ID

**Response** (200 OK):
```json
{
  "message": "Integration disconnected successfully"
}
```

---

## Rate Limiting & Quotas

### Rate Limits
All API endpoints are rate limited:

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Authentication | 5 attempts | 15 minutes |
| General API | 100 requests | 1 minute |
| Public endpoints | 30 requests | 1 minute |
| Webhooks | 1000 deliveries | 1 hour |

### Rate Limit Headers
Every response includes rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642252800
```

### When Rate Limited
**Response** (429 Too Many Requests):
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again in 60 seconds.",
    "retry_after": 60
  }
}
```

### Subscription Quotas
Different plans have different quotas:

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| Workspaces | 1 | 10 | Unlimited |
| Projects per workspace | 5 | 50 | Unlimited |
| Tasks per project | 100 | 1000 | Unlimited |
| Team members | 5 | 50 | Unlimited |
| API calls/month | 10,000 | 100,000 | Unlimited |
| File storage | 1 GB | 100 GB | Custom |

---

## Webhooks

### Webhook Events
Available webhook events:

#### Workspace Events
- `workspace.created`
- `workspace.updated`
- `workspace.deleted`
- `workspace.member.added`
- `workspace.member.removed`

#### Project Events
- `project.created`
- `project.updated`
- `project.archived`
- `project.deleted`
- `project.member.added`

#### Task Events
- `task.created`
- `task.updated`
- `task.completed`
- `task.deleted`
- `task.assigned`
- `task.comment.added`

#### User Events
- `user.created`
- `user.updated`
- `user.deleted`

### Webhook Payload Format
All webhooks use this format:

```json
{
  "event": "task.created",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "workspace_id": "550e8400-e29b-41d4-a716-446655440001",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440002",
    "title": "New Task",
    "status": "todo",
    "created_by": "550e8400-e29b-41d4-a716-446655440003"
  }
}
```

### Webhook Security
Verify webhook signatures using HMAC-SHA256:

**Header**:
```
X-PronaFlow-Signature: sha256=abc123...
```

**Verification** (Python):
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

### Retry Logic
Failed webhook deliveries are retried with exponential backoff:

- Attempt 1: Immediate
- Attempt 2: After 1 minute
- Attempt 3: After 5 minutes
- Attempt 4: After 30 minutes
- Attempt 5: After 2 hours

After 5 failed attempts, the webhook is marked as failed.

---

## Testing & Examples
| Code | Meaning | Typical Cause |
|------|---------|---------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 204 | No Content | Resource deleted successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists / Constraint violation |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Server temporarily unavailable |

### Common Error Codes
```
INVALID_REQUEST         - Invalid request parameters
UNAUTHORIZED            - Missing or invalid authentication token
FORBIDDEN               - Insufficient permissions
NOT_FOUND               - Resource not found
ALREADY_EXISTS          - Resource already exists
VALIDATION_ERROR        - Validation failed
RATE_LIMIT_EXCEEDED     - Too many requests
INTERNAL_ERROR          - Internal server error
```

### Error Example
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Email is required",
    "status_code": 400
  }
}
```

---

## Testing & Examples

### HTTP Status Codes
| Code | Meaning | Typical Cause |
|------|---------|---------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 204 | No Content | Resource deleted successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists / Constraint violation |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Server temporarily unavailable |

### Common Error Codes
```
INVALID_REQUEST         - Invalid request parameters
UNAUTHORIZED            - Missing or invalid authentication token
FORBIDDEN               - Insufficient permissions
NOT_FOUND               - Resource not found
ALREADY_EXISTS          - Resource already exists
VALIDATION_ERROR        - Validation failed
RATE_LIMIT_EXCEEDED     - Too many requests
INTERNAL_ERROR          - Internal server error
```

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "status_code": 422,
    "details": [
      {
        "field": "email",
        "message": "Email is required",
        "code": "required"
      },
      {
        "field": "password",
        "message": "Password must be at least 12 characters",
        "code": "min_length"
      }
    ]
  }
}
```

---

### Postman Collection
Download the Postman collection from:
- **Path**: `/docs/postman/pronaflow-api-v1.postman_collection.json`
- **Import**: Open Postman → Import → Upload file

### Environment Variables (Postman)
```json
{
  "base_url": "http://localhost:8000",
  "access_token": "{{access_token}}",
  "workspace_id": "{{workspace_id}}",
  "project_id": "{{project_id}}",
  "task_id": "{{task_id}}"
}
```

### cURL Examples

#### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123!@#",
    "full_name": "John Doe"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!@#"
  }'
```

#### Get Current User
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {access_token}"
```

#### Create Workspace
```bash
curl -X POST http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Team",
    "description": "Our development team workspace"
  }'
```

#### List Projects
```bash
curl -X GET "http://localhost:8000/api/v1/projects?workspace_id={workspace_id}&page=1&page_size=20" \
  -H "Authorization: Bearer {access_token}"
```

#### Create Task
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "{project_id}",
    "title": "Implement login feature",
    "description": "Add user authentication",
    "priority": "high",
    "due_date": "2024-01-20T00:00:00Z"
  }'
```

#### Update Task Status
```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/{task_id} \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

#### Upload File
```bash
curl -X POST http://localhost:8000/api/v1/tasks/{task_id}/files \
  -H "Authorization: Bearer {access_token}" \
  -F "file=@/path/to/file.pdf" \
  -F "description=Design mockup"
```

### JavaScript/TypeScript Examples

#### Using Fetch API
```typescript
// Login
const login = async (email: string, password: string) => {
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  if (!response.ok) {
    throw new Error('Login failed');
  }
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
};

// Get tasks with pagination
const getTasks = async (projectId: string, page = 1, pageSize = 20) => {
  const token = localStorage.getItem('access_token');
  const params = new URLSearchParams({
    project_id: projectId,
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  
  const response = await fetch(
    `http://localhost:8000/api/v1/tasks?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
  
  return response.json();
};

// Create task
const createTask = async (taskData: any) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/v1/tasks', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(taskData),
  });
  
  return response.json();
};

// Upload file
const uploadFile = async (taskId: string, file: File) => {
  const token = localStorage.getItem('access_token');
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(
    `http://localhost:8000/api/v1/tasks/${taskId}/files`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    }
  );
  
  return response.json();
};
```

#### Using Axios
```typescript
import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API methods
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  
  register: (data: any) =>
    api.post('/auth/register', data),
  
  getMe: () =>
    api.get('/auth/me'),
  
  logout: () =>
    api.post('/auth/logout'),
};

export const workspaceAPI = {
  list: () =>
    api.get('/workspaces'),
  
  create: (data: any) =>
    api.post('/workspaces', data),
  
  get: (id: string) =>
    api.get(`/workspaces/${id}`),
  
  update: (id: string, data: any) =>
    api.patch(`/workspaces/${id}`, data),
};

export const taskAPI = {
  list: (params: any) =>
    api.get('/tasks', { params }),
  
  create: (data: any) =>
    api.post('/tasks', data),
  
  get: (id: string) =>
    api.get(`/tasks/${id}`),
  
  update: (id: string, data: any) =>
    api.patch(`/tasks/${id}`, data),
  
  delete: (id: string) =>
    api.delete(`/tasks/${id}`),
};
```

### Python Examples

#### Using requests library
```python
import requests
from typing import Dict, Optional

class PronaFlowAPI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
    
    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def login(self, email: str, password: str) -> Dict:
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
        return data
    
    def get_workspaces(self) -> Dict:
        response = requests.get(
            f"{self.base_url}/api/v1/workspaces",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_task(self, project_id: str, title: str, **kwargs) -> Dict:
        data = {"project_id": project_id, "title": title, **kwargs}
        response = requests.post(
            f"{self.base_url}/api/v1/tasks",
            json=data,
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
    
    def list_tasks(self, project_id: str, page: int = 1, page_size: int = 20) -> Dict:
        params = {
            "project_id": project_id,
            "page": page,
            "page_size": page_size
        }
        response = requests.get(
            f"{self.base_url}/api/v1/tasks",
            params=params,
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

# Usage
api = PronaFlowAPI()
api.login("user@example.com", "password")
workspaces = api.get_workspaces()
task = api.create_task(
    project_id="123",
    title="New Task",
    description="Task description",
    priority="high"
)
```

---

## Best Practices

### Authentication
1. **Store tokens securely** - Use httpOnly cookies or secure storage
2. **Implement token refresh** - Refresh tokens before expiration
3. **Handle 401 errors** - Redirect to login on unauthorized
4. **Use HTTPS** - Always use HTTPS in production

### Error Handling
1. **Check response status** - Always check HTTP status codes
2. **Parse error details** - Use error.details for field-specific errors
3. **Show user-friendly messages** - Don't expose technical errors to users
4. **Log errors** - Log all API errors for debugging

### Performance
1. **Use pagination** - Always paginate list requests
2. **Request only needed fields** - Use field selection
3. **Cache responses** - Cache static or rarely-changing data
4. **Batch operations** - Use bulk endpoints when available
5. **Implement retry logic** - Retry failed requests with exponential backoff

### Security
1. **Validate input** - Validate all user input client-side
2. **Sanitize data** - Sanitize data before displaying
3. **Use CSRF tokens** - Implement CSRF protection
4. **Verify webhooks** - Always verify webhook signatures

---

## Documentation References
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Module Documentation**: See `/docs/modules/` directory
- **GitHub Repository**: https://github.com/pronaflow/backend

---

## Support & Feedback
- **Technical Support**: support@pronaflow.com
- **Bug Reports**: https://github.com/pronaflow/backend/issues
- **Feature Requests**: https://feedback.pronaflow.com
- **Documentation**: https://docs.pronaflow.com

---

**Last Updated**: February 3, 2026  
**API Version**: 1.3  
**Documentation Version**: 1.3.0  
**Maintainer**: PronaFlow Development Team
