> Job Cron

# Module 8
|Field|Type|
|---|---|
|job_id (PK)|UUID|
|policy_id (FK)|UUID|
|entity_id|UUID|
|status|enum|
|executed_at|timestamp|
|error_log|text|