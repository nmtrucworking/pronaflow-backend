> Chỉ bật khi `governance_mode = STRICT`

# Phân hệ 3
|Field|Type|
|---|---|
|baseline_id (PK)|UUID|
|project_id (FK)|UUID|
|version|int|
|snapshot_ref|varchar|
|created_by (FK → User)|UUID|
|created_at|timestamp|
|is_active|boolean|