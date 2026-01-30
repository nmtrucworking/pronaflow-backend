# Module 14
| Field          | Type                 |     |               |
| -------------- | -------------------- | --- | ------------- |
| review_id (PK) | UUID                 |     |               |
| admin_id       | UUID                 |     | [[AdminUser]] |
| reviewer_id    | UUID                 |     |               |
| review_result  | enum (KEEP / REVOKE) |     |               |
| reviewed_at    | timestamp            |     |               |
