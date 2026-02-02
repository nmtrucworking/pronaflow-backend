"""
Database enums for field value constraints.
Provides standardized enumeration types for database columns across all modules.
"""
from enum import Enum


# ============ Module 1: Identity & Access Management (IAM) ============

class UserStatus(str, Enum):
    """User lifecycle status"""
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class AuthProvider(str, Enum):
    """Authentication providers"""
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"


# ============ Module 2: Multi-tenancy Workspace Governance ============

class WorkspaceRole(str, Enum):
    """
    Roles within a workspace.
    Defines permission levels for workspace members.
    """
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"
    GUEST = "guest"


# ============ Module 3: Project Lifecycle Management ============

class ProjectStatus(str, Enum):
    """
    Project lifecycle status.
    Represents different stages a project can be in.
    """
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"


class ProjectGovernanceMode(str, Enum):
    """
    Project governance mode.
    Controls the level of constraint and process formality.
    """
    SIMPLE = "simple"      # Flexible, minimal constraints
    STANDARD = "standard"  # Moderate controls
    STRICT = "strict"      # Formal, high controls


class ProjectVisibility(str, Enum):
    """
    Project visibility.
    PUBLIC: Visible to all workspace members
    PRIVATE: Visible only to selected members
    """
    PUBLIC = "public"
    PRIVATE = "private"


class ProjectRole(str, Enum):
    """
    Project-level roles.
    Defines permission levels for project members.
    Ref: Module 3 - AC 2.3
    """
    MANAGER = "manager"      # Project Manager - highest authority
    PLANNER = "planner"      # Planner - schedule and planning authority
    MEMBER = "member"        # Member - execution role
    VIEWER = "viewer"        # Viewer - read-only access


class ProjectPriority(str, Enum):
    """
    Project priority levels.
    Used for resource allocation and conflict resolution.
    Ref: Module 3 - Feature 2.20
    """
    CRITICAL = "critical"    # Critical - absolute priority
    HIGH = "high"            # High - important project
    MEDIUM = "medium"        # Medium - standard (default)
    LOW = "low"              # Low - filler project


class ChangeRequestStatus(str, Enum):
    """
    Change request workflow status.
    Used in strict governance mode.
    Ref: Module 3 - Feature 2.11
    """
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"


class ChangeRequestType(str, Enum):
    """
    Types of change requests.
    Ref: Module 3 - Feature 2.11 AC 1
    """
    SCOPE = "scope"          # Scope change
    SCHEDULE = "schedule"    # Schedule change
    COST = "cost"            # Cost/budget change
    RESOURCE = "resource"    # Resource change


class ProjectHealthStatus(str, Enum):
    """
    Project health indicator (traffic light).
    Ref: Module 3 - Feature 2.10
    """
    GREEN = "green"          # On track
    AMBER = "amber"          # At risk
    RED = "red"              # Off track


# ============ Module 4 & 15: Tag & Categorization System ============

class TagEntityType(str, Enum):
    """
    Entity type limit for tags.
    Ref: Entities/Tag.md
    """
    TASK = "task"
    PROJECT = "project"
    ALL = "all"


# ============ Module 5: Task & Work Item Management ============

class TaskStatus(str, Enum):
    """Task workflow status"""
    BACKLOG = "backlog"
    TO_DO = "to_do"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============ Module 7: Time & Resource Management ============

class TimesheetStatus(str, Enum):
    """Timesheet workflow status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


# ============ Module 8: Integration & Webhooks ============

class WebhookEventType(str, Enum):
    """Webhook event types"""
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"


class WebhookDeliveryStatus(str, Enum):
    """Webhook delivery attempt status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


# ============ Module 14: Reporting & Analytics ============

class ReportExecutionStatus(str, Enum):
    """Report execution status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportFormat(str, Enum):
    """Report export format"""
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


# ============ Module 5: Temporal Planning and Scheduling ============

class PlanStateEnum(str, Enum):
    """
    Plan state machine for planning governance.
    Ref: Module 5 - Feature 2.11 - AC 1 - Plan State Machine
    """
    DRAFT = "draft"          # PM is drafting, editable
    SUBMITTED = "submitted"  # Submitted for approval
    APPROVED = "approved"    # Approved, baseline created
    LOCKED = "locked"        # Locked, no direct changes allowed


class SchedulingModeEnum(str, Enum):
    """
    Task scheduling mode.
    Ref: Module 5 - Feature 2.2 - AC 3 - Scheduling Mode
    """
    AUTO = "auto"            # Auto-scheduled (default)
    MANUAL = "manual"        # Manually scheduled (Pinned)


class DependencyTypeEnum(str, Enum):
    """
    Task dependency types.
    Ref: Module 5 - Feature 2.2 - AC 4 - Dependency Types
    """
    FS = "FS"  # Finish-to-Start (default)
    SS = "SS"  # Start-to-Start
    FF = "FF"  # Finish-to-Finish
    SF = "SF"  # Start-to-Finish


class SLAStatusEnum(str, Enum):
    """
    SLA status tracking.
    Ref: Module 5 - Feature 2.7 - AC 3 - Visual Warning
    """
    ON_TRACK = "on_track"    # < 75% of SLA consumed
    AT_RISK = "at_risk"      # >= 75% to < 100% of SLA consumed
    BREACHED = "breached"    # >= 100% of SLA consumed


class PersonalExceptionType(str, Enum):
    """
    Type of personal calendar exceptions.
    Ref: Module 5 - Feature 2.19 - AC 1
    """
    VACATION = "vacation"
    SICK_LEAVE = "sick_leave"
    HALF_DAY = "half_day"
    OTHER = "other"


class ZoomLevel(str, Enum):
    """
    Gantt chart zoom levels.
    Ref: Module 5 - Feature 2.1 - AC 1 - Timeline
    """
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"


class ResourceLevelingStrategy(str, Enum):
    """
    Resource leveling strategies.
    Ref: Module 5 - Feature 2.17 - AC 1
    """
    WITHIN_SLACK = "within_slack"    # Only move tasks with Float
    EXTEND_PROJECT = "extend_project"  # Can extend project end date


# ============ Module 6: Unified Collaboration Hub ============

class ApprovalStatusEnum(str, Enum):
    """
    Approval workflow status for files and tasks.
    Ref: Module 6 - Feature 2.4 - AC 1 - Decision State Machine
    """
    PENDING = "pending"              # Awaiting review
    APPROVED = "approved"            # Approved and locked
    CHANGES_REQUESTED = "changes_requested"  # Need modifications
    REJECTED = "rejected"            # Not approved


class NoteAccessEnum(str, Enum):
    """
    Access level for project and personal notes.
    Ref: Module 6 - Feature 2.6, 2.7
    """
    PRIVATE = "private"              # Only owner can see (Feature 2.7)
    PROJECT = "project"              # All project members (Feature 2.6)
    WORKSPACE = "workspace"          # All workspace members
    PUBLIC = "public"                # Anyone with public link (Feature 2.9)


class AttachmentStatusEnum(str, Enum):
    """
    Status of file attachments.
    Ref: Module 6 - Feature 2.2 - AC 2 - Security (Sandbox scanning)
    """
    PENDING_SCAN = "pending_scan"    # Waiting for virus scan
    CLEAN = "clean"                  # Passed scan, safe to view
    QUARANTINED = "quarantined"      # Malware detected
    PROCESSING = "processing"        # Preview generation in progress
    READY = "ready"                  # Preview generated and ready


class PublicLinkStatusEnum(str, Enum):
    """
    Status of public publication links for notes.
    Ref: Module 6 - Feature 2.9
    """
    ACTIVE = "active"                # Link is accessible
    EXPIRED = "expired"              # Expiration date passed
    DISABLED = "disabled"            # Manually disabled
    PASSWORD_PROTECTED = "password_protected"  # Requires password


# ============ Module 7: Event-Driven Notification System ============

class NotificationTypeEnum(str, Enum):
    """
    Notification event types.
    Ref: Module 7 - Feature 2.1 - Intelligent Aggregation
    """
    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    TASK_COMMENTED = "task_commented"
    TASK_COMPLETED = "task_completed"
    PROJECT_UPDATED = "project_updated"
    PROJECT_STATUS_CHANGED = "project_status_changed"
    USER_MENTIONED = "user_mentioned"
    FILE_UPLOADED = "file_uploaded"
    FILE_APPROVED = "file_approved"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_DECISION = "approval_decision"
    SLA_BREACHED = "sla_breached"
    SLA_AT_RISK = "sla_at_risk"
    SECURITY_ALERT = "security_alert"
    SYSTEM_ERROR = "system_error"


class NotificationChannelEnum(str, Enum):
    """
    Notification delivery channels.
    Ref: Module 7 - Feature 2.2 - Real-time Delivery & Fallback
    """
    IN_APP = "in_app"                # In-application notification
    EMAIL = "email"                  # Email delivery
    MOBILE_PUSH = "mobile_push"      # Mobile push notification
    WEBSOCKET = "websocket"          # WebSocket for real-time toast


class NotificationPriorityEnum(str, Enum):
    """
    Notification priority levels.
    Ref: Module 7 - Business Rule 3.4 - Priority Queues & QoS
    """
    HIGH = "high"                    # Critical (< 1s, no debounce)
    MEDIUM = "medium"                # Transactional (5-10s, with debounce)
    LOW = "low"                      # Promotional (background jobs)


class NotificationStatusEnum(str, Enum):
    """
    Notification delivery status.
    Ref: Module 7 - Business Rule 3.1 - Retry Mechanism
    """
    PENDING = "pending"              # Queued for delivery
    SENT = "sent"                    # Successfully delivered
    READ = "read"                    # Read by recipient
    FAILED = "failed"                # Delivery failed after retries
    EXPIRED = "expired"              # TTL expired before delivery


class TemplateLocaleEnum(str, Enum):
    """
    Supported notification template locales.
    Ref: Module 7 - Feature 2.4 - AC 2 - Localization Support
    """
    EN = "en"                        # English
    VI = "vi"                        # Vietnamese
    JA = "ja"                        # Japanese
    ZH_CN = "zh_cn"                  # Simplified Chinese
    ZH_TW = "zh_tw"                  # Traditional Chinese
    KO = "ko"                        # Korean


# ============ Module 8: Data Archiving and Compliance ============

class ArchiveStatusEnum(str, Enum):
    """
    Archive status for projects and entities.
    Ref: Module 8 - Feature 2.1 - Automated Archiving Strategy
    """
    ACTIVE = "active"                # Currently active, in hot storage
    ARCHIVED = "archived"            # Archived to cold storage, read-only


class DataRetentionTypeEnum(str, Enum):
    """
    Types of data retention policies.
    Ref: Module 8 - Section 3.2 - Data Retention Policy
    """
    DELETED_ITEMS = "deleted_items"  # Soft-deleted items (30 days)
    SYSTEM_LOGS = "system_logs"      # Audit logs (90 days)
    USER_UPLOADS = "user_uploads"    # User-uploaded files (depends on project lifecycle)


class ExportFormatEnum(str, Enum):
    """
    Supported export formats for data portability.
    Ref: Module 8 - Feature 2.3 - Data Export & Portability
    """
    JSON = "json"                    # Hierarchical JSON format
    CSV = "csv"                      # Comma-separated values for spreadsheets


# ============ Module 9: User Experience Personalization ============

class ThemeModeEnum(str, Enum):
    """
    UI theme modes for appearance customization.
    Ref: Module 9 - Feature 2.2 - Theme & Appearance
    """
    LIGHT = "light"                  # Light theme (default)
    DARK = "dark"                    # Dark theme (reduces eye strain)
    SYSTEM = "system"                # Sync with OS settings (prefers-color-scheme)


class FontSizeEnum(str, Enum):
    """
    Global font size options for typography accessibility.
    Ref: Module 9 - Feature 2.5 - Typographic Accessibility (AC 1)
    """
    SMALL = "small"                  # 12px base font
    MEDIUM = "medium"                # 14px base font (default)
    LARGE = "large"                  # 16px base font
    EXTRA_LARGE = "extra_large"      # 18px base font


class FontFamilyEnum(str, Enum):
    """
    Font family options for readability and accessibility.
    Ref: Module 9 - Feature 2.5 - Typographic Accessibility (AC 2)
    """
    SYSTEM_DEFAULT = "system_default"        # San Francisco (Mac) / Segoe UI (Win)
    DYSLEXIC_FRIENDLY = "dyslexic_friendly"  # OpenDyslexic or similar
    MONOSPACE = "monospace"                   # Code-like appearance for developers


class InfoDensityModeEnum(str, Enum):
    """
    Information density modes for workspace layout optimization.
    Ref: Module 9 - Feature 2.4 - Workspace Layout Optimization (AC 2)
    """
    COMFORTABLE = "comfortable"      # Spacious layout (12-16px padding) - default
    COMPACT = "compact"              # Dense layout (4-8px padding) for data analysts


class ColorBlindnessModeEnum(str, Enum):
    """
    Color vision deficiency support modes.
    Ref: Module 9 - Feature 2.8 - Color Vision Deficiency Support
    """
    NORMAL = "normal"                # Standard color palette
    DEUTERANOPIA = "deuteranopia"    # Red-Green color blindness (Protanopia alternative)
    TRITANOPIA = "tritanopia"        # Blue-Yellow color blindness


class NotificationChannelEnum(str, Enum):
    """
    Notification delivery channels.
    Ref: Module 9 - Feature 2.6 - Notification Granularity (AC 1)
    """
    IN_APP = "in_app"                # In-app notification badge
    EMAIL = "email"                  # Email notification
    BROWSER_PUSH = "browser_push"    # Browser push notification


class NotificationEventTypeEnum(str, Enum):
    """
    Types of events that trigger notifications.
    Ref: Module 9 - Feature 2.6 - Notification Granularity (AC 1)
    """
    MENTION = "mention"              # User mentioned (@mention)
    TASK_ASSIGNED = "task_assigned"  # Task assigned to user
    TASK_STATUS_CHANGED = "task_status_changed"  # Task status updated
    DEADLINE_APPROACHING = "deadline_approaching"  # Deadline reminder
    COMMENT_ADDED = "comment_added"  # Comment on task
    PROJECT_UPDATED = "project_updated"  # Project changes
    COLLABORATION_REQUEST = "collaboration_request"  # Collaboration invite


# ============ Module 11: Advanced Analytics and Reporting ============

class AnalyticsTypeEnum(str, Enum):
    """
    Types of analytics visualizations supported.
    Ref: Module 11 - Features 2.1-2.4
    """
    BURN_DOWN = "burn_down"          # Sprint burn-down chart
    BURN_UP = "burn_up"              # Sprint burn-up chart with scope creep
    VELOCITY = "velocity"            # Sprint velocity comparison
    HEATMAP = "heatmap"              # Resource utilization heatmap
    TIME_TRACKING = "time_tracking"  # Time entry tracking
    CUSTOM_REPORT = "custom_report"  # Custom report


class ReportFormatEnum(str, Enum):
    """
    Supported export formats for reports.
    Ref: Module 11 - Feature 2.4 AC 2 - Filtering & Export
    """
    PDF = "pdf"                      # PDF format for printing
    CSV = "csv"                      # CSV for spreadsheet processing
    XLSX = "xlsx"                    # Excel format


class TimesheetStatusEnum(str, Enum):
    """
    Timesheet approval workflow status.
    Ref: Module 11 - Feature 2.3 AC 3 - Timesheet Approval Workflow
    """
    DRAFT = "draft"                  # Work in progress
    SUBMITTED = "submitted"          # Awaiting approval
    APPROVED = "approved"            # Approved by PM/Manager
    REJECTED = "rejected"            # Rejected with feedback


class BillableStatusEnum(str, Enum):
    """
    Billable status for time entries.
    Ref: Module 11 - Feature 2.3 AC 2 - Billable vs. Non-billable
    """
    BILLABLE = "billable"            # Hours charged to client/customer
    NON_BILLABLE = "non_billable"    # Internal or overhead hours


class ReportScheduleFrequencyEnum(str, Enum):
    """
    Frequency for automated report generation.
    Ref: Module 11 - Feature 2.4 - Custom Report Builder (Scheduling)
    """
    DAILY = "daily"                  # Generated daily
    WEEKLY = "weekly"                # Generated weekly
    MONTHLY = "monthly"              # Generated monthly
    QUARTERLY = "quarterly"          # Generated quarterly
    ANNUALLY = "annually"            # Generated annually

# ========== Module 12: Integration Ecosystem Enums ==========

class RetryPolicyEnum(str, Enum):
    """
    Retry policy for webhook deliveries.
    Ref: Module 12 - Feature 2.2 - Webhook Reliability
    """
    EXPONENTIAL = "exponential"      # Exponential backoff
    LINEAR = "linear"                # Linear backoff
    NO_RETRY = "no_retry"            # No retries


class WebhookDeliveryStatusEnum(str, Enum):
    """
    Status of webhook event delivery.
    Ref: Module 12 - Feature 2.2 - AC 2 - Delivery Status
    """
    PENDING = "pending"              # Awaiting delivery
    DELIVERED = "delivered"          # Successfully delivered
    FAILED = "failed"                # Delivery failed
    RETRYING = "retrying"            # Retrying delivery


class OAuthStatusEnum(str, Enum):
    """
    Status of OAuth connection.
    Ref: Module 12 - Feature 3 - OAuth Integration
    """
    ACTIVE = "active"                # Connection active
    INACTIVE = "inactive"            # Connection inactive
    EXPIRED = "expired"              # Token expired
    REVOKED = "revoked"              # User revoked connection


class ConsentTypeEnum(str, Enum):
    """
    Types of user consent for privacy compliance.
    Ref: Module 12 - Feature 6 - Governance & Compliance
    """
    DATA_USAGE = "data_usage"        # Consent for data usage
    THIRD_PARTY = "third_party"      # Third-party integration
    ANALYTICS = "analytics"          # Analytics and tracking
    MARKETING = "marketing"           # Marketing communications


class IntegrationStatusEnum(str, Enum):
    """
    Status of external service integration.
    Ref: Module 12 - Feature 4 - Integration Binding
    """
    ACTIVE = "active"                # Integration is active
    INACTIVE = "inactive"            # Integration is inactive
    ERROR = "error"                  # Integration has errors
    PENDING = "pending"              # Integration pending setup


class PluginStatusEnum(str, Enum):
    """
    Status of plugin installation and operation.
    Ref: Module 12 - Feature 5 - Plugin Marketplace
    """
    INSTALLED = "installed"          # Plugin installed
    ENABLED = "enabled"              # Plugin enabled
    DISABLED = "disabled"            # Plugin disabled
    ERROR = "error"                  # Plugin error state
    UNINSTALLED = "uninstalled"      # Plugin uninstalled