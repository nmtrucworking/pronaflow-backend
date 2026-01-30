"""
Entity Models for Functional Module 4 & 5: Task Management & Execution.
Provides Task, TaskList, Subtask, TaskAssignee, TaskDependency, ChecklistItem models.
Ref: docs/docs - PronaFlow React&FastAPI/02-Architeture/Entities/Task*.md
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Index, Table, Column, Date, Boolean, Text, Integer, Float, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin, AuditMixin
from app.db.enums import TaskPriority, TaskStatus

if TYPE_CHECKING:
    from app.db.models.users import User
    from app.db.models.projects import Project


# ======= Association Tables =======
task_assignees_association = Table(
    'task_assignees_association',
    Base.metadata,
    Column('task_id', UUID(as_uuid=True), ForeignKey('tasks.id'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
)

task_watchers_association = Table(
    'task_watchers_association',
    Base.metadata,
    Column('task_id', UUID(as_uuid=True), ForeignKey('tasks.id'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
)


# ======= TaskAssignee Table (Explicit N-N) =======
class TaskAssignee(Base, TimestampMixin):
    """
    TaskAssignee Model - Explicit N-N relationship between Tasks and Users.
    Supports multiple assignees per task with primary assignee designation.
    Ref: Entities/TaskAssignee.md
    """
    __tablename__ = "task_assignees"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for task assignee"
    )

    # Foreign Keys
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('tasks.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to task"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to user"
    )

    # Assignee Properties
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this is the primary assignee"
    )

    # Relationships
    task: Mapped["Task"] = relationship(foreign_keys=[task_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    # Indexes
    __table_args__ = (
        Index('ix_task_assignees_task_id', 'task_id'),
        Index('ix_task_assignees_user_id', 'user_id'),
        Index('ix_task_assignees_is_primary', 'is_primary'),
    )


# ======= Entity Tables =======

class TaskList(Base, TimestampMixin):
    """
    TaskList Model - Container cấp 2 trong WBS (Work Breakdown Structure).
    Groups tasks into lists within a project.
    Ref: Entities/TaskList.md
    """
    __tablename__ = "task_lists"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for task list"
    )

    # Foreign Key
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to project"
    )

    # Basic Information
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Task list name"
    )

    # Ordering
    position: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Position for drag & drop ordering"
    )

    # Status
    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether task list is archived"
    )

    # Relationships
    project: Mapped["Project"] = relationship(foreign_keys=[project_id])
    tasks: Mapped[List["Task"]] = relationship(back_populates="task_list", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_task_lists_project_id', 'project_id'),
        Index('ix_task_lists_position', 'position'),
        Index('ix_task_lists_is_archived', 'is_archived'),
    )


class Task(Base, AuditMixin):
    """
    Task Model - Đơn vị thực thi trung tâm (Central execution unit).
    Represents a task within a task list.
    Ref: Entities/Task.md
    """
    __tablename__ = "tasks"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for task"
    )

    # Foreign Keys
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to project"
    )

    task_list_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('task_lists.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to task list"
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        comment="User who created the task"
    )

    # Basic Information
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Task title"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Task description (rich-text or markdown)"
    )

    # Task Status
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus),
        default=TaskStatus.NOT_STARTED,
        nullable=False,
        index=True,
        comment="Task status"
    )

    # Priority
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(TaskPriority),
        default=TaskPriority.MEDIUM,
        nullable=False,
        index=True,
        comment="Task priority level"
    )

    # Milestone Flag
    is_milestone: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this task is a milestone"
    )

    # Planned Dates
    planned_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Planned start date/time"
    )

    planned_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Planned end date/time"
    )

    # Actual Dates (Auto)
    actual_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Auto-set when task moves to IN_PROGRESS"
    )

    actual_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Auto-set when task moves to DONE"
    )

    # Estimation
    estimated_hours: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Estimated hours to complete task"
    )

    # Relationships
    project: Mapped["Project"] = relationship(foreign_keys=[project_id])
    task_list: Mapped["TaskList"] = relationship(back_populates="tasks", foreign_keys=[task_list_id])
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    assignees: Mapped[List["User"]] = relationship(secondary=task_assignees_association)
    watchers: Mapped[List["User"]] = relationship(secondary=task_watchers_association)
    subtasks: Mapped[List["Subtask"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    comments: Mapped[List["Comment"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    dependencies: Mapped[List["TaskDependency"]] = relationship(back_populates="task", foreign_keys="TaskDependency.task_id", cascade="all, delete-orphan")
    dependent_tasks: Mapped[List["TaskDependency"]] = relationship(back_populates="depends_on_task", foreign_keys="TaskDependency.depends_on_task_id")
    checklist_items: Mapped[List["ChecklistItem"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    files: Mapped[List["File"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    time_entries: Mapped[List["TimeEntry"]] = relationship(back_populates="task", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_tasks_project_id', 'project_id'),
        Index('ix_tasks_task_list_id', 'task_list_id'),
        Index('ix_tasks_status', 'status'),
        Index('ix_tasks_priority', 'priority'),
        Index('ix_tasks_created_by', 'created_by'),
    )


class Subtask(Base, TimestampMixin):
    """
    Subtask Model - Checklist chi tiết (Detailed checklist items).
    Represents a checklist item within a task.
    Ref: Entities/Subtask.md
    """
    __tablename__ = "subtasks"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for subtask"
    )

    # Foreign Keys
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('tasks.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to parent task"
    )

    assignee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        comment="Optional assignee for subtask"
    )

    # Basic Information
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Subtask title"
    )

    # Status
    is_done: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether subtask is completed"
    )

    # Ordering
    position: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Position for ordering"
    )

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="subtasks", foreign_keys=[task_id])
    assignee: Mapped[Optional["User"]] = relationship(foreign_keys=[assignee_id])

    # Indexes
    __table_args__ = (
        Index('ix_subtasks_task_id', 'task_id'),
        Index('ix_subtasks_assignee_id', 'assignee_id'),
        Index('ix_subtasks_position', 'position'),
    )


class TaskDependency(Base, TimestampMixin):
    """
    TaskDependency Model - Task dependencies and relationships.
    Manages task-to-task dependencies (e.g., task A depends on task B).
    """
    __tablename__ = "task_dependencies"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for task dependency"
    )

    # Foreign Keys
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('tasks.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Task that has the dependency"
    )

    depends_on_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('tasks.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Task that must be completed first"
    )

    # Dependency Type
    dependency_type: Mapped[str] = mapped_column(
        SQLEnum('BLOCKS', 'BLOCKED_BY', 'RELATED_TO', 'DUPLICATES', name='dependency_type'),
        default='BLOCKS',
        nullable=False,
        comment="Type of dependency relationship"
    )

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="dependencies", foreign_keys=[task_id])
    depends_on_task: Mapped["Task"] = relationship(back_populates="dependent_tasks", foreign_keys=[depends_on_task_id])



class Comment(Base, TimestampMixin):
    """
    Comment Model - Nested comments on tasks (Module 6).
    Supports threaded discussions with self-referencing parent-child relationships.
    Ref: Entities/Comment.md
    """
    __tablename__ = "comments"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for comment"
    )

    # Foreign Keys
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('tasks.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to task (context)"
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="User who wrote the comment"
    )

    parent_comment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('comments.id', ondelete='CASCADE'),
        nullable=True,
        comment="Parent comment for nested replies (NULL = root)"
    )

    # Content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Comment content (rich-text HTML/JSON)"
    )

    # Edit Tracking
    is_edited: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether comment has been edited"
    )

    edited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of last edit"
    )

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="comments", foreign_keys=[task_id])
    author: Mapped["User"] = relationship(foreign_keys=[author_id])
    parent_comment: Mapped[Optional["Comment"]] = relationship(
        back_populates="replies",
        remote_side=[id],
        foreign_keys=[parent_comment_id]
    )
    replies: Mapped[List["Comment"]] = relationship(
        back_populates="parent_comment",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index('ix_comments_task_id', 'task_id'),
        Index('ix_comments_author_id', 'author_id'),
        Index('ix_comments_parent_comment_id', 'parent_comment_id'),
    )


class File(Base, TimestampMixin):
    """
    File Model - File attachments on tasks (Module 7).
    Manages file uploads and versions.
    Ref: Entities/File.md
    """
    __tablename__ = "files"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for file"
    )

    # Foreign Keys
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('tasks.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to task (context)"
    )

    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        comment="User who uploaded the file"
    )

    # File Properties
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Original filename"
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="MIME type (e.g., image/png)"
    )

    size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="File size in bytes"
    )

    current_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Current version number"
    )

    storage_tier: Mapped[str] = mapped_column(
        SQLEnum('HOT', 'COLD', name='storage_tier'),
        default='HOT',
        nullable=False,
        comment="Storage tier (HOT = frequently accessed, COLD = archived)"
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Path to file in storage (S3, local, etc.)"
    )

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="files", foreign_keys=[task_id])
    uploader: Mapped["User"] = relationship(foreign_keys=[uploaded_by])
    versions: Mapped[List["FileVersion"]] = relationship(back_populates="file", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_files_task_id', 'task_id'),
        Index('ix_files_uploaded_by', 'uploaded_by'),
    )


class FileVersion(Base, TimestampMixin):
    """
    FileVersion Model - Version history for files.
    Tracks different versions of uploaded files.
    """
    __tablename__ = "file_versions"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for file version"
    )

    # Foreign Keys
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('files.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to file"
    )

    # Version Information
    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Version number"
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Path to this version in storage"
    )

    size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="File size of this version"
    )

    # Relationships
    file: Mapped["File"] = relationship(back_populates="versions", foreign_keys=[file_id])


class TimeEntry(Base, TimestampMixin):
    """
    TimeEntry Model - Time tracking entries for tasks.
    Tracks work hours spent on tasks.
    """
    __tablename__ = "time_entries"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for time entry"
    )

    # Foreign Keys
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('tasks.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to task"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="User who logged the time"
    )

    # Time Information
    hours_spent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Hours spent on this task"
    )

    date_logged: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Date when time was logged"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional description of work done"
    )

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="time_entries", foreign_keys=[task_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    # Indexes
    __table_args__ = (
        Index('ix_time_entries_task_id', 'task_id'),
        Index('ix_time_entries_user_id', 'user_id'),
        Index('ix_time_entries_date_logged', 'date_logged'),
    )


class Timesheet(Base, TimestampMixin):
    """
    Timesheet Model - Aggregated time tracking for users by period.
    Summarizes time entries into weekly/periodic timesheets for approval workflow.
    Ref: Entities/Timesheet.md
    """
    __tablename__ = "timesheets"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for timesheet"
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to user"
    )

    # Period Information
    period_start: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
        comment="Start date of timesheet period"
    )

    period_end: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
        comment="End date of timesheet period"
    )

    # Aggregated Data
    total_hours: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        comment="Total hours logged in this period"
    )

    # Status for Approval Workflow
    status: Mapped[str] = mapped_column(
        SQLEnum('DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', name='timesheet_status'),
        default='DRAFT',
        nullable=False,
        comment="Timesheet status (DRAFT / SUBMITTED / APPROVED / REJECTED)"
    )

    # Submission Information
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When timesheet was submitted"
    )

    # Relationships
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    # Indexes
    __table_args__ = (
        Index('ix_timesheets_user_id', 'user_id'),
        Index('ix_timesheets_period_start', 'period_start'),
        Index('ix_timesheets_period_end', 'period_end'),
        Index('ix_timesheets_status', 'status'),
    )
