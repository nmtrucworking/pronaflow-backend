"""
Module 6: Unified Collaboration Hub - REST API Endpoints

REST endpoints for all collaboration features:
- Comments and discussions
- Attachments with versioning
- Notes and project wiki
- Approvals and workflows
- Public publishing
- Search and discovery
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.db.models import User, Task, Project
from app.schemas.collaboration import (
    CommentCreate, CommentUpdate, CommentResponse, CommentThreadResponse,
    AttachmentCreate, AttachmentResponse, AttachmentVersionResponse,
    NoteCreate, NoteUpdate, NoteResponse, NoteTreeResponse, NoteConvertToTaskRequest,
    NoteVersionResponse, NoteVersionDiffRequest, NoteVersionRestoreRequest,
    ApprovalCreate, ApprovalApprove, ApprovalRequestChanges, ApprovalReject, ApprovalRecordResponse,
    PublicLinkCreate, PublicLinkResponse, PublicLinkAccessRequest,
    SmartBacklinkResponse, BacklinkSuggestionResponse,
    MentionResponse, MentionSuggestion,
    UserPresenceResponse, TaskPresenceResponse,
    CollaborationSearchRequest, CollaborationSearchResponse,
    CollaborationNotificationResponse, MarkNotificationAsReadRequest,
)
from app.services.collaboration import (
    CommentService, AttachmentService, NoteService, NoteVersionService,
    ApprovalService, PublicLinkService, SearchService, SmartBacklinkService,
    UserPresenceService, MentionService,
)

router = APIRouter(prefix="/api/v1/collaboration", tags=["collaboration"])


# ============ Comment Endpoints ============

@router.post("/comments", response_model=CommentResponse, status_code=201)
def create_comment(
    request: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new comment
    
    Feature 2.1 AC 1-3: Rich text, mentions, threading
    """
    comment = CommentService.create_comment(
        db=db,
        task_id=request.task_id,
        user_id=current_user.id,
        content=request.content,
        parent_comment_id=request.parent_comment_id,
        mentioned_user_ids=request.mentioned_user_ids,
    )
    
    return comment


@router.get("/comments/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comment details"""
    from app.db.models import Comment
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return comment


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: str,
    request: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update comment (edit tracking)"""
    comment = CommentService.update_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id,
        new_content=request.content,
        reason=request.reason,
    )
    
    return comment


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete comment (soft delete with audit trail)"""
    CommentService.delete_comment(db=db, comment_id=comment_id, user_id=current_user.id)
    return None


@router.get("/tasks/{task_id}/comments", response_model=List[CommentThreadResponse])
def get_task_comments(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all comments for a task"""
    from app.db.models import Comment
    comments = CommentService.get_comments_for_task(db=db, task_id=task_id)
    
    return comments


@router.post("/comments/{comment_id}/reactions/{emoji}", status_code=200)
def add_reaction(
    comment_id: str,
    emoji: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add emoji reaction to comment"""
    comment = CommentService.add_reaction(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id,
        emoji=emoji,
    )
    
    return comment


# ============ Attachment Endpoints ============

@router.post("/attachments", response_model=AttachmentResponse, status_code=201)
def upload_attachment(
    task_id: str = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload file attachment
    
    Feature 2.2 AC 1: Version control (auto-versioning)
    AC 2: Virus scanning and preview generation (async)
    """
    # TODO: Save file and get storage path
    # TODO: Trigger virus scan (async)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    attachment = AttachmentService.upload_attachment(
        db=db,
        task_id=task_id,
        note_id=None,
        comment_id=None,
        user_id=current_user.id,
        project_id=None,
        file_name=file.filename,
        file_size=file_size,
        file_type=file.filename.split('.')[-1] if file.filename else "",
        mime_type=file.content_type or "application/octet-stream",
        storage_path="",  # Would be set by storage service
    )
    
    return attachment


@router.get("/attachments/{attachment_id}", response_model=AttachmentResponse)
def get_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get attachment details"""
    from app.db.models import File
    attachment = db.query(File).filter(File.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    return attachment


@router.get("/attachments/task/{task_id}/versions", response_model=AttachmentVersionResponse)
def get_attachment_versions(
    task_id: str,
    file_name: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all versions of a file"""
    versions = AttachmentService.get_attachment_versions(
        db=db,
        task_id=task_id,
        file_name=file_name,
    )
    
    if not versions:
        raise HTTPException(status_code=404, detail="No versions found")
    
    return {
        "versions": versions,
        "latest_version": versions[0],
    }


@router.post("/attachments/{attachment_id}/restore", response_model=AttachmentResponse)
def restore_attachment_version(
    attachment_id: str,
    request: NoteVersionRestoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Restore to previous attachment version"""
    attachment = AttachmentService.restore_attachment_version(
        db=db,
        file_id=attachment_id,
        target_version=request.version_number,
        user_id=current_user.id,
    )
    
    return attachment


# ============ Note Endpoints ============

@router.post("/notes", response_model=NoteResponse, status_code=201)
def create_note(
    request: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a note
    
    Feature 2.6: Project Notes (with project_id)
    Feature 2.7: Personal Notes (without project_id)
    """
    note = NoteService.create_note(
        db=db,
        user_id=current_user.id,
        title=request.title,
        content=request.content,
        project_id=request.project_id,
        parent_note_id=request.parent_note_id,
        access_level=request.access_level,
    )
    
    return note


@router.get("/notes/{note_id}", response_model=NoteTreeResponse)
def get_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get note with nested children and comments"""
    from app.db.models import Note
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note


@router.patch("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: str,
    request: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update note (creates new version)"""
    note = NoteService.update_note(
        db=db,
        note_id=note_id,
        user_id=current_user.id,
        title=request.title,
        content=request.content,
    )
    
    return note


@router.get("/notes/project/{project_id}", response_model=List[NoteTreeResponse])
def get_project_notes(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all notes in a project"""
    from app.db.models import Note
    notes = db.query(Note).filter(
        Note.project_id == project_id,
        Note.parent_note_id.is_(None),  # Only top-level
    ).all()
    
    return notes


@router.get("/notes/user/personal", response_model=List[NoteResponse])
def get_personal_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Feature 2.7 AC 1: Get user's personal notes
    """
    from app.db.models import Note
    from app.db.enums import NoteAccessEnum
    notes = db.query(Note).filter(
        Note.user_id == current_user.id,
        Note.access_level == NoteAccessEnum.PRIVATE,
    ).all()
    
    return notes


@router.post("/notes/{note_id}/convert-to-task", status_code=201)
def convert_note_to_task(
    note_id: str,
    request: NoteConvertToTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Feature 2.7 AC 2: Convert personal note to task
    """
    task = NoteService.convert_to_task(
        db=db,
        note_id=note_id,
        project_id=request.project_id,
        task_list_id=request.task_list_id,
        user_id=current_user.id,
    )
    
    return {"task_id": task.id, "message": "Note converted to task"}


# ============ Note Version Endpoints ============

@router.get("/notes/{note_id}/versions", response_model=List[NoteVersionResponse])
def get_note_versions(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all versions of a note"""
    versions = NoteVersionService.get_versions(db=db, note_id=note_id)
    
    return versions


@router.post("/notes/{note_id}/restore", response_model=NoteResponse)
def restore_note_version(
    note_id: str,
    request: NoteVersionRestoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Restore to previous note version"""
    note = NoteVersionService.restore_version(
        db=db,
        note_id=note_id,
        version_number=request.version_number,
        user_id=current_user.id,
    )
    
    return note


# ============ Approval Endpoints ============

@router.post("/approvals", response_model=ApprovalRecordResponse, status_code=201)
def create_approval_request(
    request: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create approval request
    
    Feature 2.4 AC 1: Decision State Machine (start in PENDING)
    AC 2: Digital Signature Audit
    """
    # TODO: Calculate checksum of content
    
    approval = ApprovalService.create_approval_request(
        db=db,
        task_id=request.task_id,
        file_id=request.file_id,
        approver_id=request.approver_id,
        requestor_id=current_user.id,
        checksum="",  # Would be calculated from actual content
    )
    
    return approval


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalRecordResponse)
def approve(
    approval_id: str,
    request: ApprovalApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve (transition to APPROVED)"""
    approval = ApprovalService.approve(
        db=db,
        approval_id=approval_id,
        approver_id=current_user.id,
        decision_notes=request.decision_notes,
        signature=request.signature,
    )
    
    return approval


@router.post("/approvals/{approval_id}/request-changes", response_model=ApprovalRecordResponse)
def request_changes(
    approval_id: str,
    request: ApprovalRequestChanges,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Request changes (transition to CHANGES_REQUESTED)"""
    approval = ApprovalService.request_changes(
        db=db,
        approval_id=approval_id,
        approver_id=current_user.id,
        change_instructions=request.change_instructions,
    )
    
    return approval


@router.get("/approvals/user/pending", response_model=List[ApprovalRecordResponse])
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get pending approvals for current user"""
    from app.db.models import ApprovalRecord
    from app.db.enums import ApprovalStatusEnum
    
    approvals = db.query(ApprovalRecord).filter(
        ApprovalRecord.approver_id == current_user.id,
        ApprovalRecord.status == ApprovalStatusEnum.PENDING,
    ).all()
    
    return approvals


# ============ Public Link Endpoints ============

@router.post("/public-links", response_model=PublicLinkResponse, status_code=201)
def create_public_link(
    request: PublicLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create public link for note
    
    Feature 2.9 AC 1-3: Generate link, password protection, live updates
    """
    link = PublicLinkService.create_public_link(
        db=db,
        note_id=request.note_id,
        created_by=current_user.id,
        link_title=request.link_title,
        password=request.password if request.is_password_protected else None,
        expiration_date=request.expiration_date,
        auto_update=request.auto_update,
    )
    
    return link


@router.get("/public/{slug}", response_model=NoteResponse)
def access_public_link(
    slug: str,
    password: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Access public note (no authentication required)
    """
    link = PublicLinkService.verify_access(db=db, slug=slug, password=password)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found or expired")
    
    from app.db.models import Note
    note = db.query(Note).filter(Note.id == link.note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note


# ============ Smart Backlink Endpoints ============

@router.get("/notes/{note_id}/backlinks", response_model=List[SmartBacklinkResponse])
def get_backlinks(
    note_id: str,
    include_unlinked: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Feature 2.11 AC 1: Get references to this note
    """
    backlinks = SmartBacklinkService.get_backlinks(
        db=db,
        note_id=note_id,
        include_unlinked=include_unlinked,
    )
    
    return backlinks


# ============ Search Endpoints ============

@router.post("/search", response_model=CollaborationSearchResponse)
def search_collaboration(
    request: CollaborationSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Feature 2.5: Collaborative Search
    AC 1: Full-text search across multiple entities
    AC 2: Contextual results with snippets and deep linking
    """
    total_count, results = SearchService.search(
        db=db,
        query=request.query,
        project_id=request.project_id,
        entity_types=request.search_scope,
        limit=request.limit,
        offset=request.offset,
    )

    mapped_results = []
    for item in results:
        mapped_results.append({
            "id": str(item.id),
            "entity_type": item.entity_type,
            "entity_id": item.entity_id,
            "title": item.title,
            "snippet": item.snippet or "",
            "url_path": item.url_path or "",
            "created_by": item.created_by,
            "created_at": item.original_created_at or item.created_at,
            "relevance_score": 0.0,
        })
    
    return {
        "total_count": total_count,
        "limit": request.limit,
        "offset": request.offset,
        "results": mapped_results,
        "query": request.query,
        "search_time_ms": 0,  # Would measure actual search time
    }


# ============ Presence Endpoints ============

@router.post("/presence/update")
def update_presence(
    task_id: Optional[str] = Query(None),
    note_id: Optional[str] = Query(None),
    status: str = Query("viewing"),
    is_typing: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Feature 2.3: Update user presence
    AC 1: Visual indicators for active users and typing status
    """
    presence = UserPresenceService.update_presence(
        db=db,
        user_id=current_user.id,
        task_id=task_id,
        note_id=note_id,
        status=status,
        is_typing=is_typing,
    )
    
    return presence


@router.get("/presence/task/{task_id}", response_model=TaskPresenceResponse)
def get_task_presence(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get active users on task"""
    users = UserPresenceService.get_active_users_on_task(db=db, task_id=task_id)
    
    typing_users = [u.user_id for u in users if u.is_typing]
    
    return {
        "task_id": task_id,
        "active_users": users,
        "typing_users": typing_users,
    }


# ============ Mention Endpoints ============

@router.get("/mentions/suggestions", response_model=List[MentionSuggestion])
def get_mention_suggestions(
    project_id: str = Query(...),
    task_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Feature 2.1 AC 2: Smart mention suggestions
    Priority: Assignee > Reporter > Recent collaborators
    """
    suggestions = MentionService.get_mention_suggestions(
        db=db,
        project_id=project_id,
        current_user_id=current_user.id,
        task_id=task_id,
    )
    
    return suggestions


# ============ Notification Endpoints ============

@router.get("/notifications", response_model=List[CollaborationNotificationResponse])
def get_notifications(
    is_read: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get collaboration notifications for user"""
    from app.db.models import CollaborationNotification
    
    query = db.query(CollaborationNotification).filter(
        CollaborationNotification.recipient_user_id == current_user.id
    )
    
    if is_read is not None:
        query = query.filter(CollaborationNotification.is_read == is_read)
    
    notifications = query.order_by(CollaborationNotification.created_at.desc()).offset(offset).limit(limit).all()
    
    return notifications


@router.patch("/notifications/{notification_id}/read", status_code=200)
def mark_notification_as_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark notification as read"""
    from app.db.models import CollaborationNotification
    
    notification = db.query(CollaborationNotification).filter(
        CollaborationNotification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification.recipient_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    
    db.commit()
    
    return {"status": "read"}
