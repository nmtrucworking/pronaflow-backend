# Module 1: Identity & Access Management (IAM)

## Overview
Identity and Access Management system covering:
- User registration and authentication
- Multi-Factor Authentication (MFA)
- Role-Based Access Control (RBAC)
- Session management
- Audit logging

## Key Components

### Models
- **User** - Core user identity with soft delete
- **Role** - System roles with hierarchical structure
- **Permission** - Fine-grained permissions
- **MFAConfig** - Two-factor authentication setup
- **Session** - User login sessions with device tracking
- **AuditLog** - Audit trail for compliance

### Services
- `AuthService` - Authentication and token management
- `MFAService` - Two-factor authentication
- `PermissionService` - Permission checking
- `AuditService` - Audit log recording

### API Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/mfa/setup` - Setup MFA
- `POST /api/v1/auth/mfa/verify` - Verify MFA code

## Database Tables (8 + 2 associations)
- users
- roles
- permissions
- mfa_configs
- mfa_backup_codes
- auth_providers
- audit_logs
- sessions
- user_roles (association)
- role_permissions (association)

## Security Features
- Password strength validation (12+ chars)
- JWT token-based authentication
- MFA with backup codes
- Session tracking per device
- Audit logging for compliance

