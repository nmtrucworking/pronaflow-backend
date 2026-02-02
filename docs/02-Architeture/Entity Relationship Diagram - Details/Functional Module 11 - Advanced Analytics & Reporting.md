**Project**: PronaFlow 
**Version**: 1.0
**State**: Draft 
_**Last updated:** Jan 14, 2026_

---
# Entity
| Domain             | Mục tiêu             | Entity                                      | Status |
| ------------------ | -------------------- | ------------------------------------------- | -------|
| Metrics Core       | Snapshot & KPI       | [[MetricSnapshot]]<br>[[KPI]]               | ✅ |
| Agile Analytics    | Burn-down, Velocity  | [[SprintMetric]]                            | ✅ |
| Resource Analytics | Utilization          | [[ResourceUtilization]]                     | ✅ |
| Time Tracking      | Time log & Timesheet | [[TimeEntry]]<br>[[Timesheet]]              | ✅ |
| Approval           | Timesheet workflow   | [[TimesheetApproval]]                       | ✅ |
| Reporting          | Custom report        | [[ReportDefinition]]<br>[[ReportExecution]] | ✅ |
| Security           | Data visibility      | [[ReportPermission]]                        | ✅ |
# ERD
```mermaid
erDiagram
    PROJECT ||--o{ KPI : evaluates
    PROJECT ||--o{ METRIC_SNAPSHOT : measured_by

    SPRINT ||--o{ SPRINT_METRIC : analyzed_by
    SPRINT_METRIC ||--o{ METRIC_SNAPSHOT : records_evm

    USER ||--o{ TIME_ENTRY : logs
    TASK ||--o{ TIME_ENTRY : consumes

    USER ||--o{ TIMESHEET : submits
    TIMESHEET ||--o{ TIMESHEET_APPROVAL : reviewed_by
    USER ||--o{ TIMESHEET_APPROVAL : approves

    WORKSPACE ||--o{ REPORT_DEFINITION : defines
    REPORT_DEFINITION ||--o{ REPORT_EXECUTION : generates
    REPORT_DEFINITION ||--o{ REPORT_PERMISSION : secures
    USER ||--o{ REPORT_PERMISSION : grants_access
```
# Mapping Function into Entity
|Tài liệu|Entity|
|---|---|
|Burn-down / Burn-up|SprintMetric|
|Velocity 3 sprint|SprintMetric.average_velocity|
|Heatmap|ResourceUtilization|
|Drill-down|ResourceUtilization → TimeEntry|
|Timer & Manual|TimeEntry.source|
|Billable flag|TimeEntry.is_billable|
|Timesheet approval|TimesheetApproval|
|EVM (CPI/SPI)|MetricSnapshot|
|Pareto Bug|ReportDefinition + metrics|
