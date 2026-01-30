> Ghi nhận thời gian làm việc
# Module 11
|Field|Type|
|---|---|
|time_entry_id (PK)|UUID|
|user_id (FK)|UUID|
|task_id (FK)|UUID|
|start_time|timestamp|
|end_time|timestamp|
|duration_minutes|int|
|is_billable|boolean|
|source|enum|
|created_at|timestamp|