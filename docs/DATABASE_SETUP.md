# PronaFlow Backend - Database Setup Guide

## Tổng quan
Hướng dẫn này giúp bạn triển khai và quản lý database cho dự án PronaFlow Backend sử dụng PostgreSQL, SQLAlchemy, và Alembic.

## Yêu cầu hệ thống
- Python 3.10+
- PostgreSQL 14+
- pip hoặc poetry để quản lý packages

## Bước 1: Cài đặt Dependencies

```bash
# Cài đặt tất cả dependencies
pip install -r requirements.txt
```

## Bước 2: Cấu hình Database

### 2.1 Tạo PostgreSQL Database

```sql
-- Đăng nhập vào PostgreSQL
psql -U postgres

-- Tạo database
CREATE DATABASE pronaflow_db;

-- Tạo user
CREATE USER pronaflow_user WITH PASSWORD 'pronaflow@123';

-- Cấp quyền
GRANT ALL PRIVILEGES ON DATABASE pronaflow_db TO pronaflow_user;
ALTER DATABASE pronaflow_db OWNER TO pronaflow_user;

-- Thoát
\q
```

#### Kết quả khởi chạy
```bash
(.venv) PS E:\Workspace\project\pronaflow\backend> psql -U postgres
Password for user postgres: 

psql (16.11)
Type "help" for help.

postgres=# CREATE DATABASE pronaflow_db
postgres-# CREATE USER pronaflow_user WITH PASSWORD 'pronaflow@123'        
postgres-# GRANT ALL PRIVILEGES ON DATABASE pronaflow_db TO pronaflow_user;
ERROR:  syntax error at or near "CREATE"
LINE 2: CREATE USER pronaflow_user WITH PASSWORD 'pronaflow@123'
        ^
postgres=# CREATE USER pronaflow_user WITH PASSWORD 'pronaflow@123';       
CREATE ROLE
postgres=# GRANT ALL PRIVILEGES ON DATABASE pronaflow_db TO pronaflow_user;
ERROR:  database "pronaflow_db" does not exist
postgres=# CREATE DATABASE pronaflow_db;
CREATE DATABASE
postgres=# GRANT ALL PRIVILEGES ON DATABASE pronaflow_db TO pronaflow_user;
GRANT
postgres=# ALTER DATABASE pronaflow_db OWNER TO pronaflow_user;
```

### 2.2 Cấu hình Environment Variables

```bash
# Copy file .env.example thành .env
cp .env.example .env

# Chỉnh sửa file .env với thông tin database của bạn
# DATABASE_URL=postgresql+psycopg2://pronaflow_user:your_password_here@localhost:5432/pronaflow_db
```

## Bước 3: Khởi tạo Database

### Option 1: Sử dụng Alembic (Khuyến nghị)

```bash
# Tạo migration ban đầu
alembic revision --autogenerate -m "Initial migration"

# Áp dụng migrations
alembic upgrade head

# Kiểm tra phiên bản hiện tại
alembic current
```

### Option 2: Sử dụng Script init_db.py

```bash
# Khởi tạo tất cả tables
python init_db.py init

# Hoặc xóa tất cả tables (CẨN THẬN!)
python init_db.py drop
```

## Bước 4: Quản lý Migrations

### Tạo migration mới

```bash
# Tạo migration tự động từ thay đổi models
alembic revision --autogenerate -m "Mô tả thay đổi"

# Tạo migration thủ công
alembic revision -m "Mô tả thay đổi"
```

### Áp dụng migrations

```bash
# Upgrade lên phiên bản mới nhất
alembic upgrade head

# Upgrade lên một phiên bản cụ thể
alembic upgrade <revision_id>

# Upgrade lên phiên bản kế tiếp
alembic upgrade +1
```

### Rollback migrations

```bash
# Downgrade về phiên bản trước
alembic downgrade -1

# Downgrade về một phiên bản cụ thể
alembic downgrade <revision_id>

# Downgrade về ban đầu
alembic downgrade base
```

### Xem lịch sử migrations

```bash
# Xem phiên bản hiện tại
alembic current

# Xem lịch sử migrations
alembic history

# Xem chi tiết một migration
alembic show <revision_id>
```

## Cấu trúc Database

### Models hiện có:

1. **Module 1: Identity & Access Management (IAM)**
   - `users` - Quản lý người dùng
   - `roles` - Vai trò người dùng
   - `permissions` - Quyền hạn
   - `user_roles` - Liên kết User-Role
   - `role_permissions` - Liên kết Role-Permission

2. **Module 2: Multi-tenancy Workspace**
   - `workspaces` - Workspace/Organization
   - `workspace_members` - Thành viên workspace
   - `workspace_invitations` - Lời mời tham gia
   - `workspace_access_logs` - Logs truy cập
   - `workspace_settings` - Cài đặt workspace

## Naming Conventions

Database sử dụng naming conventions chuẩn:
- **Index**: `ix_<column_name>`
- **Unique**: `uq_<table_name>_<column_name>`
- **Check**: `ck_<table_name>_<constraint_name>`
- **Foreign Key**: `fk_<table_name>_<column_name>_<referred_table>`
- **Primary Key**: `pk_<table_name>`

## Troubleshooting

### Lỗi kết nối database

```bash
# Kiểm tra PostgreSQL đang chạy
# Windows:
Get-Service postgresql*

# Kiểm tra connection string
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

### Lỗi migration

```bash
# Stamp lại version nếu bị lỗi đồng bộ
alembic stamp head

# Hoặc xóa alembic_version table và chạy lại
# DROP TABLE alembic_version;
```

### Reset database hoàn toàn

```bash
# 1. Drop tất cả tables
python init_db.py drop

# 2. Xóa version history
# DELETE FROM alembic_version;

# 3. Tạo lại migrations
alembic revision --autogenerate -m "Initial migration"

# 4. Áp dụng migrations
alembic upgrade head
```

## Best Practices

1. **Luôn tạo backup** trước khi chạy migrations trên production
2. **Test migrations** trên môi trường development trước
3. **Sử dụng --autogenerate** nhưng luôn review migration files
4. **Commit migration files** vào Git cùng với code changes
5. **Đặt tên migrations** rõ ràng và mô tả đầy đủ

## Tài liệu tham khảo

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
