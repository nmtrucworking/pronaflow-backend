"""
Pydantic schemas for Task API
Request/Response models for task operations
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date
import uuid
from app.db.enums import TaskStatus, TaskPriority


# ==================== TASK SCHEMAS ====================

class TaskBase(BaseModel):
    """Base task schema with common fields."""
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: Optional[str] = Field(None, max_length=5000, description="Task description")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    status: TaskStatus = Field(default=TaskStatus.TODO)


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    project_id: uuid.UUID = Field(..., description="Project ID")
    task_list_id: uuid.UUID = Field(..., description="Task list ID")
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = Field(None, ge=0)


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = Field(None, ge=0)


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: uuid.UUID
    project_id: uuid.UUID
    task_list_id: uuid.UUID
    created_by: uuid.UUID
    due_date: Optional[date]
    estimated_hours: Optional[float]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskDetailResponse(TaskResponse):
    """Detailed task response with relationships."""
    assignees: List['TaskAssigneeResponse'] = Field(default_factory=list)
    subtask_count: int = 0
    comment_count: int = 0
    
    class Config:
        from_attributes = True


# ==================== TASK ASSIGNEE SCHEMAS ====================

class TaskAssigneeResponse(BaseModel):
    """Schema for task assignee."""
    id: uuid.UUID
    user_id: uuid.UUID
    user_email: str
    user_name: str
    is_primary: bool
    assigned_at: datetime
    
    class Config:
        from_attributes = True


class TaskAssigneeCreate(BaseModel):
    """Schema for assigning a user to task."""
    user_id: uuid.UUID = Field(..., description="User ID to assign")
    is_primary: bool = Field(default=False)


# ==================== SUBTASK SCHEMAS ====================

class SubtaskCreate(BaseModel):
    """Schema for creating a subtask."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)


class SubtaskUpdate(BaseModel):
    """Schema for updating a subtask."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    is_completed: Optional[bool] = None


class SubtaskResponse(BaseModel):
    """Schema for subtask response."""
    id: uuid.UUID
    task_id: uuid.UUID
    title: str
    description: Optional[str]
    is_completed: bool
    order: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== TASK LIST SCHEMAS ====================

class TaskListCreate(BaseModel):
    """Schema for creating a task list."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)


class TaskListUpdate(BaseModel):
    """Schema for updating a task list."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    order: Optional[int] = None


class TaskListResponse(BaseModel):
    """Schema for task list response."""
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    description: Optional[str]
    order: int
    task_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== LIST/PAGINATION SCHEMAS ====================

class TaskListResponse_Paginated(BaseModel):
    """Paginated task list response."""
    items: List[TaskResponse]
    total: int
    skip: int
    limit: int
    page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class SubtaskListResponse(BaseModel):
    """Paginated subtask list."""
    items: List[SubtaskResponse]
    total: int
    skip: int
    limit: int


class TaskListListResponse(BaseModel):
    """List of task lists in project."""
    items: List[TaskListResponse]
    total: int


# ==================== TASK STATISTICS SCHEMAS ====================

class TaskStatsResponse(BaseModel):
    """Schema for task statistics."""
    total_tasks: int
    todo: int
    in_progress: int
    in_review: int
    done: int
    completion_percentage: float
    overdue_count: int
    assigned_to_me: int


class TaskSearchResponse(BaseModel):
    """Task search results."""
    items: List[TaskResponse]
    query: str
    total: int


# ==================== BULK OPERATION SCHEMAS ====================

class BulkTaskStatusUpdate(BaseModel):
    """Schema for bulk status update."""
    task_ids: List[uuid.UUID]
    status: TaskStatus


class BulkTaskAssign(BaseModel):
    """Schema for bulk assignment."""
    task_ids: List[uuid.UUID]
    user_id: uuid.UUID
