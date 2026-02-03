# Module 3: Project Lifecycle Management

## Overview
Project creation, configuration, and governance:
- Project templates and standardization
- Project member roles and permissions
- Change control and approval workflows
- Project baselines and snapshots
- Project archiving

## Key Components

### Models
- **Project** - Main project container with multiple status states
- **ProjectMember** - Project-level role assignment
- **ProjectTemplate** - Standardized project creation templates
- **ProjectBaseline** - Change control snapshots (STRICT mode)
- **ProjectChangeRequest** - Formal change management with approval
- **ProjectArchive** - Archived project metadata

### Services
- `ProjectService` - Project lifecycle management
- `TemplateService` - Template management
- `ChangeManagementService` - Change control workflow
- `ArchiveService` - Project archiving

### API Endpoints
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List projects
- `PATCH /api/v1/projects/{id}` - Update project
- `POST /api/v1/projects/{id}/members` - Add member
- `POST /api/v1/projects/{id}/archive` - Archive project

## Database Tables (6 + 1 association)
- projects
- project_members
- project_templates
- project_baselines
- project_change_requests
- project_archives
- project_members_association

## Governance Modes
- **FREE** - Minimal governance
- **STANDARD** - Basic change control
- **STRICT** - Full change management with baselines

