# PronaFlow Backend Documentation Index

## Quick Navigation

### 🚀 Getting Started
- [Quick Start Guide](../README_DEVELOPMENT.md) - Setup and run server
- [API Documentation](API_DOCUMENTATION.md) - Full API reference
- [Architecture Overview](architecture/README.md) - System design

### 📚 Documentation by Module

#### Core Modules
1. [Module 1: Identity & Access Management (IAM)](modules/module_01_iam/README.md)
   - User authentication, authorization, MFA
   
2. [Module 2: Workspace Management](modules/module_02_workspace/README.md)
   - Multi-tenant workspaces, member management
   
3. [Module 3: Project Lifecycle](modules/module_03_project/README.md)
   - Project creation, templates, governance modes

#### Execution & Planning
4. [Module 4 & 5: Task Management](modules/module_04_task/README.md)
   - Tasks, subtasks, dependencies, time tracking
   
5. [Module 6: Collaboration Hub](modules/module_06_collaboration/README.md)
   - Notifications, comments, activity streams

#### Advanced Features
6. [Module 8: Archive & Data Management](modules/module_08_archive/README.md)
   - Data archiving, retention policies
   
7. [Module 9: Reports & Analytics](modules/module_09_reports/README.md)
   - Dashboards, KPIs, business intelligence

#### Integration & Extension
8. [Module 10: API Integration](modules/module_10_api_integration/README.md)
   - External APIs, OAuth, tokens
   
9. [Module 11: Webhooks](modules/module_11_webhooks/README.md)
   - Event delivery, subscriptions
   
10. [Module 12: Plugins](modules/module_12_plugins/README.md)
    - Plugin system, extensibility

#### Business & Operations
11. [Module 13: Billing & Subscriptions](modules/module_13_billing/README.md)
    - Plans, invoicing, payments
    
12. [Module 14: System Administration](modules/module_14_admin/README.md)
    - Admin features, monitoring, feature flags
    
13. [Module 15: Help Center](modules/module_15_help_center/README.md)
    - Knowledge base, articles, search

#### User Experience
14. [Module 16: Onboarding](modules/module_16_onboarding/README.md)
    - Product tours, guided flows, gamification

### 🔧 Technical Documentation

#### Architecture & Design
- [System Architecture](architecture/README.md) - Overall design
- [Database Schema](database/README.md) - Entity relationships
- [API Design](api/README.md) - REST conventions
- [Design Patterns](architecture/README.md) - Used patterns

#### Development
- [Developer Guides](guides/README.md) - Development setup and standards
- [Testing Guide](guides/README.md) - Testing strategies
- [Database Migrations](guides/README.md) - Schema changes
- [Debugging Tips](guides/README.md) - Troubleshooting

#### Deployment & Operations
- [Docker Setup](deployment/README.md) - Containerization
- [Kubernetes](deployment/README.md) - K8s deployment
- [Database Setup](deployment/README.md) - Database initialization
- [Monitoring](deployment/README.md) - Logging and alerting

### ✨ Cross-Cutting Concerns
- [Authentication](features/README.md) - Auth implementation
- [Authorization](features/README.md) - RBAC and permissions
- [Notifications](features/README.md) - Real-time and email
- [File Management](features/README.md) - Upload and versioning
- [Time Tracking](features/README.md) - Time entries and timesheets
- [Tagging System](features/README.md) - Flexible categorization
- [Webhooks](features/README.md) - Event-driven integrations
- [Caching](features/README.md) - Performance optimization

### 📖 API Reference
- [API v1 Overview](api/v1/README.md)
- [Authentication Endpoints](api/v1/README.md#authentication)
- [Workspace Endpoints](api/v1/README.md#workspaces)
- [Project Endpoints](api/v1/README.md#projects)
- [Task Endpoints](api/v1/README.md#tasks)

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API endpoints by module
│   ├── services/        # Business logic by module
│   ├── models/          # Database models by module
│   ├── schemas/         # Request/response schemas
│   ├── repositories/    # Data access layer
│   ├── core/            # Shared utilities
│   └── middleware/      # Custom middleware
├── tests/               # Test suites
├── docs/                # This documentation
├── scripts/             # Utility scripts
└── config/              # Configuration
```

## Key Statistics

- **Modules**: 14 core modules
- **Database Tables**: 55+ tables
- **API Endpoints**: 100+ endpoints
- **Models**: 40+ ORM models
- **Services**: 30+ service classes

## Important Links

- **API Docs**: http://localhost:8000/docs (Swagger)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI**: http://localhost:8000/openapi.json
- **GitHub**: [PronaFlow Repository]
- **Issues**: Report bugs and feature requests

## Contributing

Please read [Developer Guides](guides/README.md) before contributing.

## License

[Your License Here]

---

**Last Updated**: February 3, 2026
**Status**: Active Development
