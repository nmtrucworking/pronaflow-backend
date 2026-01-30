> Chuẩn hóa khởi tạo dự án

# Phân hệ 3
|Field|Type|
|---|---|
|template_id (PK)|UUID|
|workspace_id (FK)|UUID|
|name|varchar|
|description|text|
|is_global|boolean|
|created_by (FK → User)|UUID|
|created_at|timestamp|