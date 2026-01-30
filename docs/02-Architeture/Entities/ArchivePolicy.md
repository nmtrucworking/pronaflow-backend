> Automation Archiving Policy

# Module 8
|Field|Type|Note|
|---|---|---|
|policy_id (PK)|UUID||
|entity_type|enum|PROJECT|
|trigger_status|enum|DONE / CANCELLED|
|inactive_days|int|default 180|
|target_tier|enum|COLD|
|is_active|boolean||