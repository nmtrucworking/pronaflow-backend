# Module 12
|Field|Type|
|---|---|
|delivery_id (PK)|UUID|
|webhook_id (FK)|UUID|
|payload|jsonb|
|response_code|int|
|status|enum|
|attempt_no|int|
|delivered_at|timestamp|
