> Quản lý thay đổi trong chế độ Strict

# Module 3
| Field                    | Type      |
| ------------------------ | --------- |
| pcr_id (PK)              | UUID      |
| project_id (FK)          | UUID      |
| title                    | varchar   |
| description              | text      |
| impact_summary           | text      |
| requested_by (FK → User) | UUID      |
| approved_by (FK → User)  | UUID      |
| created_at               | timestamp |
| decided_at               | timestamp |