# PronaFlow Backend Documentation

Complete documentation for the PronaFlow backend system with 16 modules and 55+ database tables.

## 📋 Quick Links

- **[Documentation Index](INDEX.md)** - Start here for navigation
- **[System Architecture](architecture/README.md)** - System design and patterns
- **[API Reference](api/README.md)** - REST API documentation
- **[Database Schema](database/README.md)** - Entity relationships

## 📦 Module Documentation

The system is organized into 14 core modules:

### Identity & Workspace (Modules 1-3)
- [Module 1: IAM](modules/module_01_iam/README.md) - Authentication & Authorization
- [Module 2: Workspace](modules/module_02_workspace/README.md) - Multi-tenancy
- [Module 3: Project](modules/module_03_project/README.md) - Project Lifecycle

### Execution & Collaboration (Modules 4-6)
- [Module 4 & 5: Tasks](modules/module_04_task/README.md) - Task Management
- [Module 6: Collaboration](modules/module_06_collaboration/README.md) - Communication

### Data Management (Modules 8-9)
- [Module 8: Archive](modules/module_08_archive/README.md) - Data Archiving
- [Module 9: Reports](modules/module_09_reports/README.md) - Analytics & Reporting

### Integration & Extension (Modules 10-12)
- [Module 10: API Integration](modules/module_10_api_integration/README.md) - External APIs
- [Module 11: Webhooks](modules/module_11_webhooks/README.md) - Event Delivery
- [Module 12: Plugins](modules/module_12_plugins/README.md) - Extensibility

### Business & Operations (Modules 13-16)
- [Module 13: Billing](modules/module_13_billing/README.md) - Subscriptions
- [Module 14: Admin](modules/module_14_admin/README.md) - Administration
- [Module 15: Help Center](modules/module_15_help_center/README.md) - Knowledge Base
- [Module 16: Onboarding](modules/module_16_onboarding/README.md) - User Adoption

## 🔧 Technical Documentation

### Architecture & Design
- **[Architecture Overview](architecture/README.md)** - System architecture
- **[Database Design](database/README.md)** - Schema and models
- **[API Design](api/README.md)** - REST conventions

### Development
- **[Developer Guides](guides/README.md)** - Setup and standards
- **[Testing](guides/README.md)** - Testing strategies
- **[Debugging](guides/README.md)** - Troubleshooting

### Deployment & Operations
- **[Deployment](deployment/README.md)** - Docker, K8s, hosting
- **[Monitoring](deployment/README.md)** - Logging and alerting
- **[Database Operations](database/README.md)** - Migrations

### Cross-Cutting Features
- **[Features](features/README.md)** - Shared capabilities
  - Authentication & Authorization
  - Notifications
  - File Management
  - Time Tracking
  - Tags & Categories
  - Webhooks
  - Caching

## 📚 Documentation Structure

```
docs/
├── INDEX.md                       # Start here!
├── README.md                      # This file
├── modules/                       # 14 module docs
│   ├── module_01_iam/
│   ├── module_02_workspace/
│   ├── ... (12 more modules)
│   └── module_16_onboarding/
├── features/                      # Cross-cutting concerns
├── api/                           # API documentation
│   └── v1/                        # v1 endpoints
├── database/                      # Database docs
├── architecture/                  # System design
├── deployment/                    # Operations guides
├── guides/                        # Developer guides
└── draft/                         # Work-in-progress
```

## 🚀 Getting Started

1. **Quick Start**: See [README_DEVELOPMENT.md](../README_DEVELOPMENT.md)
2. **Architecture**: Read [architecture/README.md](architecture/README.md)
3. **Module Details**: Check relevant module in [modules/](modules/)
4. **API**: Review [api/](api/) for endpoint details
5. **Database**: Understand schema in [database/](database/)

## 📊 System Overview

- **16 Modules** - Organized by business domain
- **55+ Tables** - Comprehensive database schema
- **100+ APIs** - RESTful endpoints across modules
- **8 Repositories** - Data access layer
- **30+ Services** - Business logic implementation

## 🔐 Key Features

- **Multi-tenancy** - Complete workspace isolation
- **RBAC** - Role-based access control
- **MFA** - Multi-factor authentication
- **Audit Logging** - Compliance and tracking
- **Event-Driven** - Webhooks and event system
- **Extensible** - Plugin architecture
- **Scalable** - SaaS-ready architecture

## 📝 Documentation Standards

All documentation follows these standards:
- Markdown format (.md files)
- Clear section headers
- Code examples where applicable
- Links to related documentation
- Updated regularly with code changes

## 🤝 Contributing

When adding new documentation:
1. Update relevant module README
2. Add links to INDEX.md if creating new sections
3. Follow existing structure and formatting
4. Keep code examples current and tested

## 📞 Support

For questions or issues:
- Check [FAQs](guides/README.md)
- Review [Debugging Guide](guides/README.md)
- Check related module documentation
- Open an issue in repository

---

**Last Updated**: February 3, 2026
**Documentation Version**: 1.3
**System Status**: Active Development

