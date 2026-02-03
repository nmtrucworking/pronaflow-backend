# Database Models

This directory contains SQLAlchemy ORM models for database tables.

## Organization
- Each model represents a database table
- Models should inherit from Base
- Use snake_case for table names

## Example
```python
from app.db import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
```
