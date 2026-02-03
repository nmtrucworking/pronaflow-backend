"""
Task Repository
Handles all database operations for Task, TaskList, and Subtask models.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import uuid

from app.repositories.base import BaseRepository
from app.db.models.tasks import Task, TaskList, Subtask, TaskAssignee
from app.db.enums import TaskStatus, TaskPriority


class TaskListRepository(BaseRepository[TaskList]):
    """Repository for TaskList model."""
    
    def __init__(self, db: Session):
        super().__init__(TaskList, db)
    
    def get_project_task_lists(
        self,
        project_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskList]:
        """
        Get all task lists in a project.
        
        Args:
            project_id: Project ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of task lists
        """
        return (
            self.db.query(TaskList)
            .filter(TaskList.project_id == project_id)
            .order_by(TaskList.order.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_name(self, project_id: uuid.UUID, name: str) -> Optional[TaskList]:
        """
        Get task list by name.
        
        Args:
            project_id: Project ID
            name: Task list name
            
        Returns:
            TaskList instance or None if not found
        """
        return (
            self.db.query(TaskList)
            .filter(
                and_(
                    TaskList.project_id == project_id,
                    TaskList.name == name
                )
            )
            .first()
        )
    
    def update_order(self, task_list_id: uuid.UUID, new_order: int) -> Optional[TaskList]:
        """
        Update task list order.
        
        Args:
            task_list_id: TaskList ID
            new_order: New order value
            
        Returns:
            Updated task list or None if not found
        """
        task_list = self.get_by_id(task_list_id)
        if task_list:
            task_list.order = new_order
            self.db.commit()
            self.db.refresh(task_list)
        return task_list


class TaskRepository(BaseRepository[Task]):
    """Repository for Task model with advanced querying."""
    
    def __init__(self, db: Session):
        super().__init__(Task, db)
    
    # ==================== TASK QUERIES ====================
    
    def get_project_tasks(
        self,
        project_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get all tasks in a project.
        
        Args:
            project_id: Project ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of tasks
        """
        return (
            self.db.query(Task)
            .filter(Task.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_task_list_tasks(
        self,
        task_list_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get all tasks in a task list.
        
        Args:
            task_list_id: TaskList ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of tasks
        """
        return (
            self.db.query(Task)
            .filter(Task.task_list_id == task_list_id)
            .order_by(Task.order.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_assigned_to_user(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks assigned to a user.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of tasks assigned to user
        """
        return (
            self.db.query(Task)
            .join(TaskAssignee)
            .filter(TaskAssignee.user_id == user_id)
            .filter(Task.status != TaskStatus.DONE)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_status(
        self,
        project_id: uuid.UUID,
        status: TaskStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks by status.
        
        Args:
            project_id: Project ID
            status: Task status
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of tasks with given status
        """
        return (
            self.db.query(Task)
            .filter(
                and_(
                    Task.project_id == project_id,
                    Task.status == status
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_priority(
        self,
        project_id: uuid.UUID,
        priority: TaskPriority,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks by priority.
        
        Args:
            project_id: Project ID
            priority: Task priority
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of tasks with given priority
        """
        return (
            self.db.query(Task)
            .filter(
                and_(
                    Task.project_id == project_id,
                    Task.priority == priority
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_overdue_tasks(self, project_id: uuid.UUID) -> List[Task]:
        """
        Get overdue tasks (due_date passed and not completed).
        
        Args:
            project_id: Project ID
            
        Returns:
            List of overdue tasks
        """
        now = datetime.utcnow()
        return (
            self.db.query(Task)
            .filter(
                and_(
                    Task.project_id == project_id,
                    Task.due_date < now,
                    Task.status != TaskStatus.DONE
                )
            )
            .all()
        )
    
    def get_due_soon(self, project_id: uuid.UUID, days: int = 7) -> List[Task]:
        """
        Get tasks due within specified days.
        
        Args:
            project_id: Project ID
            days: Number of days to look ahead
            
        Returns:
            List of tasks due soon
        """
        now = datetime.utcnow()
        future_date = now + timedelta(days=days)
        
        return (
            self.db.query(Task)
            .filter(
                and_(
                    Task.project_id == project_id,
                    Task.due_date >= now,
                    Task.due_date <= future_date,
                    Task.status != TaskStatus.DONE
                )
            )
            .order_by(Task.due_date.asc())
            .all()
        )
    
    def search_tasks(
        self,
        project_id: uuid.UUID,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Task]:
        """
        Search tasks by title or description.
        
        Args:
            project_id: Project ID
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching tasks
        """
        return (
            self.db.query(Task)
            .filter(Task.project_id == project_id)
            .filter(
                or_(
                    Task.title.ilike(f"%{query}%"),
                    Task.description.ilike(f"%{query}%")
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    # ==================== STATUS MANAGEMENT ====================
    
    def update_status(
        self,
        task_id: uuid.UUID,
        status: TaskStatus
    ) -> Optional[Task]:
        """
        Update task status.
        
        Args:
            task_id: Task ID
            status: New task status
            
        Returns:
            Updated task or None if not found
        """
        task = self.get_by_id(task_id)
        if task:
            task.status = status
            if status == TaskStatus.DONE:
                task.completed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(task)
        return task
    
    # ==================== ASSIGNMENT MANAGEMENT ====================
    
    def add_assignee(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        is_primary: bool = False
    ) -> TaskAssignee:
        """
        Add an assignee to task.
        
        Args:
            task_id: Task ID
            user_id: User ID
            is_primary: Whether this is the primary assignee
            
        Returns:
            Created TaskAssignee instance
        """
        assignee = TaskAssignee(
            task_id=task_id,
            user_id=user_id,
            is_primary=is_primary
        )
        self.db.add(assignee)
        self.db.commit()
        self.db.refresh(assignee)
        return assignee
    
    def remove_assignee(self, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Remove assignee from task.
        
        Args:
            task_id: Task ID
            user_id: User ID
            
        Returns:
            True if removed, False if not found
        """
        assignee = (
            self.db.query(TaskAssignee)
            .filter(
                and_(
                    TaskAssignee.task_id == task_id,
                    TaskAssignee.user_id == user_id
                )
            )
            .first()
        )
        
        if assignee:
            self.db.delete(assignee)
            self.db.commit()
            return True
        return False
    
    def get_assignees(self, task_id: uuid.UUID) -> List[TaskAssignee]:
        """
        Get all assignees for a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            List of task assignees
        """
        return (
            self.db.query(TaskAssignee)
            .filter(TaskAssignee.task_id == task_id)
            .all()
        )
    
    def get_primary_assignee(self, task_id: uuid.UUID) -> Optional[TaskAssignee]:
        """
        Get primary assignee for a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Primary TaskAssignee or None if not found
        """
        return (
            self.db.query(TaskAssignee)
            .filter(
                and_(
                    TaskAssignee.task_id == task_id,
                    TaskAssignee.is_primary == True
                )
            )
            .first()
        )
    
    # ==================== STATISTICS ====================
    
    def count_by_status(self, project_id: uuid.UUID, status: TaskStatus) -> int:
        """
        Count tasks by status.
        
        Args:
            project_id: Project ID
            status: Task status
            
        Returns:
            Number of tasks with given status
        """
        return (
            self.db.query(func.count(Task.id))
            .filter(
                and_(
                    Task.project_id == project_id,
                    Task.status == status
                )
            )
            .scalar() or 0
        )
    
    def get_status_distribution(self, project_id: uuid.UUID) -> Dict[str, int]:
        """
        Get distribution of tasks by status.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with status: count pairs
        """
        results = (
            self.db.query(
                Task.status,
                func.count(Task.id).label('count')
            )
            .filter(Task.project_id == project_id)
            .group_by(Task.status)
            .all()
        )
        
        return {
            str(status): count
            for status, count in results
        }
    
    def get_project_stats(self, project_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get comprehensive project task statistics.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with task statistics
        """
        total = (
            self.db.query(func.count(Task.id))
            .filter(Task.project_id == project_id)
            .scalar() or 0
        )
        
        completed = self.count_by_status(project_id, TaskStatus.DONE)
        
        return {
            "total_tasks": total,
            "todo": self.count_by_status(project_id, TaskStatus.TODO),
            "in_progress": self.count_by_status(project_id, TaskStatus.IN_PROGRESS),
            "in_review": self.count_by_status(project_id, TaskStatus.IN_REVIEW),
            "done": completed,
            "completion_percentage": round((completed / total * 100) if total > 0 else 0, 2),
            "overdue_count": len(self.get_overdue_tasks(project_id)),
        }
    
    def count_user_assigned_tasks(self, user_id: uuid.UUID) -> int:
        """
        Count tasks assigned to user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of assigned tasks
        """
        return (
            self.db.query(func.count(Task.id))
            .join(TaskAssignee)
            .filter(
                and_(
                    TaskAssignee.user_id == user_id,
                    Task.status != TaskStatus.DONE
                )
            )
            .scalar() or 0
        )


class SubtaskRepository(BaseRepository[Subtask]):
    """Repository for Subtask model."""
    
    def __init__(self, db: Session):
        super().__init__(Subtask, db)
    
    def get_task_subtasks(
        self,
        task_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Subtask]:
        """
        Get all subtasks for a task.
        
        Args:
            task_id: Task ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of subtasks
        """
        return (
            self.db.query(Subtask)
            .filter(Subtask.task_id == task_id)
            .order_by(Subtask.order.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_completed(self, task_id: uuid.UUID) -> int:
        """
        Count completed subtasks.
        
        Args:
            task_id: Task ID
            
        Returns:
            Number of completed subtasks
        """
        return (
            self.db.query(func.count(Subtask.id))
            .filter(
                and_(
                    Subtask.task_id == task_id,
                    Subtask.is_completed == True
                )
            )
            .scalar() or 0
        )
    
    def toggle_completion(self, subtask_id: uuid.UUID) -> Optional[Subtask]:
        """
        Toggle subtask completion status.
        
        Args:
            subtask_id: Subtask ID
            
        Returns:
            Updated subtask or None if not found
        """
        subtask = self.get_by_id(subtask_id)
        if subtask:
            subtask.is_completed = not subtask.is_completed
            self.db.commit()
            self.db.refresh(subtask)
        return subtask
