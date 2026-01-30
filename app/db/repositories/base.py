"""
Base Repository Class - Generic CRUD operations.
Provides common database operations for all repositories.
"""
from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from sqlalchemy.ext.declarative import DeclarativeMeta

T = TypeVar("T", bound=DeclarativeMeta)


class BaseRepository(Generic[T]):
    """
    Generic base repository for CRUD operations.
    
    Args:
        session: SQLAlchemy session
        model: SQLAlchemy model class
    """

    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def create(self, obj_data: Dict[str, Any]) -> T:
        """Create and return a new object."""
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        self.session.flush()
        return db_obj

    def read(self, id: Any) -> Optional[T]:
        """Read object by ID."""
        return self.session.execute(
            select(self.model).where(self.model.id == id)
        ).scalar_one_or_none()

    def read_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: Any
    ) -> List[T]:
        """Read multiple objects with optional filters."""
        query = select(self.model)
        
        # Apply filters
        if filters:
            conditions = [
                getattr(self.model, key) == value
                for key, value in filters.items()
                if hasattr(self.model, key)
            ]
            if conditions:
                query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        return self.session.execute(query).scalars().all()

    def update(self, id: Any, obj_data: Dict[str, Any]) -> Optional[T]:
        """Update an object by ID."""
        db_obj = self.read(id)
        if db_obj:
            for key, value in obj_data.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            self.session.flush()
        return db_obj

    def delete(self, id: Any) -> bool:
        """Delete an object by ID (hard delete)."""
        db_obj = self.read(id)
        if db_obj:
            self.session.delete(db_obj)
            self.session.flush()
            return True
        return False

    def soft_delete(self, id: Any) -> Optional[T]:
        """Soft delete an object (if model supports it)."""
        db_obj = self.read(id)
        if db_obj and hasattr(db_obj, 'soft_delete'):
            db_obj.soft_delete()
            self.session.flush()
        return db_obj

    def count(self, **filters: Any) -> int:
        """Count objects with optional filters."""
        query = select(self.model)
        
        if filters:
            conditions = [
                getattr(self.model, key) == value
                for key, value in filters.items()
                if hasattr(self.model, key)
            ]
            if conditions:
                query = query.where(and_(*conditions))
        
        return self.session.query(self.model).filter_by(**filters).count()

    def exists(self, **filters: Any) -> bool:
        """Check if object exists with given filters."""
        query = select(self.model)
        
        if filters:
            conditions = [
                getattr(self.model, key) == value
                for key, value in filters.items()
                if hasattr(self.model, key)
            ]
            if conditions:
                query = query.where(and_(*conditions))
        
        return self.session.execute(query).scalar_one_or_none() is not None

    def commit(self) -> None:
        """Commit the session."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the session."""
        self.session.rollback()

    def refresh(self, db_obj: T) -> None:
        """Refresh an object from the database."""
        self.session.refresh(db_obj)
