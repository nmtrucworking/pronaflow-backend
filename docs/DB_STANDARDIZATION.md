# Database Module Standardization Guide

## 📋 Cấu trúc đã được chuẩn hóa

### Thư mục `app/db/`

```
app/db/
├── __init__.py                 # Central exports
├── declarative_base.py         # SQLAlchemy Base class (renamed from base_class.py)
├── base.py                     # Model registry for Alembic
├── session.py                  # Database engine & session management
├── enums.py                    # Database enumerations
├── mixins.py                   # Reusable model mixins
├── models/
│   ├── __init__.py            # Central model imports
│   ├── module_1.py            # IAM models
│   ├── workspaces.py          # Workspace models
│   ├── projects.py            # Project models
│   ├── tasks.py               # Task models
│   ├── tags.py                # Tag models
│   ├── notifications.py       # Notification models
│   ├── integrations.py        # Integration models
│   ├── projects_extended.py   # Extended project models
│   └── reports.py             # Report models
└── repositories/              # Data access layer (future)
    ├── __init__.py
    ├── base.py
    ├── user_repo.py
    └── task_repo.py
```

## 🔄 Thay đổi chính

### 1. Rename: `base_class.py` → `declarative_base.py`
**Lý do:** Tên file rõ ràng hơn về chức năng
- **Cũ:** `from app.db.base_class import Base`
- **Mới:** `from app.db.declarative_base import Base`

### 2. Cập nhật `app/db/base.py`
- Tách riêng model registry
- Import từ `models/__init__.py` thay vì từng module
- Chuẩn bị cho Alembic auto-generation

### 3. Hoàn thiện `app/db/__init__.py`
- Export tất cả các components chính
- Dễ dàng import từ `from app.db import ...`

### 4. Chuẩn hóa Docstrings
- Thêm docstring tiếng Anh
- Giải thích rõ ràng chức năng của mỗi module

### 5. Tối ưu `app/db/enums.py`
- Tổ chức theo modules
- Thêm đầy đủ enums cần thiết

## 📦 Import Patterns

### ✅ Recommended (New)
```python
# Từ declarative_base
from app.db.declarative_base import Base

# Từ session
from app.db.session import SessionLocal, engine, get_db

# Từ db package
from app.db import (
    Base, SessionLocal, get_db,
    User, Workspace, Project,
    TimestampMixin, SoftDeleteMixin
)
```

### ❌ Deprecated (Old)
```python
# Không còn sử dụng
from app.db.base_class import Base
```

## 🔗 Relationship Diagram

```
declarative_base.py (Base class)
         ↓
    models/*.py (Model definitions)
         ↓
    models/__init__.py (Model exports)
         ↓
    base.py (Model registry)
         ↓
    __init__.py (Package exports)
```

## 📝 Model File Template

```python
"""
Entity models for [Module Name].
Provides [description of models].
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin, SoftDeleteMixin
from app.db.enums import YourEnum

if TYPE_CHECKING:
    from app.db.models.other_module import OtherModel


class MyModel(Base, TimestampMixin, SoftDeleteMixin):
    """Model description"""
    __tablename__ = "my_models"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
```

## 🚀 Usage Examples

### FastAPI with Dependency Injection
```python
from fastapi import FastAPI, Depends
from app.db import get_db, User
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return user
```

### Creating Tables
```python
from app.db.declarative_base import Base
from app.db.session import engine

# Create all tables
Base.metadata.create_all(bind=engine)
```

### Alembic Migration
```python
# app/alembic/env.py automatically imports
from app.db.base import Base, User, Workspace, Project, ...

# Run migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## ✨ Best Practices

1. **Imports:** Luôn import từ `app.db` hoặc `app.db.declarative_base`
2. **Models:** Sử dụng Type hints (Mapped, Optional)
3. **Mixins:** Kết hợp TimestampMixin, SoftDeleteMixin theo nhu cầu
4. **Enums:** Định nghĩa tất cả enums trong `enums.py`
5. **Relationships:** Sử dụng `TYPE_CHECKING` để tránh circular imports

## 🔍 Kiểm tra

Để xác nhận chuẩn hóa:
```bash
# Kiểm tra imports
grep -r "from app.db.base_class" app/

# Kết quả không nên có match (tất cả đã được thay thế)
```

## 📚 Tài liệu tham khảo
- [SQLAlchemy ORM Documentation](https://docs.sqlalchemy.org/en/20/orm/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
