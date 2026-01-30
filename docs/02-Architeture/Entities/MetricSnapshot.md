> Snapshot dữ liệu đã tổng hợp (CQRS - Read side)
# Module 11
| Field            | Type      | Note                     |
| ---------------- | --------- | ------------------------ |
| snapshot_id (PK) | UUID      |                          |
| entity_type      | enum      | PROJECT / SPRINT         |
| entity_id        | UUID      |                          |
| metric_type      | enum      | PV / EV / AC / SPI / CPI |
| metric_value     | numeric   |                          |
| stamp            | timestamp |                          |
- Không tích real-time tại UI
- Được cập nhật bởi worker / stream
