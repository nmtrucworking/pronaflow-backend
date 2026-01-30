|Field|Type|
|---|---|
|version_id (PK)|UUID|
|model_id (FK)|UUID|
|version_no|varchar|
|artifact_path|text|
|trained_on|timestamp|
|confidence_threshold|float|
|metrics|jsonb|
|is_production|boolean|