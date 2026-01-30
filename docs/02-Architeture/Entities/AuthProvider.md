> Định nghĩa các nhà cung cấp dịch vụ xác thực được hệ thống chấp nhật.
> Nhà cung cấp xác thực (Local / Google / Github / ...)

# Module 1

| Field       | Type      | Key | Constrant    | Note                                           |
| ----------- | --------- | --- | ------------ | ---------------------------------------------- |
| provider_id | UUID      | PK  |              | Định danh duy nhất kiểu UUID                   |
| name        | enum      |     | in {`Local`} | Tên nhà cung cấp                               |
| created_at  | timestamp |     | not-null     | Thời điểm khởi tạo nhà cung cấp trong hệ thống |
- Trường `name` tuân thủ theo file: [[auth-privider.json]]