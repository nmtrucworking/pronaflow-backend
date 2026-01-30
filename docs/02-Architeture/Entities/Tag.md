# Module 4 and 15

| Field             | Type      | Key | Description                                          |
| ----------------- | --------- | --- | ---------------------------------------------------- |
| tag_id            | UUID      | PK  |                                                      |
| workspace_id      | UUID      | FK  | [[Workspace]]                                        |
| name              | varchar   |     | Tên thẻ                                              |
| color_code        | varchar   |     | Mã màu HEX                                           |
| entity_type_limit | enum      |     | Giới hạn tag này chỉ dùng cho Task, Project hoặc All |
| created_at        | timestamp |     | Thời điểm tạo                                        |

```mermaid
erDiagram
	WORKSPACE ||--o{ TAG : "owns"
    TAG ||--o{ PROJECT_TAG_MAP : "categorizes"
    TAG ||--o{ NOTE_TAG_MAP : "organizes"
    TAG ||--o{ PLUGIN_TAG_MAP : "classifies"
    TAG ||--o{ ARTICLE_TAG : "applies_to"
    TAG ||--o{ TASK_TAG_MAP : "applies_to"

    PROJECT_TAG_MAP {
        uuid project_id FK
        uuid tag_id FK
    }
    NOTE_TAG_MAP {
        uuid note_id FK
        uuid tag_id FK
    }
    PLUGIN_TAG_MAP {
        uuid plugin_id FK
        uuid tag_id FK
    }
    TASK_TAG_MAP { 
	    uuid task_id FK 
	    uuid tag_id FK 
	}
```
