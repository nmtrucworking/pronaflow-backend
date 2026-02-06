# Frontend Connection Checklist - PronaFlow Backend

**Ngày kiểm tra:** February 3, 2026  
**Trạng thái:** ✅ READY FOR FE CONNECTION (với một số lưu ý)

---

## 1. ✅ CORS Configuration

### Status: PASSED

Backend đã cấu hình CORS đúng cách để chấp nhận kết nối từ Frontend:

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Các origins được phép (theo .env):**
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

**Lưu ý:** Nếu Frontend chạy trên port/domain khác, cần cập nhật `ALLOWED_ORIGINS` trong `.env`

---

## 2. ✅ Authentication & Authorization

### Status: FIXED

#### Vấn đề phát hiện:
`get_current_user()` dependency không đọc token từ Authorization header.

#### Giải pháp đã áp dụng:
Updated `app/core/security.py`:
- Thêm import: `from fastapi import Header`
- Thay đổi parameter: `token: Optional[str] = None` → `authorization: Optional[str] = Header(None)`
- Thêm logic extract token từ header: `"Bearer <token>" → token`

#### Cách Frontend gửi request:
```javascript
// JavaScript/TypeScript
const response = await fetch('http://localhost:8000/api/v1/projects', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
```

#### Token format:
- **Type:** JWT (JSON Web Token)
- **Header format:** `Authorization: Bearer <access_token>`
- **Expiration:** 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Algorithm:** HS256

---

## 3. ✅ API Endpoints Available

### Status: PASSED - 15 Module Routers Registered

```
/api/v1/auth          - Authentication (register, login, MFA, etc.)
/api/v1/workspaces    - Workspace management
/api/v1/projects      - Project management
/api/v1/tasks         - Task management
/api/v1/scheduling    - Task scheduling
/api/v1/collaboration - Real-time collaboration
/api/v1/notifications - Notifications
/api/v1/archive       - Archive management
/api/v1/personalization - User preferences
/api/v1/analytics     - Analytics & reports
/api/v1/integration   - 3rd party integrations
/api/v1/subscription  - Billing & subscription (Module 13)
/api/v1/admin/system  - Admin system settings
/api/v1/help-center   - Help center & documentation
/api/v1/onboarding    - User onboarding
/api/v1/admin         - Admin management
```

### Health Check Endpoints:
```
GET  /                 - API info
GET  /health           - Health check
GET  /docs             - Swagger UI
GET  /redoc            - ReDoc documentation
```

---

## 4. ✅ Database Configuration

### Status: CONFIGURED

**Connection Details (from .env):**
```
DATABASE_URL=postgresql+psycopg2://pronaflow_user:pronaflow123@localhost:5432/pronaflow_db
```

**Database Features:**
- ✅ SQLAlchemy ORM configured
- ✅ Session management with `get_db()` dependency
- ✅ Connection pooling enabled (pool_size=10, max_overflow=20)
- ✅ Pre-ping enabled for health checks

**⚠️ Prerequisites for Frontend to work:**
1. PostgreSQL server phải running on `localhost:5432`
2. Database `pronaflow_db` phải được tạo
3. User `pronaflow_user` with password `pronaflow123` phải tồn tại

### Kiểm tra Database:
```bash
# PowerShell / CMD
psql -U pronaflow_user -h localhost -d pronaflow_db -c "SELECT version();"
```

---

## 5. ✅ Authentication Flow

### Status: PASSED

#### Login Flow:
```
1. Frontend: POST /api/v1/auth/login
   {
     "email": "user@example.com",
     "password": "password123"
   }

2. Backend: Verify credentials, create session
   Response: {
     "access_token": "eyJhbGc...",
     "token_type": "bearer",
     "session_id": "uuid-xxx",
     "user": { ... }
   }

3. Frontend: Save access_token
   Add to all requests: Authorization: Bearer <token>

4. Backend: Validates token on every request
   - Checks JWT signature
   - Verifies session is not revoked
   - Returns 401 if invalid
```

#### MFA (Multi-Factor Authentication):
- Enabled via `/api/v1/auth/mfa/enable`
- Uses TOTP (Time-based One-Time Password)
- Backup codes provided for recovery
- If MFA enabled: Login returns 403 with "MFA verification required"

---

## 6. ✅ Request/Response Format

### Status: PASSED

#### Standard Response Format:
```json
{
  "id": "uuid",
  "created_at": "2026-02-03T10:00:00",
  "updated_at": "2026-02-03T10:00:00",
  ...data fields...
}
```

#### Error Response Format:
```json
{
  "detail": "Error message here"
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions / MFA required)
- `404` - Not Found
- `429` - Too Many Requests (rate limiting)
- `500` - Server Error

---

## 7. ✅ Security Features

### Status: IMPLEMENTED

- ✅ **Password Hashing:** bcrypt with 12 rounds
- ✅ **JWT Authentication:** HS256 algorithm
- ✅ **CORS Protection:** Configured for allowed origins only
- ✅ **Session Management:** Sessions tracked and revocable
- ✅ **Brute-Force Protection:** Max 5 login attempts, 15-min lockout
- ✅ **Email Verification:** Required before account activation
- ✅ **MFA/TOTP:** Multi-factor authentication available
- ✅ **Password Reset:** Secure token-based reset (15 min expiration)
- ✅ **Login Attempt Tracking:** IP, User-Agent, timestamps logged

---

## 8. ✅ Dependencies

### Status: VERIFIED

**Core Dependencies Installed:**
```
fastapi==0.109.0        ✅
uvicorn==0.27.0         ✅
sqlalchemy>=2.0.36      ✅
psycopg2-binary==2.9.9  ✅
pydantic==2.5.3         ✅
python-jose==3.3.0      ✅
passlib==1.7.4          ✅
python-dotenv==1.0.0    ✅
```

All dependencies in `requirements.txt` are compatible.

---

## 9. ✅ Development Server Setup

### Status: READY

**Start Backend Server:**
```bash
cd e:\Workspace\project\pronaflow\backend

# Method 1: Using Python directly
python app/main.py

# Method 2: Using Uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Method 3: Using VS Code task
# Press Ctrl+Shift+B to run build task
```

**Server will be available at:**
- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

---

## 10. 🔧 Common Issues & Solutions

### Issue 1: "Not authenticated" Error
**Cause:** Frontend not sending Authorization header  
**Solution:** Add header to all requests:
```javascript
headers: { 'Authorization': `Bearer ${token}` }
```

### Issue 2: CORS Error
**Cause:** Frontend running on different origin  
**Solution:** Add origin to `ALLOWED_ORIGINS` in `.env`:
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://your-frontend-url
```

### Issue 3: "Invalid authorization header format"
**Cause:** Missing "Bearer " prefix in token  
**Solution:** Ensure format is exactly: `Authorization: Bearer eyJ...`

### Issue 4: 401 "Session has been revoked"
**Cause:** Token's session was revoked or expired  
**Solution:** Re-login to get new token

### Issue 5: Database Connection Error
**Cause:** PostgreSQL not running or wrong connection string  
**Solution:**
```bash
# Check if PostgreSQL is running
# Update DATABASE_URL in .env if connection string is wrong
# Ensure database exists: createdb -U pronaflow_user pronaflow_db
```

---

## 11. ✅ Sample Frontend Integration

### Example: Login & Get Projects
```javascript
// 1. Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
const { access_token } = await loginResponse.json();

// 2. Save token (localStorage or sessionStorage)
localStorage.setItem('accessToken', access_token);

// 3. Get projects
const projectsResponse = await fetch(
  'http://localhost:8000/api/v1/projects?workspace_id=workspace-uuid',
  {
    headers: {
      'Authorization': `Bearer ${access_token}`,
      'Content-Type': 'application/json'
    }
  }
);
const projects = await projectsResponse.json();
```

---

## 12. ✅ Testing Endpoints with cURL

```bash
# 1. Health Check
curl http://localhost:8000/health

# 2. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'

# 3. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'

# 4. Get Profile (with token)
curl -X GET http://localhost:8000/api/v1/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 5. List Workspaces
curl -X GET http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 6. Create Project
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "New Project",
    "description": "Test project",
    "workspace_id": "workspace-uuid"
  }'
```

---

## 13. 📋 Pre-Deployment Checklist

Before Frontend goes to production:

- [ ] Backend running on accessible host/port
- [ ] PostgreSQL database created and accessible
- [ ] `.env` file configured with correct DATABASE_URL
- [ ] `ALLOWED_ORIGINS` includes Frontend URL
- [ ] All required Python packages installed
- [ ] Database migrations applied (Alembic)
- [ ] Test endpoints respond correctly
- [ ] Error handling working (CORS, 401, 403)
- [ ] Token expiration working properly
- [ ] Database backups configured

---

## 14. ✅ Summary

| Component | Status | Notes |
|-----------|--------|-------|
| CORS | ✅ Ready | Configured for localhost:3000 & :5173 |
| Auth | ✅ Fixed | Token extraction from Authorization header |
| API Routes | ✅ Ready | 15 module routers registered |
| Database | ✅ Configured | PostgreSQL with SQLAlchemy |
| Security | ✅ Implemented | JWT, MFA, Password hashing |
| Error Handling | ✅ Ready | Standard HTTP status codes |
| Docs | ✅ Available | Swagger & ReDoc at /docs & /redoc |

---

## 🚀 Ready for Frontend Connection

Backend is **READY** for Frontend to connect and fetch data.

**Key Points for Frontend Developer:**
1. ✅ All endpoints are available at `/api/v1/*`
2. ✅ Always send: `Authorization: Bearer <token>` header
3. ✅ Handle 401/403 errors for re-authentication
4. ✅ CORS is enabled for localhost:3000 and :5173
5. ✅ API documentation at `http://localhost:8000/docs`

---

**Generated:** 2026-02-03  
**Backend Version:** 1.0.0  
**Last Updated:** February 3, 2026
