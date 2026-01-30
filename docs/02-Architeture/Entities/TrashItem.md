# Module 8
|Field|Type|
|---|---|
|trash_id (PK)|UUID|
|entity_type|enum|
|entity_id|UUID|
|deleted_by|UUID|
|deleted_at|timestamp|
|purge_after|timestamp|
- Auto-pure after 30 days
- 