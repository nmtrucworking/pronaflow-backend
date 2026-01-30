**Project**: PronaFlow 
**Version**: 1.0
**State**: Draft 
_**Last updated:** Jan 9, 2026_

---
# Relationship
## Quan hệ & Cardinality
- **User 1–N WorkspaceMember**
- **Workspace 1–N WorkspaceMember**
- **Workspace 1–N WorkspaceInvitation**
- **Workspace 1–1 WorkspaceSetting**
- **User 1–N WorkspaceInvitation (invited_by)**
- **User 1–N WorkspaceAccessLog**
# ERD
```mermaid
erDiagram
    USER ||--o{ WORKSPACE_MEMBER : participates
    WORKSPACE ||--o{ WORKSPACE_MEMBER : contains

    WORKSPACE ||--o{ WORKSPACE_INVITATION : invites
    USER ||--o{ WORKSPACE_INVITATION : sends

    WORKSPACE ||--|| WORKSPACE_SETTING : configures

    USER ||--o{ WORKSPACE_ACCESS_LOG : switches
    WORKSPACE ||--o{ WORKSPACE_ACCESS_LOG : accessed

    WORKSPACE {
        uuid workspace_id PK
        string name
        string description
        enum status
        boolean is_deleted
        timestamp deleted_at
    }

    WORKSPACE_MEMBER {
        uuid workspace_member_id PK
        enum role
        boolean is_active
        timestamp joined_at
    }

    WORKSPACE_INVITATION {
        uuid invitation_id PK
        string email
        enum invited_role
        timestamp expires_at
    }

    WORKSPACE_SETTING {
        uuid workspace_id PK
        string timezone
        string work_days
        string work_hours
    }

```