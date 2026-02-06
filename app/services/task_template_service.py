"""
Task Template Service - Provides template management for tasks
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.tasks import Task
from app.repositories.task_repository import TaskRepository


class TaskTemplateService:
    """Service for managing task templates."""
    
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
    
    def create_template(
        self,
        title: str,
        description: Optional[str],
        workspace_id: UUID,
        created_by: UUID,
        **kwargs
    ) -> Task:
        """
        Create a new task template.
        
        Args:
            title: Template name
            description: Template description
            workspace_id: Workspace ID
            created_by: User ID who creates the template
            **kwargs: Additional template fields
        
        Returns:
            Created template task
        """
        template_data = {
            "title": title,
            "description": description,
            "workspace_id": workspace_id,
            "created_by": created_by,
            "is_template": True,  # Mark as template
            **kwargs
        }
        
        template = self.task_repo.create(**template_data)
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def get_workspace_templates(
        self,
        workspace_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get all templates for a workspace.
        
        Args:
            workspace_id: Workspace ID
            skip: Number of records to skip
            limit: Maximum number of records
        
        Returns:
            List of template tasks
        """
        templates = self.db.query(Task).filter(
            Task.workspace_id == workspace_id,
            Task.is_template == True
        ).offset(skip).limit(limit).all()
        
        return templates
    
    def instantiate_from_template(
        self,
        template_id: UUID,
        project_id: UUID,
        created_by: UUID,
        overrides: Optional[dict] = None
    ) -> Task:
        """
        Create a new task from a template.
        
        Args:
            template_id: Template task ID
            project_id: Target project ID
            created_by: User creating the task
            overrides: Optional field overrides
        
        Returns:
            New task instance
        
        Raises:
            ValueError: If template not found
        """
        template = self.task_repo.get(template_id)
        if not template or not template.is_template:
            raise ValueError("Template not found")
        
        # Copy template fields
        task_data = {
            "title": template.title,
            "description": template.description,
            "priority": template.priority,
            "estimated_hours": template.estimated_hours,
            "project_id": project_id,
            "created_by": created_by,
            "is_template": False  # This is an instance, not a template
        }
        
        # Apply overrides
        if overrides:
            task_data.update(overrides)
        
        # Create task instance
        task = self.task_repo.create(**task_data)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def update_template(
        self,
        template_id: UUID,
        **updates
    ) -> Task:
        """
        Update a template.
        
        Args:
            template_id: Template ID
            **updates: Fields to update
        
        Returns:
            Updated template
        """
        template = self.task_repo.update(template_id, **updates)
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def delete_template(self, template_id: UUID) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: Template ID
        
        Returns:
            True if deleted successfully
        """
        result = self.task_repo.delete(template_id)
        self.db.commit()
        
        return result
