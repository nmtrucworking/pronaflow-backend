# Module 7
|Field|Type|
|---|---|
|attempt_id (PK)|UUID|
|notification_id (FK)|UUID|
|channel_id (FK)|UUID|
|attempt_no|int|
|status|enum|
|error_message|text|
|attempted_at|timestamp|