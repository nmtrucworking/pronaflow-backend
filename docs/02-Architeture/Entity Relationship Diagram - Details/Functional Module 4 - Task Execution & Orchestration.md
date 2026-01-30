**Project**: PronaFlow 
**Version**: 1.0
**State**: Draft 
_**Last updated:** Jan 9, 2026_

---
## Quan hệ tổng thể
- **Project 1–N TaskList**
- **TaskList 1–N Task**
- **Task 1–N Subtask**
- **Task N–N User** (Assignee)
- **Task N–N Task** (Dependency)
- **Workspace 1–N TaskTag**
- **Task N–N TaskTag**
- **Project 1–N TaskCustomField**
- **Task 1–N TaskCustomFieldValue**

# ERD
```mermaid
erDiagram
    PROJECT ||--o{ TASK_LIST : contains
    TASK_LIST ||--o{ TASK : includes
    TASK ||--o{ SUBTASK : breaks_into

    TASK ||--o{ TASK_ASSIGNEE : assigned
    USER ||--o{ TASK_ASSIGNEE : works_on

    TASK ||--o{ TASK_DEPENDENCY : precedes
    TASK ||--o{ TASK_WATCHER : watched_by

    TASK ||--o{ TASK_CUSTOM_FIELD_VALUE : has
    TASK_CUSTOM_FIELD ||--o{ TASK_CUSTOM_FIELD_VALUE : defines

    WORKSPACE ||--o{ TASK_TAG : owns
    TASK ||--o{ TASK_TAG_MAP : tagged

```