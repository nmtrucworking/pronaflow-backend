> Định nghĩa lặp

# Phân hệ 4
|Field|Type|
|---|---|
|recurrence_id (PK)|UUID|
|task_id (FK)|UUID|
|pattern|enum|
|config|jsonb|
|next_run_at|timestamp|
|is_active|boolean|