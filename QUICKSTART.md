# PronaFlow Backend - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Prerequisites
```bash
# Ensure you have:
- Python 3.10+
- PostgreSQL 12+
- pip
```

### 2. Install Dependencies
```bash
cd e:\Workspace\project\pronaflow\backend

# Activate virtual environment (if exists)
.venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy example environment file
copy .env.example .env

# Edit .env and set minimum required values:
# 1. DATABASE_URL (your PostgreSQL connection)
# 2. SECRET_KEY (generate: python -c "import secrets; print(secrets.token_hex(32))")
```

### 4. Setup Database
```bash
# Create database (if not exists)
createdb pronaflow

# Option A: Auto-create tables (Development)
# Tables will be created automatically when app starts with DEBUG=True

# Option B: Use Alembic migrations (Production)
alembic upgrade head
```

### 5. Run Application
```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload

# Or using Python directly
python -m app.main
```

### 6. Access API
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Test the API

### Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### Get Current User
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📝 Environment Variables

Minimum required in `.env`:

```env
# Database
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/pronaflow

# Security (CHANGE THIS!)
SECRET_KEY=your-super-secret-key-here

# Application
DEBUG=True
```

## 🔍 Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_ctl status

# Verify database exists
psql -l | grep pronaflow

# Create database if missing
createdb pronaflow
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

## 📚 Next Steps

1. **Read Documentation**: [MODULE_1_IMPLEMENTATION.md](MODULE_1_IMPLEMENTATION.md)
2. **Test Endpoints**: Use Swagger UI at http://localhost:8000/docs
3. **Configure Email**: Setup SMTP for production emails
4. **Enable HTTPS**: Configure SSL for production

## 🎯 Key Features Ready

- ✅ User Registration & Email Verification
- ✅ Login/Logout with JWT
- ✅ Multi-Factor Authentication (MFA)
- ✅ Session Management (5 concurrent devices)
- ✅ Password Reset & Change
- ✅ Brute-force Protection

## 📖 API Documentation

Visit http://localhost:8000/docs for:
- Interactive API testing
- Request/response schemas
- Authentication flows
- Example payloads

---

**Need Help?** Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for detailed information.
