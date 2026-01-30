> Predecessor / Successor

# Phân hệ 4
|Field|Type|
|---|---|
|dependency_id (PK)|UUID|
|predecessor_task_id (FK → Task)|UUID|
|successor_task_id (FK → Task)|UUID|
|dependency_type|enum|
|created_at|timestamp|
**Constraint**
- Không được tạo vòng (Cycle Detection – App Layer)