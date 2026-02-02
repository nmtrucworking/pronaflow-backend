# PronaFlow API Documentation - Version 1.0
**Modules: 1-6 | Last Updated: February 2, 2026**

---

## 📋 Table of Contents
1. [Base Information](#base-information)
2. [Authentication & Security](#authentication--security)
3. [Module 1: Identity & Access Management (IAM)](#module-1-identity--access-management-iam)
4. [Module 2: Workspace Management](#module-2-workspace-management)
5. [Module 3: Project Lifecycle Management](#module-3-project-lifecycle-management)
6. [Module 4: Task Execution & Orchestration](#module-4-task-execution--orchestration)
7. [Module 5: Temporal Planning & Scheduling](#module-5-temporal-planning--scheduling)
8. [Module 6: Unified Collaboration Hub](#module-6-unified-collaboration-hub)
9. [Common Response Formats](#common-response-formats)
10. [Error Handling](#error-handling)

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

## Testing

### Postman Collection
Download the Postman collection from:
- **Path**: `/docs/postman/pronaflow-api-v1.postman_collection.json`
- **Import**: Open Postman → Import → Upload file

### Environment Variables (Postman)
```
{
  "base_url": "http://localhost:8000",
  "access_token": "your_token_here",
  "workspace_id": "...",
  "project_id": "..."
}
```

### cURL Examples

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

---

## Documentation References
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

**Last Updated**: February 2, 2026  
**Version**: 1.0  
**Maintainer**: PronaFlow Development Team
