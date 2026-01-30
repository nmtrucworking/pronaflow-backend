> Checklist chi tiết

# Phân hệ 4
|Field|Type|
|---|---|
|subtask_id (PK)|UUID|
|task_id (FK)|UUID|
|title|varchar|
|is_done|boolean|
|assignee_id (FK → User)|UUID|
|position|int|