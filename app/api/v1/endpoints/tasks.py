"""
API endpoints for Task management.
Implements Functional Module 4: Task Execution and Orchestration.
Ref: docs/01-Requirements/Functional-Modules/4 - Task Execution and Orchestration.md
"""
import uuid
from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.db.models.users import User
from app.db.enums import TaskStatus
from app.schemas.task import (
    # TaskList schemas
    TaskListCreate,
    TaskListUpdate,
    TaskListResponse,
    # Task schemas
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskResponse,
    TaskBulkUpdate,
    TaskMove,
    # Subtask schemas
    SubtaskCreate,
    SubtaskUpdate,
    SubtaskResponse,
    # Dependency schemas
    TaskDependencyCreate,
    TaskDependencyResponse,
    # Comment schemas
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    # File schemas
    FileResponse,
    # Assignment schemas
    TaskAssignmentAdd,
    TaskAssignmentRemove,
)
from app.services.task import (
    TaskListService,
    TaskService,
    SubtaskService,
    TaskDependencyService,
    CommentService,
)

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


# ===== TaskList Endpoints =====

@router.post("/lists", response_model=TaskListResponse, status_code=status.HTTP_201_CREATED)
def create_task_list(
    task_list_data: TaskListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new task list.
    
    Ref: Module 4 - Feature 2.1 - AC 1
    """
    task_list = TaskListService.create_task_list(db, task_list_data, current_user.id)
    return task_list


@router.get("/lists/{task_list_id}", response_model=TaskListResponse)
def get_task_list(
    task_list_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get task list by ID"""
    task_list = TaskListService.get_task_list(db, task_list_id, current_user.id)
    if not task_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task list not found"
        )
    return task_list


@router.get("/lists", response_model=List[TaskListResponse])
def list_task_lists(
    project_id: uuid.UUID = Query(..., description="Project ID"),
    include_archived: bool = Query(False, description="Include archived task lists"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all task lists in a project.
    
    Ref: Module 4 - Feature 2.1 - AC 1
    """
    task_lists = TaskListService.list_task_lists(
        db, project_id, current_user.id, include_archived
    )
    return task_lists


@router.patch("/lists/{task_list_id}", response_model=TaskListResponse)
def update_task_list(
    task_list_id: uuid.UUID,
    task_list_data: TaskListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update task list"""
    task_list = TaskListService.update_task_list(db, task_list_id, task_list_data, current_user.id)
    return task_list


@router.delete("/lists/{task_list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_list(
    task_list_id: uuid.UUID,
    force: bool = Query(False, description="Force delete even with tasks"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete task list.
    
    Ref: Module 4 - Feature 2.1 - AC 1 - Cannot delete if contains tasks (unless force=true)
    """
    TaskListService.delete_task_list(db, task_list_id, current_user.id, force)
    return None


# ===== Task Endpoints =====

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new task.
    
    Ref: Module 4 - Feature 2.2 - AC 1 & AC 2
    """
    task = TaskService.create_task(db, task_data, current_user.id)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get task by ID.
    
    Ref: Module 4 - Feature 2.2 - AC 1
    """
    task = TaskService.get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.get("/", response_model=dict)
def list_tasks(
    project_id: Optional[uuid.UUID] = Query(None, description="Filter by project"),
    task_list_id: Optional[uuid.UUID] = Query(None, description="Filter by task list"),
    status_filter: Optional[TaskStatus] = Query(None, alias="status", description="Filter by status"),
    assignee_id: Optional[uuid.UUID] = Query(None, description="Filter by assignee"),
    is_milestone: Optional[bool] = Query(None, description="Filter milestones"),
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(50, ge=1, le=100, description="Limit"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List tasks with filters and pagination.
    
    Ref: Module 4 - Feature 2.2 - AC 1
    """
    tasks, total = TaskService.list_tasks(
        db,
        project_id=project_id,
        task_list_id=task_list_id,
        user_id=current_user.id,
        status=status_filter,
        assignee_id=assignee_id,
        is_milestone=is_milestone,
        skip=skip,
        limit=limit,
    )
    
    return {
        "items": tasks,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: uuid.UUID,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update task.
    
    Ref: Module 4 - Feature 2.2 - AC 2
    """
    task = TaskService.update_task(db, task_id, task_data, current_user.id)
    return task


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: uuid.UUID,
    status_data: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update task status with automatic actual date tracking.
    
    Ref: Module 4 - Business Rule 3.4 - Actual vs Planned
    """
    task = TaskService.update_task_status(db, task_id, status_data, current_user.id)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete task"""
    TaskService.delete_task(db, task_id, current_user.id)
    return None


@router.post("/{task_id}/move", response_model=TaskResponse)
def move_task(
    task_id: uuid.UUID,
    move_data: TaskMove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Move task to different list or project.
    
    Ref: Module 4 - Feature 2.7 - AC 2
    """
    task = TaskService.move_task(db, task_id, move_data, current_user.id)
    return task


# ===== Subtask Endpoints =====

@router.post("/{task_id}/subtasks", response_model=SubtaskResponse, status_code=status.HTTP_201_CREATED)
def create_subtask(
    task_id: uuid.UUID,
    subtask_data: SubtaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create subtask.
    
    Ref: Module 4 - Feature 2.3 - AC 1
    """
    # Override task_id from path
    subtask_data.task_id = task_id
    subtask = SubtaskService.create_subtask(db, subtask_data, current_user.id)
    return subtask


@router.patch("/subtasks/{subtask_id}", response_model=SubtaskResponse)
def update_subtask(
    subtask_id: uuid.UUID,
    subtask_data: SubtaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update subtask"""
    subtask = SubtaskService.update_subtask(db, subtask_id, subtask_data, current_user.id)
    return subtask


@router.delete("/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subtask(
    subtask_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete subtask"""
    SubtaskService.delete_subtask(db, subtask_id, current_user.id)
    return None


# ===== Task Dependency Endpoints =====

@router.post("/{task_id}/dependencies", response_model=TaskDependencyResponse, status_code=status.HTTP_201_CREATED)
def create_task_dependency(
    task_id: uuid.UUID,
    dependency_data: TaskDependencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create task dependency with cycle detection.
    
    Ref: Module 4 - Feature 2.4 - AC 2
    """
    # Override task_id from path
    dependency_data.task_id = task_id
    dependency = TaskDependencyService.create_dependency(db, dependency_data, current_user.id)
    return dependency


@router.delete("/dependencies/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_dependency(
    dependency_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete task dependency"""
    TaskDependencyService.delete_dependency(db, dependency_id, current_user.id)
    return None


# ===== Comment Endpoints =====

@router.post("/{task_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    task_id: uuid.UUID,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create comment and auto-add user as watcher.
    
    Ref: Module 4 - Feature 2.10 - AC 1
    """
    # Override task_id from path
    comment_data.task_id = task_id
    comment = CommentService.create_comment(db, comment_data, current_user.id)
    return comment


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: uuid.UUID,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update comment (only by author)"""
    comment = CommentService.update_comment(db, comment_id, comment_data, current_user.id)
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete comment (author or PM)"""
    CommentService.delete_comment(db, comment_id, current_user.id)
    return None
