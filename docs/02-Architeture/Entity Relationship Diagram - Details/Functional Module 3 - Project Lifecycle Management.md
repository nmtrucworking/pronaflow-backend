**Project**: PronaFlow 
**Version**: 1.0
**State**: Draft 
_**Last updated:** Jan 9, 2026_

---
## Quan hệ tổng thể (Cardinality)
- **Workspace 1–N Project**
- **Project 1–N ProjectMember**
- **User 1–N ProjectMember**
- **Project 1–N ProjectLifecycleState**
- **Project 1–N ProjectBaseline**
- **Project 1–N ProjectChangeRequest**
- **Workspace 1–N ProjectTemplate**
- **Project 0–1 ProjectArchive**

```mermaid
erDiagram
    WORKSPACE ||--o{ PROJECT : owns
    PROJECT ||--o{ PROJECT_MEMBER : assigns
    USER ||--o{ PROJECT_MEMBER : participates

    PROJECT ||--o{ PROJECT_LIFECYCLE_STATE : transitions
    USER ||--o{ PROJECT_LIFECYCLE_STATE : changes

    PROJECT ||--o{ PROJECT_BASELINE : snapshots
    PROJECT ||--o{ PROJECT_CHANGE_REQUEST : controls

    WORKSPACE ||--o{ PROJECT_TEMPLATE : defines
    PROJECT ||--|| PROJECT_ARCHIVE : archived

    PROJECT {
        uuid project_id PK
        string name
        enum status
        enum governance_mode
        enum visibility
    }

    PROJECT_MEMBER {
        uuid project_member_id PK
        enum role
    }

    PROJECT_BASELINE {
        uuid baseline_id PK
        int version
        boolean is_active
    }

    PROJECT_CHANGE_REQUEST {
        uuid pcr_id PK
        enum status
    }

```