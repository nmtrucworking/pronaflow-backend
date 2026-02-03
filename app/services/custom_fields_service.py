"""
Custom Fields Service - Dynamic field management for entities
"""
from typing import List, Optional, Any, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import JSON

from app.db.models.tasks import Task
from app.db.repositories.task_repo import TaskRepository


class FieldType:
    """Custom field types."""
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    DATE = "DATE"
    BOOLEAN = "BOOLEAN"
    SELECT = "SELECT"
    MULTISELECT = "MULTISELECT"
    URL = "URL"
    EMAIL = "EMAIL"


class CustomFieldsService:
    """Service for managing custom fields on entities."""
    
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
    
    def define_custom_field(
        self,
        workspace_id: UUID,
        field_name: str,
        field_type: str,
        entity_type: str = "task",
        options: Optional[List[str]] = None,
        is_required: bool = False,
        default_value: Optional[Any] = None
    ) -> Dict:
        """
        Define a custom field for an entity type.
        
        Args:
            workspace_id: Workspace ID
            field_name: Name of the custom field
            field_type: Type of field (TEXT, NUMBER, DATE, etc.)
            entity_type: Type of entity (task, project, etc.)
            options: Available options for SELECT/MULTISELECT fields
            is_required: Whether field is required
            default_value: Default value for the field
        
        Returns:
            Custom field definition
        """
        field_definition = {
            "workspace_id": str(workspace_id),
            "field_name": field_name,
            "field_type": field_type,
            "entity_type": entity_type,
            "options": options or [],
            "is_required": is_required,
            "default_value": default_value,
            "created_at": "utcnow()"
        }
        
        # In a real implementation, this would be stored in a custom_field_definitions table
        # For now, we'll return the definition structure
        return field_definition
    
    def set_custom_field_value(
        self,
        task_id: UUID,
        field_name: str,
        value: Any
    ) -> Task:
        """
        Set a custom field value on a task.
        
        Args:
            task_id: Task ID
            field_name: Name of custom field
            value: Value to set
        
        Returns:
            Updated task
        
        Raises:
            ValueError: If validation fails
        """
        task = self.task_repo.get(task_id)
        if not task:
            raise ValueError("Task not found")
        
        # Get current custom fields
        custom_fields = task.custom_fields or {}
        
        # Validate value type (basic validation)
        # In production, this should validate against field definition
        
        # Update custom fields
        custom_fields[field_name] = value
        
        # Update task
        updated_task = self.task_repo.update(
            task_id,
            custom_fields=custom_fields
        )
        self.db.commit()
        self.db.refresh(updated_task)
        
        return updated_task
    
    def get_custom_field_value(
        self,
        task_id: UUID,
        field_name: str
    ) -> Optional[Any]:
        """
        Get a custom field value from a task.
        
        Args:
            task_id: Task ID
            field_name: Name of custom field
        
        Returns:
            Field value or None if not set
        """
        task = self.task_repo.get(task_id)
        if not task:
            return None
        
        custom_fields = task.custom_fields or {}
        return custom_fields.get(field_name)
    
    def set_multiple_custom_fields(
        self,
        task_id: UUID,
        fields: Dict[str, Any]
    ) -> Task:
        """
        Set multiple custom field values at once.
        
        Args:
            task_id: Task ID
            fields: Dictionary of field_name: value pairs
        
        Returns:
            Updated task
        """
        task = self.task_repo.get(task_id)
        if not task:
            raise ValueError("Task not found")
        
        # Get current custom fields
        custom_fields = task.custom_fields or {}
        
        # Update all fields
        custom_fields.update(fields)
        
        # Update task
        updated_task = self.task_repo.update(
            task_id,
            custom_fields=custom_fields
        )
        self.db.commit()
        self.db.refresh(updated_task)
        
        return updated_task
    
    def remove_custom_field(
        self,
        task_id: UUID,
        field_name: str
    ) -> Task:
        """
        Remove a custom field from a task.
        
        Args:
            task_id: Task ID
            field_name: Name of field to remove
        
        Returns:
            Updated task
        """
        task = self.task_repo.get(task_id)
        if not task:
            raise ValueError("Task not found")
        
        custom_fields = task.custom_fields or {}
        
        if field_name in custom_fields:
            del custom_fields[field_name]
        
        updated_task = self.task_repo.update(
            task_id,
            custom_fields=custom_fields
        )
        self.db.commit()
        self.db.refresh(updated_task)
        
        return updated_task
    
    def get_all_custom_fields(self, task_id: UUID) -> Dict[str, Any]:
        """
        Get all custom fields for a task.
        
        Args:
            task_id: Task ID
        
        Returns:
            Dictionary of all custom fields
        """
        task = self.task_repo.get(task_id)
        if not task:
            return {}
        
        return task.custom_fields or {}
    
    def validate_custom_field_value(
        self,
        field_type: str,
        value: Any,
        options: Optional[List[str]] = None
    ) -> bool:
        """
        Validate a custom field value against its type.
        
        Args:
            field_type: Type of field
            value: Value to validate
            options: Available options for SELECT fields
        
        Returns:
            True if valid
        
        Raises:
            ValueError: If validation fails
        """
        if field_type == FieldType.TEXT:
            if not isinstance(value, str):
                raise ValueError("Value must be a string")
        
        elif field_type == FieldType.NUMBER:
            if not isinstance(value, (int, float)):
                raise ValueError("Value must be a number")
        
        elif field_type == FieldType.BOOLEAN:
            if not isinstance(value, bool):
                raise ValueError("Value must be a boolean")
        
        elif field_type == FieldType.SELECT:
            if options and value not in options:
                raise ValueError(f"Value must be one of: {', '.join(options)}")
        
        elif field_type == FieldType.MULTISELECT:
            if not isinstance(value, list):
                raise ValueError("Value must be a list")
            if options:
                for v in value:
                    if v not in options:
                        raise ValueError(f"All values must be from: {', '.join(options)}")
        
        elif field_type == FieldType.EMAIL:
            if not isinstance(value, str) or '@' not in value:
                raise ValueError("Value must be a valid email")
        
        elif field_type == FieldType.URL:
            if not isinstance(value, str) or not value.startswith(('http://', 'https://')):
                raise ValueError("Value must be a valid URL")
        
        return True
