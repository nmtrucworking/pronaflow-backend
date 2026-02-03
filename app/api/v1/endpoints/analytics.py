"""
Analytics and Reporting API Endpoints for Module 11.

Endpoints (22+):
- Sprint Metrics: GET burn-down/up, GET velocity
- Resource Utilization: GET heatmap, GET allocation by user
- Time Tracking: POST/GET/UPDATE entries, GET daily summary
- Timesheet: POST create, PATCH submit/approve/reject, GET list
- Custom Reports: POST create, POST execute, GET list
- Report Schedules: POST create, PATCH update, GET list
- Export: GET report export (PDF/CSV/XLSX)

Ref: Module 11 - Advanced Analytics and Reporting
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.db.models.users import User
from app.schemas.analytics import (
    SprintMetricCreate, SprintMetricRead, SprintMetricUpdate,
    VelocityMetricCreate, VelocityMetricRead,
    ResourceAllocationCreate, ResourceAllocationRead, ResourceHeatmapRead,
    TimeEntryCreate, TimeEntryRead, TimeEntryUpdate, TimerControlRequest,
    TimesheetCreate, TimesheetRead, TimesheetSubmit, TimesheetApprove, TimesheetReject,
    CustomReportCreate, CustomReportRead, CustomReportUpdate, ReportExecuteRequest, ReportExecuteResponse,
    ReportScheduleCreate, ReportScheduleRead, ReportScheduleUpdate,
    BurndownChartData, VelocityChartData, AnalyticsOverviewRead,
    MetricSnapshotCreate, MetricSnapshotRead,
    KPICreate, KPIRead,
    TimesheetApprovalCreate, TimesheetApprovalRead,
    ReportPermissionCreate, ReportPermissionRead,
)
from app.services.analytics import (
    SprintMetricsService, VelocityService, ResourceUtilizationService,
    TimeTrackingService, TimesheetApprovalService,
    CustomReportService, ReportSchedulingService,
    MetricSnapshotService, KPIService, ReportPermissionService,
)
from app.core.config import settings

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


# ==================== Sprint Metrics Endpoints ====================

@router.post("/sprint-metrics", response_model=SprintMetricRead, status_code=201)
def create_sprint_metric(
    sprint_data: SprintMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create sprint metric (Project Manager only)"""
    metric = SprintMetricsService.create_sprint_metric(db, sprint_data)
    return metric


@router.get("/sprint-metrics/{sprint_id}", response_model=SprintMetricRead)
def get_sprint_metric(
    sprint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get sprint metrics"""
    # TODO: Implement DB query
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.patch("/sprint-metrics/{sprint_id}", response_model=SprintMetricRead)
def update_sprint_metric(
    sprint_id: str,
    update_data: SprintMetricUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update sprint metrics"""
    metric = SprintMetricsService.update_metrics(db, sprint_id, update_data)
    if not metric:
        raise HTTPException(status_code=404, detail="Sprint metric not found")
    return metric


@router.get("/sprint-metrics/{sprint_id}/burn-down", response_model=BurndownChartData)
def get_burndown_chart(
    sprint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get burn-down chart (Real-time)"""
    chart = SprintMetricsService.get_burndown_chart(db, sprint_id)
    if not chart:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return chart


@router.get("/sprint-metrics/{sprint_id}/burn-up")
def get_burnup_chart(
    sprint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get burn-up chart with scope creep visualization"""
    # TODO: Similar to burn-down but shows accumulated completed + scope changes
    raise HTTPException(status_code=501, detail="Not yet implemented")


# ==================== Velocity Metrics Endpoints ====================

@router.post("/velocity-metrics", response_model=VelocityMetricRead, status_code=201)
def create_velocity_metric(
    velocity_data: VelocityMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create velocity metric for sprint"""
    metric = VelocityService.create_velocity_metric(db, velocity_data)
    return metric


@router.get("/projects/{project_id}/velocity-chart", response_model=VelocityChartData)
def get_velocity_chart(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get velocity trend chart (last 6 sprints)"""
    chart = VelocityService.get_velocity_chart(db, project_id)
    if not chart:
        raise HTTPException(status_code=404, detail="No velocity data found")
    return chart


# ==================== Resource Utilization Heatmap Endpoints ====================

@router.get("/projects/{project_id}/heatmap", response_model=ResourceHeatmapRead)
def get_resource_heatmap(
    project_id: str,
    date_filter: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get resource utilization heatmap"""
    heatmap_data = ResourceUtilizationService.get_heatmap_data(db, project_id, date_filter)
    return ResourceHeatmapRead(
        date=date_filter or date.today(),
        resources=heatmap_data
    )


@router.get("/users/{user_id}/allocations")
def get_user_allocations(
    user_id: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's resource allocations for period (drill-down from heatmap)"""
    # TODO: Query allocations with task details for this user
    raise HTTPException(status_code=501, detail="Not yet implemented")


# ==================== Time Entry Endpoints ====================

@router.post("/time-entries", response_model=TimeEntryRead, status_code=201)
def create_time_entry(
    entry_data: TimeEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create time entry (timer or manual)"""
    entry = TimeTrackingService.create_time_entry(db, entry_data)
    return entry


@router.get("/time-entries/{entry_id}", response_model=TimeEntryRead)
def get_time_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get time entry details"""
    # TODO: Implement DB query
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.patch("/time-entries/{entry_id}", response_model=TimeEntryRead)
def update_time_entry(
    entry_id: UUID,
    update_data: TimeEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update time entry (with edit history)"""
    entry = TimeTrackingService.update_time_entry(db, entry_id, update_data)
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return entry


@router.delete("/time-entries/{entry_id}", status_code=204)
def delete_time_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete time entry (soft delete)"""
    # TODO: Implement soft delete with audit trail
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/users/{user_id}/time-entries")
def get_user_time_entries(
    user_id: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's time entries for date range"""
    # TODO: Query time entries with daily summaries
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/timer/start")
def start_timer(
    request: TimerControlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start floating timer widget"""
    # TODO: Create active timer entry
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/timer/stop", response_model=TimeEntryRead)
def stop_timer(
    request: TimerControlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stop timer and save time entry"""
    # TODO: Complete active timer entry
    raise HTTPException(status_code=501, detail="Not yet implemented")


# ==================== Timesheet Endpoints ====================

@router.post("/timesheets", response_model=TimesheetRead, status_code=201)
def create_timesheet(
    timesheet_data: TimesheetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create timesheet (DRAFT status)"""
    timesheet = TimesheetApprovalService.create_timesheet(db, timesheet_data)
    return timesheet


@router.get("/timesheets/{timesheet_id}", response_model=TimesheetRead)
def get_timesheet(
    timesheet_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get timesheet details"""
    # TODO: Implement DB query
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/users/{user_id}/timesheets")
def get_user_timesheets(
    user_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's timesheets (with optional status filter)"""
    # TODO: Query timesheets
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.patch("/timesheets/{timesheet_id}/submit", response_model=TimesheetRead)
def submit_timesheet(
    timesheet_id: UUID,
    submit_data: TimesheetSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit timesheet for approval"""
    timesheet = TimesheetApprovalService.submit_timesheet(
        db, timesheet_id, submit_data.notes
    )
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    return timesheet


@router.patch("/timesheets/{timesheet_id}/approve", response_model=TimesheetRead)
def approve_timesheet(
    timesheet_id: UUID,
    approve_data: TimesheetApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve timesheet (PM/Owner only)"""
    timesheet = TimesheetApprovalService.approve_timesheet(
        db, timesheet_id, current_user.id, approve_data.approval_notes
    )
    if not timesheet:
        raise HTTPException(status_code=400, detail="Cannot approve this timesheet")
    return timesheet


@router.patch("/timesheets/{timesheet_id}/reject", response_model=TimesheetRead)
def reject_timesheet(
    timesheet_id: UUID,
    reject_data: TimesheetReject,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject timesheet with feedback"""
    timesheet = TimesheetApprovalService.reject_timesheet(
        db, timesheet_id, reject_data.rejection_reason
    )
    if not timesheet:
        raise HTTPException(status_code=400, detail="Cannot reject this timesheet")
    return timesheet


# ==================== Custom Report Endpoints ====================

@router.post("/custom-reports", response_model=CustomReportRead, status_code=201)
def create_custom_report(
    report_data: CustomReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create custom report (drag-drop configured)"""
    report = CustomReportService.create_custom_report(db, report_data, current_user.id)
    return report


@router.get("/custom-reports/{report_id}", response_model=CustomReportRead)
def get_custom_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get custom report configuration"""
    # TODO: Implement DB query
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/projects/{project_id}/custom-reports")
def list_custom_reports(
    project_id: str,
    include_templates: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List custom reports in project"""
    # TODO: Query reports with pagination
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/custom-reports/{report_id}/execute", response_model=ReportExecuteResponse)
def execute_custom_report(
    report_id: UUID,
    request: ReportExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute report and return results"""
    result = CustomReportService.execute_report(db, report_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return ReportExecuteResponse(
        report_id=report_id,
        execution_time_ms=result["execution_time_ms"],
        result_count=result["result_count"],
        data=result.get("data"),
    )


@router.post("/custom-reports/{report_id}/export")
def export_custom_report(
    report_id: UUID,
    export_format: str = Query("PDF"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export report to PDF/CSV/XLSX"""
    # TODO: Generate export file and return download URL
    raise HTTPException(status_code=501, detail="Not yet implemented")


# ==================== Report Schedule Endpoints ====================

@router.post("/report-schedules", response_model=ReportScheduleRead, status_code=201)
def create_report_schedule(
    schedule_data: ReportScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create automated report schedule"""
    schedule = ReportSchedulingService.create_schedule(db, schedule_data, current_user.id)
    return schedule


@router.get("/report-schedules/{schedule_id}", response_model=ReportScheduleRead)
def get_report_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get report schedule"""
    # TODO: Implement DB query
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/custom-reports/{report_id}/schedules")
def list_report_schedules(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all schedules for a report"""
    # TODO: Query schedules
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.patch("/report-schedules/{schedule_id}", response_model=ReportScheduleRead)
def update_report_schedule(
    schedule_id: UUID,
    update_data: ReportScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update report schedule"""
    # TODO: Implement update
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.delete("/report-schedules/{schedule_id}", status_code=204)
def delete_report_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete report schedule"""
    # TODO: Implement delete
    raise HTTPException(status_code=501, detail="Not yet implemented")


# ==================== Analytics Overview ====================

@router.get("/projects/{project_id}/overview", response_model=AnalyticsOverviewRead)
def get_analytics_overview(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get high-level analytics dashboard overview"""
    # TODO: Aggregate sprint health, velocity, resource utilization, time tracking
    raise HTTPException(status_code=501, detail="Not yet implemented")


# ==================== Metric Snapshot Endpoints ====================

@router.post("/metric-snapshots", response_model=MetricSnapshotRead, status_code=201)
def create_metric_snapshot(
    snapshot_data: MetricSnapshotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create EVM metric snapshot"""
    snapshot = MetricSnapshotService.create_snapshot(
        db=db,
        project_id=snapshot_data.project_id,
        sprint_id=snapshot_data.sprint_id,
        snapshot_data={
            'snapshot_date': snapshot_data.snapshot_date,
            'planned_value': snapshot_data.planned_value,
            'earned_value': snapshot_data.earned_value,
            'actual_cost': snapshot_data.actual_cost,
            'recorded_by': current_user.id,
        }
    )
    return snapshot


@router.get("/projects/{project_id}/metric-snapshots/history")
def get_metric_snapshot_history(
    project_id: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get EVM metric trend history"""
    snapshots = MetricSnapshotService.get_trend(db=db, project_id=project_id, days=days)
    return {
        'project_id': project_id,
        'days': days,
        'count': len(snapshots),
        'snapshots': [
            {
                'id': s.id,
                'snapshot_date': s.snapshot_date,
                'cpi': MetricSnapshotService.calculate_evm_metrics(s)['cpi'],
                'spi': MetricSnapshotService.calculate_evm_metrics(s)['spi'],
                'cost_variance': s.cost_variance,
                'schedule_variance': s.schedule_variance,
                'health_status': s.health_status,
            }
            for s in snapshots
        ]
    }


# ==================== KPI Endpoints ====================

@router.post("/kpis", response_model=KPIRead, status_code=201)
def create_kpi(
    kpi_data: KPICreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create KPI for project"""
    kpi_obj = KPIService.create_kpi(
        db=db,
        project_id=kpi_data.project_id,
        kpi_data={
            'sprint_id': kpi_data.sprint_id,
            'created_by': current_user.id,
            'name': kpi_data.name,
            'description': kpi_data.description,
            'kpi_type': kpi_data.kpi_type,
            'unit': kpi_data.unit,
            'target_value': kpi_data.target_value,
            'weight': kpi_data.weight,
            'start_date': kpi_data.start_date,
            'target_date': kpi_data.target_date,
        }
    )
    return kpi_obj


@router.get("/projects/{project_id}/kpis")
def get_project_kpis(
    project_id: str,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all KPIs for project"""
    from sqlalchemy import and_
    from app.db.models.analytics import KPI
    
    query = db.query(KPI).filter(KPI.project_id == project_id)
    if status:
        query = query.filter(KPI.status == status)
    
    kpis = query.all()
    return {
        'project_id': project_id,
        'count': len(kpis),
        'kpis': kpis
    }


@router.patch("/kpis/{kpi_id}", response_model=KPIRead)
def update_kpi_value(
    kpi_id: UUID,
    actual_value: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update KPI actual value"""
    from app.db.models.analytics import KPI
    
    kpi = db.query(KPI).get(kpi_id)
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")
    
    KPIService.evaluate_kpi(kpi, actual_value)
    db.commit()
    db.refresh(kpi)
    return kpi


# ==================== Timesheet Approval Endpoints ====================

@router.post("/timesheet-approvals", response_model=TimesheetApprovalRead, status_code=201)
def create_timesheet_approval(
    approval_data: TimesheetApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create timesheet approval record"""
    approval = TimesheetApprovalService.submit_for_approval(
        db=db,
        timesheet_id=approval_data.timesheet_id,
        approver_id=current_user.id
    )
    return approval


@router.get("/timesheet-approvals/{approval_id}", response_model=TimesheetApprovalRead)
def get_timesheet_approval(
    approval_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get timesheet approval details"""
    from app.db.models.analytics import TimesheetApproval
    
    approval = db.query(TimesheetApproval).get(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    return approval


@router.patch("/timesheet-approvals/{approval_id}/approve")
def approve_timesheet(
    approval_id: UUID,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve timesheet"""
    approval = TimesheetApprovalService.approve(
        db=db,
        approval_id=approval_id,
        notes=notes
    )
    return {'status': 'approved', 'approval': approval}


@router.patch("/timesheet-approvals/{approval_id}/reject")
def reject_timesheet(
    approval_id: UUID,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject timesheet"""
    approval = TimesheetApprovalService.reject(
        db=db,
        approval_id=approval_id,
        reason=reason,
        rejected_by=current_user.id
    )
    return {'status': 'rejected', 'approval': approval}


# ==================== Report Permission Endpoints ====================

@router.post("/report-permissions", response_model=ReportPermissionRead, status_code=201)
def grant_report_access(
    permission_data: ReportPermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Grant report access to user"""
    permission = ReportPermissionService.grant_access(
        db=db,
        report_id=permission_data.report_id,
        user_id=permission_data.user_id,
        permission_level=permission_data.permission_level,
        granted_by=current_user.id,
        expires_at=permission_data.expires_at,
        grant_reason=permission_data.grant_reason
    )
    return permission


@router.get("/report-permissions/{permission_id}", response_model=ReportPermissionRead)
def get_report_permission(
    permission_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get report permission details"""
    from app.db.models.analytics import ReportPermission
    
    permission = db.query(ReportPermission).get(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    return permission


@router.get("/reports/{report_id}/permissions")
def get_report_permissions(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all permissions for report"""
    from app.db.models.analytics import ReportPermission
    
    permissions = db.query(ReportPermission).filter(
        ReportPermission.report_id == report_id
    ).all()
    
    return {
        'report_id': report_id,
        'count': len(permissions),
        'permissions': permissions
    }


@router.patch("/report-permissions/{permission_id}/revoke")
def revoke_report_access(
    permission_id: UUID,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoke report access"""
    permission = ReportPermissionService.revoke_access(
        db=db,
        permission_id=permission_id,
        revoked_by=current_user.id,
        reason=reason
    )
    return {'status': 'revoked', 'permission': permission}


@router.get("/users/{user_id}/report-permissions")
def get_user_report_permissions(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all reports accessible by user"""
    permissions = ReportPermissionService.get_user_reports(
        db=db,
        user_id=user_id,
        permission_level="VIEW"
    )
    
    return {
        'user_id': user_id,
        'count': len(permissions),
        'permissions': permissions
    }

