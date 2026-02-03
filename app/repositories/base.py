"""
Base Repository Pattern Implementation
Provides generic CRUD operations for all models
"""
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid

from app.db.declarative_base import Base

# Generic type variable for model
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with generic CRUD operations.
    
    Example:
        class UserRepository(BaseRepository[User]):
            def __init__(self, db: Session):
                super().__init__(User, db)
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository with model and database session.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    # ==================== CREATE ====================
    
    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        Create a new record.
        
        Args:
            obj_in: Dictionary with object data
            
        Returns:
            Created model instance
            
        Raises:
            IntegrityError: If unique constraint violation
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def create_many(self, objs_in: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Create multiple records in bulk.
        
        Args:
            objs_in: List of dictionaries with object data
            
        Returns:
            List of created model instances
        """
        db_objs = [self.model(**obj_data) for obj_data in objs_in]
        self.db.add_all(db_objs)
        self.db.commit()
        for obj in db_objs:
            self.db.refresh(obj)
        return db_objs
    
    # ==================== READ ====================
    
    def get_by_id(self, id: uuid.UUID) -> Optional[ModelType]:
        """
        Get record by ID.
        
        Args:
            id: Record UUID
            
        Returns:
            Model instance or None if not found
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        descending: bool = False
    ) -> List[ModelType]:
        """
        Get all records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Column name to order by
            descending: Sort in descending order
            
        Returns:
            List of model instances
        """
        query = self.db.query(self.model)
        
        # Apply ordering
        if order_by:
            order_column = getattr(self.model, order_by, None)
            if order_column is not None:
                query = query.order_by(
                    order_column.desc() if descending else order_column.asc()
                )
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_field(
        self,
        field_name: str,
        field_value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get records by field value.
        
        Args:
            field_name: Name of the field
            field_value: Value to search for
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        field = getattr(self.model, field_name, None)
        if field is None:
            raise ValueError(f"Field {field_name} does not exist on {self.model.__name__}")
        
        return (
            self.db.query(self.model)
            .filter(field == field_value)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_one_by_field(self, field_name: str, field_value: Any) -> Optional[ModelType]:
        """
        Get single record by field value.
        
        Args:
            field_name: Name of the field
            field_value: Value to search for
            
        Returns:
            Model instance or None if not found
        """
        field = getattr(self.model, field_name, None)
        if field is None:
            raise ValueError(f"Field {field_name} does not exist on {self.model.__name__}")
        
        return self.db.query(self.model).filter(field == field_value).first()
    
    def get_multi_by_ids(self, ids: List[uuid.UUID]) -> List[ModelType]:
        """
        Get multiple records by IDs.
        
        Args:
            ids: List of UUIDs
            
        Returns:
            List of model instances
        """
        return self.db.query(self.model).filter(self.model.id.in_(ids)).all()
    
    def filter_by(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        descending: bool = False
    ) -> List[ModelType]:
        """
        Filter records by multiple conditions.
        
        Args:
            filters: Dictionary of field_name: value pairs
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Column name to order by
            descending: Sort in descending order
            
        Returns:
            List of model instances
        """
        query = self.db.query(self.model)
        
        # Apply filters
        for field_name, value in filters.items():
            field = getattr(self.model, field_name, None)
            if field is not None:
                query = query.filter(field == value)
        
        # Apply ordering
        if order_by:
            order_column = getattr(self.model, order_by, None)
            if order_column is not None:
                query = query.order_by(
                    order_column.desc() if descending else order_column.asc()
                )
        
        return query.offset(skip).limit(limit).all()
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records matching filters.
        
        Args:
            filters: Optional dictionary of field_name: value pairs
            
        Returns:
            Number of matching records
        """
        query = self.db.query(func.count(self.model.id))
        
        if filters:
            for field_name, value in filters.items():
                field = getattr(self.model, field_name, None)
                if field is not None:
                    query = query.filter(field == value)
        
        return query.scalar()
    
    def exists(self, id: uuid.UUID) -> bool:
        """
        Check if record exists by ID.
        
        Args:
            id: Record UUID
            
        Returns:
            True if exists, False otherwise
        """
        return self.db.query(
            self.db.query(self.model).filter(self.model.id == id).exists()
        ).scalar()
    
    # ==================== UPDATE ====================
    
    def update(
        self,
        id: uuid.UUID,
        obj_in: Dict[str, Any],
        commit: bool = True
    ) -> Optional[ModelType]:
        """
        Update a record by ID.
        
        Args:
            id: Record UUID
            obj_in: Dictionary with fields to update
            commit: Whether to commit immediately
            
        Returns:
            Updated model instance or None if not found
        """
        db_obj = self.get_by_id(id)
        if db_obj is None:
            return None
        
        # Update fields
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # Update timestamp if model has updated_at
        if hasattr(db_obj, 'updated_at'):
            setattr(db_obj, 'updated_at', datetime.utcnow())
        
        if commit:
            self.db.commit()
            self.db.refresh(db_obj)
        
        return db_obj
    
    def update_many(
        self,
        ids: List[uuid.UUID],
        obj_in: Dict[str, Any]
    ) -> List[ModelType]:
        """
        Update multiple records by IDs.
        
        Args:
            ids: List of UUIDs
            obj_in: Dictionary with fields to update
            
        Returns:
            List of updated model instances
        """
        db_objs = self.get_multi_by_ids(ids)
        
        for db_obj in db_objs:
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            # Update timestamp if model has updated_at
            if hasattr(db_obj, 'updated_at'):
                setattr(db_obj, 'updated_at', datetime.utcnow())
        
        self.db.commit()
        for obj in db_objs:
            self.db.refresh(obj)
        
        return db_objs
    
    # ==================== DELETE ====================
    
    def delete(self, id: uuid.UUID, soft: bool = False) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: Record UUID
            soft: Use soft delete if model supports it
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = self.get_by_id(id)
        if db_obj is None:
            return False
        
        # Soft delete if model has is_deleted field and soft=True
        if soft and hasattr(db_obj, 'is_deleted'):
            setattr(db_obj, 'is_deleted', True)
            setattr(db_obj, 'deleted_at', datetime.utcnow())
            self.db.commit()
        else:
            # Hard delete
            self.db.delete(db_obj)
            self.db.commit()
        
        return True
    
    def delete_many(self, ids: List[uuid.UUID], soft: bool = False) -> int:
        """
        Delete multiple records by IDs.
        
        Args:
            ids: List of UUIDs
            soft: Use soft delete if model supports it
            
        Returns:
            Number of deleted records
        """
        db_objs = self.get_multi_by_ids(ids)
        
        if soft and hasattr(self.model, 'is_deleted'):
            # Soft delete
            for obj in db_objs:
                setattr(obj, 'is_deleted', True)
                setattr(obj, 'deleted_at', datetime.utcnow())
        else:
            # Hard delete
            for obj in db_objs:
                self.db.delete(obj)
        
        self.db.commit()
        return len(db_objs)
    
    def restore(self, id: uuid.UUID) -> Optional[ModelType]:
        """
        Restore a soft-deleted record.
        
        Args:
            id: Record UUID
            
        Returns:
            Restored model instance or None if not found
        """
        if not hasattr(self.model, 'is_deleted'):
            raise ValueError(f"{self.model.__name__} does not support soft delete")
        
        db_obj = self.db.query(self.model).filter(
            and_(self.model.id == id, self.model.is_deleted == True)
        ).first()
        
        if db_obj is None:
            return None
        
        setattr(db_obj, 'is_deleted', False)
        setattr(db_obj, 'deleted_at', None)
        self.db.commit()
        self.db.refresh(db_obj)
        
        return db_obj
    
    # ==================== UTILITY ====================
    
    def get_or_create(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> tuple[ModelType, bool]:
        """
        Get existing record or create new one.
        
        Args:
            defaults: Default values for creation
            **kwargs: Fields to search for
            
        Returns:
            Tuple of (instance, created) where created is True if new record
        """
        instance = self.db.query(self.model).filter_by(**kwargs).first()
        
        if instance:
            return instance, False
        else:
            params = {**kwargs, **(defaults or {})}
            instance = self.model(**params)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance, True
    
    def refresh(self, db_obj: ModelType) -> ModelType:
        """
        Refresh a model instance from database.
        
        Args:
            db_obj: Model instance to refresh
            
        Returns:
            Refreshed model instance
        """
        self.db.refresh(db_obj)
        return db_obj
    
    def commit(self) -> None:
        """Commit current transaction."""
        self.db.commit()
    
    def rollback(self) -> None:
        """Rollback current transaction."""
        self.db.rollback()
    
    def flush(self) -> None:
        """Flush pending changes to database."""
        self.db.flush()
