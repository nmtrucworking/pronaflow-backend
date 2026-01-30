> Bảng trung tâm của Multi-tenancy (User ↔ Workspace)

# Phân hệ 2
|Field|Type|Note|
|---|---|---|
|workspace_member_id (PK)|UUID||
|workspace_id (FK)|UUID||
|user_id (FK)|UUID||
|role|enum|OWNER / ADMIN / MEMBER / VIEWER|
|joined_at|timestamp||
|left_at|timestamp|nullable|
|is_active|boolean||
## Constraint:
- `(workspace_id, user_id)` **UNIQUE**
- Workspace **luôn ≥ 1 OWNER**
