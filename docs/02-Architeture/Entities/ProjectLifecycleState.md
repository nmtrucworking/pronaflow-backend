> Máy trạng thái dự án (State Machine)
> Dùng cho audit, timeline, rollback logic.

# Phân hệ 3
|Field|Type|
|---|---|
|state_id (PK)|UUID|
|project_id (FK)|UUID|
|state|enum|
|changed_by (FK → User)|UUID|
|changed_at|timestamp|
|note|text|