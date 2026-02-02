"""
Module 6: Unified Collaboration Hub - Pydantic Schemas

Validation and serialization schemas for all collaboration features:
- Comments and threaded discussions
- File attachments with versioning
- Project and personal notes
- Formal approval workflows
- Public publishing
- Collaborative search
"""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field, validator, EmailStr
from app.db.enums import (
    ApprovalStatusEnum, NoteAccessEnum, AttachmentStatusEnum, PublicLinkStatusEnum
)


# ============ Comment Schemas ============

class MentionCreate(BaseModel):
    """Create a mention"""
    mentioned_user_id: str = Field(..., description="User ID to mention")
    context: Optional[str] = Field(None, description="Context: assignee, reporter, collaborator")


class CommentCreate(BaseModel):
    """Create a new comment"""
    task_id: str = Field(..., description="Task ID")
    parent_comment_id: Optional[str] = Field(None, description="Parent comment ID (for nested replies)")
    content: str = Field(..., min_length=1, max_length=10000, description="Rich text content")
    mentioned_user_ids: Optional[List[str]] = Field(None, description="List of @mentioned user IDs")


class CommentUpdate(BaseModel):
    """Update an existing comment"""
    content: str = Field(..., min_length=1, max_length=10000, description="Updated content")
    reason: Optional[str] = Field(None, description="Reason for edit (audit trail)")


class CommentResponse(BaseModel):
    """Comment response"""
    id: str
    task_id: str
    parent_comment_id: Optional[str]
    author_id: str
    content: str
    mentioned_user_ids: Optional[List[str]]
    edited_at: Optional[datetime]
    edit_count: int
    reply_count: int
    is_pinned: bool
    reactions: Optional[Dict[str, List[str]]]  # emoji -> [user_ids]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentThreadResponse(CommentResponse):
    """Comment with nested replies"""
    replies: List[CommentResponse] = Field(default_factory=list)


# ============ Attachment Schemas ============

class AttachmentCreate(BaseModel):
    """Create/upload an attachment"""
    task_id: str = Field(..., description="Attach to task")
    filename: str = Field(..., description="File name with extension")
    size: int = Field(..., gt=0, le=1073741824, description="File size in bytes (max 1GB)")
    mime_type: str = Field(..., description="MIME type (e.g., 'image/png')")
    storage_provider: Optional[str] = Field("local", description="Where to store: local, s3, azure")


class AttachmentResponse(BaseModel):
    """Attachment details"""
    id: str
    task_id: str
    filename: str
    size: int
    mime_type: str
    current_version: int
    status: AttachmentStatusEnum
    preview_url: Optional[str]
    preview_generated: bool
    approval_status: ApprovalStatusEnum
    uploaded_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class FileVersionResponse(BaseModel):
    """File version details"""
    id: str
    file_id: str
    version_number: int
    storage_path: str
    size: int
    checksum: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AttachmentVersionResponse(BaseModel):
    """List of attachment versions"""
    versions: List[FileVersionResponse]
    latest_version: FileVersionResponse


# ============ Note Schemas ============

class NoteCreate(BaseModel):
    """Create a new note"""
    project_id: Optional[str] = Field(None, description="Project ID (for project notes)")
    parent_note_id: Optional[str] = Field(None, description="Parent note ID (for hierarchy)")
    title: str = Field(..., min_length=1, max_length=255, description="Note title")
    content: str = Field(..., min_length=1, description="Rich text content")
    access_level: NoteAccessEnum = Field(NoteAccessEnum.PRIVATE, description="Access control")
    is_template: bool = Field(False, description="Save as template?")
    template_name: Optional[str] = Field(None, description="Template name (if is_template=True)")
    template_category: Optional[str] = Field(None, description="Template category: meeting, bug_report, feature_spec")


class NoteUpdate(BaseModel):
    """Update an existing note"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    access_level: Optional[NoteAccessEnum] = None
    is_pinned: Optional[bool] = None
    order_index: Optional[int] = None


class NoteResponse(BaseModel):
    """Note details"""
    id: str
    project_id: Optional[str]
    parent_note_id: Optional[str]
    user_id: str
    title: str
    content: str
    access_level: NoteAccessEnum
    is_template: bool
    template_name: Optional[str]
    is_pinned: bool
    view_count: int
    comment_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteTreeResponse(NoteResponse):
    """Note with hierarchy and nested children"""
    children: List['NoteTreeResponse'] = Field(default_factory=list)


class NoteConvertToTaskRequest(BaseModel):
    """Convert note to task"""
    project_id: str = Field(..., description="Target project")
    task_list_id: str = Field(..., description="Target task list")
    title: Optional[str] = Field(None, description="Override note title as task name")
    description: Optional[str] = Field(None, description="Override note content as task description")


# ============ Note Version Schemas ============

class NoteVersionResponse(BaseModel):
    """Note version details"""
    id: str
    note_id: str
    version_number: int
    change_description: Optional[str]
    title: str
    content: str
    added_content: Optional[str]
    removed_content: Optional[str]
    created_at: datetime
    created_by: str

    class Config:
        from_attributes = True


class NoteVersionDiffRequest(BaseModel):
    """Request diff between versions"""
    version_from: int = Field(..., ge=1, description="From version number")
    version_to: int = Field(..., ge=1, description="To version number")


class NoteVersionRestoreRequest(BaseModel):
    """Restore to previous version"""
    version_number: int = Field(..., ge=1, description="Version to restore")
    reason: Optional[str] = Field(None, description="Reason for restoration (audit)")


# ============ Approval Schemas ============

class ApprovalCreate(BaseModel):
    """Create approval request"""
    task_id: Optional[str] = Field(None, description="Task to approve")
    file_id: Optional[str] = Field(None, description="File to approve")
    approver_id: str = Field(..., description="Approver user ID")
    decision_notes: Optional[str] = Field(None, description="Instructions/context for approver")


class ApprovalApprove(BaseModel):
    """Approve a document/task"""
    decision_notes: Optional[str] = Field(None, description="Approval notes/reason")
    signature: Optional[str] = Field(None, description="Base64 encoded digital signature")


class ApprovalRequestChanges(BaseModel):
    """Request changes on approval"""
    change_instructions: str = Field(..., description="What needs to change")
    priority: str = Field("normal", description="Urgency: low, normal, high, critical")


class ApprovalReject(BaseModel):
    """Reject approval"""
    rejection_reason: str = Field(..., description="Why rejected")
    allow_resubmit: bool = Field(True, description="Can be resubmitted?")


class ApprovalRecordResponse(BaseModel):
    """Approval record details"""
    id: str
    task_id: Optional[str]
    file_id: Optional[str]
    approver_id: str
    requestor_id: Optional[str]
    status: ApprovalStatusEnum
    decision_notes: Optional[str]
    decision_timestamp: Optional[datetime]
    checksum: str
    invalidated_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Public Link Schemas ============

class PublicLinkCreate(BaseModel):
    """Create public link for note"""
    note_id: str = Field(..., description="Note to publish")
    link_title: Optional[str] = Field(None, description="Display title for public page")
    is_password_protected: bool = Field(False, description="Require password?")
    password: Optional[str] = Field(None, description="Password (if protected)")
    expiration_date: Optional[datetime] = Field(None, description="When link expires")
    auto_update: bool = Field(True, description="Auto-update with note changes?")


class PublicLinkResponse(BaseModel):
    """Public link details"""
    id: str
    note_id: str
    slug: str
    url: str = Field(None)  # Computed: /public/{slug}
    link_title: Optional[str]
    is_password_protected: bool
    status: PublicLinkStatusEnum
    view_count: int
    last_accessed_at: Optional[datetime]
    expiration_date: Optional[datetime]
    auto_update: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PublicLinkAccessRequest(BaseModel):
    """Access password-protected public link"""
    password: str = Field(..., description="Password to access")


# ============ Smart Backlink Schemas ============

class SmartBacklinkResponse(BaseModel):
    """Smart backlink reference"""
    id: str
    note_id: str
    source_note_id: Optional[str]
    source_task_id: Optional[str]
    mention_text: str
    is_linked: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BacklinkSuggestionResponse(BaseModel):
    """Suggested unlinked mention"""
    mention_text: str
    suggested_link_id: str
    link_type: str  # "note" or "task"
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")


# ============ Mention Schemas ============

class MentionResponse(BaseModel):
    """Mention details"""
    id: str
    mentioned_user_id: str
    mentioned_by_user_id: str
    comment_id: Optional[str]
    note_id: Optional[str]
    context: Optional[str]
    mention_priority: int
    created_at: datetime

    class Config:
        from_attributes = True


class MentionSuggestion(BaseModel):
    """Suggested user to mention (Feature 2.1 AC 2)"""
    user_id: str
    user_name: str
    avatar_url: Optional[str]
    priority: int  # 1: assignee, 2: reporter, 3: recent, 4: others
    reason: str  # "assignee", "reporter", "recent_collaborator"


# ============ User Presence Schemas ============

class UserPresenceUpdate(BaseModel):
    """Update user presence"""
    task_id: Optional[str] = None
    note_id: Optional[str] = None
    status: str = Field("viewing", description="viewing, editing, commenting")
    is_typing: bool = Field(False, description="Is currently typing?")


class UserPresenceResponse(BaseModel):
    """User presence status"""
    user_id: str
    user_name: str
    avatar_url: Optional[str]
    task_id: Optional[str]
    note_id: Optional[str]
    status: str
    is_typing: bool
    last_activity_at: datetime

    class Config:
        from_attributes = True


class TaskPresenceResponse(BaseModel):
    """All active users on a task"""
    task_id: str
    active_users: List[UserPresenceResponse]
    typing_users: List[str]  # User names


# ============ Search Schemas ============

class CollaborationSearchRequest(BaseModel):
    """Search collaboration content"""
    query: str = Field(..., min_length=1, max_length=200, description="Search keywords")
    project_id: Optional[str] = Field(None, description="Limit to project")
    search_scope: List[str] = Field(
        ["comments", "notes", "attachments", "tasks"],
        description="What to search: comments, notes, attachments, tasks"
    )
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class SearchResultItem(BaseModel):
    """Individual search result"""
    id: str
    entity_type: str  # "comment", "note", "attachment", "task"
    entity_id: str
    title: Optional[str]
    snippet: str  # Preview text with query highlighted
    url_path: str  # Deep link
    created_by: Optional[str]
    created_at: datetime
    relevance_score: float = Field(..., ge=0, le=1)


class CollaborationSearchResponse(BaseModel):
    """Search results"""
    total_count: int
    limit: int
    offset: int
    results: List[SearchResultItem]
    query: str
    search_time_ms: int


# ============ Real-time Collaboration Schemas ============

class CollaborationEvent(BaseModel):
    """WebSocket event for real-time collaboration"""
    event_type: str  # "comment_added", "user_typing", "file_uploaded", "approval_changed"
    entity_id: str
    entity_type: str
    data: Dict
    timestamp: datetime
    user_id: str


class TypingIndicator(BaseModel):
    """Typing indicator event"""
    task_id: Optional[str]
    note_id: Optional[str]
    user_id: str
    user_name: str
    is_typing: bool


# ============ Notification Schemas ============

class CollaborationNotificationResponse(BaseModel):
    """Collaboration notification"""
    id: str
    recipient_user_id: str
    trigger_type: str  # mention, approval, reply, note_shared
    task_id: Optional[str]
    note_id: Optional[str]
    comment_id: Optional[str]
    triggered_by_user_id: str
    title: str
    message: str
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class MarkNotificationAsReadRequest(BaseModel):
    """Mark notification as read"""
    notification_id: str = Field(..., description="Notification ID")


# ============ Bulk/Batch Schemas ============

class BulkCommentCreateRequest(BaseModel):
    """Create multiple comments in batch"""
    comments: List[CommentCreate] = Field(..., min_items=1, max_items=100)


class BulkAttachmentUploadRequest(BaseModel):
    """Upload multiple files"""
    attachments: List[AttachmentCreate] = Field(..., min_items=1, max_items=50)


class BulkApprovalRequest(BaseModel):
    """Approve multiple items"""
    approval_ids: List[str] = Field(..., min_items=1, max_items=100)
    decision_notes: Optional[str] = Field(None)
    approve: bool = Field(True, description="True: approve, False: reject")


# ============ Statistics Schemas ============

class CollaborationStats(BaseModel):
    """Collaboration statistics for a project"""
    project_id: str
    total_comments: int
    total_attachments: int
    total_notes: int
    active_collaborators: int
    total_approvals: int
    approved_count: int
    pending_approvals: int
    most_recent_activity: datetime
    comment_trend_7d: List[int]  # Comments per day for last 7 days


class UserCollaborationStats(BaseModel):
    """User's collaboration activity"""
    user_id: str
    comments_created: int
    files_uploaded: int
    notes_created: int
    mentions_received: int
    approvals_given: int
    approvals_pending: int
