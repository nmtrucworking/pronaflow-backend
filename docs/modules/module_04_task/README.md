# Module 4 & 5: Task Management & Execution

## Overview
Core task execution and temporal planning:
- Task creation and management
- Subtasks and checklists
- Dependencies and scheduling
- Time tracking and estimation
- File attachments and comments

## Key Components

### Models
- **TaskList** - Container for work breakdown structure (WBS)
- **Task** - Core execution unit with multiple statuses
- **Subtask** - Checklist items within tasks
- **TaskAssignee** - N-N relationship with primary flag
- **TaskDependency** - Task-to-task relationships
- **Comment** - Threaded discussions
- **File** - Attachments with version history
- **TimeEntry** - Individual time logs
- **Timesheet** - Aggregated time with approval workflow

### Services
- `TaskService` - Task CRUD and lifecycle
- `ExecutionService` - Task execution and state management
- `TimeTrackingService` - Time entry and timesheet management
- `DependencyService` - Dependency resolution
- `CommentService` - Comment and discussion management

### API Endpoints
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks` - List tasks
- `PATCH /api/v1/tasks/{id}` - Update task
- `POST /api/v1/tasks/{id}/subtasks` - Add subtask
- `POST /api/v1/tasks/{id}/comments` - Add comment
- `POST /api/v1/time-entries` - Log time
- `GET /api/v1/timesheets` - Get timesheets

## Database Tables (10 + 1 association)
- task_lists
- tasks
- subtasks
- task_assignees
- task_dependencies
- comments
- files
- file_versions
- time_entries
- timesheets
- task_watchers (association)

## Features
- Drag & drop task ordering
- Multiple status states
- Task dependencies and blocking
- Time estimation and tracking
- File versioning
- Threaded comments

