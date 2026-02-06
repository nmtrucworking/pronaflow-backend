"""
API endpoints for scheduling and planning.
Implements Functional Module 5: Temporal Planning and Scheduling.
Ref: docs/01-Requirements/Functional-Modules/5 - Temporal Planning and Scheduling.md
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.scheduling import (
    PlanStateResponse,
    TaskBaselineCreate,
    TaskBaselineResponse,
    SchedulingModeCreate,
    SchedulingModeResponse,
    SLAPolicyCreate,
    SLAPolicyResponse,
    SLATrackerResponse,
    WorkingHoursPolicyCreate,
    WorkingHoursPolicyResponse,
    HolidayCalendarCreate,
    HolidayCalendarResponse,
    PersonalExceptionCreate,
    PersonalExceptionResponse,
    PlanningScopeCreate,
    PlanningScopeResponse,
    SimulationSessionStart,
    SimulationSessionResponse,
    CrossProjectDependencyCreate,
    CrossProjectDependencyResponse,
    GanttChartFilter,
    CriticalPathAnalysisResponse,
    ImpactAnalysisResponse,
    ResourceLevelingRequest,
    ResourceLevelingResponse,
)
from app.services.scheduling import (
    PlanStateService,
    TaskBaselineService,
    SchedulingModeService,
    SLAPolicyService,
    SLATrackerService,
    WorkingHoursService,
    PersonalExceptionService,
    PlanningScopeService,
    SimulationService,
    CriticalPathService,
    PlanningAuditService,
)

router = APIRouter(prefix="/v1/scheduling", tags=["scheduling"])


# ===== Plan State Endpoints =====

@router.get("/plans/{project_id}/state", response_model=PlanStateResponse)
def get_plan_state(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get plan state for project"""
    plan_state = PlanStateService.get_or_create_plan_state(db, project_id)
    return plan_state


@router.post("/plans/{project_id}/submit", response_model=PlanStateResponse)
def submit_plan(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit plan for approval"""
    plan_state = PlanStateService.submit_plan(db, project_id, current_user.id)
    return plan_state


@router.post("/plans/{project_id}/approve", response_model=PlanStateResponse)
def approve_plan(
    project_id: uuid.UUID,
    notes: Optional[str] = Query(None, description="Approval notes"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve plan and create baseline"""
    plan_state = PlanStateService.approve_plan(db, project_id, current_user.id, notes)
    return plan_state


@router.post("/plans/{project_id}/lock", response_model=PlanStateResponse)
def lock_plan(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lock plan to prevent direct changes"""
    plan_state = PlanStateService.lock_plan(db, project_id, current_user.id)
    return plan_state


# ===== Baseline Endpoints =====

@router.post("/baselines", response_model=TaskBaselineResponse, status_code=status.HTTP_201_CREATED)
def create_task_baseline(
    baseline_data: TaskBaselineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create baseline snapshot of task schedule.
    Ref: Module 5 - Feature 2.4 - AC 1
    """
    baseline = TaskBaselineService.create_baseline(db, baseline_data, current_user.id)
    return baseline


@router.get("/baselines/task/{task_id}/latest", response_model=TaskBaselineResponse)
def get_latest_baseline(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get latest baseline for task"""
    baseline = TaskBaselineService.get_latest_baseline(db, task_id)
    if not baseline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No baseline found for task"
        )
    return baseline


# ===== Scheduling Mode Endpoints =====

@router.post("/scheduling-modes", response_model=SchedulingModeResponse, status_code=status.HTTP_201_CREATED)
def set_scheduling_mode(
    mode_data: SchedulingModeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Set scheduling mode for task.
    Ref: Module 5 - Feature 2.2 - AC 3
    """
    mode = SchedulingModeService.set_scheduling_mode(db, mode_data, current_user.id)
    return mode


# ===== SLA Policy Endpoints =====

@router.post("/sla-policies", response_model=SLAPolicyResponse, status_code=status.HTTP_201_CREATED)
def create_sla_policy(
    policy_data: SLAPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create SLA policy.
    Ref: Module 5 - Feature 2.7 - AC 1
    """
    policy = SLAPolicyService.create_sla_policy(db, policy_data, current_user.id)
    return policy


# ===== SLA Tracker Endpoints =====

@router.get("/sla-trackers/task/{task_id}", response_model=SLATrackerResponse)
def get_sla_tracker(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get SLA tracker for task"""
    from sqlalchemy import select
    from app.models.scheduling import SLATracker
    
    tracker = db.scalar(select(SLATracker).where(SLATracker.task_id == task_id))
    if not tracker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA tracker not found"
        )
    return tracker


@router.post("/sla-trackers/task/{task_id}/pause", response_model=SLATrackerResponse)
def pause_sla_timer(
    task_id: uuid.UUID,
    reason: str = Query(..., description="Pause reason"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Pause SLA timer.
    Ref: Module 5 - Feature 2.7 - AC 4
    """
    tracker = SLATrackerService.pause_sla_timer(db, task_id, reason)
    return tracker


@router.post("/sla-trackers/task/{task_id}/resume", response_model=SLATrackerResponse)
def resume_sla_timer(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resume paused SLA timer"""
    tracker = SLATrackerService.resume_sla_timer(db, task_id)
    return tracker


# ===== Working Hours Policy Endpoints =====

@router.post("/working-hours-policies", response_model=WorkingHoursPolicyResponse, status_code=status.HTTP_201_CREATED)
def create_working_hours_policy(
    policy_data: WorkingHoursPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create working hours policy"""
    policy = WorkingHoursService.create_working_hours_policy(db, policy_data)
    return policy


# ===== Holiday Calendar Endpoints =====

@router.post("/holidays", response_model=HolidayCalendarResponse, status_code=status.HTTP_201_CREATED)
def add_holiday(
    holiday_data: HolidayCalendarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add holiday to workspace calendar"""
    holiday = WorkingHoursService.add_holiday(db, holiday_data, current_user.id)
    return holiday


# ===== Personal Exception Endpoints =====

@router.post("/personal-exceptions", response_model=PersonalExceptionResponse, status_code=status.HTTP_201_CREATED)
def add_personal_exception(
    exception_data: PersonalExceptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add personal exception (leave, vacation).
    Ref: Module 5 - Feature 2.19 - AC 1
    """
    exception = PersonalExceptionService.add_personal_exception(db, exception_data)
    return exception


# ===== Planning Scope Endpoints =====

@router.post("/planning-scopes", response_model=PlanningScopeResponse, status_code=status.HTTP_201_CREATED)
def set_planning_scope(
    scope_data: PlanningScopeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Set planning scope for task.
    Ref: Module 5 - Feature 2.9 - AC 1
    """
    scope = PlanningScopeService.set_planning_scope(db, scope_data)
    return scope


# ===== Simulation Endpoints =====

@router.post("/simulations", response_model=SimulationSessionResponse, status_code=status.HTTP_201_CREATED)
def start_simulation(
    sim_data: SimulationSessionStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start simulation mode for What-If analysis.
    Ref: Module 5 - Feature 2.10 - AC 1
    """
    simulation = SimulationService.start_simulation(db, sim_data, current_user.id)
    return simulation


@router.post("/simulations/{simulation_id}/apply", response_model=SimulationSessionResponse)
def apply_simulation(
    simulation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Apply simulation changes to database.
    Ref: Module 5 - Feature 2.10 - AC 4
    """
    simulation = SimulationService.end_simulation(db, simulation_id, apply_changes=True)
    return simulation


@router.post("/simulations/{simulation_id}/discard", response_model=SimulationSessionResponse)
def discard_simulation(
    simulation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Discard simulation changes"""
    simulation = SimulationService.end_simulation(db, simulation_id, apply_changes=False)
    return simulation


# ===== Gantt Chart Endpoints =====

@router.get("/gantt", response_model=dict)
def get_gantt_chart(
    filter: GanttChartFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get Gantt chart data for project.
    Ref: Module 5 - Feature 2.1
    """
    # TODO: Implement Gantt chart data fetching
    return {
        "tasks": [],
        "dependencies": [],
        "milestones": [],
        "baselines": [],
    }


# ===== Critical Path Endpoints =====

@router.get("/critical-path/{project_id}", response_model=CriticalPathAnalysisResponse)
def analyze_critical_path(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze critical path for project.
    Ref: Module 5 - Feature 2.3
    """
    critical_tasks = CriticalPathService.calculate_critical_path(db, project_id)
    
    return CriticalPathAnalysisResponse(
        total_float_hours=0.0,  # TODO: Calculate
        critical_task_ids=list(critical_tasks),
        project_end_date=None,  # TODO: Calculate
        updated_at=None,  # TODO: Set
    )


# ===== Impact Analysis Endpoints =====

@router.post("/impact-analysis/{task_id}", response_model=ImpactAnalysisResponse)
def analyze_change_impact(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze impact of task changes.
    Ref: Module 5 - Feature 2.12
    """
    # TODO: Implement impact analysis
    return ImpactAnalysisResponse(
        delta_project_end_days=0,
        affected_task_ids=[],
        new_critical_path_count=0,
        sla_at_risk_count=0,
        resource_overload_increase=0,
    )


# ===== Resource Leveling Endpoints =====

@router.post("/resource-leveling", response_model=ResourceLevelingResponse)
def level_resources(
    request: ResourceLevelingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Apply resource leveling to project.
    Ref: Module 5 - Feature 2.17
    """
    # TODO: Implement resource leveling algorithm
    return ResourceLevelingResponse(
        tasks_to_move=[],
        conflict_reduction_percent=0.0,
        project_end_date_delta_days=0,
        affected_resources=[],
    )
