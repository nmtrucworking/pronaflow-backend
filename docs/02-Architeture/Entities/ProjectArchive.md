> Lưu trữ dự án đã đóng

# Phân hệ 3
|Field|Type|
|---|---|
|archive_id (PK)|UUID|
|project_id (FK)|UUID|
|archived_by (FK → User)|UUID|
|archived_at|timestamp|
|reason|text|