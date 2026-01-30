> Phục vụ **Aggregation / Batching**

# Module 7

| Field                | Type    |
| -------------------- | ------- |
| item_id (PK)         | UUID    |
| notification_id (FK) | UUID    |
| actor_id (FK → User) | UUID    |
| action               | varchar |
| target_type          | enum    |
| target_id            | UUID    |
