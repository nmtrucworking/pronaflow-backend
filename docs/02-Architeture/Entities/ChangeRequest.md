# Module 14
|Field|Type|
|---|---|
|change_id (PK)|UUID|
|requested_by|UUID|
|change_type|enum (DEPLOY / CONFIG)|
|risk_level|enum (LOW / HIGH)|
|status|enum (PENDING / APPROVED / REJECTED)|
|approved_by|UUID|
|executed_at|timestamp|
