"""
API endpoints for Project management.
Provides REST API for Functional Module 3: Project Lifecycle Management.
Ref: docs/01-Requirements/Functional-Modules/3 - Project Lifecycle Management.md
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.db.models.users import User
from app.db.enums import ProjectStatus
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectStatusUpdate,
    ProjectResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectMemberCreate,
    ProjectMemberUpdate,
    ProjectMemberResponse,
    ProjectTemplateCreate,
    ProjectTemplateUpdate,
    ProjectTemplateResponse,
    ProjectFromTemplateCreate,
    ProjectBaselineCreate,
    ProjectBaselineResponse,
    ChangeRequestCreate,
    ChangeRequestUpdate,
    ChangeRequestApprove,
    ChangeRequestResponse,
    ProjectClone,
    ProjectHealthUpdate,
    ProjectMetricsResponse,
)
from app.services.project import (
    ProjectService,
    ProjectMemberService,
    ProjectTemplateService,
    ProjectChangeRequestService,
)

router = APIRouter(prefix="/v1/projects", tags=["projects"])


# ===== Project CRUD Operations =====

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new project",
)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new project.
    
    **AC 1 - Create Project Validation:**
    - User inputs Title (Required, Max 100 chars), Description (Optional)
    - Start Date and End Date (End Date >= Start Date if provided)
    - Default state: NOT_STARTED
    - Creator becomes Project Manager automatically
    
    Ref: Module 3 - Feature 2.1 - AC 1
    """
    project = ProjectService.create_project(db, project_data, current_user.id)
    return project


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List projects in workspace",
)
def list_projects(
    workspace_id: UUID = Query(..., description="Workspace ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[ProjectStatus] = Query(None, description="Filter by status"),
    archived: bool = Query(False, description="Include archived projects"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all projects in a workspace.
    
    - Public projects are visible to all workspace members
    - Private projects are only visible to members
    - Workspace admins can see all projects
    
    Ref: Module 3 - Feature 2.4
    """
    projects, total = ProjectService.list_projects(
        db,
        workspace_id,
        current_user.id,
        skip,
        limit,
        status_filter,
        archived,
    )
    
    return ProjectListResponse(total=total, items=projects)


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Get project details",
)
def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific project.
    
    Returns:
    - Project metadata
    - Member count
    - Task count
    - Health status
    """
    project = ProjectService.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    # TODO: Add member_count, task_count, health_status
    return ProjectDetailResponse(**project.__dict__)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project information",
)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update project metadata.
    
    **Permission:** Only Project Manager or Workspace Admin
    
    Ref: Module 3 - Feature 2.1 - AC 2
    """
    project = ProjectService.update_project(db, project_id, project_data, current_user.id)
    return project


@router.patch(
    "/{project_id}/status",
    response_model=ProjectResponse,
    summary="Update project status",
)
def update_project_status(
    project_id: UUID,
    status_data: ProjectStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update project status with transition validation.
    
    **Valid transitions:**
    - NOT_STARTED → IN_PROGRESS, CANCELLED
    - IN_PROGRESS → IN_REVIEW, DONE, CANCELLED
    - IN_REVIEW → DONE, IN_PROGRESS, CANCELLED
    
    **Special rules:**
    - CANCELLED requires cancellation_reason
    - DONE triggers Definition of Done check
    
    Ref: Module 3 - Feature 2.2
    """
    project = ProjectService.update_project_status(
        db, project_id, status_data, current_user.id
    )
    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project (soft delete)",
)
def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Move project to trash (soft delete).
    
    - Project becomes invisible in active lists
    - Hard delete after 30 days (by cronjob)
    - Only PM or Workspace Admin can delete
    
    Ref: Module 3 - Feature 2.5 - AC 1
    """
    ProjectService.delete_project(db, project_id, current_user.id, soft_delete=True)
    return None


@router.post(
    "/{project_id}/clone",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Clone/duplicate project",
)
def clone_project(
    project_id: UUID,
    clone_data: ProjectClone,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Clone an existing project.
    
    **Options:**
    - copy_structure: Copy task lists and settings
    - copy_tasks: Copy tasks (usually not selected)
    - copy_members: Copy project members
    
    Result: New project with name "Copy of [Old Name]"
    
    Ref: Module 3 - Feature 2.1 - AC 3
    """
    project = ProjectService.clone_project(db, project_id, clone_data, current_user.id)
    return project


# ===== Project Member Management =====

@router.get(
    "/{project_id}/members",
    response_model=List[ProjectMemberResponse],
    summary="List project members",
)
def list_project_members(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all members of a project.
    
    Shows:
    - User ID
    - Role (MANAGER, PLANNER, MEMBER, VIEWER)
    - Joined date
    """
    members = ProjectMemberService.list_members(db, project_id, current_user.id)
    return members


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add member to project",
)
def add_project_member(
    project_id: UUID,
    member_data: ProjectMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a member to the project.
    
    **Conditions:**
    - User must already be a workspace member
    - Only PM can add members
    - Notification sent to added user
    
    Ref: Module 3 - Feature 2.3 - AC 1
    """
    member = ProjectMemberService.add_member(
        db, project_id, member_data, current_user.id
    )
    return member


@router.patch(
    "/{project_id}/members/{member_id}",
    response_model=ProjectMemberResponse,
    summary="Update member role",
)
def update_project_member(
    project_id: UUID,
    member_id: UUID,
    role_data: ProjectMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a project member's role.
    
    **Permission:** Only Project Manager
    
    Ref: Module 3 - Feature 2.3 - AC 2
    """
    member = ProjectMemberService.update_member_role(
        db, project_id, member_id, role_data, current_user.id
    )
    return member


@router.delete(
    "/{project_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove member from project",
)
def remove_project_member(
    project_id: UUID,
    member_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove a member from the project.
    
    **Restrictions:**
    - Cannot remove project owner
    - Only PM can remove members
    """
    ProjectMemberService.remove_member(db, project_id, member_id, current_user.id)
    return None


# ===== Project Template Management =====

@router.post(
    "/templates",
    response_model=ProjectTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project template",
)
def create_template(
    template_data: ProjectTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a project template.
    
    Templates include:
    - Task list structure
    - Project settings
    - Workflow configuration
    
    Does NOT include:
    - Specific members
    - Specific dates
    
    Ref: Module 3 - Feature 2.6 - AC 1
    """
    template = ProjectTemplateService.create_template(
        db, template_data, current_user.id
    )
    return template


@router.get(
    "/templates",
    response_model=List[ProjectTemplateResponse],
    summary="List available templates",
)
def list_templates(
    workspace_id: UUID = Query(..., description="Workspace ID"),
    include_global: bool = Query(True, description="Include global templates"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List available project templates.
    
    Returns:
    - Workspace-specific templates
    - Global templates (if include_global=true)
    """
    templates = ProjectTemplateService.list_templates(
        db, workspace_id, include_global
    )
    return templates


@router.post(
    "/from-template",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project from template",
)
def create_project_from_template(
    project_data: ProjectFromTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Initialize a new project from a template.
    
    **Date Remapping:**
    - System asks for new start date
    - Automatically shifts task dates based on relative duration
    
    Ref: Module 3 - Feature 2.6 - AC 2
    """
    # TODO: Implement template-based project creation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Template-based project creation not yet implemented"
    )


# ===== Change Request Management (STRICT Mode) =====

@router.post(
    "/{project_id}/change-requests",
    response_model=ChangeRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create change request",
)
def create_change_request(
    project_id: UUID,
    cr_data: ChangeRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a change request (STRICT governance mode only).
    
    **Types:**
    - SCOPE: Scope change
    - SCHEDULE: Schedule/timeline change
    - COST: Budget change
    - RESOURCE: Resource change
    
    **Workflow:** DRAFT → PENDING → APPROVED/REJECTED
    
    Ref: Module 3 - Feature 2.11 - AC 1
    """
    # Ensure project_id matches
    cr_data.project_id = project_id
    
    cr = ProjectChangeRequestService.create_change_request(
        db, cr_data, current_user.id
    )
    return cr


@router.get(
    "/{project_id}/change-requests",
    response_model=List[ChangeRequestResponse],
    summary="List change requests",
)
def list_change_requests(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all change requests for a project.
    """
    # TODO: Implement list_change_requests
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="List change requests not yet implemented"
    )


@router.patch(
    "/{project_id}/change-requests/{cr_id}/approve",
    response_model=ChangeRequestResponse,
    summary="Approve/reject change request",
)
def approve_change_request(
    project_id: UUID,
    cr_id: UUID,
    approval_data: ChangeRequestApprove,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Approve or reject a change request.
    
    **Permission:** Workspace Admin or Steering Committee only
    
    **Post-approval:**
    - Unlock constraints in Module 5
    - Require new baseline creation
    
    Ref: Module 3 - Feature 2.11 - AC 2 & AC 3
    """
    cr = ProjectChangeRequestService.approve_change_request(
        db, cr_id, approval_data, current_user.id
    )
    return cr


# ===== Project Health & Metrics =====

@router.get(
    "/{project_id}/metrics",
    response_model=ProjectMetricsResponse,
    summary="Get project metrics",
)
def get_project_metrics(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get project health and metrics.
    
    **Includes:**
    - Task completion statistics
    - Health indicators (schedule, resource, budget)
    - Traffic light status (GREEN/AMBER/RED)
    
    Ref: Module 3 - Feature 2.10
    """
    # TODO: Implement metrics calculation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Project metrics not yet implemented"
    )


@router.patch(
    "/{project_id}/health",
    response_model=ProjectResponse,
    summary="Update project health (manual override)",
)
def update_project_health(
    project_id: UUID,
    health_data: ProjectHealthUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Manually override project health status.
    
    **Constraint:** Must provide reason/justification
    
    Ref: Module 3 - Feature 2.10 - AC 3
    """
    # TODO: Implement health update
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Health update not yet implemented"
    )
