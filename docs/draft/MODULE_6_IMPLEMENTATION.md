# Module 6: Unified Collaboration Hub - Implementation Documentation

## Overview

Module 6 implements a comprehensive collaboration system for PronaFlow, providing real-time communication, document management, and knowledge sharing capabilities across projects and tasks.

### Key Features

1. **Threaded Comments & Discussions**
   - Rich text comments with reactions and mentions
   - Nested reply threads with unlimited depth
   - Pinned comments for important information
   - Edit history tracking

2. **File Attachments & Versioning**
   - Multi-version file management
   - Automatic version tracking with checksums
   - File status tracking (scanning, quarantine, approved)
   - Storage provider flexibility (local, S3, Azure)
   - Preview generation support

3. **Notes & Wiki System**
   - Hierarchical note organization
   - Project-wide and personal notes
   - Rich text editing with version history
   - Tag-based categorization
   - Access control (public, private, team)

4. **Approval Workflows**
   - Formal approval process for files and notes
   - Multi-approver support
   - Status tracking (pending, approved, rejected)
   - Approval comments and justification

5. **Smart Features**
   - @mentions with notifications
   - Automatic backlink detection
   - Full-text search across content
   - Public link sharing with expiration
   - Real-time presence indicators

## Database Models

### Core Models

#### Comment (Extended from tasks.py)
```python
class Comment(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    content: Mapped[str]
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    parent_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("comments.id"))
    
    # Module 6 Extensions
    mentioned_user_ids: Mapped[Optional[dict]] = mapped_column(JSON)
    original_content: Mapped[Optional[str]]
    edit_count: Mapped[int] = mapped_column(default=0)
    reply_count: Mapped[int] = mapped_column(default=0)
    is_pinned: Mapped[bool] = mapped_column(default=False)
    reactions: Mapped[Optional[dict]] = mapped_column(JSON)
```

**Key Features:**
- Self-referential parent-child relationship for threading
- JSON storage for reactions (`{"👍": [user_id1, user_id2], "🎉": [user_id3]}`)
- Mentioned users tracked for notification triggering
- Edit history preserved in `original_content`

#### File (Extended from tasks.py)
```python
class File(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    file_name: Mapped[str]
    file_path: Mapped[str]
    file_size: Mapped[int]
    mime_type: Mapped[str]
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    uploaded_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    
    # Module 6 Extensions
    storage_provider: Mapped[Optional[str]]  # "local", "s3", "azure"
    status: Mapped[Optional[AttachmentStatusEnum]]  # scanning, clean, quarantine
    scan_result: Mapped[Optional[str]]
    preview_url: Mapped[Optional[str]]
    preview_generated: Mapped[bool] = mapped_column(default=False)
    approval_status: Mapped[Optional[ApprovalStatusEnum]]
```

**Key Features:**
- Multi-provider storage support
- Virus scanning integration via `status` field
- Preview generation for supported formats
- Approval workflow integration

#### FileVersion
```python
class FileVersion(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    file_id: Mapped[UUID] = mapped_column(ForeignKey("files.id", ondelete="CASCADE"))
    version_number: Mapped[int]
    file_path: Mapped[str]
    file_size: Mapped[int]
    uploaded_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    checksum: Mapped[Optional[str]]  # SHA-256 hash
    change_summary: Mapped[Optional[str]]
```

**Key Features:**
- Automatic version incrementing
- Checksum validation for integrity
- Change summary for version history
- Cascade delete when parent file removed

#### Note
```python
class Note(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    content: Mapped[str]
    project_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("projects.id"))
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    parent_note_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("notes.id"))
    access_level: Mapped[NoteAccessEnum]  # public, private, team
    is_template: Mapped[bool] = mapped_column(default=False)
    tags: Mapped[Optional[str]]  # Comma-separated
    approval_status: Mapped[Optional[ApprovalStatusEnum]]
    
    # Relationships
    versions: Mapped[List["NoteVersion"]] = relationship(back_populates="note")
    child_notes: Mapped[List["Note"]] = relationship(back_populates="parent_note")
    parent_note: Mapped[Optional["Note"]] = relationship(back_populates="child_notes")
```

**Key Features:**
- Hierarchical structure for wiki-style organization
- Project association or personal (project_id=None)
- Access control with three levels
- Template support for reusable notes
- Tag-based categorization

#### NoteVersion
```python
class NoteVersion(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    note_id: Mapped[UUID] = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"))
    version_number: Mapped[int]
    content: Mapped[str]
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    change_summary: Mapped[Optional[str]]
```

**Key Features:**
- Full content snapshot per version
- Automatic version numbering
- Change summary for tracking modifications
- Cascade delete with parent note

#### ApprovalRecord
```python
class ApprovalRecord(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    file_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("files.id"))
    note_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("notes.id"))
    approver_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[ApprovalStatusEnum]  # pending, approved, rejected
    comments: Mapped[Optional[str]]
    approved_at: Mapped[Optional[datetime]]
```

**Key Features:**
- Supports both file and note approvals
- Multiple approvers per item
- Status tracking with timestamp
- Approval comments for justification

#### SmartBacklink
```python
class SmartBacklink(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_note_id: Mapped[UUID] = mapped_column(ForeignKey("notes.id"))
    target_note_id: Mapped[UUID] = mapped_column(ForeignKey("notes.id"))
    link_text: Mapped[Optional[str]]
    context_snippet: Mapped[Optional[str]]  # Surrounding text
```

**Key Features:**
- Bidirectional note linking
- Context preservation
- Automatic link detection
- Supports wiki-style [[notation]]

#### Mention
```python
class Mention(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mentioned_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    comment_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("comments.id"))
    note_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("notes.id"))
    mentioned_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    is_read: Mapped[bool] = mapped_column(default=False)
```

**Key Features:**
- Tracks @mentions across comments and notes
- Read status for notification management
- Links to source user and content

#### UserPresence
```python
class UserPresence(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("tasks.id"))
    note_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("notes.id"))
    status: Mapped[str]  # "viewing", "editing", "typing"
    last_heartbeat: Mapped[datetime]
```

**Key Features:**
- Real-time activity tracking
- Supports task and note contexts
- Heartbeat mechanism for timeout detection
- Status indicators for UI

#### PublicLink
```python
class PublicLink(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    note_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("notes.id"))
    file_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("files.id"))
    token: Mapped[str] = mapped_column(unique=True, index=True)
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[Optional[datetime]]
    password_hash: Mapped[Optional[str]]
    max_views: Mapped[Optional[int]]
    view_count: Mapped[int] = mapped_column(default=0)
    status: Mapped[PublicLinkStatusEnum]  # active, expired, revoked
```

**Key Features:**
- Secure token-based sharing
- Optional password protection
- View count limits
- Expiration management
- Revocation support

#### SearchIndex
```python
class SearchIndex(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    content_type: Mapped[str]  # "note", "comment", "file"
    content_id: Mapped[UUID]
    title: Mapped[Optional[str]]
    content: Mapped[str]
    tags: Mapped[Optional[str]]
    project_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("projects.id"))
    last_indexed: Mapped[datetime]
```

**Key Features:**
- Unified search across all content types
- Full-text indexing
- Tag-based filtering
- Project scoping
- Timestamp for reindexing

#### CollaborationNotification
```python
class CollaborationNotification(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str]  # "mention", "reply", "approval_request", "approval_decision"
    title: Mapped[str]
    message: Mapped[str]
    reference_type: Mapped[Optional[str]]  # "comment", "note", "file"
    reference_id: Mapped[Optional[UUID]]
    is_read: Mapped[bool] = mapped_column(default=False)
    action_url: Mapped[Optional[str]]
```

**Key Features:**
- Multiple notification types
- Reference tracking to source content
- Read/unread status
- Action links for quick navigation

## Enumerations

```python
class AttachmentStatusEnum(str, enum.Enum):
    SCANNING = "scanning"
    CLEAN = "clean"
    QUARANTINE = "quarantine"

class ApprovalStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class NoteAccessEnum(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    TEAM = "team"

class PublicLinkStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
```

## Pydantic Schemas

### Comment Schemas

```python
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    task_id: UUID
    parent_id: Optional[UUID] = None

class CommentUpdate(BaseModel):
    content: Optional[str] = None
    is_pinned: Optional[bool] = None

class CommentResponse(CommentBase):
    id: UUID
    task_id: UUID
    user_id: UUID
    parent_id: Optional[UUID]
    mentioned_user_ids: Optional[dict]
    edit_count: int
    reply_count: int
    is_pinned: bool
    reactions: Optional[dict]
    created_at: datetime
    updated_at: datetime
```

### File/Attachment Schemas

```python
class AttachmentCreate(BaseModel):
    task_id: UUID
    file_name: str
    file_size: int
    mime_type: str
    storage_provider: Optional[str] = "local"

class AttachmentResponse(BaseModel):
    id: UUID
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    task_id: UUID
    uploaded_by_id: UUID
    storage_provider: Optional[str]
    status: Optional[AttachmentStatusEnum]
    preview_url: Optional[str]
    approval_status: Optional[ApprovalStatusEnum]
    created_at: datetime

class FileVersionResponse(BaseModel):
    id: UUID
    file_id: UUID
    version_number: int
    file_path: str
    file_size: int
    uploaded_by_id: UUID
    checksum: Optional[str]
    change_summary: Optional[str]
    created_at: datetime
```

### Note Schemas

```python
class NoteCreate(BaseModel):
    title: str
    content: str
    project_id: Optional[UUID] = None
    parent_note_id: Optional[UUID] = None
    access_level: NoteAccessEnum = NoteAccessEnum.PRIVATE
    is_template: bool = False
    tags: Optional[str] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    access_level: Optional[NoteAccessEnum] = None
    tags: Optional[str] = None
    change_summary: Optional[str] = None

class NoteResponse(BaseModel):
    id: UUID
    title: str
    content: str
    project_id: Optional[UUID]
    created_by_id: UUID
    parent_note_id: Optional[UUID]
    access_level: NoteAccessEnum
    is_template: bool
    tags: Optional[str]
    approval_status: Optional[ApprovalStatusEnum]
    created_at: datetime
    updated_at: datetime
```

### Approval Schemas

```python
class ApprovalCreate(BaseModel):
    file_id: Optional[UUID] = None
    note_id: Optional[UUID] = None
    approver_id: UUID
    status: ApprovalStatusEnum = ApprovalStatusEnum.PENDING
    comments: Optional[str] = None

class ApprovalUpdate(BaseModel):
    status: ApprovalStatusEnum
    comments: Optional[str] = None

class ApprovalResponse(BaseModel):
    id: UUID
    file_id: Optional[UUID]
    note_id: Optional[UUID]
    approver_id: UUID
    status: ApprovalStatusEnum
    comments: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
```

## Service Layer

### CommentService

**Key Methods:**
- `create_comment(comment_data, current_user)` - Create comment with mention extraction
- `get_comment(comment_id)` - Retrieve single comment
- `update_comment(comment_id, comment_data)` - Update with edit tracking
- `delete_comment(comment_id)` - Soft/hard delete
- `get_thread(parent_id)` - Get all replies
- `add_reaction(comment_id, emoji, user_id)` - Add reaction
- `remove_reaction(comment_id, emoji, user_id)` - Remove reaction
- `pin_comment(comment_id)` - Toggle pin status

**Business Logic:**
- Extracts @mentions from content
- Increments reply_count on parent
- Preserves original content on edit
- Manages reactions JSON structure

### AttachmentService (File)

**Key Methods:**
- `upload_attachment(file_data, file_content, current_user)` - Create file + version
- `get_attachment(attachment_id)` - Retrieve file info
- `get_versions(attachment_id)` - List all versions
- `add_version(attachment_id, file_content, change_summary, current_user)` - New version
- `download_attachment(attachment_id, version_number)` - Get file content
- `update_status(attachment_id, status, scan_result)` - Update scan status
- `generate_preview(attachment_id)` - Create preview

**Business Logic:**
- Creates FileVersion for each upload
- Calculates SHA-256 checksum
- Manages storage provider paths
- Triggers virus scanning
- Generates previews for images/PDFs

### NoteService

**Key Methods:**
- `create_note(note_data, current_user)` - Create note with initial version
- `get_note(note_id, current_user)` - Get note with access check
- `update_note(note_id, note_data, current_user)` - Update + create version
- `delete_note(note_id)` - Delete note and children
- `get_project_notes(project_id)` - List project notes
- `get_child_notes(parent_id)` - Get note hierarchy
- `convert_to_task(note_id, task_list_id, current_user)` - Convert note to task
- `search_notes(query, project_id, tags)` - Search with filters

**Business Logic:**
- Enforces access control (public/private/team)
- Creates NoteVersion on each update
- Detects and creates SmartBacklinks
- Supports hierarchical navigation
- Processes tags for categorization

### NoteVersionService

**Key Methods:**
- `create_version(note_id, content, created_by_id, change_summary)` - New version
- `get_versions(note_id)` - Version history
- `get_version(version_id)` - Single version
- `revert_to_version(note_id, version_number, current_user)` - Rollback
- `compare_versions(version1_id, version2_id)` - Diff

**Business Logic:**
- Auto-increments version numbers
- Preserves full content snapshots
- Supports version comparison
- Enables rollback functionality

### ApprovalService

**Key Methods:**
- `request_approval(approval_data, current_user)` - Create request
- `update_approval(approval_id, approval_data, current_user)` - Approve/reject
- `get_pending_approvals(user_id)` - Approver's queue
- `get_approval_history(file_id, note_id)` - Audit trail
- `bulk_approve(approval_ids, current_user)` - Batch approval

**Business Logic:**
- Creates CollaborationNotifications
- Updates file/note approval_status
- Records approval timestamp
- Supports multi-approver workflows

### PublicLinkService

**Key Methods:**
- `create_link(link_data, current_user)` - Generate shareable link
- `get_link(token, password)` - Access via token
- `revoke_link(link_id)` - Disable link
- `check_expiration(token)` - Validate expiry
- `increment_view_count(link_id)` - Track usage

**Business Logic:**
- Generates secure random tokens
- Hashes passwords with bcrypt
- Checks expiration and view limits
- Auto-updates status (active → expired)

### SearchService

**Key Methods:**
- `index_content(content_type, content_id, title, content, tags, project_id)` - Add to index
- `search(query, content_type, project_id, tags)` - Full-text search
- `reindex_all()` - Rebuild entire index
- `delete_from_index(content_type, content_id)` - Remove entry

**Business Logic:**
- Indexes notes, comments, files
- Supports PostgreSQL full-text search
- Filters by type, project, tags
- Updates last_indexed timestamp

### SmartBacklinkService

**Key Methods:**
- `create_backlink(source_note_id, target_note_id, link_text, context)` - Manual link
- `detect_backlinks(note_id, content)` - Auto-detect [[links]]
- `get_backlinks(note_id)` - Get all references
- `update_backlinks(note_id, new_content)` - Sync on edit

**Business Logic:**
- Parses [[Note Title]] syntax
- Extracts surrounding context
- Prevents duplicate links
- Cascades delete with notes

### UserPresenceService

**Key Methods:**
- `update_presence(user_id, task_id, note_id, status)` - Heartbeat
- `get_active_users(task_id, note_id)` - Who's here
- `cleanup_stale_presence(timeout_minutes)` - Remove inactive
- `set_typing(user_id, task_id, note_id)` - Typing indicator

**Business Logic:**
- Updates last_heartbeat timestamp
- Filters by heartbeat age (default: 5 min)
- Supports "viewing", "editing", "typing"
- WebSocket integration ready

### MentionService

**Key Methods:**
- `create_mention(mention_data)` - Record @mention
- `get_user_mentions(user_id, is_read)` - User's notifications
- `mark_as_read(mention_id)` - Update read status
- `extract_mentions(content)` - Parse @username from text

**Business Logic:**
- Parses @username syntax
- Creates CollaborationNotifications
- Tracks read/unread state
- Links to source comment/note

## API Endpoints

### Comments
```
POST   /api/v1/collaboration/comments          - Create comment
GET    /api/v1/collaboration/comments/{id}     - Get comment
PUT    /api/v1/collaboration/comments/{id}     - Update comment
DELETE /api/v1/collaboration/comments/{id}     - Delete comment
GET    /api/v1/collaboration/comments/{id}/thread - Get replies
POST   /api/v1/collaboration/comments/{id}/reactions - Add reaction
DELETE /api/v1/collaboration/comments/{id}/reactions/{emoji} - Remove reaction
PUT    /api/v1/collaboration/comments/{id}/pin - Toggle pin
```

### Attachments
```
POST   /api/v1/collaboration/attachments        - Upload file
GET    /api/v1/collaboration/attachments/{id}   - Get file info
GET    /api/v1/collaboration/attachments/{id}/versions - List versions
POST   /api/v1/collaboration/attachments/{id}/versions - Upload new version
GET    /api/v1/collaboration/attachments/{id}/download - Download file
PUT    /api/v1/collaboration/attachments/{id}/status - Update scan status
POST   /api/v1/collaboration/attachments/{id}/preview - Generate preview
```

### Notes
```
POST   /api/v1/collaboration/notes              - Create note
GET    /api/v1/collaboration/notes/{id}         - Get note
PUT    /api/v1/collaboration/notes/{id}         - Update note
DELETE /api/v1/collaboration/notes/{id}         - Delete note
GET    /api/v1/collaboration/notes              - List notes (filter by project)
GET    /api/v1/collaboration/notes/{id}/children - Get child notes
GET    /api/v1/collaboration/notes/{id}/versions - Get version history
POST   /api/v1/collaboration/notes/{id}/convert-to-task - Convert to task
GET    /api/v1/collaboration/notes/search       - Search notes
```

### Approvals
```
POST   /api/v1/collaboration/approvals          - Request approval
GET    /api/v1/collaboration/approvals/{id}     - Get approval
PUT    /api/v1/collaboration/approvals/{id}     - Update approval status
GET    /api/v1/collaboration/approvals/pending  - Get pending approvals
GET    /api/v1/collaboration/approvals/history  - Get approval history
POST   /api/v1/collaboration/approvals/bulk     - Bulk approve/reject
```

### Public Links
```
POST   /api/v1/collaboration/public-links       - Create public link
GET    /api/v1/collaboration/public-links/{token} - Access via link
PUT    /api/v1/collaboration/public-links/{id}/revoke - Revoke link
GET    /api/v1/collaboration/public-links/{id}  - Get link details
```

### Search
```
GET    /api/v1/collaboration/search             - Search all content
POST   /api/v1/collaboration/search/reindex     - Rebuild search index
```

### User Presence
```
POST   /api/v1/collaboration/presence           - Update presence
GET    /api/v1/collaboration/presence/{resource_type}/{resource_id} - Get active users
DELETE /api/v1/collaboration/presence/cleanup  - Cleanup stale presence
```

### Backlinks
```
GET    /api/v1/collaboration/backlinks/{note_id} - Get note backlinks
POST   /api/v1/collaboration/backlinks          - Create manual backlink
```

### Mentions
```
GET    /api/v1/collaboration/mentions           - Get user's mentions
PUT    /api/v1/collaboration/mentions/{id}/read - Mark as read
```

## Usage Examples

### Example 1: Creating a Threaded Comment

```python
# Create parent comment
comment_data = {
    "content": "This feature looks great! @john what do you think?",
    "task_id": "123e4567-e89b-12d3-a456-426614174000"
}
response = requests.post(
    "http://localhost:8000/api/v1/collaboration/comments",
    json=comment_data,
    headers={"Authorization": f"Bearer {token}"}
)
parent_comment = response.json()

# Create reply
reply_data = {
    "content": "I agree! Let's proceed.",
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "parent_id": parent_comment["id"]
}
response = requests.post(
    "http://localhost:8000/api/v1/collaboration/comments",
    json=reply_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Example 2: File Upload with Versioning

```python
# Initial upload
files = {"file": open("document.pdf", "rb")}
data = {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "file_name": "document.pdf",
    "mime_type": "application/pdf"
}
response = requests.post(
    "http://localhost:8000/api/v1/collaboration/attachments",
    files=files,
    data=data,
    headers={"Authorization": f"Bearer {token}"}
)
file_id = response.json()["id"]

# Upload new version
files = {"file": open("document_v2.pdf", "rb")}
data = {"change_summary": "Updated section 3"}
response = requests.post(
    f"http://localhost:8000/api/v1/collaboration/attachments/{file_id}/versions",
    files=files,
    data=data,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Example 3: Creating Hierarchical Notes

```python
# Create parent note
parent_note = {
    "title": "API Documentation",
    "content": "Overview of REST API endpoints",
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "access_level": "team",
    "tags": "documentation,api"
}
response = requests.post(
    "http://localhost:8000/api/v1/collaboration/notes",
    json=parent_note,
    headers={"Authorization": f"Bearer {token}"}
)
parent_id = response.json()["id"]

# Create child note
child_note = {
    "title": "Authentication Endpoints",
    "content": "Details about /auth/* endpoints",
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "parent_note_id": parent_id,
    "access_level": "team",
    "tags": "documentation,api,auth"
}
response = requests.post(
    "http://localhost:8000/api/v1/collaboration/notes",
    json=child_note,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Example 4: Approval Workflow

```python
# Request approval
approval_request = {
    "file_id": "123e4567-e89b-12d3-a456-426614174000",
    "approver_id": "987e6543-e21b-12d3-a456-426614174000",
    "status": "pending",
    "comments": "Please review for security compliance"
}
response = requests.post(
    "http://localhost:8000/api/v1/collaboration/approvals",
    json=approval_request,
    headers={"Authorization": f"Bearer {token}"}
)
approval_id = response.json()["id"]

# Approve/Reject
approval_update = {
    "status": "approved",
    "comments": "Security review passed"
}
response = requests.put(
    f"http://localhost:8000/api/v1/collaboration/approvals/{approval_id}",
    json=approval_update,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Example 5: Public Link Sharing

```python
# Create shareable link
public_link = {
    "note_id": "123e4567-e89b-12d3-a456-426614174000",
    "expires_at": "2026-03-01T00:00:00",
    "password_hash": "secure_password_123",  # Will be hashed by backend
    "max_views": 100
}
response = requests.post(
    "http://localhost:8000/api/v1/collaboration/public-links",
    json=public_link,
    headers={"Authorization": f"Bearer {token}"}
)
link_token = response.json()["token"]

# Access via public link (no auth required)
response = requests.get(
    f"http://localhost:8000/api/v1/collaboration/public-links/{link_token}",
    params={"password": "secure_password_123"}
)
note_content = response.json()
```

### Example 6: Full-Text Search

```python
# Search across all content
search_params = {
    "query": "authentication implementation",
    "content_type": "note",  # Optional: filter by type
    "project_id": "123e4567-e89b-12d3-a456-426614174000",  # Optional
    "tags": "documentation,api"  # Optional
}
response = requests.get(
    "http://localhost:8000/api/v1/collaboration/search",
    params=search_params,
    headers={"Authorization": f"Bearer {token}"}
)
results = response.json()  # List of matching notes/comments/files
```

### Example 7: Real-Time Presence

```python
# Update user presence (heartbeat)
presence_data = {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "editing"
}
response = requests.post(
    "http://localhost:8000/api/v1/collaboration/presence",
    json=presence_data,
    headers={"Authorization": f"Bearer {token}"}
)

# Get active users
response = requests.get(
    "http://localhost:8000/api/v1/collaboration/presence/task/123e4567-e89b-12d3-a456-426614174000",
    headers={"Authorization": f"Bearer {token}"}
)
active_users = response.json()  # [{"user_id": "...", "status": "editing", ...}]
```

## Migration Information

**Migration File:** `cd6041d7e8ce_add_module6_unified_collaboration.py`

**Database Changes:**
- **New Tables:** 9 (notes, note_versions, public_links, smart_backlinks, user_presence, approval_records, collaboration_notifications, mentions, search_indexes)
- **Extended Tables:** 3 (comments: 6 fields, files: 7 fields, file_versions: 1 field)
- **New Enums:** 4 (AttachmentStatusEnum, ApprovalStatusEnum, NoteAccessEnum, PublicLinkStatusEnum)
- **Indexes:** Foreign key indexes on all relationships

**Important Notes:**
- Enum types must be created before column addition
- CASCADE deletes configured for versions and child relationships
- JSON columns used for reactions and mentioned_user_ids
- UUID primary keys throughout

**Migration Commands:**
```bash
# Generate migration (already done)
alembic revision --autogenerate -m "add_module6_unified_collaboration"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## Integration Points

### With Module 3 (Task Management)
- Comments linked to tasks via `task_id`
- Files attached to tasks via `task_id`
- Task-specific presence tracking
- Convert notes to tasks

### With Module 4 (Notifications)
- Mention notifications via `CollaborationNotification`
- Approval request/decision notifications
- Reply notifications for threaded comments
- File upload notifications

### With Module 5 (Search & Analytics)
- SearchIndex integration for full-text search
- Analytics on collaboration metrics (comments per task, file versions, etc.)
- Tag-based filtering and reporting

### Authentication & Authorization
- All endpoints require JWT authentication
- Access control enforced at service layer
- NoteAccessEnum controls note visibility
- Project membership checked for team notes

## Testing Recommendations

### Unit Tests
```python
# tests/services/test_comment_service.py
def test_create_comment_with_mention():
    comment_data = CommentCreate(
        content="Great work @john!",
        task_id=UUID("...")
    )
    comment = comment_service.create_comment(comment_data, current_user)
    assert comment.mentioned_user_ids is not None
    assert "john" in comment.content

def test_add_reaction():
    reaction = comment_service.add_reaction(comment_id, "👍", user_id)
    assert "👍" in reaction.reactions
    assert user_id in reaction.reactions["👍"]
```

### Integration Tests
```python
# tests/api/test_collaboration.py
def test_file_versioning_workflow(client, auth_headers):
    # Upload initial file
    response = client.post("/api/v1/collaboration/attachments", ...)
    file_id = response.json()["id"]
    
    # Upload version 2
    response = client.post(f"/api/v1/collaboration/attachments/{file_id}/versions", ...)
    assert response.json()["version_number"] == 2
    
    # List versions
    response = client.get(f"/api/v1/collaboration/attachments/{file_id}/versions")
    assert len(response.json()) == 2
```

## Future Enhancements

### Phase 2 (WebSocket Integration)
- Real-time comment updates
- Live presence indicators
- Typing indicators for comments
- Collaborative editing for notes

### Phase 3 (Advanced Features)
- Rich text editor integration (Quill, TipTap)
- Inline image uploads
- Code syntax highlighting in notes
- Markdown preview
- Export notes to PDF/HTML
- Import from Confluence/Notion

### Phase 4 (AI Features)
- Smart tag suggestions
- Auto-summarization of long notes
- Similar note recommendations
- Sentiment analysis on comments
- Auto-linking related content

## Performance Considerations

1. **Database Indexing**
   - Foreign key columns indexed automatically
   - Add composite indexes for common queries:
     ```sql
     CREATE INDEX idx_comments_task_created ON comments(task_id, created_at DESC);
     CREATE INDEX idx_notes_project_access ON notes(project_id, access_level);
     CREATE INDEX idx_search_content_type ON search_indexes(content_type, project_id);
     ```

2. **Pagination**
   - All list endpoints support limit/offset
   - Default limit: 50 items
   - Maximum limit: 200 items

3. **Caching Strategy**
   - Cache note content for public notes
   - Cache search results (5-minute TTL)
   - Cache user presence data (30-second TTL)

4. **File Storage**
   - Stream large file downloads
   - Generate thumbnails asynchronously
   - Use CDN for file delivery
   - Implement file size limits (default: 50MB)

## Security Considerations

1. **Access Control**
   - Enforce project membership for team notes
   - Verify user ownership before edits
   - Rate limit file uploads (10 per minute)
   - Sanitize HTML content in notes/comments

2. **File Security**
   - Virus scanning for all uploads
   - File type validation
   - Secure filename generation
   - Prevent path traversal attacks

3. **Public Links**
   - Use cryptographically secure tokens
   - Hash passwords with bcrypt
   - Implement rate limiting
   - Log access attempts

4. **XSS Prevention**
   - Sanitize user-generated content
   - Escape HTML in comments
   - Use Content Security Policy headers

## Troubleshooting

### Common Issues

**Issue 1: Enum type does not exist**
```
psycopg2.errors.UndefinedObject: type "attachmentstatusenum" does not exist
```
**Solution:** Ensure enum types are created before column addition in migration:
```python
attachment_status_enum.create(op.get_bind(), checkfirst=True)
op.add_column('files', sa.Column('status', attachment_status_enum, ...))
```

**Issue 2: Cascade delete not working**
```
IntegrityError: update or delete on table "notes" violates foreign key constraint
```
**Solution:** Add `ondelete="CASCADE"` to ForeignKey:
```python
note_id = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"))
```

**Issue 3: JSON column query fails**
```
DataError: invalid input syntax for type json
```
**Solution:** Ensure JSON values are properly serialized:
```python
reactions = {"👍": [str(user_id)]}  # Convert UUIDs to strings
```

## Support & Resources

- **API Documentation:** http://localhost:8000/docs
- **Database Schema:** [docs/02-Architecture/Database-Schema.md](docs/02-Architecture/Database-Schema.md)
- **Entity Analysis:** [docs/ENTITY_ANALYSIS_FINAL_REPORT.md](docs/ENTITY_ANALYSIS_FINAL_REPORT.md)
- **General Architecture:** [docs/02-Architecture/Application Structure.md](docs/02-Architecture/Application Structure.md)

---

**Version:** 1.0  
**Last Updated:** February 2, 2026  
**Status:** ✅ Implemented & Migrated
