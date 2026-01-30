> Rate limit + audit

# Module 12

| Field         | Type      |
| ------------- | --------- |
| log_id (PK)   | UUID      |
| token_id (FK) | UUID      |
| endpoint      | varchar   |
| http_method   | varchar   |
| status_code   | int       |
| request_at    | timestamp |