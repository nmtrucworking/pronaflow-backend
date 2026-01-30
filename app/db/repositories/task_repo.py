"""
Task Repository - Database access for Task model and related models.
"""
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.db.models.tasks import Task, TaskList, Subtask, TaskAssignee, Comment, File, TimeEntry, Timesheet
from app.db.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Repository for Task model with specialized queries."""

    def __init__(self, session: Session):
        super().__init__(session, Task)

    def get_by_project(self, project_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks in a project."""
        return self.session.execute(
            select(Task)
            .where(Task.project_id == project_id)
            .offset(skip)
            .limit(limit)
        ).scalars().all()

    def get_by_task_list(self, task_list_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks in a task list."""
        return self.session.execute(
            select(Task)
            .where(Task.task_list_id == task_list_id)
            .offset(skip)
            .limit(limit)
        ).scalars().all()

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks with given status."""
        return self.session.execute(
            select(Task)
            .where(Task.status == status)
            .offset(skip)
            .limit(limit)
        ).scalars().all()

    def get_assigned_to(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks assigned to a user."""
        return self.session.execute(
            select(Task)
            .join(Task.assignees)
            .where(Task.assignees.id == user_id)
            .offset(skip)
            .limit(limit)
        ).scalars().all()

    def get_by_priority(self, priority: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks with given priority."""
        return self.session.execute(
            select(Task)
            .where(Task.priority == priority)
            .offset(skip)
            .limit(limit)
        ).scalars().all()


class TaskListRepository(BaseRepository[TaskList]):
    """Repository for TaskList model."""

    def __init__(self, session: Session):
        super().__init__(session, TaskList)

    def get_by_project(self, project_id: uuid.UUID) -> List[TaskList]:
        """Get all task lists in a project."""
        return self.session.execute(
            select(TaskList)
            .where(TaskList.project_id == project_id)
            .order_by(TaskList.position)
        ).scalars().all()


class SubtaskRepository(BaseRepository[Subtask]):
    """Repository for Subtask model."""

    def __init__(self, session: Session):
        super().__init__(session, Subtask)

    def get_by_task(self, task_id: uuid.UUID) -> List[Subtask]:
        """Get all subtasks for a task."""
        return self.session.execute(
            select(Subtask)
            .where(Subtask.task_id == task_id)
            .order_by(Subtask.position)
        ).scalars().all()

    def get_completed(self, task_id: uuid.UUID) -> int:
        """Count completed subtasks for a task."""
        return self.session.query(Subtask).filter(
            and_(Subtask.task_id == task_id, Subtask.is_done == True)
        ).count()


class CommentRepository(BaseRepository[Comment]):
    """Repository for Comment model."""

    def __init__(self, session: Session):
        super().__init__(session, Comment)

    def get_by_task(self, task_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Get all root comments for a task."""
        return self.session.execute(
            select(Comment)
            .where(and_(Comment.task_id == task_id, Comment.parent_comment_id == None))
            .order_by(Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).scalars().all()

    def get_replies(self, parent_comment_id: uuid.UUID) -> List[Comment]:
        """Get all replies to a comment."""
        return self.session.execute(
            select(Comment)
            .where(Comment.parent_comment_id == parent_comment_id)
            .order_by(Comment.created_at)
        ).scalars().all()


class FileRepository(BaseRepository[File]):
    """Repository for File model."""

    def __init__(self, session: Session):
        super().__init__(session, File)

    def get_by_task(self, task_id: uuid.UUID) -> List[File]:
        """Get all files for a task."""
        return self.session.execute(
            select(File)
            .where(File.task_id == task_id)
            .order_by(File.created_at.desc())
        ).scalars().all()


class TimeEntryRepository(BaseRepository[TimeEntry]):
    """Repository for TimeEntry model."""

    def __init__(self, session: Session):
        super().__init__(session, TimeEntry)

    def get_by_task(self, task_id: uuid.UUID) -> List[TimeEntry]:
        """Get all time entries for a task."""
        return self.session.execute(
            select(TimeEntry)
            .where(TimeEntry.task_id == task_id)
            .order_by(TimeEntry.date_logged.desc())
        ).scalars().all()

    def get_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[TimeEntry]:
        """Get all time entries for a user."""
        return self.session.execute(
            select(TimeEntry)
            .where(TimeEntry.user_id == user_id)
            .order_by(TimeEntry.date_logged.desc())
            .offset(skip)
            .limit(limit)
        ).scalars().all()

    def get_total_hours(self, task_id: uuid.UUID) -> float:
        """Get total hours logged for a task."""
        result = self.session.query(TimeEntry).filter(
            TimeEntry.task_id == task_id
        ).all()
        return sum(entry.hours_spent for entry in result)


class TaskAssigneeRepository(BaseRepository[TaskAssignee]):
    """Repository for TaskAssignee model."""

    def __init__(self, session: Session):
        super().__init__(session, TaskAssignee)

    def get_by_task(self, task_id: uuid.UUID) -> List[TaskAssignee]:
        """Get all assignees for a task."""
        return self.session.execute(
            select(TaskAssignee)
            .where(TaskAssignee.task_id == task_id)
        ).scalars().all()

    def get_primary_assignee(self, task_id: uuid.UUID) -> Optional[TaskAssignee]:
        """Get primary assignee for a task."""
        return self.session.execute(
            select(TaskAssignee)
            .where(and_(TaskAssignee.task_id == task_id, TaskAssignee.is_primary == True))
        ).scalar_one_or_none()

    def get_tasks_for_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[TaskAssignee]:
        """Get all task assignments for a user."""
        return self.session.execute(
            select(TaskAssignee)
            .where(TaskAssignee.user_id == user_id)
            .offset(skip)
            .limit(limit)
        ).scalars().all()


class TimesheetRepository(BaseRepository[Timesheet]):
    """Repository for Timesheet model."""

    def __init__(self, session: Session):
        super().__init__(session, Timesheet)

    def get_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Timesheet]:
        """Get all timesheets for a user."""
        return self.session.execute(
            select(Timesheet)
            .where(Timesheet.user_id == user_id)
            .order_by(Timesheet.period_start.desc())
            .offset(skip)
            .limit(limit)
        ).scalars().all()

    def get_by_period(self, user_id: uuid.UUID, period_start, period_end) -> Optional[Timesheet]:
        """Get timesheet for a specific period."""
        return self.session.execute(
            select(Timesheet)
            .where(and_(
                Timesheet.user_id == user_id,
                Timesheet.period_start == period_start,
                Timesheet.period_end == period_end
            ))
        ).scalar_one_or_none()

    def get_by_status(self, user_id: uuid.UUID, status: str) -> List[Timesheet]:
        """Get timesheets by status for a user."""
        return self.session.execute(
            select(Timesheet)
            .where(and_(Timesheet.user_id == user_id, Timesheet.status == status))
            .order_by(Timesheet.period_start.desc())
        ).scalars().all()
