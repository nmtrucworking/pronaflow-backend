# Module 1: Identity & Access Management - Deployment Checklist

**Version**: 1.0  
**Status**: Ready for Deployment (95%)  
**Date**: February 6, 2026

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### ✅ Database Setup
- [x] **Migration Files**: Tất cả migrations có sẵn
  - `37d437544626` - Initial tables (users, roles, permissions, sessions, mfa)
  - `38137451d0df` - Additional tables (email_verification, login_attempts, oauth)
- [x] **Models Verified**: 11 core entities + 2 audit entities
- [ ] **Run Migrations**: `alembic upgrade head`
- [ ] **Seed Initial Data**: Roles, Permissions, Admin user

### ✅ Configuration & Environment
- [ ] **Environment Variables**:
  ```env
  # JWT Configuration
  SECRET_KEY=<generate-secure-random-key>
  JWT_ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  REFRESH_TOKEN_EXPIRE_DAYS=7
  
  # Database
  DATABASE_URL=postgresql://user:pass@host:5432/pronaflow
  
  # Email Service
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=noreply@pronaflow.com
  SMTP_PASSWORD=<app-specific-password>
  
  # Security
  BCRYPT_ROUNDS=12
  MAX_LOGIN_ATTEMPTS=5
  LOGIN_ATTEMPT_WINDOW_MINUTES=10
  ACCOUNT_LOCKOUT_MINUTES=15
  
  # Session Management
  MAX_CONCURRENT_SESSIONS=5
  SESSION_TIMEOUT_DAYS=7
  
  # MFA
  MFA_ISSUER_NAME=PronaFlow
  MFA_BACKUP_CODES_COUNT=10
  
  # OAuth (Optional)
  GOOGLE_CLIENT_ID=<your-google-client-id>
  GOOGLE_CLIENT_SECRET=<your-google-client-secret>
  GITHUB_CLIENT_ID=<your-github-client-id>
  GITHUB_CLIENT_SECRET=<your-github-client-secret>
  ```

- [ ] **Dependencies Installed**: Verify `requirements.txt`
  - `fastapi`, `sqlalchemy`, `alembic`
  - `passlib[bcrypt]`, `python-jose[cryptography]`
  - `pyotp`, `qrcode`, `python-multipart`
  - `pydantic[email]`

### ✅ API Endpoints Testing

#### 1. User Registration Flow
```bash
# Register new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!@#",
    "full_name": "Test User"
  }'

# Expected: 201 Created, user with status PENDING
```

- [ ] Email format validation works
- [ ] Username uniqueness enforced
- [ ] Password strength validation works
- [ ] Email verification sent

#### 2. Email Verification
```bash
# Verify email
curl -X POST http://localhost:8000/api/v1/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "uuid-from-registration",
    "token": "token-from-email"
  }'

# Expected: User status -> ACTIVE
```

- [ ] Token expiration (24 hours) works
- [ ] Token is one-time use
- [ ] Resend verification works

#### 3. Login Flow
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!@#"
  }'

# Expected: JWT token + session info
```

- [ ] Successful login returns JWT
- [ ] Invalid credentials rejected
- [ ] Brute-force protection (5 attempts in 10 min)
- [ ] Account lockout (15 minutes) works
- [ ] Unverified email blocked

#### 4. MFA Setup
```bash
# Enable MFA (requires authentication)
curl -X POST http://localhost:8000/api/v1/auth/mfa/enable \
  -H "Authorization: Bearer <token>"

# Expected: secret_key, qr_code, backup_codes
```

- [ ] TOTP secret generated
- [ ] QR code image valid
- [ ] 10 backup codes generated
- [ ] Authenticator app (Google/Microsoft) can scan QR

```bash
# Confirm MFA with OTP
curl -X POST http://localhost:8000/api/v1/auth/mfa/confirm \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"otp_code": "123456"}'
```

- [ ] Valid OTP enables MFA
- [ ] Invalid OTP rejected
- [ ] MFA status persisted

#### 5. MFA Login
```bash
# Login with MFA enabled
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d '{"email": "test@example.com", "password": "SecurePass123!@#"}'

# Expected: 403 with X-Session-ID header (requires MFA)

# Verify MFA
curl -X POST http://localhost:8000/api/v1/auth/mfa/verify \
  -d '{"session_id": "session-id", "otp_code": "123456"}'
```

- [ ] MFA required after password
- [ ] OTP verification works
- [ ] Backup code works as fallback
- [ ] Backup code marked as used

#### 6. Session Management
```bash
# List active sessions
curl -X GET http://localhost:8000/api/v1/auth/sessions \
  -H "Authorization: Bearer <token>"
```

- [ ] All sessions listed with device info
- [ ] Current session marked
- [ ] Max 5 concurrent sessions enforced
- [ ] Oldest session auto-revoked on 6th login

```bash
# Revoke specific session
curl -X POST http://localhost:8000/api/v1/auth/sessions/revoke \
  -H "Authorization: Bearer <token>" \
  -d '{"session_id": "uuid"}'
```

- [ ] Remote session revocation works
- [ ] Revoke all (except current) works

#### 7. Password Reset
```bash
# Request reset
curl -X POST http://localhost:8000/api/v1/auth/password-reset \
  -d '{"email": "test@example.com"}'

# Reset password
curl -X POST http://localhost:8000/api/v1/auth/password-reset/confirm \
  -d '{
    "user_id": "uuid",
    "token": "reset-token",
    "new_password": "NewSecurePass123!@#"
  }'
```

- [ ] Reset email sent
- [ ] Token expires after 15 minutes
- [ ] Token is one-time use
- [ ] All sessions terminated after reset

#### 8. Password Change
```bash
curl -X POST http://localhost:8000/api/v1/auth/password-change \
  -H "Authorization: Bearer <token>" \
  -d '{
    "current_password": "OldPass123!@#",
    "new_password": "NewPass456!@#"
  }'
```

- [ ] Current password verified
- [ ] Password strength validated
- [ ] All other sessions terminated

### ✅ Security Testing

#### Brute-Force Protection
- [ ] 5 failed login attempts in 10 minutes locks account
- [ ] Security alert email sent on lockout
- [ ] Account auto-unlocks after 15 minutes

#### Session Security
- [ ] JWT tokens expire correctly
- [ ] Revoked sessions cannot be reused
- [ ] Session hijacking prevented (IP/device tracking)

#### Password Security
- [ ] Passwords hashed with bcrypt (12 rounds minimum)
- [ ] Plain passwords never logged or returned
- [ ] Password history prevents reuse (if implemented)

#### MFA Security
- [ ] TOTP codes time-based (30s window)
- [ ] Backup codes hashed in database
- [ ] Used backup codes cannot be reused

### ✅ Role-Based Access Control (RBAC)

#### Seed Initial Roles & Permissions
```sql
-- Roles
INSERT INTO roles (id, role_name, hierarchy_level) VALUES
  (uuid_generate_v4(), 'OWNER', 1),
  (uuid_generate_v4(), 'ADMIN', 2),
  (uuid_generate_v4(), 'MEMBER', 3),
  (uuid_generate_v4(), 'GUEST', 4);

-- Permissions
INSERT INTO permissions (id, code, description) VALUES
  (uuid_generate_v4(), 'workspace:delete', 'Delete workspace'),
  (uuid_generate_v4(), 'workspace:manage', 'Manage workspace settings'),
  (uuid_generate_v4(), 'project:create', 'Create projects'),
  (uuid_generate_v4(), 'project:delete', 'Delete projects'),
  (uuid_generate_v4(), 'task:create', 'Create tasks'),
  (uuid_generate_v4(), 'task:edit', 'Edit tasks'),
  (uuid_generate_v4(), 'task:delete', 'Delete tasks');
```

- [ ] Roles seeded successfully
- [ ] Permissions seeded successfully
- [ ] Role-Permission mappings created
- [ ] Permission middleware enforces access control

### ✅ Audit & Monitoring

#### Audit Logs
- [ ] All login attempts logged (success/failure)
- [ ] Password changes logged
- [ ] MFA enable/disable logged
- [ ] Account lockouts logged
- [ ] Sensitive operations logged

#### Monitoring Metrics
- [ ] Failed login rate monitored
- [ ] Active sessions count tracked
- [ ] MFA adoption rate tracked
- [ ] Password reset requests monitored

---

## 🚨 KNOWN ISSUES & LIMITATIONS

### ❌ Not Yet Implemented (5%)

1. **OAuth Social Login** (Planned)
   - Google OAuth endpoints missing
   - GitHub OAuth endpoints missing
   - Models ready, need endpoint implementation

2. **Unit Tests** (Recommended for Production)
   - Auth service tests needed
   - MFA service tests needed
   - Session service tests needed

3. **Impossible Travel Detection**
   - Logic in SessionService but not fully tested
   - Requires geographic IP lookup integration

### ⚠️ Production Considerations

1. **Rate Limiting**
   - Implement API rate limiting (e.g., 100 requests/minute per IP)
   - Consider using Redis for distributed rate limiting

2. **Email Service**
   - Configure production SMTP provider
   - Consider email queue for async processing
   - Add email templates with branding

3. **Security Headers**
   - Add CORS configuration
   - Implement CSP headers
   - Enable HTTPS only in production

4. **Database Optimization**
   - Add indexes for frequently queried fields
   - Monitor query performance
   - Consider read replicas if needed

5. **Backup Strategy**
   - Regular database backups
   - User data export capability
   - Disaster recovery plan

---

## 📦 DEPLOYMENT STEPS

### Step 1: Database Setup
```bash
# Run migrations
alembic upgrade head

# Seed initial data
python scripts/seed_roles_permissions.py
```

### Step 2: Start Application
```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Step 3: Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### Step 4: Create Admin User
```bash
python scripts/create_admin.py \
  --email admin@pronaflow.com \
  --username admin \
  --password <secure-password>
```

### Step 5: Smoke Tests
Run through all test scenarios above

---

## ✅ SIGN-OFF

- [ ] **Database Migration**: Applied and verified
- [ ] **API Endpoints**: All tested and working
- [ ] **Security**: Brute-force, MFA, sessions verified
- [ ] **RBAC**: Roles and permissions enforced
- [ ] **Audit Logs**: Writing correctly
- [ ] **Documentation**: Complete
- [ ] **Monitoring**: In place

**Deployed By**: _________________  
**Date**: _________________  
**Environment**: [ ] Development [ ] Staging [ ] Production

---

## 📞 SUPPORT & ESCALATION

**Technical Contact**: backend-team@pronaflow.com  
**Security Issues**: security@pronaflow.com  
**Emergency Hotline**: +84-xxx-xxx-xxxx

---

**Next Steps**: After Module 1 is stable, proceed with Module 2 (Workspace Management) deployment.
