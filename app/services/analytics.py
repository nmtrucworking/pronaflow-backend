"""
Analytics and Reporting Service Layer for Module 11.
Implements business logic for analytics, metrics calculations, and report generation.

Services:
- SprintMetricsService: EVM calculations (CPI, SPI), burn-down/up tracking
- VelocityService: 3/6-sprint averages, trend analysis
- ResourceUtilizationService: Capacity heatmap, overload detection
- TimeTrackingService: Timer logic, entry validation, daily limits
- TimesheetApprovalService: Workflow management, approval routing
- CustomReportService: Drag-drop query building, execution
- ReportSchedulingService: Automated generation and email delivery

Ref: Module 11 - Advanced Analytics and Reporting
"""
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.db.models.analytics import (
    SprintMetric, VelocityMetric, ResourceAllocation, TimeEntry,
    Timesheet, CustomReport, ReportSchedule, MetricSnapshot, KPI,
    TimesheetApproval, ReportPermission
)
from app.db.models.task import Task
from app.db.models.sprint import Sprint
from app.schemas.analytics import (
    SprintMetricCreate, SprintMetricUpdate, SprintMetricRead,
    VelocityMetricCreate, VelocityMetricRead,
    TimeEntryCreate, TimeEntryUpdate, TimeEntryRead,
    TimesheetCreate, TimesheetRead,
    CustomReportCreate, CustomReportRead,
    ReportScheduleCreate, ReportScheduleRead,
    BurndownChartData, VelocityChartData
)
from app.db.enums import TimesheetStatusEnum, BillableStatusEnum


class SprintMetricsService:
    """
    Sprint performance metrics with Earned Value Management (EVM) calculations.
    
    Calculations:
    - CPI = Earned Value / Actual Cost (1.0 = on budget)
    - SPI = Earned Value / Planned Value (1.0 = on schedule)
    - Risk level determination based on metrics
    
    Ref: Module 11 - Feature 2.1, Section 4.1 (EVM)
    """

    @staticmethod
    def create_sprint_metric(db: Session, sprint_data: SprintMetricCreate) -> SprintMetric:
        """Create initial sprint metric"""
        metric = SprintMetric(
            sprint_id=sprint_data.sprint_id,
            project_id=sprint_data.project_id,
            total_story_points=sprint_data.total_story_points,
            initial_story_points=sprint_data.initial_story_points,
            sprint_start_date=sprint_data.sprint_start_date,
            sprint_end_date=sprint_data.sprint_end_date,
            total_sprint_days=sprint_data.total_sprint_days,
            planned_value=Decimal(sprint_data.total_story_points),
        )
        db.add(metric)
        db.commit()
        return metric

    @staticmethod
    def update_metrics(
        db: Session,
        sprint_id: str,
        update_data: SprintMetricUpdate
    ) -> Optional[SprintMetric]:
        """Update sprint metrics and recalculate EVM indices"""
        metric = db.query(SprintMetric).filter(
            SprintMetric.sprint_id == sprint_id
        ).first()

        if not metric:
            return None

        # Update provided fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                setattr(metric, field, value)

        # Recalculate EVM indices
        metric = SprintMetricsService._calculate_evm_indices(metric)

        # Determine risk level
        metric.risk_level = SprintMetricsService._calculate_risk_level(metric)
        metric.is_on_track = metric.schedule_performance_index >= 0.9

        db.commit()
        return metric

    @staticmethod
    def _calculate_evm_indices(metric: SprintMetric) -> SprintMetric:
        """
        Calculate Cost Performance Index (CPI) and Schedule Performance Index (SPI).
        
        CPI = EV / AC (Actual Cost)
        - > 1.0: Under budget
        - = 1.0: On budget
        - < 1.0: Over budget
        
        SPI = EV / PV (Planned Value)
        - > 1.0: Ahead of schedule
        - = 1.0: On schedule
        - < 1.0: Behind schedule
        """
        if metric.actual_cost and metric.actual_cost > 0:
            metric.cost_performance_index = float(metric.earned_value / metric.actual_cost)
        else:
            metric.cost_performance_index = None

        if metric.planned_value and metric.planned_value > 0:
            metric.schedule_performance_index = float(metric.earned_value / metric.planned_value)
        else:
            metric.schedule_performance_index = None

        return metric

    @staticmethod
    def _calculate_risk_level(metric: SprintMetric) -> str:
        """Determine risk level based on SPI"""
        if metric.schedule_performance_index is None:
            return "MEDIUM"

        if metric.schedule_performance_index >= 0.95:
            return "LOW"
        elif metric.schedule_performance_index >= 0.80:
            return "MEDIUM"
        else:
            return "HIGH"

    @staticmethod
    def get_burndown_chart(
        db: Session,
        sprint_id: str
    ) -> Optional[BurndownChartData]:
        """
        Generate burn-down chart data.
        
        Shows ideal line (linear decline) vs actual progress.
        Includes scope line if there's scope creep.
        """
        metric = db.query(SprintMetric).filter(
            SprintMetric.sprint_id == sprint_id
        ).first()

        if not metric:
            return None

        # Calculate ideal line (linear decline from total to 0)
        total_days = metric.total_sprint_days
        days_elapsed = metric.days_elapsed
        days = list(range(0, total_days + 1))
        ideal_line = [
            max(0, metric.initial_story_points - (metric.initial_story_points / total_days) * d)
            for d in days
        ]

        # Actual line (current remaining)
        actual_line = [metric.remaining_story_points] * len(days)

        # Scope line (scope creep)
        scope_line = None
        if metric.added_story_points > 0:
            scope_line = [
                (metric.initial_story_points + metric.added_story_points - metric.removed_story_points)
                if d <= days_elapsed else 0
                for d in days
            ]

        return BurndownChartData(
            sprint_id=sprint_id,
            days=days,
            ideal_line=ideal_line,
            actual_line=actual_line,
            scope_line=scope_line,
            on_track=metric.is_on_track,
            risk_level=metric.risk_level
        )


class VelocityService:
    """
    Sprint velocity tracking and trend analysis.
    
    Calculates:
    - Velocity = Completed / Commitment ratio
    - 3-sprint and 6-sprint averages for planning
    - Trend (INCREASING, STABLE, DECREASING)
    
    Ref: Module 11 - Feature 2.1 AC 2
    """

    @staticmethod
    def create_velocity_metric(
        db: Session,
        velocity_data: VelocityMetricCreate
    ) -> VelocityMetric:
        """Create velocity metric"""
        velocity = (velocity_data.completed / velocity_data.commitment
                   if velocity_data.commitment > 0 else 0.0)

        metric = VelocityMetric(
            sprint_id=velocity_data.sprint_id,
            project_id=velocity_data.project_id,
            commitment=velocity_data.commitment,
            completed=velocity_data.completed,
            velocity=velocity,
            team_size=velocity_data.team_size,
            sprint_number=velocity_data.sprint_number,
            sprint_start_date=velocity_data.sprint_start_date,
            sprint_end_date=velocity_data.sprint_end_date,
        )
        db.add(metric)
        db.commit()

        # Calculate averages
        VelocityService._update_velocity_averages(db, velocity_data.project_id)

        return metric

    @staticmethod
    def _update_velocity_averages(db: Session, project_id: str) -> None:
        """Calculate 3-sprint and 6-sprint moving averages"""
        # Get last 6 sprints
        metrics = db.query(VelocityMetric).filter(
            VelocityMetric.project_id == project_id
        ).order_by(desc(VelocityMetric.sprint_number)).limit(6).all()

        if len(metrics) >= 3:
            # Update 3-sprint average
            last_3_velocity = sum(m.velocity for m in metrics[:3]) / 3
            for m in metrics[:3]:
                m.avg_velocity_3_sprints = last_3_velocity

        if len(metrics) >= 6:
            # Update 6-sprint average
            all_6_velocity = sum(m.velocity for m in metrics) / 6
            for m in metrics:
                m.avg_velocity_6_sprints = all_6_velocity

        # Determine trend
        if len(metrics) >= 2:
            for m in metrics:
                current_velocity = m.velocity
                prev_velocity = metrics[metrics.index(m) + 1].velocity if metrics.index(m) + 1 < len(metrics) else current_velocity

                if current_velocity > prev_velocity * 1.1:
                    m.trend = "INCREASING"
                elif current_velocity < prev_velocity * 0.9:
                    m.trend = "DECREASING"
                else:
                    m.trend = "STABLE"

        db.commit()

    @staticmethod
    def get_velocity_chart(db: Session, project_id: str) -> Optional[VelocityChartData]:
        """Get velocity chart data for last 6 sprints"""
        metrics = db.query(VelocityMetric).filter(
            VelocityMetric.project_id == project_id
        ).order_by(VelocityMetric.sprint_number).limit(6).all()

        if not metrics:
            return None

        return VelocityChartData(
            sprints=[f"Sprint {m.sprint_number}" for m in metrics],
            commitments=[m.commitment for m in metrics],
            completed=[m.completed for m in metrics],
            velocities=[m.velocity for m in metrics],
            avg_velocity_3=metrics[-1].avg_velocity_3_sprints if metrics else None,
            trend=metrics[-1].trend if metrics else "STABLE"
        )


class ResourceUtilizationService:
    """
    Resource capacity and utilization tracking.
    
    Heatmap color coding:
    - GREEN: 70-90% utilization (optimal)
    - RED: >100% utilization (overloaded)
    - GREY: <50% utilization (underutilized)
    
    Ref: Module 11 - Feature 2.2 - Resource Utilization Heatmap
    """

    @staticmethod
    def create_allocation(
        db: Session,
        allocation_data: Dict[str, Any]
    ) -> ResourceAllocation:
        """Create resource allocation record"""
        allocation = ResourceAllocation(
            user_id=allocation_data["user_id"],
            project_id=allocation_data["project_id"],
            working_capacity_hours=allocation_data.get("working_capacity_hours", 8.0),
            assigned_hours=allocation_data.get("assigned_hours", 0),
            allocation_date=allocation_data.get("allocation_date", datetime.utcnow()),
        )

        # Calculate utilization
        allocation = ResourceUtilizationService._calculate_utilization(allocation)

        db.add(allocation)
        db.commit()
        return allocation

    @staticmethod
    def _calculate_utilization(allocation: ResourceAllocation) -> ResourceAllocation:
        """Calculate utilization metrics and status"""
        if allocation.working_capacity_hours > 0:
            allocation.utilization_percentage = (
                allocation.assigned_hours / allocation.working_capacity_hours * 100
            )
        else:
            allocation.utilization_percentage = 0

        # Color coding (AC 1)
        util = allocation.utilization_percentage
        if util > 100:
            allocation.capacity_status = "RED"
            allocation.is_overloaded = True
        elif util >= 70 and util <= 90:
            allocation.capacity_status = "GREEN"
        else:
            allocation.capacity_status = "GREY"
            allocation.is_underutilized = util < 50

        return allocation

    @staticmethod
    def get_heatmap_data(
        db: Session,
        project_id: str,
        date_filter: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get heatmap data for resource utilization.
        
        Returns list of resources with capacity status for drill-down.
        """
        if date_filter is None:
            date_filter = date.today()

        allocations = db.query(ResourceAllocation).filter(
            and_(
                ResourceAllocation.project_id == project_id,
                ResourceAllocation.allocation_date >= datetime.combine(date_filter, datetime.min.time()),
                ResourceAllocation.allocation_date <= datetime.combine(date_filter, datetime.max.time()),
            )
        ).all()

        return [
            {
                "user_id": a.user_id,
                "capacity_status": a.capacity_status,
                "utilization_percentage": a.utilization_percentage,
                "assigned_hours": a.assigned_hours,
                "working_capacity": a.working_capacity_hours,
                "is_overloaded": a.is_overloaded,
                "is_underutilized": a.is_underutilized,
            }
            for a in allocations
        ]


class TimeTrackingService:
    """
    Time entry tracking with timer and manual entry support.
    
    Features:
    - Timer mode (Start/Stop auto-calculation)
    - Manual entry mode (hh:mm:ss input)
    - Edit history tracking with validation
    - Billable vs Non-billable classification
    - Daily limit validation (hard limit 24h, soft warning 12h)
    
    Ref: Module 11 - Feature 2.3 - Time Tracking & Timesheets
    """

    @staticmethod
    def create_time_entry(
        db: Session,
        entry_data: TimeEntryCreate
    ) -> TimeEntry:
        """Create time entry"""
        duration = entry_data.end_time - entry_data.start_time
        duration_seconds = int(duration.total_seconds())
        duration_hours = duration_seconds / 3600

        entry = TimeEntry(
            user_id=entry_data.user_id,
            project_id=entry_data.project_id,
            task_id=entry_data.task_id,
            start_time=entry_data.start_time,
            end_time=entry_data.end_time,
            duration_seconds=duration_seconds,
            duration_hours=duration_hours,
            entry_type=entry_data.entry_type,
            is_billable=entry_data.is_billable,
            billable_status=entry_data.billable_status,
            category=entry_data.category,
            description=entry_data.description,
        )

        # Validate daily limits
        entry = TimeTrackingService._validate_daily_limits(db, entry)

        db.add(entry)
        db.commit()
        return entry

    @staticmethod
    def update_time_entry(
        db: Session,
        entry_id: UUID,
        update_data: TimeEntryUpdate
    ) -> Optional[TimeEntry]:
        """Update time entry (with edit tracking)"""
        entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()

        if not entry:
            return None

        # Track edits
        edit_history = entry.edit_history or []
        old_values = {
            "end_time": str(entry.end_time),
            "is_billable": entry.is_billable,
            "category": entry.category,
        }

        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None and field != "edit_reason":
                setattr(entry, field, value)

        # Recalculate duration if end_time changed
        if "end_time" in update_dict and update_dict["end_time"]:
            duration = entry.end_time - entry.start_time
            entry.duration_seconds = int(duration.total_seconds())
            entry.duration_hours = entry.duration_seconds / 3600

        # Validate daily limits
        entry = TimeTrackingService._validate_daily_limits(db, entry)

        # Record edit
        entry.edit_count += 1
        entry.manually_edited = True
        edit_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "old_values": old_values,
            "reason": update_data.edit_reason,
        })
        entry.edit_history = edit_history

        db.commit()
        return entry

    @staticmethod
    def _validate_daily_limits(db: Session, entry: TimeEntry) -> TimeEntry:
        """
        Validate daily time logging limits (Business Rules).
        
        - Hard limit: 24h per day
        - Soft warning: > 12h per day
        """
        # Get all entries for this user on this day
        entry_date = entry.start_time.date()
        daily_entries = db.query(TimeEntry).filter(
            and_(
                TimeEntry.user_id == entry.user_id,
                TimeEntry.start_time >= datetime.combine(entry_date, datetime.min.time()),
                TimeEntry.start_time <= datetime.combine(entry_date, datetime.max.time()),
                TimeEntry.id != entry.id,  # Exclude current entry
            )
        ).all()

        daily_total = sum(e.duration_hours for e in daily_entries) + entry.duration_hours

        entry.daily_warning_exceeded = daily_total > 12
        entry.daily_max_exceeded = daily_total > 24

        return entry


class TimesheetApprovalService:
    """
    Timesheet aggregation and approval workflow.
    
    Workflow:
    DRAFT → SUBMITTED → APPROVED or REJECTED
    
    Features:
    - Aggregates time entries into timesheet
    - Tracks billable vs non-billable hours
    - Approval by Project Manager/Owner
    - Rejection with feedback
    
    Ref: Module 11 - Feature 2.3 AC 3 - Timesheet Approval Workflow
    """

    @staticmethod
    def create_timesheet(
        db: Session,
        timesheet_data: TimesheetCreate
    ) -> Timesheet:
        """Create timesheet (initially DRAFT)"""
        timesheet = Timesheet(
            user_id=timesheet_data.user_id,
            project_id=timesheet_data.project_id,
            period_start_date=timesheet_data.period_start_date,
            period_end_date=timesheet_data.period_end_date,
            period_type=timesheet_data.period_type,
            status=TimesheetStatusEnum.DRAFT,
            notes=timesheet_data.notes,
        )

        # Aggregate time entries
        TimesheetApprovalService._aggregate_time_entries(db, timesheet)

        db.add(timesheet)
        db.commit()
        return timesheet

    @staticmethod
    def _aggregate_time_entries(db: Session, timesheet: Timesheet) -> None:
        """Aggregate time entries into timesheet"""
        entries = db.query(TimeEntry).filter(
            and_(
                TimeEntry.user_id == timesheet.user_id,
                TimeEntry.project_id == timesheet.project_id,
                TimeEntry.start_time >= timesheet.period_start_date,
                TimeEntry.start_time <= timesheet.period_end_date,
            )
        ).all()

        billable_hours = sum(
            e.duration_hours for e in entries if e.is_billable
        )
        total_hours = sum(e.duration_hours for e in entries)

        timesheet.total_hours = total_hours
        timesheet.billable_hours = billable_hours
        timesheet.non_billable_hours = total_hours - billable_hours
        timesheet.time_entries_count = len(entries)

        # Calculate billable amount
        billable_amount = Decimal(0)
        for e in entries:
            if e.is_billable and e.billable_amount:
                billable_amount += e.billable_amount
        timesheet.billable_amount = billable_amount

    @staticmethod
    def submit_timesheet(
        db: Session,
        timesheet_id: UUID,
        notes: Optional[str] = None
    ) -> Optional[Timesheet]:
        """Submit timesheet for approval"""
        timesheet = db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()

        if not timesheet or timesheet.status != TimesheetStatusEnum.DRAFT:
            return None

        timesheet.status = TimesheetStatusEnum.SUBMITTED
        timesheet.submitted_at = datetime.utcnow()
        if notes:
            timesheet.notes = notes

        db.commit()
        return timesheet

    @staticmethod
    def approve_timesheet(
        db: Session,
        timesheet_id: UUID,
        approved_by: str,
        approval_notes: Optional[str] = None
    ) -> Optional[Timesheet]:
        """Approve timesheet"""
        timesheet = db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()

        if not timesheet or timesheet.status != TimesheetStatusEnum.SUBMITTED:
            return None

        timesheet.status = TimesheetStatusEnum.APPROVED
        timesheet.approved_by = approved_by
        timesheet.approved_at = datetime.utcnow()
        timesheet.approval_notes = approval_notes

        db.commit()
        return timesheet

    @staticmethod
    def reject_timesheet(
        db: Session,
        timesheet_id: UUID,
        rejection_reason: str
    ) -> Optional[Timesheet]:
        """Reject timesheet"""
        timesheet = db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()

        if not timesheet or timesheet.status != TimesheetStatusEnum.SUBMITTED:
            return None

        timesheet.status = TimesheetStatusEnum.REJECTED
        timesheet.rejected_at = datetime.utcnow()
        timesheet.rejection_reason = rejection_reason

        db.commit()
        return timesheet


class CustomReportService:
    """
    Custom report builder with drag-drop interface.
    
    Features:
    - Dimension/Metric selection
    - Advanced filtering (AND/OR logic)
    - Report execution and export
    - Template support
    
    Ref: Module 11 - Feature 2.4 - Custom Report Builder
    """

    @staticmethod
    def create_custom_report(
        db: Session,
        report_data: CustomReportCreate,
        created_by: str
    ) -> CustomReport:
        """Create custom report"""
        report = CustomReport(
            name=report_data.name,
            project_id=report_data.project_id,
            description=report_data.description,
            created_by=created_by,
            dimensions=report_data.dimensions,
            metrics=report_data.metrics,
            filters=report_data.filters or [],
            report_type=AnalyticsTypeEnum.CUSTOM_REPORT,
            visualization_type=report_data.visualization_type,
            is_public=report_data.is_public,
            is_template=report_data.is_template,
        )

        db.add(report)
        db.commit()
        return report

    @staticmethod
    def execute_report(db: Session, report_id: UUID) -> Dict[str, Any]:
        """
        Execute custom report and return results.
        
        This is a placeholder for query building logic.
        In production, would construct and execute dynamic queries
        based on dimensions, metrics, and filters.
        """
        report = db.query(CustomReport).filter(CustomReport.id == report_id).first()

        if not report:
            return {"error": "Report not found"}

        # Update last run
        report.last_run_at = datetime.utcnow()

        # TODO: Implement dynamic query builder based on dimensions and metrics
        result_data = []
        report.last_run_result_size = len(result_data)

        db.commit()

        return {
            "report_id": str(report_id),
            "execution_time_ms": 0,
            "result_count": len(result_data),
            "data": result_data,
        }


class ReportSchedulingService:
    """
    Automated report generation and email delivery.
    
    Features:
    - Frequency scheduling (Daily, Weekly, Monthly, etc.)
    - Recipient management
    - Export format selection
    - Execution tracking
    
    Ref: Module 11 - Feature 2.4 - Custom Report Builder (Scheduling)
    """

    @staticmethod
    def create_schedule(
        db: Session,
        schedule_data: ReportScheduleCreate,
        created_by: str
    ) -> ReportSchedule:
        """Create report schedule"""
        schedule = ReportSchedule(
            custom_report_id=schedule_data.custom_report_id,
            project_id=schedule_data.project_id,
            created_by=created_by,
            frequency=schedule_data.frequency,
            is_active=True,
            start_date=schedule_data.start_date,
            end_date=schedule_data.end_date,
            execution_days=schedule_data.execution_days,
            execution_time=schedule_data.execution_time,
            recipient_emails=schedule_data.recipient_emails,
            export_format=schedule_data.export_format,
            include_charts=schedule_data.include_charts,
        )

        # Calculate next run
        schedule.next_run_at = ReportSchedulingService._calculate_next_run(schedule)

        db.add(schedule)
        db.commit()
        return schedule

    @staticmethod
    def _calculate_next_run(schedule: ReportSchedule) -> datetime:
        """Calculate next scheduled execution time"""
        now = datetime.utcnow()
        exec_time = datetime.strptime(
            schedule.execution_time or "09:00", "%H:%M"
        ).time() if schedule.execution_time else None

        if schedule.frequency.value == "DAILY":
            if exec_time and now.time() >= exec_time:
                return now.replace(hour=exec_time.hour, minute=exec_time.minute) + timedelta(days=1)
            else:
                return now.replace(hour=exec_time.hour, minute=exec_time.minute)

        elif schedule.frequency.value == "WEEKLY":
            # TODO: Implement based on execution_days
            return now + timedelta(days=7)

        elif schedule.frequency.value == "MONTHLY":
            return now + timedelta(days=30)

        else:
            return now + timedelta(days=365)


# ==================== Metric Snapshot Service ====================

class MetricSnapshotService:
    """
    Historical tracking of EVM metrics for trend analysis and dashboards.
    
    Records: CPI, SPI, cost/schedule variance for performance history.
    """

    @staticmethod
    def create_snapshot(
        db: Session,
        project_id: str,
        sprint_id: Optional[str],
        snapshot_data: Dict[str, Any]
    ) -> MetricSnapshot:
        """Create EVM metric snapshot"""
        snapshot = MetricSnapshot(
            project_id=project_id,
            sprint_id=sprint_id,
            snapshot_date=snapshot_data.get('snapshot_date', datetime.utcnow()),
            planned_value=snapshot_data['planned_value'],
            earned_value=snapshot_data['earned_value'],
            actual_cost=snapshot_data['actual_cost'],
            recorded_by=snapshot_data.get('recorded_by'),
            notes=snapshot_data.get('notes')
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    @staticmethod
    def calculate_evm_metrics(snapshot: MetricSnapshot) -> Dict[str, float]:
        """Calculate performance indexes from snapshot"""
        pv = float(snapshot.planned_value) or 1
        ev = float(snapshot.earned_value)
        ac = float(snapshot.actual_cost) or 1
        
        return {
            'cpi': ev / ac if ac > 0 else 0,
            'spi': ev / pv if pv > 0 else 0,
            'cost_variance': ev - ac,
            'schedule_variance': ev - pv
        }

    @staticmethod
    def get_trend(db: Session, project_id: str, days: int = 30) -> List[MetricSnapshot]:
        """Get EVM trend for period"""
        since = datetime.utcnow() - timedelta(days=days)
        return db.query(MetricSnapshot).filter(
            and_(
                MetricSnapshot.project_id == project_id,
                MetricSnapshot.snapshot_date >= since
            )
        ).order_by(MetricSnapshot.snapshot_date).all()


# ==================== KPI Service ====================

class KPIService:
    """
    Key Performance Indicator tracking and evaluation.
    
    Tracks: target vs actual, status (ON_TRACK/AT_RISK/OFF_TRACK), achievement.
    """

    @staticmethod
    def create_kpi(
        db: Session,
        project_id: str,
        kpi_data: Dict[str, Any]
    ) -> KPI:
        """Create KPI for project"""
        kpi = KPI(
            project_id=project_id,
            sprint_id=kpi_data.get('sprint_id'),
            created_by=kpi_data.get('created_by'),
            name=kpi_data['name'],
            description=kpi_data.get('description'),
            kpi_type=kpi_data['kpi_type'],
            unit=kpi_data['unit'],
            target_value=kpi_data['target_value'],
            weight=kpi_data.get('weight', 1.0),
            start_date=kpi_data['start_date'],
            target_date=kpi_data['target_date']
        )
        db.add(kpi)
        db.commit()
        db.refresh(kpi)
        return kpi

    @staticmethod
    def evaluate_kpi(kpi: KPI, actual_value: float) -> str:
        """Evaluate KPI status"""
        kpi.actual_value = actual_value
        
        # Determine status based on thresholds
        if actual_value >= kpi.green_threshold:
            status = "ON_TRACK"
        elif actual_value >= kpi.amber_threshold:
            status = "AT_RISK"
        else:
            status = "OFF_TRACK"
        
        kpi.status = status
        kpi.achieved = actual_value >= kpi.target_value
        return status

    @staticmethod
    def bulk_update_kpis(db: Session, project_id: str, updates: Dict[str, float]):
        """Bulk update KPI values"""
        kpis = db.query(KPI).filter(KPI.project_id == project_id).all()
        for kpi in kpis:
            if kpi.id in updates:
                KPIService.evaluate_kpi(kpi, updates[kpi.id])
        db.commit()


# ==================== Timesheet Approval Service ====================

class TimesheetApprovalService:
    """
    Manage timesheet approval workflow separately from Timesheet entity.
    
    Implements: DRAFT → SUBMITTED → APPROVED/REJECTED workflow
    Validates: compliance rules, escalation requirements
    """

    @staticmethod
    def submit_for_approval(
        db: Session,
        timesheet_id: UUID,
        approver_id: str
    ) -> TimesheetApproval:
        """Submit timesheet for approval"""
        # Get or create approval record
        approval = db.query(TimesheetApproval).filter(
            TimesheetApproval.timesheet_id == timesheet_id
        ).first()
        
        if not approval:
            approval = TimesheetApproval(
                timesheet_id=timesheet_id,
                approver_id=approver_id
            )
            db.add(approval)
        
        approval.status = TimesheetStatusEnum.SUBMITTED
        approval.submitted_at = datetime.utcnow()
        db.commit()
        db.refresh(approval)
        return approval

    @staticmethod
    def approve(
        db: Session,
        approval_id: UUID,
        notes: Optional[str] = None
    ) -> TimesheetApproval:
        """Approve timesheet"""
        approval = db.query(TimesheetApproval).get(approval_id)
        approval.status = TimesheetStatusEnum.APPROVED
        approval.approved_at = datetime.utcnow()
        approval.approval_notes = notes
        db.commit()
        db.refresh(approval)
        return approval

    @staticmethod
    def reject(
        db: Session,
        approval_id: UUID,
        reason: str,
        rejected_by: str
    ) -> TimesheetApproval:
        """Reject timesheet"""
        approval = db.query(TimesheetApproval).get(approval_id)
        approval.status = TimesheetStatusEnum.REJECTED
        approval.rejected_at = datetime.utcnow()
        approval.rejection_reason = reason
        approval.rejected_by = rejected_by
        db.commit()
        db.refresh(approval)
        return approval

    @staticmethod
    def validate_compliance(approval: TimesheetApproval) -> bool:
        """Check compliance rules"""
        # Check business rules
        if not approval.validation_passed:
            approval.is_compliant = False
            approval.requires_escalation = True
            return False
        
        approval.is_compliant = True
        return True


# ==================== Report Permission Service ====================

class ReportPermissionService:
    """
    Granular access control for custom reports.
    
    Features: time-limited access, delegation, scope hierarchy
    """

    @staticmethod
    def grant_access(
        db: Session,
        report_id: str,
        user_id: str,
        permission_level: str,
        granted_by: str,
        expires_at: Optional[datetime] = None,
        grant_reason: Optional[str] = None
    ) -> ReportPermission:
        """Grant permission to report"""
        # Check existing permission
        existing = db.query(ReportPermission).filter(
            and_(
                ReportPermission.report_id == report_id,
                ReportPermission.user_id == user_id
            )
        ).first()
        
        if existing:
            existing.permission_level = permission_level
            existing.expires_at = expires_at
            permission = existing
        else:
            permission = ReportPermission(
                report_id=report_id,
                user_id=user_id,
                granted_by=granted_by,
                permission_level=permission_level,
                grant_reason=grant_reason,
                expires_at=expires_at
            )
            db.add(permission)
        
        permission.is_active = True
        permission.granted_at = datetime.utcnow()
        db.commit()
        db.refresh(permission)
        return permission

    @staticmethod
    def revoke_access(
        db: Session,
        permission_id: UUID,
        revoked_by: str,
        reason: Optional[str] = None
    ) -> ReportPermission:
        """Revoke report access"""
        permission = db.query(ReportPermission).get(permission_id)
        permission.is_active = False
        permission.revoked_at = datetime.utcnow()
        permission.revoked_by = revoked_by
        db.commit()
        db.refresh(permission)
        return permission

    @staticmethod
    def check_access(
        db: Session,
        report_id: str,
        user_id: str,
        required_level: str = "VIEW"
    ) -> bool:
        """Check if user has access to report"""
        permission = db.query(ReportPermission).filter(
            and_(
                ReportPermission.report_id == report_id,
                ReportPermission.user_id == user_id,
                ReportPermission.is_active == True
            )
        ).first()
        
        if not permission:
            return False
        
        # Check expiration
        if permission.expires_at and permission.expires_at < datetime.utcnow():
            return False
        
        # Level hierarchy: VIEW < EDIT < SHARE < ADMIN
        levels = {"VIEW": 1, "EDIT": 2, "SHARE": 3, "ADMIN": 4}
        return levels.get(permission.permission_level, 0) >= levels.get(required_level, 0)

    @staticmethod
    def get_user_reports(
        db: Session,
        user_id: str,
        permission_level: str = "VIEW"
    ) -> List[ReportPermission]:
        """Get reports accessible by user"""
        return db.query(ReportPermission).filter(
            and_(
                ReportPermission.user_id == user_id,
                ReportPermission.is_active == True
            )
        ).all()

