> Thực thể trung tâm của phân hệ 3

# Phân hệ 3
|Field|Type|Note|
|---|---|---|
|project_id (PK)|UUID||
|workspace_id (FK)|UUID|Multi-tenant isolation|
|name|varchar||
|description|text||
|status|enum|NOT_STARTED / IN_PROGRESS / IN_REVIEW / DONE / CANCELLED|
|governance_mode|enum|SIMPLE / STRICT|
|visibility|enum|PUBLIC / PRIVATE|
|owner_id (FK → User)|UUID||
|start_date|date|nullable|
|end_date|date|nullable|
|archived_at|timestamp|nullable|
|created_at|timestamp||
|updated_at|timestamp||