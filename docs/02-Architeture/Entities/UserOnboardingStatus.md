# Module 16
|Field|Type|
|---|---|
|status_id (PK)|UUID|
|user_id (FK)|UUID|
|flow_id (FK)|UUID|
|current_step|int|
|completion_rate|float|
|is_completed|boolean|
|last_updated|timestamp|

- Persisted in DB (Not LocalStorage)
- Dùng cho Frequency Cap
