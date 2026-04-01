"""
Service layer for scheduling and planning.
Handles business logic for Functional Module 5: Temporal Planning and Scheduling.
Ref: docs/01-Requirements/Functional-Modules/5 - Temporal Planning and Scheduling.md
"""
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Set

from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status

from app.repositories.project_repository import ProjectRepository
from app.models.scheduling import (
    PlanState,
    TaskBaseline,
    TaskDependencySchedule,
    SchedulingMode,
    SLAPolicy,
    SLATracker,
    WorkingHoursPolicy,
    HolidayCalendar,
    PersonalException,
    PlanningScope,
    ResourceHistogram,
    SimulationSession,
    CrossProjectDependency,
    PlanningAuditLog,
)
from app.models.tasks import Task, TaskDependency
from app.models.projects import Project
from app.models.projects_extended import ProjectMember
from app.db.enums import (
    PlanStateEnum,
    SchedulingModeEnum,
    SLAStatusEnum,
    ProjectRole,
    TaskStatus,
)
from app.schemas.scheduling import (
    TaskBaselineCreate,
    SchedulingModeCreate,
    SLAPolicyCreate,
    WorkingHoursPolicyCreate,
    HolidayCalendarCreate,
    PersonalExceptionCreate,
    PlanningScopeCreate,
    SimulationSessionStart,
)


class PlanStateService:
    """Service for plan state management and approval workflow"""

    @staticmethod
    def get_or_create_plan_state(db: Session, project_id: uuid.UUID) -> PlanState:
        """Get or create plan state for project"""
        plan_state = db.scalar(
            select(PlanState).where(PlanState.project_id == project_id)
        )

        if not plan_state:
            plan_state = PlanState(project_id=project_id, state=PlanStateEnum.DRAFT)
            db.add(plan_state)
            db.commit()
            db.refresh(plan_state)

        return plan_state

    @staticmethod
    def submit_plan(
        db: Session,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> PlanState:
        """Submit plan for approval"""
        plan_state = PlanStateService.get_or_create_plan_state(db, project_id)

        if plan_state.state != PlanStateEnum.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plan must be in DRAFT state to submit"
            )

        plan_state.state = PlanStateEnum.SUBMITTED
        plan_state.submitted_by = user_id
        plan_state.submitted_at = datetime.utcnow()

        db.commit()
        db.refresh(plan_state)
        return plan_state

    @staticmethod
    def approve_plan(
        db: Session,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        notes: Optional[str] = None,
    ) -> PlanState:
        """Approve plan and create baseline"""
        plan_state = PlanStateService.get_or_create_plan_state(db, project_id)

        if plan_state.state != PlanStateEnum.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plan must be SUBMITTED to approve"
            )

        plan_state.state = PlanStateEnum.APPROVED
        plan_state.approved_by = user_id
        plan_state.approved_at = datetime.utcnow()
        plan_state.notes = notes

        db.commit()
        db.refresh(plan_state)
        return plan_state

    @staticmethod
    def lock_plan(
        db: Session,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> PlanState:
        """Lock plan to prevent direct changes"""
        plan_state = PlanStateService.get_or_create_plan_state(db, project_id)

        if plan_state.state != PlanStateEnum.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plan must be APPROVED to lock"
            )

        plan_state.state = PlanStateEnum.LOCKED
        plan_state.locked_by = user_id
        plan_state.locked_at = datetime.utcnow()

        db.commit()
        db.refresh(plan_state)
        return plan_state


class TaskBaselineService:
    """Service for task baseline management"""

    @staticmethod
    def create_baseline(
        db: Session,
        baseline_data: TaskBaselineCreate,
        user_id: uuid.UUID,
    ) -> TaskBaseline:
        """Create baseline snapshot of task schedule"""
        task = db.scalar(select(Task).where(Task.id == baseline_data.task_id))

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Get next version number
        max_version = db.scalar(
            select(func.max(TaskBaseline.baseline_version)).where(
                TaskBaseline.task_id == baseline_data.task_id
            )
        ) or 0

        baseline = TaskBaseline(
            task_id=baseline_data.task_id,
            baseline_version=max_version + 1,
            baseline_start=task.planned_start or datetime.utcnow(),
            baseline_end=task.planned_end or datetime.utcnow(),
            baseline_duration_hours=task.estimated_hours or 0,
            created_by=user_id,
        )

        db.add(baseline)
        db.commit()
        db.refresh(baseline)
        return baseline

    @staticmethod
    def get_latest_baseline(db: Session, task_id: uuid.UUID) -> Optional[TaskBaseline]:
        """Get latest baseline for task"""
        baseline = db.scalar(
            select(TaskBaseline)
            .where(TaskBaseline.task_id == task_id)
            .order_by(TaskBaseline.baseline_version.desc())
            .limit(1)
        )
        return baseline


class SchedulingModeService:
    """Service for task scheduling mode"""

    @staticmethod
    def set_scheduling_mode(
        db: Session,
        mode_data: SchedulingModeCreate,
        user_id: uuid.UUID,
    ) -> SchedulingMode:
        """Set or update scheduling mode for task"""
        # Check if task exists
        task = db.scalar(select(Task).where(Task.id == mode_data.task_id))
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        mode = db.scalar(
            select(SchedulingMode).where(SchedulingMode.task_id == mode_data.task_id)
        )

        if not mode:
            mode = SchedulingMode(
                task_id=mode_data.task_id,
                mode=mode_data.mode,
                is_pinned=mode_data.is_pinned,
            )
            db.add(mode)
        else:
            mode.mode = mode_data.mode
            mode.is_pinned = mode_data.is_pinned
            mode.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(mode)
        return mode


class SLAPolicyService:
    """Service for SLA policy management"""

    @staticmethod
    def create_sla_policy(
        db: Session,
        policy_data: SLAPolicyCreate,
        user_id: uuid.UUID,
    ) -> SLAPolicy:
        """Create SLA policy for project"""
        # Check project exists
        project = db.scalar(select(Project).where(Project.id == policy_data.project_id))
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        policy = SLAPolicy(
            project_id=policy_data.project_id,
            priority=policy_data.priority,
            sla_hours=policy_data.sla_hours,
            warning_threshold_percent=policy_data.warning_threshold_percent,
            enable_escalation=policy_data.enable_escalation,
            escalation_level_1_hours=policy_data.escalation_level_1_hours,
            escalation_level_2_hours=policy_data.escalation_level_2_hours,
        )

        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    @staticmethod
    def get_policy_by_priority(
        db: Session,
        project_id: uuid.UUID,
        priority: str,
    ) -> Optional[SLAPolicy]:
        """Get SLA policy for priority level"""
        policy = db.scalar(
            select(SLAPolicy).where(
                and_(
                    SLAPolicy.project_id == project_id,
                    SLAPolicy.priority == priority,
                )
            )
        )
        return policy


class SLATrackerService:
    """Service for SLA tracking"""

    @staticmethod
    def initialize_sla_tracker(
        db: Session,
        task_id: uuid.UUID,
        sla_policy: SLAPolicy,
        user_id: uuid.UUID,
    ) -> SLATracker:
        """
        Initialize SLA tracker for task.
        Ref: Module 5 - Feature 2.7 - AC 2 - Business Hours Logic
        """
        task = db.scalar(select(Task).where(Task.id == task_id))
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Calculate SLA deadline based on business hours
        sla_start = datetime.utcnow()
        sla_deadline = SLATrackerService._calculate_deadline(
            db, task.project_id, sla_start, sla_policy.sla_hours
        )

        tracker = SLATracker(
            task_id=task_id,
            status=SLAStatusEnum.ON_TRACK,
            sla_start_time=sla_start,
            sla_deadline=sla_deadline,
            elapsed_business_seconds=0,
            paused_business_seconds=0,
            is_paused=False,
        )

        db.add(tracker)
        db.commit()
        db.refresh(tracker)
        return tracker

    @staticmethod
    def _calculate_deadline(
        db: Session,
        project_id: uuid.UUID,
        start_time: datetime,
        business_hours: int,
    ) -> datetime:
        """
        Calculate SLA deadline considering business hours and holidays.
        Ref: Module 5 - Algorithm 4.2 - SLA Calculation
        """
        # TODO: Implement business hours calculation
        # For now, return start_time + hours as calendar time
        return start_time + timedelta(hours=business_hours)

    @staticmethod
    def check_sla_status(
        db: Session,
        task_id: uuid.UUID,
    ) -> str:
        """
        Check and update SLA status.
        Ref: Module 5 - Feature 2.7 - AC 3 - Visual Warning
        """
        tracker = db.scalar(
            select(SLATracker).where(SLATracker.task_id == task_id)
        )

        if not tracker:
            return SLAStatusEnum.ON_TRACK

        # Calculate elapsed time
        if tracker.is_paused:
            elapsed = tracker.elapsed_business_seconds
        else:
            elapsed = tracker.elapsed_business_seconds + int(
                (datetime.utcnow() - tracker.sla_start_time).total_seconds()
            )

        # Get SLA policy
        task = db.scalar(select(Task).where(Task.id == task_id))
        policy = SLAPolicyService.get_policy_by_priority(
            db, task.project_id, str(task.priority)
        )

        if not policy:
            return SLAStatusEnum.ON_TRACK

        sla_seconds = policy.sla_hours * 3600
        warning_seconds = sla_seconds * policy.warning_threshold_percent / 100

        # Determine status
        if elapsed > sla_seconds:
            new_status = SLAStatusEnum.BREACHED
        elif elapsed > warning_seconds:
            new_status = SLAStatusEnum.AT_RISK
        else:
            new_status = SLAStatusEnum.ON_TRACK

        # Update tracker if status changed
        if tracker.status != new_status:
            tracker.status = new_status
            if new_status == SLAStatusEnum.BREACHED and not tracker.sla_breach_time:
                tracker.sla_breach_time = datetime.utcnow()
            tracker.updated_at = datetime.utcnow()
            db.commit()

        return new_status

    @staticmethod
    def pause_sla_timer(
        db: Session,
        task_id: uuid.UUID,
        reason: str,
    ) -> SLATracker:
        """
        Pause SLA timer.
        Ref: Module 5 - Feature 2.7 - AC 4 - SLA Pause Conditions
        """
        tracker = db.scalar(
            select(SLATracker).where(SLATracker.task_id == task_id)
        )

        if not tracker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA tracker not found"
            )

        tracker.is_paused = True
        tracker.pause_reason = reason
        tracker.paused_at = datetime.utcnow()
        tracker.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(tracker)
        return tracker

    @staticmethod
    def resume_sla_timer(db: Session, task_id: uuid.UUID) -> SLATracker:
        """Resume paused SLA timer"""
        tracker = db.scalar(
            select(SLATracker).where(SLATracker.task_id == task_id)
        )

        if not tracker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA tracker not found"
            )

        if tracker.is_paused and tracker.paused_at:
            pause_duration = int(
                (datetime.utcnow() - tracker.paused_at).total_seconds()
            )
            tracker.paused_business_seconds += pause_duration

        tracker.is_paused = False
        tracker.pause_reason = None
        tracker.paused_at = None
        tracker.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(tracker)
        return tracker


class WorkingHoursService:
    """Service for working hours and calendar management"""

    @staticmethod
    def create_working_hours_policy(
        db: Session,
        policy_data: WorkingHoursPolicyCreate,
    ) -> WorkingHoursPolicy:
        """Create working hours policy"""
        policy = WorkingHoursPolicy(
            workspace_id=policy_data.workspace_id,
            working_days_mask=policy_data.working_days_mask,
            work_start_time=policy_data.work_start_time,
            work_end_time=policy_data.work_end_time,
            lunch_start_time=policy_data.lunch_start_time,
            lunch_end_time=policy_data.lunch_end_time,
            timezone=policy_data.timezone,
        )

        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    @staticmethod
    def add_holiday(
        db: Session,
        holiday_data: HolidayCalendarCreate,
        user_id: uuid.UUID,
    ) -> HolidayCalendar:
        """Add holiday to workspace calendar"""
        holiday = HolidayCalendar(
            workspace_id=holiday_data.workspace_id,
            holiday_date=holiday_data.holiday_date,
            name=holiday_data.name,
            is_recurring=holiday_data.is_recurring,
            created_by=user_id,
        )

        db.add(holiday)
        db.commit()
        db.refresh(holiday)
        return holiday


class PersonalExceptionService:
    """Service for personal exceptions (leave, vacation)"""

    @staticmethod
    def add_personal_exception(
        db: Session,
        exception_data: PersonalExceptionCreate,
    ) -> PersonalException:
        """
        Add personal exception for team member.
        Ref: Module 5 - Feature 2.19 - AC 1
        """
        exception = PersonalException(
            user_id=exception_data.user_id,
            project_id=exception_data.project_id,
            exception_date=exception_data.exception_date,
            exception_type=exception_data.exception_type,
            notes=exception_data.notes,
        )

        db.add(exception)
        db.commit()
        db.refresh(exception)
        return exception


class PlanningScopeService:
    """Service for planning scope control"""

    @staticmethod
    def set_planning_scope(
        db: Session,
        scope_data: PlanningScopeCreate,
    ) -> PlanningScope:
        """
        Set planning scope for task.
        Ref: Module 5 - Feature 2.9 - AC 1
        """
        task = db.scalar(select(Task).where(Task.id == scope_data.task_id))
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        scope = db.scalar(
            select(PlanningScope).where(PlanningScope.task_id == scope_data.task_id)
        )

        if not scope:
            scope = PlanningScope(
                task_id=scope_data.task_id,
                include_in_planning=scope_data.include_in_planning,
                override_parent=scope_data.override_parent,
            )
            db.add(scope)
        else:
            scope.include_in_planning = scope_data.include_in_planning
            scope.override_parent = scope_data.override_parent
            scope.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(scope)
        return scope

    @staticmethod
    def is_in_planning_scope(db: Session, task_id: uuid.UUID) -> bool:
        """
        Check if task is in planning scope.
        Ref: Module 5 - Feature 2.9 - AC 2 - Scope Inheritance
        """
        scope = db.scalar(
            select(PlanningScope).where(PlanningScope.task_id == task_id)
        )

        if not scope:
            # Default: high-level tasks included, subtasks excluded
            # TODO: Check task level to determine default
            return True

        return scope.include_in_planning


class SimulationService:
    """Service for What-If simulation mode"""

    @staticmethod
    def start_simulation(
        db: Session,
        sim_data: SimulationSessionStart,
        user_id: uuid.UUID,
    ) -> SimulationSession:
        """
        Start simulation mode for planning.
        Ref: Module 5 - Feature 2.10 - AC 1
        """
        session = SimulationSession(
            project_id=sim_data.project_id,
            created_by=user_id,
            is_active=True,
            notes=sim_data.notes,
        )

        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def end_simulation(
        db: Session,
        simulation_id: uuid.UUID,
        apply_changes: bool = False,
    ) -> SimulationSession:
        """
        End simulation mode.
        Ref: Module 5 - Feature 2.10 - AC 4
        """
        simulation = db.scalar(
            select(SimulationSession).where(SimulationSession.id == simulation_id)
        )

        if not simulation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation session not found"
            )

        simulation.is_active = False

        if apply_changes:
            # TODO: Apply simulated changes to database
            pass

        db.commit()
        db.refresh(simulation)
        return simulation


class CriticalPathService:
    """Service for critical path analysis"""

    @staticmethod
    def calculate_critical_path(db: Session, project_id: uuid.UUID) -> Set[uuid.UUID]:
        """
        Calculate critical path for project using CPM.
        Ref: Module 5 - Algorithm 4.1 - Critical Path Method
        """
        return GanttChartService.calculate_critical_path(db, project_id)


class PlanningAuditService:
    """Service for planning audit trail"""

    @staticmethod
    def log_change(
        db: Session,
        task_id: uuid.UUID,
        change_type: str,
        old_value: Optional[str],
        new_value: str,
        changed_by: uuid.UUID,
        reason: Optional[str] = None,
    ) -> PlanningAuditLog:
        """
        Log planning change for audit trail.
        Ref: Module 5 - Business Rule 3.7
        """
        log = PlanningAuditLog(
            task_id=task_id,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            changed_by=changed_by,
        )

        db.add(log)
        db.commit()
        db.refresh(log)
        return log


class GanttChartService:
    """Service for building Gantt chart payloads."""

    @staticmethod
    def _task_bounds(task: Task) -> tuple[datetime, datetime]:
        start = task.planned_start or task.actual_start or task.created_at or datetime.utcnow()
        end = task.planned_end or task.actual_end

        if end is None:
            if task.estimated_hours and task.estimated_hours > 0:
                end = start + timedelta(hours=float(task.estimated_hours))
            else:
                end = start + timedelta(days=1)

        if end < start:
            end = start + timedelta(days=1)

        return start, end

    @staticmethod
    def _task_progress(task: Task) -> int:
        if task.status == TaskStatus.DONE:
            return 100
        if task.status == TaskStatus.IN_PROGRESS:
            return 60
        if task.status == TaskStatus.IN_REVIEW:
            return 85
        return 0

    @staticmethod
    def _task_assignees(task: Task) -> list[dict[str, str | None]]:
        assignees: list[dict[str, str | None]] = []
        for assignee in task.assignees or []:
            assignees.append(
                {
                    "id": str(assignee.id),
                    "name": assignee.full_name or assignee.username or assignee.email,
                    "avatar": getattr(assignee, "avatar_url", None),
                }
            )
        return assignees

    @staticmethod
    def _dependency_edge(dependency: TaskDependency) -> dict:
        source_id = dependency.depends_on_task_id if dependency.dependency_type == "BLOCKS" else dependency.task_id
        target_id = dependency.task_id if dependency.dependency_type == "BLOCKS" else dependency.depends_on_task_id
        schedule = getattr(dependency, "schedule_config", None)

        return {
            "id": str(dependency.id),
            "source": str(source_id),
            "target": str(target_id),
            "type": "FS" if dependency.dependency_type in {"BLOCKS", "BLOCKED_BY"} else "RELATED",
            "dependency_type": dependency.dependency_type,
            "lag_days": getattr(schedule, "lag_days", 0),
            "is_pinned": bool(getattr(schedule, "is_pinned", False)),
            "is_broken": False,
            "created_at": dependency.created_at,
            "updated_at": dependency.updated_at,
        }

    @staticmethod
    def _task_payload(task: Task, include_critical: bool, critical_ids: Set[uuid.UUID], include_in_planning: bool) -> dict:
        start, end = GanttChartService._task_bounds(task)

        return {
            "id": str(task.id),
            "task_id": str(task.id),
            "title": task.title,
            "name": task.title,
            "status": task.status.value if hasattr(task.status, "value") else str(task.status),
            "priority": task.priority.value if hasattr(task.priority, "value") else str(task.priority),
            "planned_start": start,
            "planned_end": end,
            "start_date": start,
            "end_date": end,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "is_milestone": bool(task.is_milestone),
            "include_in_planning": include_in_planning,
            "progress": GanttChartService._task_progress(task),
            "assignees": GanttChartService._task_assignees(task),
            "source": "scheduling-api",
            "isPersisted": True,
            "is_critical_path": include_critical and task.id in critical_ids,
        }

    @staticmethod
    def calculate_critical_path(db: Session, project_id: uuid.UUID) -> Set[uuid.UUID]:
        tasks = db.scalars(
            select(Task)
            .where(Task.project_id == project_id)
            .options(selectinload(Task.dependencies))
        ).all()

        if not tasks:
            return set()

        task_ids = {task.id for task in tasks}
        durations: dict[uuid.UUID, float] = {}
        adjacency: dict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
        indegree: dict[uuid.UUID, int] = {task.id: 0 for task in tasks}

        for task in tasks:
            start, end = GanttChartService._task_bounds(task)
            durations[task.id] = max((end - start).total_seconds() / 3600.0, 1.0)

        dependency_rows = db.scalars(
            select(TaskDependency).where(TaskDependency.task_id.in_(task_ids))
        ).all()

        for dependency in dependency_rows:
            if dependency.dependency_type == "BLOCKS":
                source_id = dependency.depends_on_task_id
                target_id = dependency.task_id
            elif dependency.dependency_type == "BLOCKED_BY":
                source_id = dependency.task_id
                target_id = dependency.depends_on_task_id
            else:
                continue

            if source_id not in task_ids or target_id not in task_ids:
                continue

            adjacency[source_id].append(target_id)
            indegree[target_id] = indegree.get(target_id, 0) + 1

        distance: dict[uuid.UUID, float] = {task_id: durations[task_id] for task_id in task_ids}
        predecessor: dict[uuid.UUID, uuid.UUID] = {}
        queue = deque([task_id for task_id, degree in indegree.items() if degree == 0])

        while queue:
            current_id = queue.popleft()
            for next_id in adjacency.get(current_id, []):
                candidate_distance = distance[current_id] + durations[next_id]
                if candidate_distance > distance.get(next_id, 0):
                    distance[next_id] = candidate_distance
                    predecessor[next_id] = current_id
                indegree[next_id] -= 1
                if indegree[next_id] == 0:
                    queue.append(next_id)

        if not distance:
            return set()

        end_task_id = max(distance, key=distance.get)
        critical_ids: Set[uuid.UUID] = {end_task_id}

        while end_task_id in predecessor:
            end_task_id = predecessor[end_task_id]
            critical_ids.add(end_task_id)

        return critical_ids

    @staticmethod
    def build_gantt_chart(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, filter_data) -> dict:
        project_repo = ProjectRepository(db)
        if not project_repo.can_access(project_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project",
            )

        tasks = db.scalars(
            select(Task)
            .where(Task.project_id == project_id)
            .options(selectinload(Task.assignees))
        ).all()

        if not tasks:
            return {
                "tasks": [],
                "dependencies": [],
                "milestones": [],
                "baselines": [],
                "critical_task_ids": [],
                "total_float_hours": 0.0,
            }

        task_ids = [task.id for task in tasks]
        critical_ids = GanttChartService.calculate_critical_path(db, project_id) if filter_data.show_critical_path else set()

        scopes = db.scalars(
            select(PlanningScope).where(PlanningScope.task_id.in_(task_ids))
        ).all()
        scope_map = {scope.task_id: scope.include_in_planning for scope in scopes}

        dependencies = db.scalars(
            select(TaskDependency)
            .where(TaskDependency.task_id.in_(task_ids))
            .options(selectinload(TaskDependency.schedule_config))
        ).all()

        baselines = db.scalars(
            select(TaskBaseline)
            .where(TaskBaseline.task_id.in_(task_ids))
            .order_by(TaskBaseline.task_id, TaskBaseline.baseline_version.desc())
        ).all()
        baseline_map: dict[uuid.UUID, TaskBaseline] = {}
        for baseline in baselines:
            baseline_map.setdefault(baseline.task_id, baseline)

        chart_tasks = []
        milestones = []
        start_filter = filter_data.start_date
        end_filter = filter_data.end_date

        for task in tasks:
            start, end = GanttChartService._task_bounds(task)
            if start_filter and end < start_filter:
                continue
            if end_filter and start > end_filter:
                continue

            include_in_planning = scope_map.get(task.id, True)
            chart_tasks.append(
                GanttChartService._task_payload(
                    task,
                    filter_data.show_critical_path,
                    critical_ids,
                    include_in_planning,
                )
            )

            if task.is_milestone and filter_data.include_milestones:
                milestones.append(
                    {
                        "id": str(task.id),
                        "task_id": str(task.id),
                        "title": task.title,
                        "date": end,
                        "status": task.status.value if hasattr(task.status, "value") else str(task.status),
                        "priority": task.priority.value if hasattr(task.priority, "value") else str(task.priority),
                    }
                )

        baseline_items = []
        if filter_data.show_baseline:
            for task in tasks:
                baseline = baseline_map.get(task.id)
                if not baseline:
                    continue
                baseline_items.append(
                    {
                        "id": str(baseline.id),
                        "task_id": str(baseline.task_id),
                        "baseline_version": baseline.baseline_version,
                        "baseline_start": baseline.baseline_start,
                        "baseline_end": baseline.baseline_end,
                        "baseline_duration_hours": baseline.baseline_duration_hours,
                        "actual_start": baseline.actual_start,
                        "actual_end": baseline.actual_end,
                        "actual_duration_hours": baseline.actual_duration_hours,
                        "schedule_variance_days": baseline.schedule_variance_days,
                    }
                )

        return {
            "tasks": chart_tasks,
            "dependencies": [GanttChartService._dependency_edge(dep) for dep in dependencies],
            "milestones": milestones,
            "baselines": baseline_items,
            "critical_task_ids": [str(task_id) for task_id in critical_ids],
            "total_float_hours": 0.0,
        }
