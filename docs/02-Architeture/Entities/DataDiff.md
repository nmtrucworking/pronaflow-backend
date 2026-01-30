
| Field      | Type  |     |                           |
| ---------- | ----- | --- | ------------------------- |
| diff_id    | UUID  | PK  |                           |
| audit_id   | UUID  | FK  | Liên kết với [[AuditLog]] |
| old_values | jsonb |     | Giá trị cũ (Key-Value)    |
| new_values | jsonb |     | Giá trị mới (Key-Value)   |
```mermaid
erDiagram
	DATA_DIFF {
		UUID diff_id PK
		UUID audit_id FK "Liên kết với Audit-log"
		jsonb old_values "Giá trị cũ"
		jsonb new_values "Giá trị mới"	
	}
	
	Audit_Log ||--o| DATA_DIFF : has_details
```
