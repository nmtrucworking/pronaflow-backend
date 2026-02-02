"""
Pydantic schemas for Task-related API requests and responses.
Implements schemas for Functional Module 4: Task Execution and Orchestration.
Ref: docs/01-Requirements/Functional-Modules/4 - Task Execution and Orchestration.md
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.db.enums import TaskStatus, TaskPriority


# ===== TaskList Schemas =====

class TaskListBase(BaseModel):
    """Base schema for task list"""
    name: str = Field(..., min_length=1, max_length=100, description="Task list name")


class TaskListCreate(TaskListBase):
    """
    Schema for creating a task list.
    Ref: Module 4 - Feature 2.1 - AC 1
    """
    project_id: UUID = Field(..., description="Project ID")
    position: Optional[int] = Field(default=0, description="Position for ordering")


class TaskListUpdate(BaseModel):
    """Schema for updating task list"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    position: Optional[int] = None


class TaskListResponse(TaskListBase):
    """Response schema for task list"""
    id: UUID
    project_id: UUID
    position: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    task_count: Optional[int] = Field(None, description="Number of tasks in list")

    class Config:
        from_attributes = True


class TaskListDetailResponse(TaskListResponse):
    """Detailed task list response with tasks"""
    pass


# ===== Task Schemas =====

class TaskBase(BaseModel):
    """Base schema for task"""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: Optional[TaskPriority] = Field(default=TaskPriority.MEDIUM)
    estimated_hours: Optional[float] = Field(None, ge=0, description="Estimated hours")
    is_milestone: Optional[bool] = Field(default=False, description="Whether task is a milestone")


class TaskCreate(TaskBase):
    """
    Schema for creating a task.
    Ref: Module 4 - Feature 2.2 - AC 1 & AC 2
    """
    project_id: UUID = Field(..., description="Project ID")
    task_list_id: UUID = Field(..., description="Task list ID (required)")
    status: Optional[TaskStatus] = Field(default=TaskStatus.TO_DO)
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    assignee_ids: Optional[List[UUID]] = Field(default_factory=list, description="List of assignee user IDs")
    primary_assignee_id: Optional[UUID] = Field(None, description="Primary assignee user ID")
    
    @field_validator('planned_end')
    @classmethod
    def validate_dates(cls, v, info):
        """Validate that planned_end >= planned_start if both are provided"""
        if v is not None and info.data.get('planned_start') is not None:
            if v < info.data['planned_start']:
                raise ValueError('planned_end must be >= planned_start')
        return v


class TaskUpdate(BaseModel):
    """
    Schema for updating task.
    Ref: Module 4 - Feature 2.2 - AC 2
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    is_milestone: Optional[bool] = None
    
    @field_validator('planned_end')
    @classmethod
    def validate_dates(cls, v, info):
        if v is not None and info.data.get('planned_start') is not None:
            if v < info.data['planned_start']:
                raise ValueError('planned_end must be >= planned_start')
        return v


class TaskStatusUpdate(BaseModel):
    """
    Schema for updating task status only.
    Ref: Module 4 - Feature 2.2
    """
    status: TaskStatus = Field(..., description="New task status")


class TaskResponse(TaskBase):
    """Response schema for task"""
    id: UUID
    project_id: UUID
    task_list_id: UUID
    status: TaskStatus
    created_by: UUID
    planned_start: Optional[datetime]
    planned_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskDetailResponse(TaskResponse):
    """Detailed task response with relationships"""
    assignee_count: Optional[int] = Field(None, description="Number of assignees")
    subtask_count: Optional[int] = Field(None, description="Number of subtasks")
    subtasks_completed: Optional[int] = Field(None, description="Number of completed subtasks")
    comment_count: Optional[int] = Field(None, description="Number of comments")
    attachment_count: Optional[int] = Field(None, description="Number of attachments")
    completion_percentage: Optional[float] = Field(None, description="% completion based on subtasks")


class TaskListResponse(BaseModel):
    """Paginated list of tasks"""
    total: int
    items: List[TaskResponse]


# ===== Task Assignment Schemas =====

class TaskAssignmentCreate(BaseModel):
    """
    Schema for assigning users to task.
    Ref: Module 4 - Feature 2.2 - AC 2
    """
    user_id: UUID = Field(..., description="User ID to assign")
    is_primary: Optional[bool] = Field(default=False, description="Set as primary assignee")


class TaskAssignmentAdd(BaseModel):
    """Schema for adding assignee to task"""
    user_id: UUID = Field(..., description="User ID to add")
    is_primary: Optional[bool] = Field(default=False, description="Set as primary assignee")


class TaskAssignmentRemove(BaseModel):
    """Schema for removing assignee from task"""
    user_id: UUID = Field(..., description="User ID to remove")


class TaskAssignmentResponse(BaseModel):
    """Response schema for task assignment"""
    id: UUID
    task_id: UUID
    user_id: UUID
    is_primary: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TaskBulkAssign(BaseModel):
    """Schema for bulk assigning users to task"""
    user_ids: List[UUID] = Field(..., min_length=1, description="List of user IDs")
    primary_user_id: Optional[UUID] = Field(None, description="Primary assignee ID")


# ===== Subtask Schemas =====

class SubtaskBase(BaseModel):
    """Base schema for subtask"""
    title: str = Field(..., min_length=1, max_length=255, description="Subtask title")


class SubtaskCreate(SubtaskBase):
    """
    Schema for creating subtask.
    Ref: Module 4 - Feature 2.3 - AC 1
    """
    task_id: UUID = Field(..., description="Parent task ID")
    assignee_id: Optional[UUID] = Field(None, description="Assignee user ID")
    position: Optional[int] = Field(default=0, description="Position for ordering")


class SubtaskUpdate(BaseModel):
    """Schema for updating subtask"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    is_completed: Optional[bool] = None
    assignee_id: Optional[UUID] = None
    position: Optional[int] = None


class SubtaskResponse(SubtaskBase):
    """Response schema for subtask"""
    id: UUID
    task_id: UUID
    is_completed: bool
    assignee_id: Optional[UUID]
    position: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Task Dependency Schemas =====

class TaskDependencyCreate(BaseModel):
    """
    Schema for creating task dependency.
    Ref: Module 4 - Feature 2.4 - AC 1
    """
    task_id: UUID = Field(..., description="Task ID (successor)")
    depends_on_task_id: UUID = Field(..., description="Predecessor task ID")
    dependency_type: Optional[str] = Field(default="FS", description="Dependency type (FS, SS, FF, SF)")


class TaskDependencyResponse(BaseModel):
    """Response schema for task dependency"""
    id: UUID
    task_id: UUID
    depends_on_task_id: UUID
    dependency_type: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Comment Schemas =====

class CommentBase(BaseModel):
    """Base schema for comment"""
    content: str = Field(..., min_length=1, description="Comment content")


class CommentCreate(CommentBase):
    """Schema for creating comment"""
    task_id: UUID = Field(..., description="Task ID")


class CommentUpdate(BaseModel):
    """Schema for updating comment"""
    content: str = Field(..., min_length=1)


class CommentResponse(CommentBase):
    """Response schema for comment"""
    id: UUID
    task_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== File/Attachment Schemas =====

class FileCreate(BaseModel):
    """Schema for file upload"""
    task_id: UUID = Field(..., description="Task ID")
    filename: str = Field(..., description="File name")
    file_path: str = Field(..., description="Storage path")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: Optional[str] = Field(None, description="MIME type")


class FileResponse(BaseModel):
    """Response schema for file"""
    id: UUID
    task_id: UUID
    filename: str
    file_path: str
    file_size: int
    mime_type: Optional[str]
    uploaded_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Watcher Schemas =====

class TaskWatcherAdd(BaseModel):
    """Schema for adding watcher to task"""
    user_id: UUID = Field(..., description="User ID to add as watcher")


class TaskWatcherResponse(BaseModel):
    """Response schema for task watcher"""
    task_id: UUID
    user_id: UUID


# ===== Bulk Operations Schemas =====

class TaskBulkUpdate(BaseModel):
    """
    Schema for bulk updating tasks.
    Ref: Module 4 - Feature 2.7 - AC 2
    """
    task_ids: List[UUID] = Field(..., min_length=1, description="List of task IDs")
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    task_list_id: Optional[UUID] = None
    assignee_ids: Optional[List[UUID]] = None


class TaskBulkDelete(BaseModel):
    """Schema for bulk deleting tasks"""
    task_ids: List[UUID] = Field(..., min_length=1, description="List of task IDs to delete")


# ===== Task Move Schemas =====

class TaskMove(BaseModel):
    """
    Schema for moving task to different list or project.
    Ref: Module 4 - Feature 2.7 - AC 2
    """
    target_task_list_id: Optional[UUID] = Field(None, description="Target task list ID")
    target_project_id: Optional[UUID] = Field(None, description="Target project ID")
    position: Optional[int] = Field(None, description="Position in target list")


# ===== Filter & Search Schemas =====

class TaskFilter(BaseModel):
    """Schema for task filtering"""
    project_id: Optional[UUID] = None
    task_list_id: Optional[UUID] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[UUID] = None
    is_milestone: Optional[bool] = None
    overdue: Optional[bool] = None
    search: Optional[str] = Field(None, description="Search in title and description")


# ===== Progress & Metrics Schemas =====

class TaskProgress(BaseModel):
    """Schema for task progress"""
    total_subtasks: int
    completed_subtasks: int
    completion_percentage: float
    is_overdue: bool
    days_overdue: Optional[int]
