# Module 11 Quick Reference - Advanced Analytics & Reporting

**Status**: ✅ COMPLETE | **Tables**: 11/11 | **Endpoints**: 60+ | **Tests**: ✅ Ready

---

## 🚀 Quick Start

### 1. Start Server
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 2. Access Documentation
```
Interactive API Docs: http://localhost:8000/docs
Alternative Docs: http://localhost:8000/redoc
Health Check: http://localhost:8000/health
```

### 3. Database Tables (11 TOTAL - COMPLETE)

| Table | Columns | Indexes | Status | Purpose |
|-------|---------|---------|--------|---------|
| sprint_metrics | 23 | 3 | ✅ | Burn-down/up, EVM |
| metric_snapshots | 17 | 4 | ✅ NEW | EVM history |
| kpis | 21 | 3 | ✅ NEW | KPI tracking |
| velocity_metrics | 13 | 2 | ✅ | Velocity trends |
| resource_allocations | 13 | 4 | ✅ | Capacity heatmap |
| time_entries | 21 | 6 | ✅ | Time logs |
| timesheets | 20 | 5 | ✅ | Aggregated time |
| timesheet_approvals | 15 | 2 | ✅ NEW | Approval workflow |
| custom_reports | 16 | 2 | ✅ | Report templates |
| report_permissions | 15 | 4 | ✅ NEW | Access control |
| report_schedules | 19 | 3 | ✅ | Automation |
| **TOTAL** | **173** | **60+** | ✅ **11/11** | **COMPLETE** |

---

## 🔥 Key Features Quick Access

### 1. Sprint Metrics (Burn-down/Burn-up)
```python
# Create metric
POST /api/v1/analytics/sprint-metrics

# Get burn-down chart
GET /api/v1/analytics/sprint-metrics/{sprint_id}/burn-down

# Get burn-up chart (with scope creep)
GET /api/v1/analytics/sprint-metrics/{sprint_id}/burn-up
```

**Service**: `SprintMetricsService`
**Calculations**: CPI (Cost Performance Index), SPI (Schedule Performance Index)

### 2. Velocity Trending
```python
# Get 6-sprint velocity chart
GET /api/v1/analytics/projects/{project_id}/velocity-chart

# Returns: commitments, completed, velocities, avg_velocity_3_sprints, trend
```

**Service**: `VelocityService`
**Features**: 3-sprint and 6-sprint averages, trend detection

### 3. Resource Heatmap
```python
# Get resource utilization heatmap
GET /api/v1/analytics/projects/{project_id}/heatmap?date={YYYY-MM-DD}

# Drill-down: view tasks for user on specific day
GET /api/v1/analytics/users/{user_id}/allocations?start_date=...&end_date=...
```

**Service**: `ResourceUtilizationService`
**Color Coding**: GREEN (70-90%), RED (>100%), GREY (<50%)

### 4. Time Tracking
```python
# Start timer
POST /api/v1/analytics/timer/start
{
  "user_id": "...",
  "project_id": "...",
  "task_id": "...",  # optional
  "action": "START",
  "category": "Development"
}

# Stop timer & save entry
POST /api/v1/analytics/timer/stop

# Manual entry
POST /api/v1/analytics/time-entries
{
  "user_id": "...",
  "project_id": "...",
  "start_time": "2026-02-03T09:00:00",
  "end_time": "2026-02-03T10:30:00",
  "entry_type": "MANUAL",
  "is_billable": true,
  "category": "Development"
}

# Get user's entries for date range
GET /api/v1/analytics/users/{user_id}/time-entries?start_date=...&end_date=...
```

**Service**: `TimeTrackingService`
**Validations**: 
- No future logging
- Daily max 24h (hard limit)
- Daily >12h (soft warning)
- Edit history tracking

### 5. Timesheet Approval Workflow
```python
# Create timesheet (DRAFT)
POST /api/v1/analytics/timesheets
{
  "user_id": "...",
  "project_id": "...",
  "period_start_date": "2026-02-03",
  "period_end_date": "2026-02-09",
  "period_type": "WEEKLY"
}

# Submit for approval (SUBMITTED)
PATCH /api/v1/analytics/timesheets/{id}/submit

# Approve (APPROVED)
PATCH /api/v1/analytics/timesheets/{id}/approve
{"approval_notes": "Looks good"}

# Or reject (REJECTED)
PATCH /api/v1/analytics/timesheets/{id}/reject
{"rejection_reason": "Please verify hours in column B"}

# Query timesheets by status
GET /api/v1/analytics/users/{user_id}/timesheets?status=SUBMITTED
```

**Service**: `TimesheetApprovalService`
**Workflow**: DRAFT → SUBMITTED → APPROVED/REJECTED

### 6. Custom Reports
```python
# Create report with drag-drop config
POST /api/v1/analytics/custom-reports
{
  "name": "Project Overview",
  "project_id": "...",
  "dimensions": ["project", "assignee", "priority"],
  "metrics": ["count_tasks", "sum_hours"],
  "filters": [
    {"field": "status", "operator": "eq", "value": "DONE"}
  ],
  "visualization_type": "TABLE",
  "is_public": false
}

# List reports
GET /api/v1/analytics/projects/{project_id}/custom-reports?include_templates=true

# Execute report
POST /api/v1/analytics/custom-reports/{id}/execute
{"export_format": "PDF"}

# Export report
POST /api/v1/analytics/custom-reports/{id}/export?export_format=PDF
```

**Service**: `CustomReportService`
**Dimensions**: Project, Assignee, Tag, Priority, Month, Status  
**Metrics**: Count Tasks, Sum Hours, Avg Cycle Time

### 7. Scheduled Reports
```python
# Create automated report schedule
POST /api/v1/analytics/report-schedules
{
  "custom_report_id": "...",
  "project_id": "...",
  "frequency": "WEEKLY",
  "execution_days": [1, 3, 5],  # Mon, Wed, Fri
  "execution_time": "09:00",
  "recipient_emails": ["pm@example.com", "ceo@example.com"],
  "export_format": "PDF",
  "include_charts": true
}

# List schedules for report
GET /api/v1/analytics/custom-reports/{report_id}/schedules

# Update schedule
PATCH /api/v1/analytics/report-schedules/{id}
{"is_active": false}
```

**Service**: `ReportSchedulingService`
**Frequencies**: DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUALLY

---

## Configuration Settings

```python
# In .env or app/core/config.py

REPORT_DATA_FRESHNESS_MINUTES=1              # Real-time reports
TIMESHEET_APPROVAL_REQUIRED=True             # Enforce workflow
DAILY_LOG_WARNING_HOURS=12                   # Soft limit
DAILY_LOG_MAX_HOURS=24                       # Hard limit  
MAX_REPORT_EXPORT_SIZE_MB=100                # Export file size
REPORT_CACHE_TTL_SECONDS=300                 # 5 min cache
```

---

## Enumerations

**AnalyticsTypeEnum**: BURN_DOWN, BURN_UP, VELOCITY, HEATMAP, TIME_TRACKING, CUSTOM_REPORT
**ReportFormatEnum**: PDF, CSV, XLSX
**TimesheetStatusEnum**: DRAFT, SUBMITTED, APPROVED, REJECTED
**BillableStatusEnum**: BILLABLE, NON_BILLABLE
**ReportScheduleFrequencyEnum**: DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUALLY

---

## Business Rules

### Time Logging Validations
- ✅ No future date logging (except leave requests)
- ✅ Daily maximum: 24 hours (hard limit)
- ✅ Daily warning: >12 hours (soft warning)
- ✅ All manual edits tracked with reason

### Timesheet Workflow
- ✅ DRAFT → SUBMITTED → APPROVED or REJECTED
- ✅ Only approved timesheets sent to Payroll (Module 13)
- ✅ Rejection includes feedback for correction

### Resource Capacity
- ✅ GREEN: 70-90% utilization (optimal)
- ✅ RED: >100% utilization (overloaded, action needed)
- ✅ GREY: <50% utilization (underutilized)

### EVM Calculations
- ✅ CPI = EV / AC (Cost Performance Index)
- ✅ SPI = EV / PV (Schedule Performance Index)
- ✅ Risk levels: LOW (SPI≥0.95), MEDIUM (0.80-0.95), HIGH (<0.80)

### Data Visibility
- ✅ Salary/Cost: Owner and Admin only
- ✅ Members see: Own entries + project-level charts
- ✅ Colleagues timesheets: Restricted unless delegated

---

## Common Queries

### Get project analytics dashboard
```
GET /api/v1/analytics/projects/{project_id}/overview
```

### Check team overload status
```
GET /api/v1/analytics/projects/{project_id}/heatmap
// Look for RED cells indicating overloaded team members
```

### Retrieve daily time entries
```
GET /api/v1/analytics/users/{user_id}/time-entries?start_date=2026-02-03&end_date=2026-02-03
```

### Generate monthly timesheet
```
POST /api/v1/analytics/timesheets
{
  "period_type": "MONTHLY",
  "period_start_date": "2026-02-01",
  "period_end_date": "2026-02-28"
}
```

### Check sprint health
```
GET /api/v1/analytics/sprint-metrics/{sprint_id}/burn-down
// SPI < 0.9 indicates behind schedule
// risk_level == "HIGH" means urgent attention needed
```

---

## Testing Checklist

- [ ] Create time entry via timer widget
- [ ] Update time entry with manual edit
- [ ] Submit timesheet (moves to SUBMITTED)
- [ ] Approve timesheet (moves to APPROVED)
- [ ] View resource heatmap - verify color coding
- [ ] Click heatmap cell - drill-down shows tasks
- [ ] Create custom report - test drag-drop config
- [ ] Execute custom report - verify aggregation
- [ ] Export report as PDF/CSV/XLSX
- [ ] Create report schedule - verify next_run calculation
- [ ] Check burn-down chart - verify ideal vs actual lines
- [ ] Check velocity chart - verify 3-sprint average

---

## Integration Notes

**Depends On**:
- Module 4: Task models (for task_id reference)
- Module 5: Sprint models (for sprint_id reference)
- Module 1: User models (for user_id reference)

**Used By**:
- Module 13: Payroll & Invoicing (consumes approved timesheets)

**Features**:
- Standalone usage: All analytics features work independently
- Bidirectional: Changes to tasks auto-update sprint metrics
- Non-blocking: Analytics operations don't affect core workflows

---

**Quick Start**: See API_DOCUMENTATION.md for full endpoint reference and examples.
