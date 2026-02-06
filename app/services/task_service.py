"""
Task Service - Business logic for task operations
"""
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid
from datetime import date

from app.repositories.task_repository import TaskRepository, TaskListRepository
from app.repositories.project_repository import ProjectRepository
from app.models.tasks import Task, TaskList, TaskAssignee
from app.db.enums import TaskStatus, TaskPriority
from app.utils.exceptions import (
    NotFoundException,
    ForbiddenException,
    ConflictException,
    InvalidStateException,
)


class TaskListService:
    """Service for task list operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.task_list_repo = TaskListRepository(db)
        self.project_repo = ProjectRepository(db)
    
    def create_task_list(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        name: str,
        description: Optional[str] = None
    ) -> TaskList:
        """Create a new task list."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")
        
        if not self.project_repo.can_access(project_id, user_id):
            raise ForbiddenException("You don't have access to this project")
        
        # Get next order
        lists = self.task_list_repo.get_project_task_lists(project_id, limit=1000)
        next_order = max([tl.order for tl in lists] if lists else []) + 1
        
        task_list_data = {
            "project_id": project_id,
            "name": name,
            "order": next_order,
        }
        if description:
            task_list_data["description"] = description
        
        return self.task_list_repo.create(task_list_data)
    
    def delete_task_list(
        self,
        task_list_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Delete a task list."""
        task_list = self.task_list_repo.get_by_id(task_list_id)
        if not task_list:
            raise NotFoundException("Task list not found")
        
        if not self.project_repo.can_access(task_list.project_id, user_id):
            raise ForbiddenException("You don't have access to this project")
        
        return self.task_list_repo.delete(task_list_id)


class TaskService:
    """Service for task operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.project_repo = ProjectRepository(db)
    
    # ==================== TASK MANAGEMENT ====================
    
    def create_task(
        self,
        project_id: uuid.UUID,
        task_list_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        description: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[date] = None,
        estimated_hours: Optional[float] = None,
        **kwargs
    ) -> Task:
        """
        Create a new task.
        
        Args:
            project_id: Project ID
            task_list_id: Task list ID
            user_id: Current user ID
            title: Task title
            description: Optional description
            priority: Task priority
            due_date: Optional due date
            estimated_hours: Optional estimated hours
            
        Returns:
            Created task
        """
        # Check project access
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")
        
        if not self.project_repo.can_access(project_id, user_id):
            raise ForbiddenException("You don't have access to this project")
        
        # Check task list belongs to project
        task_list = self.db.query(TaskList).filter(
            TaskList.id == task_list_id,
            TaskList.project_id == project_id
        ).first()
        
        if not task_list:
            raise NotFoundException("Task list not found or doesn't belong to project")
        
        # Get next order
        tasks = self.task_repo.get_task_list_tasks(task_list_id, limit=1000)
        next_order = max([t.order for t in tasks] if tasks else []) + 1
        
        # Create task
        task_data = {
            "project_id": project_id,
            "task_list_id": task_list_id,
            "title": title,
            "status": TaskStatus.TODO,
            "priority": priority,
            "created_by": user_id,
            "order": next_order,
        }
        if description:
            task_data["description"] = description
        if due_date:
            task_data["due_date"] = due_date
        if estimated_hours:
            task_data["estimated_hours"] = estimated_hours
        
        return self.task_repo.create(task_data)
    
    def update_task(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        due_date: Optional[date] = None,
        estimated_hours: Optional[float] = None,
        **kwargs
    ) -> Task:
        """Update task details."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")
        
        if not self.project_repo.can_access(task.project_id, user_id):
            raise ForbiddenException("You don't have access to this task")
        
        update_data = {}
        if title:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if status:
            update_data["status"] = status
        if priority:
            update_data["priority"] = priority
        if due_date is not None:
            update_data["due_date"] = due_date
        if estimated_hours is not None:
            update_data["estimated_hours"] = estimated_hours
        
        if update_data:
            task = self.task_repo.update(task_id, update_data)
        
        return task
    
    def delete_task(self, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete a task."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")
        
        if not self.project_repo.can_access(task.project_id, user_id):
            raise ForbiddenException("You don't have access to this task")
        
        return self.task_repo.delete(task_id)
    
    # ==================== TASK QUERIES ====================
    
    def get_task(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
        """Get task details."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")
        
        if not self.project_repo.can_access(task.project_id, user_id):
            raise ForbiddenException("You don't have access to this task")
        
        return task
    
    def list_task_list_tasks(
        self,
        task_list_id: uuid.UUID,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Task], int]:
        """Get tasks in a task list."""
        task_list = self.db.query(TaskList).filter(TaskList.id == task_list_id).first()
        if not task_list:
            raise NotFoundException("Task list not found")
        
        if not self.project_repo.can_access(task_list.project_id, user_id):
            raise ForbiddenException("You don't have access to this project")
        
        tasks = self.task_repo.get_task_list_tasks(
            task_list_id,
            skip=skip,
            limit=limit
        )
        total = self.task_repo.count()
        
        return tasks, total
    
    def list_project_tasks(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Task], int]:
        """Get all tasks in a project."""
        if not self.project_repo.can_access(project_id, user_id):
            raise ForbiddenException("You don't have access to this project")
        
        tasks = self.task_repo.get_project_tasks(
            project_id,
            skip=skip,
            limit=limit
        )
        total = self.task_repo.count()
        
        return tasks, total
    
    def get_user_assigned_tasks(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Task], int]:
        """Get tasks assigned to user."""
        tasks = self.task_repo.get_assigned_to_user(
            user_id,
            skip=skip,
            limit=limit
        )
        total = self.task_repo.count_user_assigned_tasks(user_id)
        
        return tasks, total
    
    def search_tasks(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Task], int]:
        """Search tasks in project."""
        if not self.project_repo.can_access(project_id, user_id):
            raise ForbiddenException("You don't have access to this project")
        
        tasks = self.task_repo.search_tasks(
            project_id,
            query,
            skip=skip,
            limit=limit
        )
        
        return tasks, len(tasks)
    
    # ==================== STATUS MANAGEMENT ====================
    
    def update_status(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        status: TaskStatus
    ) -> Task:
        """Update task status."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")
        
        if not self.project_repo.can_access(task.project_id, user_id):
            raise ForbiddenException("You don't have access to this task")
        
        return self.task_repo.update_status(task_id, status)
    
    def get_overdue_tasks(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> List[Task]:
        """Get overdue tasks in project."""
        if not self.project_repo.can_access(project_id, user_id):
            raise ForbiddenException("You don't have access to this project")
        
        return self.task_repo.get_overdue_tasks(project_id)
    
    # ==================== ASSIGNMENT MANAGEMENT ====================
    
    def assign_task(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        assignee_id: uuid.UUID,
        is_primary: bool = False
    ) -> TaskAssignee:
        """Assign a task to user."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")
        
        if not self.project_repo.can_access(task.project_id, user_id):
            raise ForbiddenException("You don't have access to this task")
        
        return self.task_repo.add_assignee(task_id, assignee_id, is_primary=is_primary)
    
    def unassign_task(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        assignee_id: uuid.UUID
    ) -> bool:
        """Unassign a user from task."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")
        
        if not self.project_repo.can_access(task.project_id, user_id):
            raise ForbiddenException("You don't have access to this task")
        
        return self.task_repo.remove_assignee(task_id, assignee_id)
    
    def get_assignees(self, task_id: uuid.UUID, user_id: uuid.UUID) -> List[TaskAssignee]:
        """Get task assignees."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")
        
        if not self.project_repo.can_access(task.project_id, user_id):
            raise ForbiddenException("You don't have access to this task")
        
        return self.task_repo.get_assignees(task_id)
    
    # ==================== STATISTICS ====================
    
    def get_project_stats(self, project_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """Get project task statistics."""
        if not self.project_repo.can_access(project_id, user_id):
            raise ForbiddenException("You don't have access to this project")
        
        return self.task_repo.get_project_stats(project_id)
