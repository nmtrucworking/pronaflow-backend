# Module 3 Quick Reference Guide

## Project Lifecycle States

```
NOT_STARTED → IN_PROGRESS → IN_REVIEW → DONE
     ↓             ↓             ↓
  CANCELLED ← CANCELLED ← CANCELLED
```

## Project Roles & Permissions

| Role | Description | Key Permissions |
|------|-------------|----------------|
| **MANAGER** | Project Manager | Full control, add/remove members, change status |
| **PLANNER** | Scheduler | Edit Gantt, manage dependencies (Module 5) |
| **MEMBER** | Executor | Create/update tasks, log time |
| **VIEWER** | Observer | Read-only access |

## Governance Modes

### SIMPLE Mode (Default)
- ✅ Quick setup, minimal constraints
- ✅ Direct status changes
- ✅ No formal change requests
- 🎯 Use for: Small teams, Agile projects, R&D

### STRICT Mode
- 🔒 Formal change control
- 🔒 Baseline versioning
- 🔒 Approval gates
- 🎯 Use for: Enterprise, Fixed-price contracts, Compliance

## Priority Levels

- **CRITICAL**: Absolute priority, blocks other work
- **HIGH**: Important, top of queue
- **MEDIUM**: Standard (default)
- **LOW**: Filler work, when resources available

## Common Workflows

### Create a Project
```python
POST /api/v1/projects
{
  "workspace_id": "uuid",
  "name": "My Project",
  "governance_mode": "simple",  # or "strict"
  "visibility": "private",      # or "public"
  "priority": "medium"
}
```

### Add Team Members
```python
POST /api/v1/projects/{id}/members
{
  "user_id": "uuid",
  "role": "member"  # manager, planner, member, viewer
}
```

### Transition Status
```python
PATCH /api/v1/projects/{id}/status
{
  "status": "in_progress"
}

# For cancellation:
{
  "status": "cancelled",
  "cancellation_reason": "Budget constraints"
}
```

### Create Change Request (STRICT mode only)
```python
POST /api/v1/projects/{id}/change-requests
{
  "title": "Extend deadline by 1 week",
  "type": "schedule",  # scope, schedule, cost, resource
  "description": "Client requested additional features",
  "impact_assessment": "Adds 5 working days to timeline"
}
```

## Permission Checks

### Service Layer
```python
# Check if user can manage project
can_manage = ProjectService._can_manage_project(db, project, user_id)

# Check if user is workspace admin
is_admin = ProjectService._is_workspace_admin(db, workspace_id, user_id)

# Check if user is project member
is_member = ProjectService._is_project_member(db, project_id, user_id)
```

### Visibility Rules
```python
# PRIVATE: Only members + workspace admins can view
# PUBLIC: All workspace members can view
```

## Database Schema

### Projects Table
```sql
projects (
  id UUID PRIMARY KEY,
  workspace_id UUID REFERENCES workspaces,
  owner_id UUID REFERENCES users,
  name VARCHAR(100),
  status ProjectStatus,
  governance_mode ProjectGovernanceMode,
  visibility ProjectVisibility,
  priority ProjectPriority,
  start_date DATE,
  end_date DATE,
  archived_at TIMESTAMP,
  is_deleted BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Project Members Table
```sql
project_members (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects,
  user_id UUID REFERENCES users,
  role ProjectRole,
  joined_at TIMESTAMP,
  UNIQUE(project_id, user_id)
)
```

## Error Handling

### Common Error Codes

```python
400 BAD REQUEST
- Invalid date range (end_date < start_date)
- Cancellation without reason
- Invalid status transition
- Adding non-workspace member

403 FORBIDDEN
- Non-PM trying to update project
- Non-admin trying to approve CR
- Viewing private project as non-member

404 NOT FOUND
- Project doesn't exist
- User doesn't have access to private project
```

## Import Statements

### For Endpoints
```python
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectStatusUpdate,
    ProjectMemberCreate,
    ChangeRequestCreate,
)
from app.services.project import (
    ProjectService,
    ProjectMemberService,
    ProjectChangeRequestService,
)
```

### For Models
```python
from app.db.models.projects import Project
from app.db.models.projects_extended import (
    ProjectMember,
    ProjectTemplate,
    ProjectChangeRequest,
)
from app.db.enums import (
    ProjectStatus,
    ProjectRole,
    ProjectPriority,
    ProjectGovernanceMode,
)
```

## Useful Queries

### Get user's projects
```python
projects, total = ProjectService.list_projects(
    db=db,
    workspace_id=workspace_id,
    user_id=user_id,
    skip=0,
    limit=10,
    status_filter=ProjectStatus.IN_PROGRESS,  # optional
    archived=False
)
```

### Check project ownership
```python
project = ProjectService.get_project(db, project_id, user_id)
is_owner = project.owner_id == user_id
```

### List project members
```python
members = ProjectMemberService.list_members(db, project_id, user_id)
```

## Best Practices

1. **Always check permissions** before any write operation
2. **Validate status transitions** using `_validate_status_transition()`
3. **Use soft delete** instead of hard delete for audit trail
4. **Require cancellation reason** when cancelling projects
5. **Check workspace membership** before adding to project
6. **Cannot remove project owner** - transfer ownership first
7. **Log important actions** for audit trail

## Troubleshooting

### "Project not found" but it exists
- Check if user has access (visibility + membership)
- Check if project is soft-deleted (is_deleted=True)

### Cannot add member to project
- Verify user is workspace member first
- Check if user is already a project member

### Cannot change status
- Verify valid transition (see state machine)
- Check if cancellation_reason provided for CANCELLED status

### Change request not working
- Verify project is in STRICT governance mode
- Check if user has approval rights (workspace admin)

## Testing Checklist

- [ ] Create project in SIMPLE mode
- [ ] Create project in STRICT mode
- [ ] Add/update/remove members
- [ ] Transition through all valid states
- [ ] Test invalid transitions (should fail)
- [ ] Clone project
- [ ] Test PRIVATE vs PUBLIC visibility
- [ ] Create and approve change request
- [ ] Soft delete and verify filtering

---

**Last Updated:** February 2, 2026
