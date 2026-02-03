"""
Service layer for Task management.
Handles business logic for Functional Module 4: Task Execution and Orchestration.
Ref: docs/01-Requirements/Functional-Modules/4 - Task Execution and Orchestration.md
"""
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models.tasks import (
    TaskList,
    Task,
    Subtask,
    TaskDependency,
    TaskAssignee,
    Comment,
    File,
)
from app.db.models.projects import Project
from app.db.models.projects_extended import ProjectMember
from app.db.enums import TaskStatus, ProjectRole
from app.schemas.task import (
    TaskListCreate,
    TaskListUpdate,
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    SubtaskCreate,
    SubtaskUpdate,
    TaskDependencyCreate,
    CommentCreate,
    CommentUpdate,
    TaskBulkUpdate,
    TaskMove,
)
from app.services.project import ProjectService


class TaskListService:
    """Service for task list CRUD operations"""

    @staticmethod
    def create_task_list(
        db: Session,
        task_list_data: TaskListCreate,
        user_id: uuid.UUID,
    ) -> TaskList:
        """
        Create a new task list.
        
        Args:
            db: Database session
            task_list_data: Task list creation data
            user_id: User ID
            
        Returns:
            Created task list object
            
        Ref: Module 4 - Feature 2.1 - AC 1
        """
        # Check project access
        project = ProjectService.get_project(db, task_list_data.project_id, user_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )

        # Check if user is project member
        if not TaskListService._is_project_member(db, task_list_data.project_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project members can create task lists"
            )

        # Create task list
        task_list = TaskList(
            project_id=task_list_data.project_id,
            name=task_list_data.name.strip(),
            position=task_list_data.position,
        )

        db.add(task_list)
        db.commit()
        db.refresh(task_list)
        return task_list

    @staticmethod
    def get_task_list(
        db: Session,
        task_list_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[TaskList]:
        """Get task list by ID with permission check"""
        task_list = db.scalar(
            select(TaskList).where(TaskList.id == task_list_id)
        )

        if not task_list:
            return None

        # Check project access
        if not TaskListService._is_project_member(db, task_list.project_id, user_id):
            return None

        return task_list

    @staticmethod
    def list_task_lists(
        db: Session,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        include_archived: bool = False,
    ) -> List[TaskList]:
        """List all task lists in a project"""
        # Check project access
        if not TaskListService._is_project_member(db, project_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to project"
            )

        conditions = [TaskList.project_id == project_id]
        
        if not include_archived:
            conditions.append(TaskList.is_archived == False)

        task_lists = db.scalars(
            select(TaskList)
            .where(and_(*conditions))
            .order_by(TaskList.position)
        ).all()

        return list(task_lists)

    @staticmethod
    def update_task_list(
        db: Session,
        task_list_id: uuid.UUID,
        task_list_data: TaskListUpdate,
        user_id: uuid.UUID,
    ) -> TaskList:
        """Update task list"""
        task_list = TaskListService.get_task_list(db, task_list_id, user_id)
        if not task_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task list not found"
            )

        # Update fields
        update_data = task_list_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task_list, field, value)

        task_list.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task_list)
        return task_list

    @staticmethod
    def delete_task_list(
        db: Session,
        task_list_id: uuid.UUID,
        user_id: uuid.UUID,
        force: bool = False,
    ) -> None:
        """
        Delete task list.
        
        Ref: Module 4 - Feature 2.1 - AC 1 - Cannot delete if contains tasks
        """
        task_list = TaskListService.get_task_list(db, task_list_id, user_id)
        if not task_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task list not found"
            )

        # Check if contains tasks
        task_count = db.scalar(
            select(func.count()).select_from(Task).where(Task.task_list_id == task_list_id)
        )

        if task_count > 0 and not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete task list with {task_count} tasks. Move or delete tasks first."
            )

        db.delete(task_list)
        db.commit()

    @staticmethod
    def _is_project_member(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user is project member"""
        member = db.scalar(
            select(ProjectMember).where(
                and_(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id,
                )
            )
        )
        return member is not None


class TaskService:
    """Service for task CRUD and management operations"""

    @staticmethod
    def create_task(
        db: Session,
        task_data: TaskCreate,
        user_id: uuid.UUID,
    ) -> Task:
        """
        Create a new task.
        
        Args:
            db: Database session
            task_data: Task creation data
            user_id: User ID (creator)
            
        Returns:
            Created task object
            
        Ref: Module 4 - Feature 2.2 - AC 1 & AC 2
        """
        # Verify task list exists and user has access
        task_list = TaskListService.get_task_list(db, task_data.task_list_id, user_id)
        if not task_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task list not found or access denied"
            )

        # Check if user is project member
        if not TaskListService._is_project_member(db, task_data.project_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project members can create tasks"
            )

        # Milestone validation
        if task_data.is_milestone and task_data.estimated_hours:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Milestones cannot have estimated hours (duration = 0)"
            )

        # Create task
        task = Task(
            project_id=task_data.project_id,
            task_list_id=task_data.task_list_id,
            created_by=user_id,
            title=task_data.title.strip(),
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            is_milestone=task_data.is_milestone,
            planned_start=task_data.planned_start,
            planned_end=task_data.planned_end,
            estimated_hours=task_data.estimated_hours,
        )

        db.add(task)
        db.flush()

        # Add assignees if provided
        if task_data.assignee_ids:
            for assignee_id in task_data.assignee_ids:
                is_primary = (assignee_id == task_data.primary_assignee_id)
                assignee = TaskAssignee(
                    task_id=task.id,
                    user_id=assignee_id,
                    is_primary=is_primary,
                )
                db.add(assignee)

        db.commit()
        db.refresh(task)
        
        # TODO: Send notification to assignees (Module 7)
        
        return task

    @staticmethod
    def get_task(
        db: Session,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[Task]:
        """Get task by ID with permission check"""
        task = db.scalar(
            select(Task).where(Task.id == task_id)
        )

        if not task:
            return None

        # Check project access
        if not TaskListService._is_project_member(db, task.project_id, user_id):
            return None

        return task

    @staticmethod
    def list_tasks(
        db: Session,
        project_id: Optional[uuid.UUID] = None,
        task_list_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        status: Optional[TaskStatus] = None,
        assignee_id: Optional[uuid.UUID] = None,
        is_milestone: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Task], int]:
        """List tasks with filters"""
        conditions = []

        if project_id:
            conditions.append(Task.project_id == project_id)
            # Check access
            if user_id and not TaskListService._is_project_member(db, project_id, user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to project"
                )

        if task_list_id:
            conditions.append(Task.task_list_id == task_list_id)

        if status:
            conditions.append(Task.status == status)

        if is_milestone is not None:
            conditions.append(Task.is_milestone == is_milestone)

        if assignee_id:
            # Join with TaskAssignee
            conditions.append(
                Task.id.in_(
                    select(TaskAssignee.task_id).where(TaskAssignee.user_id == assignee_id)
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(Task).where(and_(*conditions))
        total = db.scalar(count_stmt)

        # Get tasks
        stmt = (
            select(Task)
            .where(and_(*conditions))
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        tasks = db.scalars(stmt).all()

        return list(tasks), total

    @staticmethod
    def update_task(
        db: Session,
        task_id: uuid.UUID,
        task_data: TaskUpdate,
        user_id: uuid.UUID,
    ) -> Task:
        """
        Update task.
        
        Ref: Module 4 - Feature 2.2 - AC 2
        """
        task = TaskService.get_task(db, task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Check if user can edit task
        if not TaskService._can_edit_task(db, task, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this task"
            )

        # Update fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task_status(
        db: Session,
        task_id: uuid.UUID,
        status_data: TaskStatusUpdate,
        user_id: uuid.UUID,
    ) -> Task:
        """
        Update task status with automatic actual date tracking.
        
        Ref: Module 4 - Business Rule 3.4 - Actual vs Planned
        """
        task = TaskService.get_task(db, task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        old_status = task.status
        new_status = status_data.status

        # Auto-set actual dates
        if new_status == TaskStatus.IN_PROGRESS and old_status != TaskStatus.IN_PROGRESS:
            if not task.actual_start:
                task.actual_start = datetime.utcnow()

        if new_status == TaskStatus.DONE and old_status != TaskStatus.DONE:
            if not task.actual_end:
                task.actual_end = datetime.utcnow()

        # Reset actual_end if moving away from DONE
        if old_status == TaskStatus.DONE and new_status != TaskStatus.DONE:
            task.actual_end = None

        task.status = new_status
        task.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(
        db: Session,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """Delete task"""
        task = TaskService.get_task(db, task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Only creator or project manager can delete
        if not TaskService._can_delete_task(db, task, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only task creator or project manager can delete tasks"
            )

        db.delete(task)
        db.commit()

    @staticmethod
    def move_task(
        db: Session,
        task_id: uuid.UUID,
        move_data: TaskMove,
        user_id: uuid.UUID,
    ) -> Task:
        """
        Move task to different list or project.
        
        Ref: Module 4 - Feature 2.7 - AC 2
        """
        task = TaskService.get_task(db, task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if move_data.target_task_list_id:
            # Verify target task list exists and user has access
            target_list = TaskListService.get_task_list(db, move_data.target_task_list_id, user_id)
            if not target_list:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target task list not found"
                )
            task.task_list_id = move_data.target_task_list_id

        if move_data.target_project_id:
            # Verify target project exists and user has access
            target_project = ProjectService.get_project(db, move_data.target_project_id, user_id)
            if not target_project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target project not found"
                )
            task.project_id = move_data.target_project_id

        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def _can_edit_task(db: Session, task: Task, user_id: uuid.UUID) -> bool:
        """Check if user can edit task"""
        # Creator can always edit
        if task.created_by == user_id:
            return True

        # Assignees can edit
        assignee = db.scalar(
            select(TaskAssignee).where(
                and_(
                    TaskAssignee.task_id == task.id,
                    TaskAssignee.user_id == user_id,
                )
            )
        )
        if assignee:
            return True

        # Project manager can edit
        pm = db.scalar(
            select(ProjectMember).where(
                and_(
                    ProjectMember.project_id == task.project_id,
                    ProjectMember.user_id == user_id,
                    ProjectMember.role == ProjectRole.MANAGER,
                )
            )
        )
        return pm is not None

    @staticmethod
    def _can_delete_task(db: Session, task: Task, user_id: uuid.UUID) -> bool:
        """Check if user can delete task"""
        # Creator can delete
        if task.created_by == user_id:
            return True

        # Project manager can delete
        pm = db.scalar(
            select(ProjectMember).where(
                and_(
                    ProjectMember.project_id == task.project_id,
                    ProjectMember.user_id == user_id,
                    ProjectMember.role == ProjectRole.MANAGER,
                )
            )
        )
        return pm is not None


class SubtaskService:
    """Service for subtask management"""

    @staticmethod
    def create_subtask(
        db: Session,
        subtask_data: SubtaskCreate,
        user_id: uuid.UUID,
    ) -> Subtask:
        """
        Create subtask.
        
        Ref: Module 4 - Feature 2.3 - AC 1
        """
        # Verify parent task exists and user has access
        task = TaskService.get_task(db, subtask_data.task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent task not found"
            )

        # Verify assignee is a task assignee if provided
        if subtask_data.assignee_id:
            task_assignee = db.scalar(
                select(TaskAssignee).where(
                    and_(
                        TaskAssignee.task_id == subtask_data.task_id,
                        TaskAssignee.user_id == subtask_data.assignee_id,
                    )
                )
            )
            if not task_assignee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Subtask assignee must be assigned to parent task"
                )

        subtask = Subtask(
            task_id=subtask_data.task_id,
            title=subtask_data.title.strip(),
            assignee_id=subtask_data.assignee_id,
            position=subtask_data.position,
        )

        db.add(subtask)
        db.commit()
        db.refresh(subtask)
        return subtask

    @staticmethod
    def update_subtask(
        db: Session,
        subtask_id: uuid.UUID,
        subtask_data: SubtaskUpdate,
        user_id: uuid.UUID,
    ) -> Subtask:
        """Update subtask"""
        subtask = db.scalar(
            select(Subtask).where(Subtask.id == subtask_id)
        )

        if not subtask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subtask not found"
            )

        # Check access to parent task
        task = TaskService.get_task(db, subtask.task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Update fields
        update_data = subtask_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(subtask, field, value)

        subtask.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(subtask)
        return subtask

    @staticmethod
    def delete_subtask(
        db: Session,
        subtask_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """Delete subtask"""
        subtask = db.scalar(
            select(Subtask).where(Subtask.id == subtask_id)
        )

        if not subtask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subtask not found"
            )

        # Check access
        task = TaskService.get_task(db, subtask.task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        db.delete(subtask)
        db.commit()


class TaskDependencyService:
    """Service for task dependency management"""

    @staticmethod
    def create_dependency(
        db: Session,
        dependency_data: TaskDependencyCreate,
        user_id: uuid.UUID,
    ) -> TaskDependency:
        """
        Create task dependency with cycle detection.
        
        Ref: Module 4 - Feature 2.4 - AC 2
        """
        # Verify both tasks exist and user has access
        task = TaskService.get_task(db, dependency_data.task_id, user_id)
        predecessor = TaskService.get_task(db, dependency_data.depends_on_task_id, user_id)

        if not task or not predecessor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Check for circular dependency
        if TaskDependencyService._would_create_cycle(
            db, dependency_data.task_id, dependency_data.depends_on_task_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TASK_001: Circular dependency detected. Cannot create this dependency."
            )

        # Create dependency
        dependency = TaskDependency(
            task_id=dependency_data.task_id,
            depends_on_task_id=dependency_data.depends_on_task_id,
            dependency_type=dependency_data.dependency_type,
        )

        db.add(dependency)
        db.commit()
        db.refresh(dependency)
        return dependency

    @staticmethod
    def _would_create_cycle(
        db: Session,
        task_id: uuid.UUID,
        depends_on_task_id: uuid.UUID,
    ) -> bool:
        """
        Check if adding dependency would create a cycle using DFS.
        
        Returns True if cycle would be created.
        """
        visited = set()
        
        def dfs(current_id: uuid.UUID) -> bool:
            if current_id == task_id:
                return True
            if current_id in visited:
                return False
            
            visited.add(current_id)
            
            # Get all dependencies of current task
            dependencies = db.scalars(
                select(TaskDependency).where(TaskDependency.task_id == current_id)
            ).all()
            
            for dep in dependencies:
                if dfs(dep.depends_on_task_id):
                    return True
            
            return False
        
        return dfs(depends_on_task_id)

    @staticmethod
    def delete_dependency(
        db: Session,
        dependency_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """Delete task dependency"""
        dependency = db.scalar(
            select(TaskDependency).where(TaskDependency.id == dependency_id)
        )

        if not dependency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dependency not found"
            )

        # Check access to task
        task = TaskService.get_task(db, dependency.task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        db.delete(dependency)
        db.commit()


class CommentService:
    """Service for task comments"""

    @staticmethod
    def create_comment(
        db: Session,
        comment_data: CommentCreate,
        user_id: uuid.UUID,
    ) -> Comment:
        """Create comment and auto-add user as watcher"""
        # Verify task exists and user has access
        task = TaskService.get_task(db, comment_data.task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        comment = Comment(
            task_id=comment_data.task_id,
            user_id=user_id,
            content=comment_data.content,
        )

        db.add(comment)
        
        # TODO: Auto-add commenter as watcher (Module 4 - Feature 2.10 - AC 1)
        
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def update_comment(
        db: Session,
        comment_id: uuid.UUID,
        comment_data: CommentUpdate,
        user_id: uuid.UUID,
    ) -> Comment:
        """Update comment (only by author)"""
        comment = db.scalar(
            select(Comment).where(Comment.id == comment_id)
        )

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )

        # Only author can edit
        if comment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only comment author can edit"
            )

        comment.content = comment_data.content
        comment.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def delete_comment(
        db: Session,
        comment_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """Delete comment (author or PM)"""
        comment = db.scalar(
            select(Comment).where(Comment.id == comment_id)
        )

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )

        # Check permission
        task = TaskService.get_task(db, comment.task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Author or PM can delete
        if comment.user_id != user_id:
            if not TaskService._can_delete_task(db, task, user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only comment author or project manager can delete"
                )

        db.delete(comment)
        db.commit()
