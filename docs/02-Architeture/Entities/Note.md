# Module 6
| Field             | Type      | Key | Description                                           |             |
| ----------------- | --------- | --- | ----------------------------------------------------- | ----------- |
| note_id ()        | UUID      | PK  |                                                       |             |
| project_id ()     | UUID      | FK  | Liên kết với dự án sở hữu.                            | [[Project]] |
| parent_note_id () | UUID      | FK  | Cho phép cấu trúc phân cấp (NULL nếu là root).        |             |
| author_id ()      | UUID      | FK  |                                                       | [[Users]]   |
| title             | varchar   |     | Tiêu đề ghi chú                                       |             |
| content           | text      |     | Nội dung định dạng Rich-text/Markdown.                |             |
| status            | enum      |     | DRAFT, PUBLISHED, ARCHIVED.                           |             |
| created_at        | timestamp |     |                                                       |             |
| is_public         | boolean   |     | Cho phép xuất bản ra ngoài dự án (Public Publishing). |             |
```mermaid
erDiagram
    PROJECT ||--o{ NOTE : "contains"
    NOTE ||--o{ NOTE : "has_subnotes"
    NOTE ||--o{ NOTE_VERSION : "tracks_history"
    NOTE ||--o{ NOTE_TAG_MAP : "categorized_by"
    TAG ||--o{ NOTE_TAG_MAP : "labels"
    NOTE ||--o{ BACKLINK : "referenced_in"

    NOTE {
        uuid note_id PK
        uuid project_id FK
        uuid parent_note_id FK
        string title
        text content
        boolean is_public
    }

    NOTE_TAG_MAP {
        uuid note_id FK
        uuid tag_id FK
    }

    BACKLINK {
        uuid backlink_id PK
        uuid source_id "ID của Note chứa liên kết"
        uuid target_note_id FK "ID của Note được trỏ tới"
    }
```
