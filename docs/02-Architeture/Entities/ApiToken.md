# Module 12
| Field         | Type      | Note                  |
| ------------- | --------- | --------------------- |
| token_id (PK) | UUID      |                       |
| user_id (FK)  | UUID      | Owner                 |
| name          | varchar   | “CI Bot”              |
| token_hash    | varchar   | Never store plaintext |
| expires_at    | timestamp | nullable              |
| revoked_at    | timestamp | nullable              |
| created_at    | timestamp |                       |