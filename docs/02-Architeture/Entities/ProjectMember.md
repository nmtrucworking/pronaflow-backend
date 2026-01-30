> Phân quyền cấp dự án (tách khỏi Workspace)

# Phân hệ 3
|Field|Type|
|---|---|
|project_member_id (PK)|UUID|
|project_id (FK)|UUID|
|user_id (FK)|UUID|
|role|enum|
|joined_at|timestamp|
**Constraint**
- `(project_id, user_id)` UNIQUE