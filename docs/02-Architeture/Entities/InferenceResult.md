# Module 10
|Field|Type|Note|
|---|---|---|
|result_id (PK)|UUID||
|request_id (FK)|UUID||
|output_type|enum|ESTIMATION / RANKING / ANOMALY|
|result_payload|jsonb||
|confidence_score|float||
|is_displayed|boolean|threshold ≥ 70%|
|created_at|timestamp||
- UI chỉ render khi `is_displayed = true`
