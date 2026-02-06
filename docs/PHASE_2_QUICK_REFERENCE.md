# Phase 2 - Quick Reference Guide

## What Was Built

### 35+ API Endpoints
- 10 Workspace endpoints (CRUD, members, stats)
- 10 Project endpoints (CRUD, search, status, stats)
- 15+ Task endpoints (CRUD, lists, assignments, stats)

### 42 Service Methods
- WorkspaceService: 11 methods
- ProjectService: 11 methods
- TaskService: 20+ methods

### 37+ Schema Classes
- Workspace: 12 schemas
- Project: 10 schemas
- Task: 15+ schemas

## API Endpoints Quick Reference

### Workspaces
```
POST   /api/v1/workspaces
GET    /api/v1/workspaces
GET    /api/v1/workspaces/{id}
PUT    /api/v1/workspaces/{id}
DELETE /api/v1/workspaces/{id}
GET    /api/v1/workspaces/{id}/members
POST   /api/v1/workspaces/{id}/members
DELETE /api/v1/workspaces/{id}/members/{mid}
PUT    /api/v1/workspaces/{id}/members/{mid}/role
GET    /api/v1/workspaces/{id}/stats
```

### Projects
```
POST   /api/v1/projects
GET    /api/v1/projects/{id}
PUT    /api/v1/projects/{id}
DELETE /api/v1/projects/{id}
GET    /api/v1/projects/workspace/{wid}
GET    /api/v1/projects/user/mine
GET    /api/v1/projects/search/{wid}
PUT    /api/v1/projects/{id}/status
GET    /api/v1/projects/{id}/stats
```

### Tasks
```
POST   /api/v1/tasks/lists
PUT    /api/v1/tasks/lists/{id}
DELETE /api/v1/tasks/lists/{id}
POST   /api/v1/tasks
GET    /api/v1/tasks/{id}
PUT    /api/v1/tasks/{id}
DELETE /api/v1/tasks/{id}
GET    /api/v1/tasks/list/{lid}
GET    /api/v1/tasks/project/{pid}
GET    /api/v1/tasks/user/assigned
GET    /api/v1/tasks/search/{pid}
PUT    /api/v1/tasks/{id}/status
GET    /api/v1/tasks/project/{pid}/overdue
POST   /api/v1/tasks/{id}/assignees
GET    /api/v1/tasks/{id}/assignees
DELETE /api/v1/tasks/{id}/assignees/{aid}
GET    /api/v1/tasks/project/{pid}/stats
```

## File Locations

### Service Layer
- `app/services/workspace_service.py` - Workspace business logic
- `app/services/project_service.py` - Project business logic
- `app/services/task_service.py` - Task business logic

### API Routes
- `app/api/workspace_routes.py` - Workspace endpoints
- `app/api/project_routes.py` - Project endpoints
- `app/api/task_routes.py` - Task endpoints

### Schemas
- `app/schemas/workspace_schemas.py` - Request/response models
- `app/schemas/project_schemas.py` - Request/response models
- `app/schemas/task_schemas.py` - Request/response models

## Common Patterns

### Creating a Resource
```python
service = WorkspaceService(db)
workspace = service.create_workspace(
    user_id=current_user.id,
    name="My Workspace",
    description="Optional description"
)
```

### Getting Resources with Pagination
```python
service = ProjectService(db)
projects, total = service.list_workspace_projects(
    workspace_id=workspace_id,
    user_id=current_user.id,
    skip=0,
    limit=20
)
```

### Updating Authorization-Protected Resource
```python
service = TaskService(db)
task = service.update_task(
    task_id=task_id,
    user_id=current_user.id,  # Current user must have access
    title="New Title"
)
```

### Error Handling
```python
try:
    service.get_workspace(workspace_id, user_id)
except NotFoundException as e:
    # Resource not found
    raise HTTPException(status_code=404, detail=e.detail)
except ForbiddenException as e:
    # User doesn't have access
    raise HTTPException(status_code=403, detail=e.detail)
```

## Pagination Pattern

All list endpoints follow this pattern:
```python
@router.get("/items", response_model=ItemListResponse)
def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ItemService(db)
    skip = (page - 1) * page_size
    items, total = service.list_items(skip=skip, limit=page_size)
    
    return ItemListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=skip + page_size < total,
        has_previous=page > 1,
    )
```

## Authorization Pattern

All services check authorization:
```python
def update_workspace(self, workspace_id: UUID, user_id: UUID, ...):
    workspace = self.workspace_repo.get_by_id(workspace_id)
    if not workspace:
        raise NotFoundException("Workspace not found")
    
    if workspace.owner_id != user_id:
        raise ForbiddenException("Only owner can update workspace")
    
    # Safe to proceed with update
    return self.workspace_repo.update(workspace_id, data)
```

## Status Codes

- **200** - Success (GET, PUT)
- **201** - Created (POST)
- **204** - No Content (DELETE)
- **400** - Bad Request (validation error)
- **403** - Forbidden (access denied)
- **404** - Not Found (resource missing)
- **409** - Conflict (duplicate resource)
- **500** - Server Error

## Dependencies

All routes use these injected dependencies:
```python
from app.core.dependencies import get_db, get_current_user

@router.get("")
def my_endpoint(
    db: Session = Depends(get_db),           # Database session
    current_user: User = Depends(get_current_user),  # Authenticated user
):
    pass
```

## Testing Endpoints

### Using curl
```bash
# Create workspace
curl -X POST http://localhost:8000/api/v1/workspaces \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name": "My Workspace"}'

# List workspaces
curl -X GET "http://localhost:8000/api/v1/workspaces?page=1&page_size=20" \
  -H "Authorization: Bearer TOKEN"

# Get workspace
curl -X GET http://localhost:8000/api/v1/workspaces/{id} \
  -H "Authorization: Bearer TOKEN"
```

### Using Python requests
```python
import requests

headers = {"Authorization": f"Bearer {token}"}

# Create
response = requests.post(
    "http://localhost:8000/api/v1/workspaces",
    json={"name": "My Workspace"},
    headers=headers
)

# List
response = requests.get(
    "http://localhost:8000/api/v1/workspaces",
    params={"page": 1, "page_size": 20},
    headers=headers
)

# Get
response = requests.get(
    f"http://localhost:8000/api/v1/workspaces/{workspace_id}",
    headers=headers
)
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 404 Not Found | Resource doesn't exist | Check ID is correct |
| 403 Forbidden | No access to resource | Check user is member |
| 409 Conflict | Duplicate resource | Check unique constraints |
| 400 Bad Request | Invalid input | Check schema validation |

## Next Steps

1. **Add Routes to App**
   - Import routers in `app/main.py`
   - Use `app.include_router()`

2. **Write Tests**
   - Unit tests for repositories
   - Unit tests for services
   - Integration tests for endpoints

3. **Implement Auth**
   - JWT token validation
   - User extraction from token

4. **Add More Modules**
   - Comments, notifications, activities
   - Reports, analytics
   - Webhooks, integrations

## Resources

- [Phase 2.3 API Endpoints Documentation](PHASE_2.3_API_ENDPOINTS_COMPLETE.md)
- [Phase 2.3 Integration Guide](PHASE_2.3_INTEGRATION_GUIDE.md)
- [Phase 2 Complete Summary](PHASE_2_IMPLEMENTATION_COMPLETE.md)
- [API Documentation V1.2](API_DOCUMENTATION_V1.2.md)

## Phase Statistics

- **Duration**: ~2 hours
- **Endpoints**: 35+
- **Services**: 42 methods
- **Schemas**: 37+ classes
- **Lines of Code**: 1200+
- **Test Coverage**: To be measured in Phase 3

## Status

✅ Phase 2.1 - API Schemas (Complete)
✅ Phase 2.2 - Service Layer (Complete)
✅ Phase 2.3 - API Routes (Complete)
⏳ Phase 3.1 - Unit Testing (Not Started)
⏳ Phase 3.2 - Integration Testing (Not Started)
⏳ Phase 3.3 - Code Coverage (Not Started)

---

Ready to move to Phase 3: Testing & Validation
