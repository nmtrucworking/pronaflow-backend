# PronaFlow Backend - Quick Start Guide

## 🚀 Bắt đầu nhanh

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Virtual environment (recommended)

### Installation

1. **Clone repository và di chuyển vào thư mục backend**
```bash
cd backend
```

2. **Tạo và kích hoạt virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **Cài đặt dependencies**
```bash
pip install -r requirements.txt
```

4. **Cấu hình environment variables**
```bash
cp .env.example .env
# Chỉnh sửa .env với thông tin database của bạn
```

5. **Chạy database migrations**
```bash
alembic upgrade head
```

6. **Khởi động server**
```bash
uvicorn app.main:app --reload
```

Server sẽ chạy tại: http://localhost:8000

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 Testing

### Chạy tất cả tests
```bash
pytest
```

### Chạy tests với coverage
```bash
pytest --cov=app --cov-report=html
```

### Chạy specific test types
```bash
# Unit tests only
pytest -m unit

# Integration/API tests only
pytest -m api

# Run specific test file
pytest tests/test_repositories/test_user_repo.py -v
```

### Xem coverage report
```bash
# Mở HTML coverage report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
```

## 🗄️ Database Management

### Alembic Commands

```bash
# Tạo migration mới
alembic revision --autogenerate -m "Description"

# Xem lịch sử migrations
alembic history

# Upgrade lên version mới nhất
alembic upgrade head

# Downgrade 1 version
alembic downgrade -1

# Xem current version
alembic current

# Upgrade/downgrade đến version cụ thể
alembic upgrade <revision>
alembic downgrade <revision>
```

### Database Seeding

```bash
# Chạy seed scripts (nếu có)
python seed_help_center_flags.py
python init_db.py
```

## 📂 Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── v1/endpoints/ # Module-based endpoints
│   │   └── legacy/       # Legacy routes (migration only)
│   ├── models/           # SQLAlchemy models
│   ├── core/             # Core configuration
│   ├── db/               # DB base/session/enums
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic layer
│   ├── middleware/       # Request middleware
│   ├── utils/            # Shared helpers
│   ├── alembic/          # Alembic env + versions
│   └── main.py           # FastAPI application
├── tests/
│   ├── test_api/         # API integration tests
│   ├── test_repositories/# Repository unit tests
│   └── test_services/    # Service unit tests
├── docs/                 # Documentation
├── alembic.ini           # Alembic configuration
├── pytest.ini            # Pytest configuration
└── requirements.txt      # Python dependencies
```

## 🔧 Development Workflow

### 1. Feature Development

```bash
# 1. Tạo branch mới
git checkout -b feature/your-feature

# 2. Implement code
# - Tạo/update models in app/models/
# - Tạo/update schemas in app/schemas/
# - Tạo/update services in app/services/
# - Tạo/update API endpoints in app/api/

# 3. Generate migration
alembic revision --autogenerate -m "Add feature X"

# 4. Write tests
# - Unit tests in tests/test_repositories/
# - API tests in tests/test_api/

# 5. Run tests
pytest

# 6. Commit changes
git add .
git commit -m "Add feature X"
```

### 2. Running in Development

```bash
# With auto-reload
uvicorn app.main:app --reload

# With specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# With log level
uvicorn app.main:app --reload --log-level debug
```

## 📦 Available Services

### Task Management Services

#### 1. Task Template Service
```python
from app.services.task_template_service import TaskTemplateService

service = TaskTemplateService(db)

# Create template
template = service.create_template(
    title="Bug Fix Template",
    description="Standard bug fix workflow",
    workspace_id=workspace_id,
    created_by=user_id
)

# Instantiate from template
task = service.instantiate_from_template(
    template_id=template.id,
    project_id=project_id,
    created_by=user_id,
    overrides={"title": "Fix login bug"}
)
```

#### 2. Recurring Task Service
```python
from app.services.recurring_task_service import RecurringTaskService, RecurrencePattern

service = RecurringTaskService(db)

# Create weekly recurring task
task = service.create_recurring_task(
    title="Weekly Team Sync",
    project_id=project_id,
    created_by=user_id,
    pattern=RecurrencePattern.WEEKLY,
    interval=1
)

# Generate next occurrence
next_task = service.generate_next_occurrence(task.id)
```

#### 3. Custom Fields Service
```python
from app.services.custom_fields_service import CustomFieldsService, FieldType

service = CustomFieldsService(db)

# Set custom field
task = service.set_custom_field_value(
    task_id=task_id,
    field_name="customer_priority",
    value="P1"
)

# Set multiple fields
task = service.set_multiple_custom_fields(
    task_id=task_id,
    fields={
        "customer": "Acme Corp",
        "contract_value": 50000,
        "deadline": "2026-03-01"
    }
)
```

## 🔐 Authentication

### Register User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "full_name": "John Doe",
    "password": "SecurePassword123!"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePassword123!"
```

### Use Access Token
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <your_access_token>"
```

## 📊 Monitoring & Debugging

### View Logs
```bash
# Application logs
tail -f logs/app.log

# Uvicorn logs
# Check terminal output
```

### Database Queries
```bash
# Connect to PostgreSQL
psql -U postgres -d pronaflow

# View tables
\dt

# Describe table
\d users

# Query data
SELECT * FROM users LIMIT 10;
```

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check PostgreSQL is running
pg_ctl status

# Verify DATABASE_URL in .env
echo $DATABASE_URL
```

**2. Migration Issues**
```bash
# Reset migrations (DANGER: drops all data)
alembic downgrade base
alembic upgrade head

# Check current version
alembic current

# Verify database state
alembic check
```

**3. Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.11+
```

**4. Test Failures**
```bash
# Run with verbose output
pytest -vv

# Run single test
pytest tests/test_repositories/test_user_repo.py::TestUserRepository::test_create_user -v

# Clear pytest cache
pytest --cache-clear
```

## 📖 Documentation

- [API Documentation v1.3](API_DOCUMENTATION.md)
- [Database Models](docs/DATABASE_MODELS.md)
- [Entity Analysis](docs/ENTITY_COMPLETE_LIST.md)
- [MVP Completion Report](docs/MVP_COMPLETION_REPORT.md)
- [Outstanding Issues](OUTSTANDING_ISSUES_REPORT.md)
- [Implementation Report](IMPLEMENTATION_COMPLETION_REPORT.md)

## ✅ Next Steps

1. ✅ **Migrations created** - Ready to deploy
2. ✅ **Tests infrastructure** - Can run in CI/CD
3. ✅ **Core services implemented** - Business logic ready
4. ⏳ **Expand test coverage** - Target 80%+
5. ⏳ **Setup CI/CD** - GitHub Actions
6. ⏳ **Deploy to staging** - Test environment

---

**Last Updated**: February 3, 2026  
**Version**: 1.0  
**Maintainer**: PronaFlow Development Team
