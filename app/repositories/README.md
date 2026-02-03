# Repository Layer

This directory contains repository/DAO classes for data access.

## Purpose
- Abstract database operations
- Provide a clean interface for services
- Separate business logic from database access

## Pattern
```python
class UserRepository:
    def __init__(self, db):
        self.db = db
    
    def get_by_id(self, user_id):
        return self.db.query(User).filter(User.id == user_id).first()
```
