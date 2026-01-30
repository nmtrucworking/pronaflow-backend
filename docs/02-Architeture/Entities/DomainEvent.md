> Sự kiện nghiệp vụ phát ra từ các Module khác

# Module 7
|Field|Type|Note|
|---|---|---|
|event_id (PK)|UUID|Idempotency key|
|source_module|enum|TASK, PROJECT, COMMENT…|
|event_type|varchar|TASK_UPDATED|
|payload|jsonb||
|priority|enum|HIGH / MEDIUM / LOW|
|occurred_at|timestamp||

- Chống duplicated event
- Không gắn user cụ thể