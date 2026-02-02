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
