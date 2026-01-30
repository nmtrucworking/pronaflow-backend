"""
Central imports for all database models.
Ensures all models are registered with SQLAlchemy metadata.
"""

# Module 1: Identity & Access Management (IAM)
from app.db.models.users import (
    User,
    Role,
    Permission,
    MFAConfig,
    MFABackupCode,
    AuthProvider,
    AuditLog,
    Session,
)

# Module 2: Multi-tenancy & Workspace Governance
from app.db.models.workspaces import (
    Workspace,
    WorkspaceMember,
    WorkspaceInvitation,
    WorkspaceAccessLog,
    WorkspaceSetting,
)

# Module 3: Project Lifecycle Management
from app.db.models.projects import (
    Project,
)
from app.db.models.projects_extended import (
    ProjectMember,
    ProjectTemplate,
    ProjectBaseline,
    ProjectChangeRequest,
    ProjectArchive,
)

# Module 4 & 5: Task Management & Execution
from app.db.models.tasks import (
    TaskList,
    Task,
    Subtask,
    TaskAssignee,
    TaskDependency,
    Comment,
    File,
    FileVersion,
    TimeEntry,
    Timesheet,
)

# Module 4 & 15: Tag & Categorization
from app.db.models.tags import (
    Tag,
)

# Module 6: Notifications & Events
from app.db.models.notifications import (
    Notification,
    NotificationTemplate,
    NotificationPreference,
    DomainEvent,
    EventConsumer,
)

# Module 9: Reports & Analytics
from app.db.models.reports import (
    ReportDefinition,
    ReportExecution,
    MetricSnapshot,
    KPI,
)

# Module 10-12: API Integration, Webhooks & External Services
from app.db.models.integrations import (
    ApiToken,
    ApiScope,
    WebhookEndpoint,
    WebhookEvent,
    WebhookDelivery,
    IntegrationBinding,
)

__all__ = [
    # Module 1
    "User",
    "Role",
    "Permission",
    "MFAConfig",
    "MFABackupCode",
    "AuthProvider",
    "AuditLog",
    "Session",
    # Module 2
    "Workspace",
    "WorkspaceMember",
    "WorkspaceInvitation",
    "WorkspaceAccessLog",
    "WorkspaceSetting",
    # Module 3
    "Project",
    "ProjectMember",
    "ProjectTemplate",
    "ProjectBaseline",
    "ProjectChangeRequest",
    "ProjectArchive",
    # Module 4 & 5
    "TaskList",
    "Task",
    "Subtask",
    "TaskAssignee",
    "TaskDependency",
    "Comment",
    "File",
    "FileVersion",
    "TimeEntry",
    "Timesheet",
    # Module 4 & 15
    "Tag",
    # Module 6
    "Notification",
    "NotificationTemplate",
    "NotificationPreference",
    "DomainEvent",
    "EventConsumer",
    # Module 9
    "ReportDefinition",
    "ReportExecution",
    "MetricSnapshot",
    "KPI",
    # Module 10-12
    "ApiToken",
    "ApiScope",
    "WebhookEndpoint",
    "WebhookEvent",
    "WebhookDelivery",
    "IntegrationBinding",
]
