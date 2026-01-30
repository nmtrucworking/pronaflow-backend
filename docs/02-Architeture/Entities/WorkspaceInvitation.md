> Invitation + Magic Link

# Phân hệ 2
|Field|Type|Note|
|---|---|---|
|invitation_id (PK)|UUID||
|workspace_id (FK)|UUID||
|email|varchar||
|invited_role|enum|ADMIN / MEMBER / VIEWER|
|token_hash|varchar||
|expires_at|timestamp|+48h|
|accepted_at|timestamp|nullable|
|invited_by (FK → User)|UUID||