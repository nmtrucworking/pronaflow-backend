> Đơn vị thực thi trung tâm

# Phân hệ 4
|Field|Type|Note|
|---|---|---|
|task_id (PK)|UUID||
|project_id (FK)|UUID||
|task_list_id (FK)|UUID|Required|
|title|varchar||
|description|text||
|status|enum|NOT_STARTED / IN_PROGRESS / DONE|
|priority|enum|LOW / MEDIUM / HIGH / URGENT|
|is_milestone|boolean||
|planned_start|timestamp|From Module 5|
|planned_end|timestamp||
|actual_start|timestamp|Auto|
|actual_end|timestamp|Auto|
|estimated_hours|float||
|created_by (FK → User)|UUID||
|created_at|timestamp||