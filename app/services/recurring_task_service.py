"""
Recurring Task Service - Manages recurring task scheduling and creation
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from enum import Enum

from app.db.models.tasks import Task
from app.db.repositories.task_repo import TaskRepository


class RecurrencePattern(str, Enum):
    """Recurrence patterns for tasks."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"


class RecurringTaskService:
    """Service for managing recurring tasks."""
    
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
    
    def create_recurring_task(
        self,
        title: str,
        project_id: UUID,
        created_by: UUID,
        pattern: RecurrencePattern,
        interval: int = 1,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        **kwargs
    ) -> Task:
        """
        Create a recurring task template.
        
        Args:
            title: Task title
            project_id: Project ID
            created_by: Creator user ID
            pattern: Recurrence pattern (DAILY, WEEKLY, MONTHLY, YEARLY)
            interval: Interval between recurrences (default: 1)
            start_date: When recurrence starts
            end_date: When recurrence ends (optional)
            **kwargs: Additional task fields
        
        Returns:
            Created recurring task template
        """
        recurrence_config = {
            "pattern": pattern.value,
            "interval": interval,
            "start_date": start_date or datetime.utcnow(),
            "end_date": end_date
        }
        
        task_data = {
            "title": title,
            "project_id": project_id,
            "created_by": created_by,
            "is_recurring": True,
            "recurrence_config": recurrence_config,
            **kwargs
        }
        
        task = self.task_repo.create(**task_data)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def generate_next_occurrence(
        self,
        recurring_task_id: UUID,
        base_date: Optional[datetime] = None
    ) -> Task:
        """
        Generate the next occurrence of a recurring task.
        
        Args:
            recurring_task_id: Recurring task template ID
            base_date: Date to calculate next occurrence from (default: now)
        
        Returns:
            New task instance
        
        Raises:
            ValueError: If task is not recurring
        """
        template = self.task_repo.get(recurring_task_id)
        if not template or not template.is_recurring:
            raise ValueError("Task is not a recurring task")
        
        config = template.recurrence_config
        base_date = base_date or datetime.utcnow()
        
        # Calculate next due date based on pattern
        next_date = self._calculate_next_date(
            base_date,
            config["pattern"],
            config["interval"]
        )
        
        # Check if we've passed the end date
        if config.get("end_date") and next_date > config["end_date"]:
            return None
        
        # Create new task instance
        task_data = {
            "title": template.title,
            "description": template.description,
            "priority": template.priority,
            "project_id": template.project_id,
            "created_by": template.created_by,
            "due_date": next_date,
            "is_recurring": False,  # Instance is not recurring
            "parent_task_id": template.id  # Link to template
        }
        
        task = self.task_repo.create(**task_data)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def _calculate_next_date(
        self,
        base_date: datetime,
        pattern: str,
        interval: int
    ) -> datetime:
        """
        Calculate the next occurrence date.
        
        Args:
            base_date: Starting date
            pattern: Recurrence pattern
            interval: Interval value
        
        Returns:
            Next occurrence datetime
        """
        if pattern == RecurrencePattern.DAILY:
            return base_date + timedelta(days=interval)
        
        elif pattern == RecurrencePattern.WEEKLY:
            return base_date + timedelta(weeks=interval)
        
        elif pattern == RecurrencePattern.MONTHLY:
            # Simple month addition (doesn't handle edge cases perfectly)
            month = base_date.month + interval
            year = base_date.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            return base_date.replace(year=year, month=month)
        
        elif pattern == RecurrencePattern.YEARLY:
            return base_date.replace(year=base_date.year + interval)
        
        else:
            # Default: add days
            return base_date + timedelta(days=interval)
    
    def get_recurring_tasks(
        self,
        project_id: UUID,
        active_only: bool = True
    ) -> List[Task]:
        """
        Get all recurring tasks for a project.
        
        Args:
            project_id: Project ID
            active_only: Only return active recurring tasks
        
        Returns:
            List of recurring task templates
        """
        query = self.db.query(Task).filter(
            Task.project_id == project_id,
            Task.is_recurring == True
        )
        
        if active_only:
            query = query.filter(Task.status != "DONE")
        
        return query.all()
    
    def stop_recurrence(self, task_id: UUID) -> Task:
        """
        Stop a recurring task from generating new occurrences.
        
        Args:
            task_id: Recurring task ID
        
        Returns:
            Updated task
        """
        task = self.task_repo.update(
            task_id,
            status="DONE",
            is_recurring=False
        )
        self.db.commit()
        self.db.refresh(task)
        
        return task
