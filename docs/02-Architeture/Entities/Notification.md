|Field|Type|Note|
|---|---|---|
|notification_id (PK)|UUID||
|user_id (FK)|UUID|Receiver|
|event_id (FK)|UUID||
|title|varchar|Rendered|
|content|text|Rendered|
|priority|enum||
|is_read|boolean||
|expires_at|timestamp|TTL|
|created_at|timestamp||