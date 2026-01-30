> Quản lý các phiên đăng nhập và duy trì trạng thái làm việc của người dùng.

# Module 1

| Field          | Type      | Key | Constrant | Note                                                            |           |
| -------------- | --------- | --- | --------- | --------------------------------------------------------------- | --------- |
| session_id     | UUID      | PK  |           | Định danh duy nhất kiểu UUID                                    |           |
| user_id        | UUID      | FK  | unique    | Người dùng sở hữu phiên làm việc                                | [[Users]] |
| device_info    | varchar   |     | not-null  | Thông tin về thiết bị và trình duyệt truy cập                   |           |
| ip_address     | varchar   |     |           | Địa chỉ IP khi đăng nhập                                        |           |
| geo_location   | varchar   |     |           | Vị trí địa lý ước tính khi đăng nhập                            |           |
| last_active_at | timestamp |     | not-null  | Thời điểm cuối cùng người dùng thực hiện thao tác trên hệ thống |           |
| is_current     | boolean   |     | not-null  | Đánh dấu phiên làm việc hiện tại đang sử dụng                   |           |
| revoked_at     | timestamp |     | not-null  | Thời điểm phiên làm việc bị thu hồi hoặc đăng xuất              |           |
