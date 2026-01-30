> Gán vai trò cho User (theo Workspace - sẽ mở rộng ở Module 2)

# 1. Phân hệ 1
| Field             | Type      |     |           |
| ----------------- | --------- | --- | --------- |
| user_role_id (PK) | UUID      |     |           |
| user_id (FK)      | UUID      |     | [[Users]] |
| role_id (FK)      | UUID      |     | [[Roles]] |
| assigned_at       | timestamp |     |           |
