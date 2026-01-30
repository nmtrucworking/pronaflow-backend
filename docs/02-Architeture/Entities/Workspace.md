> Tenant Logic - Container cao nhất

# Phân hệ 2.
|Field|Type|Note|
|---|---|---|
|workspace_id (PK)|UUID|Global unique|
|name|varchar(50)||
|description|text|nullable|
|owner_id (FK → User)|UUID|Owner hiện tại|
|status|enum|ACTIVE / SOFT_DELETED|
|is_deleted|boolean||
|deleted_at|timestamp|nullable|
|created_at|timestamp||
|updated_at|timestamp||