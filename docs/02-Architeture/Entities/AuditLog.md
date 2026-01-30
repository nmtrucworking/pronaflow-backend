> Phục vụ mục đích kiểm toán (Auditing) và truy vết hành động trong hệ thống. Accouting / Auditing ( #AAA)
# Module 1

| Field       | Type      | Key | Constrant | Note                                         |           |
| ----------- | --------- | --- | --------- | -------------------------------------------- | --------- |
| audit_id    | UUID      | PK  |           | Định danh duy nhất kiểu UUID                 |           |
| user_id     | UUID      | FK  |           | Người thực hiện                              | [[Users]] |
| action      | varchar   |     |           | Loại tác động (CRUD, Anonymize)              |           |
| entity_type | string    |     |           | Task, Comment, Project, Note, ...            |           |
| entity_id   | UUID      |     |           | ID của bản ghi bị tác động                   |           |
| ip_address  | varchar   |     |           | Địa chỉ IP tại thời điểm thực hiện hành động |           |
| created_at  | timestamp |     |           | Thời điểm ghi nhận nhật ký                   |           |

```mermaid
erDiagram
    Audit_Log {
        uuid audit_id PK
        uuid user_id FK "Người thực hiện"
        string action "CREATE, UPDATE, DELETE, ANONYMIZE"
        string entity_type "TASK, COMMENT, PROJECT, NOTE"
        uuid entity_id "ID của bản ghi bị tác động"
        string ip_address
        timestamp created_at
    }

    Audit_Log ||--o| DATA_DIFF : has_details
```