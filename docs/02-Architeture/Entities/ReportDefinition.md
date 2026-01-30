> Cấu hình báo cáo

# Module 11
|Field|Type|
|---|---|
|report_id (PK)|UUID|
|workspace_id (FK)|UUID|
|name|varchar|
|dimensions|jsonb|
|metrics|jsonb|
|filters|jsonb|
|created_by|UUID|
|created_at|timestamp|
