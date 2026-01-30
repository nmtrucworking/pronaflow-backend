# Module 6

|Field|Type|Note|
|---|---|---|
|comment_id (PK)|UUID||
|task_id (FK)|UUID|Neo ngữ cảnh|
|parent_comment_id (FK)|UUID|NULL = root|
|author_id (FK → User)|UUID||
|content|text|Rich-text (HTML/JSON)|
|is_edited|boolean||
|created_at|timestamp||
|edited_at|timestamp||
- Nested reply → self-referencing