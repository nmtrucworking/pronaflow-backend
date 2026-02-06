# Backend Application Structure

## Directory Overview

### Root Level
- **app/** - Main application code
- **tests/** - Test suites
- **docs/** - Documentation organized by module and feature
- **config/** - Configuration files
- **scripts/** - Utility scripts (setup, maintenance)
- **logs/** - Application logs
- **data/** - Local data files and exports
- **migrations/** - Database migration files

### app/ Structure
- **api/** - API endpoints and routers
  - v1/ - API v1 endpoints organized by module
  - v2/ - Future API versions
- **core/** - Core functionality (config, security, auth)
- **models/** - Database models organized by module
- **db/** - Database session and initialization
- **schemas/** - Pydantic schemas for validation
- **services/** - Business logic services by module
- **repositories/** - Data access layer
- **utils/** - Utility functions and helpers
- **middleware/** - Custom middleware

### docs/ Structure
Organized by module and cross-cutting concerns:

```
docs/
├── modules/
│   ├── module_01_iam/                    # Identity & Access Management
│   ├── module_02_workspace/              # Workspace Management
│   ├── module_03_project/                # Project Lifecycle
│   ├── module_04_task/                   # Task Management & Execution
│   ├── module_05_scheduling/             # Temporal Planning
│   ├── module_06_collaboration/          # Collaboration Hub
│   ├── module_08_archive/                # Archive & Data Management
│   ├── module_09_reports/                # Reports & Analytics
│   ├── module_10_api_integration/        # External API Integration
│   ├── module_11_webhooks/               # Webhooks & Event Delivery
│   ├── module_12_plugins/                # Plugins & Extensions
│   ├── module_13_billing/                # Subscription & Billing
│   ├── module_14_admin/                  # System Administration
│   ├── module_15_help_center/            # Help Center & Knowledge Base
│   └── module_16_onboarding/             # User Onboarding
├── features/                             # Cross-cutting concerns
│   ├── authentication.md                 # Auth implementation
│   ├── notifications.md                  # Notification system
│   ├── file_management.md                # File handling
│   ├── time_tracking.md                  # Time tracking
│   ├── tags.md                           # Tagging system
│   ├── webhooks.md                       # Event webhooks
│   └── caching.md                        # Caching strategies
├── api/                                  # API documentation
│   ├── README.md                         # API overview
│   └── v1/                               # v1 endpoint docs
├── database/                             # Database documentation
│   ├── models.md                         # Model reference
│   ├── migrations.md                     # Migration guides
│   └── relationships.md                  # Entity relationships
├── architecture/                         # System design
│   ├── overview.md                       # Architecture overview
│   ├── design_patterns.md                # Used patterns
│   └── performance.md                    # Performance considerations
├── deployment/                           # Operations guides
│   ├── docker.md                         # Docker setup
│   ├── kubernetes.md                     # K8s deployment
│   ├── database.md                       # DB setup
│   └── monitoring.md                     # Monitoring setup
├── guides/                               # Developer guides
│   ├── getting_started.md                # Setup instructions
│   ├── developing.md                     # Development guidelines
│   ├── testing.md                        # Testing strategies
│   └── debugging.md                      # Debugging tips
└── draft/                                # Work-in-progress docs
```

## Key Files
- `main.py` - FastAPI application entry point
- `requirements.txt` - Python dependencies
- `pytest.ini` - Pytest configuration
- `alembic.ini` - Alembic migration configuration
- `Dockerfile` - Docker container configuration
- `.env` - Environment variables
- `STRUCTURE.md` - This file

## 16 Modules

1. **Module 1: IAM** - Authentication, authorization, MFA, sessions
2. **Module 2: Workspace** - Multi-tenancy, workspace management
3. **Module 3: Project** - Project lifecycle, governance, templates
4. **Module 4 & 5: Task** - Task execution, scheduling, time tracking
5. **Module 6: Collaboration** - Notifications, comments, activity streams
6. **Module 8: Archive** - Data archiving, retention, restoration
7. **Module 9: Reports** - Analytics, dashboards, KPI tracking
8. **Module 10: API Integration** - Third-party APIs, OAuth, tokens
9. **Module 11: Webhooks** - Event delivery, subscriptions
10. **Module 12: Plugins** - Plugin system, extensions
11. **Module 13: Billing** - Subscriptions, invoicing, payments
12. **Module 14: Admin** - System administration, monitoring
13. **Module 15: Help Center** - Knowledge base, articles, search
14. **Module 16: Onboarding** - User onboarding, tours, adoption

## Database Tables (55+)
- **Module 1**: 8 tables + 2 associations (users, roles, permissions, etc.)
- **Module 2**: 5 tables (workspaces, members, invitations, settings)
- **Module 3**: 6 tables + 1 association (projects, templates, baselines)
- **Module 4 & 5**: 10 tables + 1 association (tasks, comments, files, time tracking)
- **Module 6**: 5 tables (notifications, templates, preferences, events)
- **Module 9**: 4 tables (reports, executions, metrics, KPIs)
- **Module 10-12**: 12 tables (API tokens, webhooks, plugins)
- **Module 13**: 6 tables (plans, subscriptions, billing, invoices)
- **Module 14**: 8 tables (admin users, roles, configs, feature flags)
- **Module 15**: 6 tables (articles, translations, categories, feedback)
- **Module 16**: 8 tables (onboarding, tours, checklists, rewards)

## Standards
- **Code Style**: PEP 8
- **Type Hints**: All functions must have type hints
- **Documentation**: Docstrings for modules, classes, and functions
- **Architecture**: Services handle business logic, repositories handle data access
- **Testing**: Unit tests for services, integration tests for APIs
- **Naming**: snake_case for tables/columns, PascalCase for classes

