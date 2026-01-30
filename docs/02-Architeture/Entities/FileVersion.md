# Module 6
using for:
	- Versioning
	- Approval checksum
	- Restore


|Field|Type|
|---|---|
|version_id (PK)|UUID|
|file_id (FK)|UUID|
|version_number|int|
|checksum|varchar|
|storage_path|text|
|created_by|UUID|
|created_at|timestamp|