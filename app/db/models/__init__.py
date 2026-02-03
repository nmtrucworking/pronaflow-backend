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

# Module 5: Temporal Planning and Scheduling
from app.db.models.scheduling import (
    PlanState,
    TaskBaseline,
    TaskDependencySchedule,
    SchedulingMode,
    SLAPolicy,
    SLATracker,
    WorkingHoursPolicy,
    HolidayCalendar,
    PersonalException,
    PlanningScope,
    ResourceHistogram,
    SimulationSession,
    CrossProjectDependency,
    PlanningAuditLog,
)
# Module 6: Unified Collaboration Hub
from app.db.models.collaboration import (
    Note,
    NoteVersion,
    SmartBacklink,
    PublicLink,
    Mention,
    UserPresence,
    ApprovalRecord,
    SearchIndex,
    CollaborationNotification,
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
    ApiTokenScope,
    ApiUsageLog,
    WebhookEndpoint,
    WebhookEvent,
    WebhookDelivery,
    OAuthApp,
    OAuthConnection,
    IntegrationBinding,
    Plugin,
    PluginInstallation,
    ConsentGrant,
)

# Module 13: Subscription & Billing Management
from app.db.models.subscriptions import (
    Plan,
    WorkspaceSubscription,
    SubscriptionUsage,
    BillingTransaction,
    Invoice,
    InvoiceLineItem,
    Client,
    FreelancerInvoice,
)

# Module 14: System Administration
from app.db.models.admin import (
    AdminUser,
    AdminRole,
    AdminPermission,
    AdminRolePermission,
    AdminUserRole,
    SystemConfig,
    FeatureFlag,
    AdminAuditLog,
    SecurityIncident,
    ChangeRequest,
    AccessReview,
)

# Module 15: Help Center & Knowledge Base
from app.db.models.help_center import (
    Article,
    ArticleVersion,
    ArticleTranslation,
    Category,
    RouteMapping,
    ArticleFeedback,
    FailedSearch,
    ArticleVisibility,
    ArticleSearchIndex,
)

# Module 16: User Onboarding & Adoption
from app.db.models.onboarding import (
    OnboardingSurvey,
    SurveyQuestion,
    SurveyResponse,
    PersonaProfile,
    OnboardingFlow,
    FlowStep,
    UserOnboardingStatus,
    ProductTour,
    TourStep,
    UserTourSession,
    OnboardingChecklist,
    OnboardingChecklistItem,
    UserChecklistProgress,
    FeatureBeacon,
    UserBeaconState,
    OnboardingReward,
    OnboardingRewardGrant,
)

# Module 13: Subscription & Billing Management
from app.db.models.subscriptions import (
    Plan,
    WorkspaceSubscription,
    SubscriptionUsage,
    BillingTransaction,
    Invoice,
    InvoiceLineItem,
    Client,
    FreelancerInvoice,
)

# Module 14: System Administration
from app.db.models.admin import (
    AdminUser,
    AdminRole,
    AdminPermission,
    AdminRolePermission,
    AdminUserRole,
    SystemConfig,
    FeatureFlag,
    AdminAuditLog,
    SecurityIncident,
    ChangeRequest,
    AccessReview,
)

# Module 15: Help Center & Knowledge Base
from app.db.models.help_center import (
    Article,
    ArticleVersion,
    ArticleTranslation,
    Category,
    RouteMapping,
    ArticleFeedback,
    FailedSearch,
    ArticleVisibility,
    ArticleSearchIndex,
)

# Module 13: Subscription & Billing Management
from app.db.models.subscriptions import (
    Plan,
    WorkspaceSubscription,
    SubscriptionUsage,
    BillingTransaction,
    Invoice,
    InvoiceLineItem,
    Client,
    FreelancerInvoice,
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
    # Module 5: Scheduling
    "PlanState",
    "TaskBaseline",
    "TaskDependencySchedule",
    "SchedulingMode",
    "SLAPolicy",
    "SLATracker",
    "WorkingHoursPolicy",
    "HolidayCalendar",
    "PersonalException",
    "PlanningScope",
    "ResourceHistogram",
    "SimulationSession",
    "CrossProjectDependency",
    "PlanningAuditLog",
    # Module 4 & 15
    "Tag",
    # Module 6: Collaboration
    "Note",
    "NoteVersion",
    "SmartBacklink",
    "PublicLink",
    "Mention",
    "UserPresence",
    "ApprovalRecord",
    "SearchIndex",
    "CollaborationNotification",
    # Module 6 (Events)
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
    "ApiTokenScope",
    "ApiUsageLog",
    "WebhookEndpoint",
    "WebhookEvent",
    "WebhookDelivery",
    "OAuthApp",
    "OAuthConnection",
    "IntegrationBinding",
    "Plugin",
    "PluginInstallation",
    "ConsentGrant",
    # Module 13
    "Plan",
    "WorkspaceSubscription",
    "SubscriptionUsage",
    "BillingTransaction",
    "Invoice",
    "InvoiceLineItem",
    "Client",
    "FreelancerInvoice",
    # Module 14
    "AdminUser",
    "AdminRole",
    "AdminPermission",
    "AdminRolePermission",
    "AdminUserRole",
    "SystemConfig",
    "FeatureFlag",
    "AdminAuditLog",
    "SecurityIncident",
    "ChangeRequest",
    "AccessReview",
    # Module 15
    "Article",
    "ArticleVersion",
    "ArticleTranslation",
    "Category",
    "RouteMapping",
    "ArticleFeedback",
    "FailedSearch",
    "ArticleVisibility",
    "ArticleSearchIndex",
    # Module 16
    "OnboardingSurvey",
    "SurveyQuestion",
    "SurveyResponse",
    "PersonaProfile",
    "OnboardingFlow",
    "FlowStep",
    "UserOnboardingStatus",
    "ProductTour",
    "TourStep",
    "UserTourSession",
    "OnboardingChecklist",
    "OnboardingChecklistItem",
    "UserChecklistProgress",
    "FeatureBeacon",
    "UserBeaconState",
    "OnboardingReward",
    "OnboardingRewardGrant",
]
