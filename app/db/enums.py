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
