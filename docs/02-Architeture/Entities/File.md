|Field|Type|Note|
|---|---|---|
|file_id (PK)|UUID||
|task_id (FK)|UUID|Context|
|uploaded_by (FK)|UUID||
|filename|varchar||
|mime_type|varchar||
|size|bigint||
|current_version|int||
|storage_tier|enum|HOT / COLD|
|created_at|timestamp||