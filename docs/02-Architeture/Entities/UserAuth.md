>- Quản lý việc liên kết giữa người dùng và các phương pháp xác thực khác nhau (Local hoặc OAuth)
>- Liên kết User ↔ AuthProvider (OAuth / Local)
# Module 1

| Field            | Type      | PK  | Constrant | Note                                                     |                  |
| ---------------- | --------- | --- | --------- | -------------------------------------------------------- | ---------------- |
| user_auth_id     | UUID      | PK  |           | Định danh duy nhất kiểu UUID                             |                  |
| user_id          | UUID      | FK  |           | Liên kết đến bảng Users                                  | [[Users]]        |
| provider_id      | UUID      | FK  |           | Nhà cung cấp xác thực                                    | [[AuthProvider]] |
| provider_user_id | varchar   |     |           | ID định danh người dùng cho phía GG hoặc Github cung cấp |                  |
| created_at       | timestamp |     |           | Thời gian liên kết được tạo                              |                  |
