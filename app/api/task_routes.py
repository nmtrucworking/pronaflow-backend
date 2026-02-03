"""
Task API Routes - Module 4
"""
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.db.models.users import User
from app.db.enums import TaskStatus, TaskPriority
from app.schemas.task_schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskDetailResponse,
    TaskListResponse,
    TaskListCreate,
    TaskListUpdate,
    TaskListItemResponse,
    SubtaskCreate,
    SubtaskUpdate,
    SubtaskResponse,
    TaskAssigneeCreate,
    TaskAssigneeResponse,
    BulkTaskStatusUpdate,
    BulkTaskAssign,
)
from app.services.task_service import TaskService, TaskListService
from app.utils.exceptions import PronaFlowException

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


# ==================== TASK LIST MANAGEMENT ====================

@router.post(
    "/lists",
    response_model=TaskListItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create task list",
    description="Create a new task list in project."
)
def create_task_list(
    data: TaskListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task list."""
    try:
        service = TaskListService(db)
        task_list = service.create_task_list(
            project_id=data.project_id,
            user_id=current_user.id,
            name=data.name,
            description=data.description,
        )
        return task_list
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put(
    "/lists/{task_list_id}",
    response_model=TaskListItemResponse,
    summary="Update task list",
    description="Update task list details."
)
def update_task_list(
    task_list_id: UUID,
    data: TaskListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update task list."""
    try:
        service = TaskListService(db)
        # Implementation: get task_list, check access, update
        # Placeholder for now
        raise HTTPException(status_code=501, detail="Not implemented")
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete(
    "/lists/{task_list_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task list",
    description="Delete task list."
)
def delete_task_list(
    task_list_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete task list."""
    try:
        service = TaskListService(db)
        service.delete_task_list(task_list_id, current_user.id)
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ==================== TASK CRUD ====================

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Create a new task in task list."
)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task."""
    try:
        service = TaskService(db)
        task = service.create_task(
            project_id=data.project_id,
            task_list_id=data.task_list_id,
            user_id=current_user.id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            due_date=data.due_date,
            estimated_hours=data.estimated_hours,
        )
        return task
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/{task_id}",
    response_model=TaskDetailResponse,
    summary="Get task",
    description="Get task details."
)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get task details."""
    try:
        service = TaskService(db)
        task = service.get_task(task_id, current_user.id)
        return task
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task",
    description="Update task details."
)
def update_task(
    task_id: UUID,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update task."""
    try:
        service = TaskService(db)
        task = service.update_task(
            task_id=task_id,
            user_id=current_user.id,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            due_date=data.due_date,
            estimated_hours=data.estimated_hours,
        )
        return task
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete task."
)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete task."""
    try:
        service = TaskService(db)
        service.delete_task(task_id, current_user.id)
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ==================== TASK QUERIES ====================

@router.get(
    "/list/{task_list_id}",
    response_model=TaskListResponse,
    summary="Get task list tasks",
    description="Get all tasks in task list."
)
def list_task_list_tasks(
    task_list_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tasks in task list."""
    try:
        service = TaskService(db)
        skip = (page - 1) * page_size
        tasks, total = service.list_task_list_tasks(
            task_list_id,
            current_user.id,
            skip=skip,
            limit=page_size
        )
        
        return TaskListResponse(
            items=tasks,
            total=total,
            page=page,
            page_size=page_size,
            has_next=skip + page_size < total,
            has_previous=page > 1,
        )
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/project/{project_id}",
    response_model=TaskListResponse,
    summary="Get project tasks",
    description="Get all tasks in project."
)
def list_project_tasks(
    project_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project tasks."""
    try:
        service = TaskService(db)
        skip = (page - 1) * page_size
        tasks, total = service.list_project_tasks(
            project_id,
            current_user.id,
            skip=skip,
            limit=page_size
        )
        
        return TaskListResponse(
            items=tasks,
            total=total,
            page=page,
            page_size=page_size,
            has_next=skip + page_size < total,
            has_previous=page > 1,
        )
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/user/assigned",
    response_model=TaskListResponse,
    summary="Get user assigned tasks",
    description="Get tasks assigned to current user."
)
def get_assigned_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user assigned tasks."""
    try:
        service = TaskService(db)
        skip = (page - 1) * page_size
        tasks, total = service.get_user_assigned_tasks(
            current_user.id,
            skip=skip,
            limit=page_size
        )
        
        return TaskListResponse(
            items=tasks,
            total=total,
            page=page,
            page_size=page_size,
            has_next=skip + page_size < total,
            has_previous=page > 1,
        )
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/search/{project_id}",
    response_model=TaskListResponse,
    summary="Search tasks",
    description="Search tasks in project."
)
def search_tasks(
    project_id: UUID,
    query: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search tasks."""
    try:
        service = TaskService(db)
        skip = (page - 1) * page_size
        tasks, total = service.search_tasks(
            project_id,
            current_user.id,
            query,
            skip=skip,
            limit=page_size
        )
        
        return TaskListResponse(
            items=tasks,
            total=total,
            page=page,
            page_size=page_size,
            has_next=skip + page_size < total,
            has_previous=page > 1,
        )
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ==================== STATUS MANAGEMENT ====================

@router.put(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Update task status",
    description="Update task status."
)
def update_status(
    task_id: UUID,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update task status."""
    try:
        service = TaskService(db)
        task = service.update_status(
            task_id,
            current_user.id,
            TaskStatus(data.get("status"))
        )
        return task
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/project/{project_id}/overdue",
    response_model=TaskListResponse,
    summary="Get overdue tasks",
    description="Get overdue tasks in project."
)
def get_overdue_tasks(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get overdue tasks."""
    try:
        service = TaskService(db)
        tasks = service.get_overdue_tasks(project_id, current_user.id)
        
        return TaskListResponse(
            items=tasks,
            total=len(tasks),
            page=1,
            page_size=len(tasks),
            has_next=False,
            has_previous=False,
        )
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ==================== ASSIGNMENT MANAGEMENT ====================

@router.post(
    "/{task_id}/assignees",
    response_model=TaskAssigneeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign task",
    description="Assign task to user."
)
def assign_task(
    task_id: UUID,
    data: TaskAssigneeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assign task to user."""
    try:
        service = TaskService(db)
        assignee = service.assign_task(
            task_id,
            current_user.id,
            data.user_id,
            is_primary=data.is_primary,
        )
        return assignee
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/{task_id}/assignees",
    response_model=list[TaskAssigneeResponse],
    summary="Get task assignees",
    description="Get all assignees for task."
)
def get_assignees(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get task assignees."""
    try:
        service = TaskService(db)
        assignees = service.get_assignees(task_id, current_user.id)
        return assignees
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete(
    "/{task_id}/assignees/{assignee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unassign task",
    description="Remove assignee from task."
)
def unassign_task(
    task_id: UUID,
    assignee_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unassign task."""
    try:
        service = TaskService(db)
        service.unassign_task(task_id, current_user.id, assignee_id)
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ==================== BULK OPERATIONS ====================

@router.put(
    "/bulk/status",
    summary="Bulk update status",
    description="Update status for multiple tasks."
)
def bulk_update_status(
    data: BulkTaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk update task status."""
    try:
        service = TaskService(db)
        # Implementation: update status for each task in data.task_ids
        # Placeholder for now
        raise HTTPException(status_code=501, detail="Not implemented")
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post(
    "/bulk/assign",
    summary="Bulk assign tasks",
    description="Assign multiple tasks to user."
)
def bulk_assign_tasks(
    data: BulkTaskAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk assign tasks."""
    try:
        service = TaskService(db)
        # Implementation: assign each task in data.task_ids to data.user_id
        # Placeholder for now
        raise HTTPException(status_code=501, detail="Not implemented")
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ==================== STATISTICS ====================

@router.get(
    "/project/{project_id}/stats",
    summary="Get project task statistics",
    description="Get task statistics for project."
)
def get_project_stats(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project task statistics."""
    try:
        service = TaskService(db)
        stats = service.get_project_stats(project_id, current_user.id)
        return stats
    except PronaFlowException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
