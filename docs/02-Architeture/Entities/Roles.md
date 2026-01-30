> Vai trò #RBAC toàn hệ thống

# Module 1

| Field           | Type | Key | Constrant | Note                                                                            |     |
| --------------- | ---- | --- | --------- | ------------------------------------------------------------------------------- | --- |
| role_id         | UUID | PK  |           | Định danh duy nhất kiểu UUID                                                    |     |
| role_name       | enum |     |           | Tên vai trò                                                                     |     |
| hierarchy_level | int  |     |           | Cấp độ phân cấp (int) để xác định thứ tự ưu tiên hoặc quản lý giữa các vai trò. |     |