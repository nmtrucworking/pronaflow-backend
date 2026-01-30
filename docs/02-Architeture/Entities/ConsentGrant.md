> Explicit user consent (GDPR-safe)

# Module 12

| Field      | Type      |     |                                                                                                                        |
| ---------- | --------- | --- | ---------------------------------------------------------------------------------------------------------------------- |
| consent_id | UUID      | PK  | Khóa chính duy nhất cho mỗi bản ghi đồng ý.                                                                            |
| user_id    | UUID      | FK  | ID của người dùng thực hiện cấp quyền.                                                                                 |
| app_type   | enum      |     | Loại ứng dụng (Ví dụ: `INTERNAL_PLUGIN`, `EXTERNAL_OAUTH_APP`).                                                        |
| app_id     | UUID      |     | ID định danh của ứng dụng/plugin cụ thể.                                                                               |
| scopes     | text      |     | Danh sách các quyền cụ thể được cấp (Ví dụ: `read:tasks`, `write:comments`).                                           |
| granted_at | timestamp |     | Thời điểm người dùng nhấn "Chấp nhận".                                                                                 |
| revoked_at | timestamp |     | Thời điểm người dùng thu hồi quyền (nếu có). Nếu trường này có giá trị, quyền truy cập sẽ bị vô hiệu hóa ngay lập tức. |
