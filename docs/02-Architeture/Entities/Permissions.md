> Đơn vị quyền nhỏ nhất (fine-grained)

# Module 1

| Field         | Type    | Key | Constrant        | Note                                  |
| ------------- | ------- | --- | ---------------- | ------------------------------------- |
| permission_id | UUID    | PK  |                  | Định danh duy nhất kiểu UUID          |
| code          | varchar |     | unique, not-null | Mã quyền định dạng chuỗi              |
| description   | text    |     | not-null         | Mô tả chi tiết chức năng của quyền đó |
