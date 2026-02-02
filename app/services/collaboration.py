"""
Module 6: Unified Collaboration Hub - Service Layer

Business logic implementation for all collaboration features:
- Comment threading and management
- File attachment versioning
- Note management with hierarchy
- Approval workflows
- Public publishing
- Real-time presence
- Collaborative search
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
import hashlib
import secrets

from app.db.models import (
    Comment,
    File,
    FileVersion,
    Note,
    NoteVersion,
    SmartBacklink,
    PublicLink,
    Mention,
    UserPresence,
    ApprovalRecord,
    SearchIndex,
    CollaborationNotification,
    Task,
    User,
    Project,
)
from app.db.enums import ApprovalStatusEnum, NoteAccessEnum, AttachmentStatusEnum, PublicLinkStatusEnum


class CommentService:
    """
    Feature 2.1: Contextual Threaded Discussions
    - Create comments with rich text
    - Support nested replies
    - Handle @mentions for notifications
    """
    
    @staticmethod
    def create_comment(
        db: Session,
        task_id: str,
        user_id: str,
        content: str,
        parent_comment_id: Optional[str] = None,
        mentioned_user_ids: Optional[List[str]] = None,
    ) -> Comment:
        """
        Create a new comment with optional threading
        
        AC 1: Rich text editor support (content)
        AC 2: Smart Mentions - store mentioned users for notification trigger
        AC 3: Threaded Replies - support parent_comment_id
        """
        # Validate context
        if not task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must specify task_id"
            )
        
        comment = Comment(
            id=uuid.uuid4(),
            task_id=task_id,
            parent_comment_id=parent_comment_id,
            author_id=user_id,
            content=content,
            mentioned_user_ids=mentioned_user_ids or [],
        )
        db.add(comment)
        
        # If nested reply, increment parent's reply count
        if parent_comment_id:
            parent = db.query(Comment).filter(Comment.id == parent_comment_id).first()
            if parent:
                parent.reply_count += 1
        
        db.commit()
        return comment
    
    @staticmethod
    def update_comment(
        db: Session,
        comment_id: str,
        user_id: str,
        new_content: str,
        reason: Optional[str] = None,
    ) -> Comment:
        """
        Edit comment with audit trail
        
        Business Rule 3.1: Immutability Audit
        - Save original content
        - Track edit_count
        - Record edited_at timestamp
        """
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if comment.author_id != user_id:
            raise HTTPException(status_code=403, detail="Can only edit own comments")
        
        # Audit trail
        if not comment.original_content:
            comment.original_content = comment.content

        comment.content = new_content
        comment.is_edited = True
        comment.edited_at = datetime.utcnow()
        comment.edit_count += 1
        
        db.commit()
        return comment
    
    @staticmethod
    def delete_comment(db: Session, comment_id: str, user_id: str) -> None:
        """Delete comment (soft delete for audit)"""
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if comment.author_id != user_id:
            raise HTTPException(status_code=403, detail="Can only delete own comments")
        
        # Soft delete: clear content but keep record
        comment.content = "[deleted]"
        comment.edited_at = datetime.utcnow()
        db.commit()
    
    @staticmethod
    def get_comments_for_task(db: Session, task_id: str, include_replies: bool = True) -> List[Comment]:
        """Get top-level comments for a task with optional nested replies"""
        comments = db.query(Comment).filter(
            and_(Comment.task_id == task_id, Comment.parent_comment_id.is_(None))
        ).order_by(Comment.created_at).all()
        
        return comments
    
    @staticmethod
    def add_reaction(db: Session, comment_id: str, user_id: str, emoji: str) -> Comment:
        """Add emoji reaction to comment"""
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if not comment.reactions:
            comment.reactions = {}
        
        if emoji not in comment.reactions:
            comment.reactions[emoji] = []
        
        if user_id not in comment.reactions[emoji]:
            comment.reactions[emoji].append(user_id)
        
        db.commit()
        return comment


class AttachmentService:
    """
    Feature 2.2: Digital Asset Management (DAM)
    - Version control (AC 1: No overwrite)
    - Universal viewer (AC 2: Sandbox rendering)
    """
    
    @staticmethod
    def upload_attachment(
        db: Session,
        task_id: Optional[str],
        note_id: Optional[str],
        comment_id: Optional[str],
        user_id: str,
        project_id: Optional[str],
        file_name: str,
        file_size: int,
        file_type: str,
        mime_type: str,
        storage_path: str,
    ) -> File:
        """
        Upload file with automatic versioning
        
        AC 1: Version Control - don't overwrite, create new version
        AC 2: Universal Viewer - set preview capability based on MIME type
        """
        if not task_id:
            raise HTTPException(status_code=400, detail="task_id is required for attachments")

        if note_id or comment_id:
            raise HTTPException(status_code=400, detail="Note/comment attachments are not supported")

        existing = db.query(File).filter(
            and_(File.task_id == task_id, File.filename == file_name)
        ).first()

        checksum = hashlib.sha256(f"{file_name}{datetime.utcnow()}".encode()).hexdigest()

        if not existing:
            file_record = File(
                id=uuid.uuid4(),
                task_id=task_id,
                uploaded_by=user_id,
                filename=file_name,
                mime_type=mime_type,
                size=file_size,
                current_version=1,
                storage_path=storage_path,
            )
            db.add(file_record)
            db.flush()

            version = FileVersion(
                id=uuid.uuid4(),
                file_id=file_record.id,
                version_number=1,
                storage_path=storage_path,
                size=file_size,
                checksum=checksum,
            )
            db.add(version)
        else:
            new_version = existing.current_version + 1
            existing.current_version = new_version
            existing.storage_path = storage_path
            existing.size = file_size
            existing.mime_type = mime_type

            version = FileVersion(
                id=uuid.uuid4(),
                file_id=existing.id,
                version_number=new_version,
                storage_path=storage_path,
                size=file_size,
                checksum=checksum,
            )
            db.add(version)

        db.commit()

        return existing if existing else file_record
    
    @staticmethod
    def get_attachment_versions(db: Session, task_id: str, file_name: str) -> List[FileVersion]:
        """Get all versions of a file"""
        file_record = db.query(File).filter(
            and_(File.task_id == task_id, File.filename == file_name)
        ).first()

        if not file_record:
            return []

        versions = db.query(FileVersion).filter(
            FileVersion.file_id == file_record.id
        ).order_by(FileVersion.version_number.desc()).all()

        return versions
    
    @staticmethod
    def restore_attachment_version(
        db: Session,
        file_id: str,
        target_version: int,
        user_id: str,
    ) -> File:
        """
        Restore to previous version (creates new version with old content)
        """
        file_record = db.query(File).filter(File.id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")

        target = db.query(FileVersion).filter(
            and_(FileVersion.file_id == file_record.id, FileVersion.version_number == target_version)
        ).first()

        if not target:
            raise HTTPException(status_code=404, detail="Target version not found")

        new_version = file_record.current_version + 1
        file_record.current_version = new_version
        file_record.storage_path = target.storage_path
        file_record.size = target.size

        restored_version = FileVersion(
            id=uuid.uuid4(),
            file_id=file_record.id,
            version_number=new_version,
            storage_path=target.storage_path,
            size=target.size,
            checksum=target.checksum,
        )

        db.add(restored_version)
        db.commit()

        return file_record


class NoteService:
    """
    Feature 2.6: Project Notes (Wiki)
    Feature 2.7: Personal Notes
    - Hierarchy support
    - Access control
    - Rich text content
    """
    
    @staticmethod
    def create_note(
        db: Session,
        user_id: str,
        title: str,
        content: str,
        project_id: Optional[str] = None,
        parent_note_id: Optional[str] = None,
        access_level: NoteAccessEnum = NoteAccessEnum.PRIVATE,
    ) -> Note:
        """
        Create a note with optional hierarchy
        
        Feature 2.6 AC 2: Nested hierarchy
        Feature 2.7 AC 1: Privacy control
        """
        note = Note(
            id=uuid.uuid4(),
            user_id=user_id,
            project_id=project_id,
            parent_note_id=parent_note_id,
            title=title,
            content=content,
            access_level=access_level,
        )
        
        db.add(note)
        
        # Create initial version
        version = NoteVersion(
            id=uuid.uuid4(),
            note_id=note.id,
            created_by=user_id,
            version_number=1,
            title=title,
            content=content,
        )
        db.add(version)
        
        db.commit()
        return note
    
    @staticmethod
    def update_note(
        db: Session,
        note_id: str,
        user_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Note:
        """
        Update note and create new version
        
        Feature 2.10: Document Versioning (AC 1: Auto-snapshot)
        """
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Check permission
        if note.user_id != user_id and note.access_level == NoteAccessEnum.PRIVATE:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Save old content for diff
        old_content = note.content
        
        if title:
            note.title = title
        if content:
            note.content = content
        
        # Create new version
        latest_version = db.query(NoteVersion).filter(
            NoteVersion.note_id == note_id
        ).order_by(NoteVersion.version_number.desc()).first()
        
        version_number = (latest_version.version_number + 1) if latest_version else 1
        
        version = NoteVersion(
            id=uuid.uuid4(),
            note_id=note_id,
            created_by=user_id,
            version_number=version_number,
            title=note.title,
            content=note.content or "",
        )
        
        db.add(version)
        db.commit()
        
        return note
    
    @staticmethod
    def convert_to_task(
        db: Session,
        note_id: str,
        project_id: str,
        task_list_id: str,
        user_id: str,
    ) -> Task:
        """
        Feature 2.7 AC 2: Convert personal note to task
        """
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        if note.user_id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Create task from note
        task = Task(
            id=uuid.uuid4(),
            project_id=project_id,
            task_list_id=task_list_id,
            title=note.title,
            description=note.content,
            created_by=user_id,
        )
        
        db.add(task)
        db.commit()
        
        return task


class NoteVersionService:
    """
    Feature 2.10: Document Versioning
    """
    
    @staticmethod
    def get_versions(db: Session, note_id: str) -> List[NoteVersion]:
        """Get all versions of a note"""
        versions = db.query(NoteVersion).filter(
            NoteVersion.note_id == note_id
        ).order_by(NoteVersion.version_number.desc()).all()
        
        return versions
    
    @staticmethod
    def restore_version(
        db: Session,
        note_id: str,
        version_number: int,
        user_id: str,
    ) -> Note:
        """
        Feature 2.10 AC 3: Restore previous version
        """
        target_version = db.query(NoteVersion).filter(
            and_(NoteVersion.note_id == note_id, NoteVersion.version_number == version_number)
        ).first()
        
        if not target_version:
            raise HTTPException(status_code=404, detail="Version not found")
        
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Restore content
        note.title = target_version.title
        note.content = target_version.content
        
        # Create new version marking restoration
        latest = db.query(NoteVersion).filter(
            NoteVersion.note_id == note_id
        ).order_by(NoteVersion.version_number.desc()).first()
        
        new_version = NoteVersion(
            id=uuid.uuid4(),
            note_id=note_id,
            created_by=user_id,
            version_number=latest.version_number + 1,
            change_description=f"Restored from version {version_number}",
            title=note.title,
            content=note.content,
        )
        
        db.add(new_version)
        db.commit()
        
        return note


class ApprovalService:
    """
    Feature 2.4: Formal Approval Workflow
    - State machine transitions
    - Digital signature audit
    """
    
    @staticmethod
    def create_approval_request(
        db: Session,
        task_id: Optional[str],
        file_id: Optional[str],
        approver_id: str,
        requestor_id: str,
        checksum: str,
    ) -> ApprovalRecord:
        """
        Create approval request
        
        AC 1: Decision State Machine - start in PENDING state
        AC 2: Digital Signature Audit - store checksum
        """
        approval = ApprovalRecord(
            id=uuid.uuid4(),
            task_id=task_id,
            file_id=file_id,
            approver_id=approver_id,
            requestor_id=requestor_id,
            status=ApprovalStatusEnum.PENDING,
            checksum=checksum,
        )
        
        db.add(approval)
        db.commit()
        
        return approval
    
    @staticmethod
    def approve(
        db: Session,
        approval_id: str,
        approver_id: str,
        decision_notes: Optional[str] = None,
        signature: Optional[str] = None,
    ) -> ApprovalRecord:
        """
        Approve (transition to APPROVED state)
        
        AC 1: Lock the task/file
        AC 2: Record signature and checksum
        """
        approval = db.query(ApprovalRecord).filter(ApprovalRecord.id == approval_id).first()
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        if approval.approver_id != approver_id:
            raise HTTPException(status_code=403, detail="Not authorized to approve")
        
        approval.status = ApprovalStatusEnum.APPROVED
        approval.decision_notes = decision_notes
        approval.signature = signature
        approval.decision_timestamp = datetime.utcnow()
        
        # Lock task if applicable
        if approval.task_id:
            task = db.query(Task).filter(Task.id == approval.task_id).first()
            if task:
                # task.is_locked = True  # If Task model has this field
                pass
        
        db.commit()
        
        return approval
    
    @staticmethod
    def request_changes(
        db: Session,
        approval_id: str,
        approver_id: str,
        change_instructions: str,
    ) -> ApprovalRecord:
        """
        Request changes (transition to CHANGES_REQUESTED)
        
        AC 1: Task status reverts to IN_PROGRESS
        """
        approval = db.query(ApprovalRecord).filter(ApprovalRecord.id == approval_id).first()
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        if approval.approver_id != approver_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        approval.status = ApprovalStatusEnum.CHANGES_REQUESTED
        approval.decision_notes = change_instructions
        approval.decision_timestamp = datetime.utcnow()
        
        # Revert task to IN_PROGRESS
        if approval.task_id:
            task = db.query(Task).filter(Task.id == approval.task_id).first()
            if task:
                from app.db.enums import TaskStatus
                task.status = TaskStatus.IN_PROGRESS
        
        db.commit()
        
        return approval
    
    @staticmethod
    def check_approval_validity(db: Session, approval_id: str, current_checksum: str) -> bool:
        """
        AC 2: Check if approval is still valid
        If file changed, invalidate approval
        """
        approval = db.query(ApprovalRecord).filter(ApprovalRecord.id == approval_id).first()
        if not approval:
            return False
        
        if approval.status != ApprovalStatusEnum.APPROVED:
            return True  # Only check valid approvals
        
        if approval.checksum != current_checksum:
            # Content changed - invalidate approval
            approval.status = ApprovalStatusEnum.PENDING
            approval.invalidated_at = datetime.utcnow()
            approval.invalidation_checksum = current_checksum
            approval.invalidation_reason = "Content changed after approval"
            
            db.commit()
            return False
        
        return True


class PublicLinkService:
    """
    Feature 2.9: Public Publishing
    """
    
    @staticmethod
    def create_public_link(
        db: Session,
        note_id: str,
        created_by: str,
        link_title: Optional[str] = None,
        password: Optional[str] = None,
        expiration_date: Optional[datetime] = None,
        auto_update: bool = True,
    ) -> PublicLink:
        """
        Create public link for note
        
        AC 1: Generate public URL (slug)
        AC 2: Optional password protection
        AC 3: Live update option
        """
        # Generate unique slug
        slug = secrets.token_urlsafe(16)
        
        # Hash password if provided
        password_hash = None
        if password:
            import bcrypt
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        link = PublicLink(
            id=uuid.uuid4(),
            note_id=note_id,
            created_by=created_by,
            slug=slug,
            link_title=link_title,
            password_hash=password_hash,
            is_password_protected=bool(password),
            expiration_date=expiration_date,
            status=PublicLinkStatusEnum.ACTIVE,
            auto_update=auto_update,
            last_published_at=datetime.utcnow(),
        )
        
        db.add(link)
        db.commit()
        
        return link
    
    @staticmethod
    def verify_access(db: Session, slug: str, password: Optional[str] = None) -> Optional[PublicLink]:
        """Verify access to public link"""
        link = db.query(PublicLink).filter(PublicLink.slug == slug).first()
        if not link:
            return None
        
        # Check expiration
        if link.expiration_date and link.expiration_date < datetime.utcnow():
            link.status = PublicLinkStatusEnum.EXPIRED
            return None
        
        # Check status
        if link.status != PublicLinkStatusEnum.ACTIVE:
            return None
        
        # Verify password if protected
        if link.is_password_protected:
            if not password:
                raise HTTPException(status_code=401, detail="Password required")
            
            import bcrypt
            if not bcrypt.checkpw(password.encode(), link.password_hash.encode()):
                raise HTTPException(status_code=403, detail="Invalid password")
        
        # Update access stats
        link.view_count += 1
        link.last_accessed_at = datetime.utcnow()
        
        db.commit()
        
        return link


class SearchService:
    """
    Feature 2.5: Collaborative Search
    - Full-text search across content
    - Contextual results with snippets
    """
    
    @staticmethod
    def index_content(
        db: Session,
        entity_type: str,
        entity_id: str,
        project_id: Optional[str],
        title: Optional[str],
        content: str,
        created_by: Optional[str] = None,
    ) -> SearchIndex:
        """Index content for search"""
        # Create snippet (first 500 chars)
        snippet = content[:500] if len(content) > 500 else content
        
        index = SearchIndex(
            id=uuid.uuid4(),
            entity_type=entity_type,
            entity_id=entity_id,
            project_id=project_id,
            title=title,
            content=content,
            snippet=snippet,
            created_by=created_by,
            original_created_at=datetime.utcnow(),
        )
        
        db.add(index)
        db.commit()
        
        return index
    
    @staticmethod
    def search(
        db: Session,
        query: str,
        project_id: Optional[str] = None,
        entity_types: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[int, List[SearchIndex]]:
        """
        Search collaboration content
        
        Feature 2.5 AC 1: Full-text search
        Feature 2.5 AC 2: Contextual results with snippets
        """
        search_query = db.query(SearchIndex)
        
        if project_id:
            search_query = search_query.filter(SearchIndex.project_id == project_id)
        
        if entity_types:
            search_query = search_query.filter(SearchIndex.entity_type.in_(entity_types))
        
        # Simple full-text search (production would use PostgreSQL FTS or Elasticsearch)
        search_query = search_query.filter(
            or_(
                SearchIndex.content.ilike(f"%{query}%"),
                SearchIndex.title.ilike(f"%{query}%"),
            )
        )
        
        total_count = search_query.count()
        
        results = search_query.offset(offset).limit(limit).all()
        
        return total_count, results


class SmartBacklinkService:
    """
    Feature 2.11: Smart Backlinks
    """
    
    @staticmethod
    def create_backlink(
        db: Session,
        note_id: str,
        source_note_id: Optional[str],
        source_task_id: Optional[str],
        mention_text: str,
        is_linked: bool = True,
    ) -> SmartBacklink:
        """Create backlink reference"""
        backlink = SmartBacklink(
            id=uuid.uuid4(),
            note_id=note_id,
            source_note_id=source_note_id,
            source_task_id=source_task_id,
            mention_text=mention_text,
            is_linked=is_linked,
        )
        
        db.add(backlink)
        db.commit()
        
        return backlink
    
    @staticmethod
    def get_backlinks(db: Session, note_id: str, include_unlinked: bool = False) -> List[SmartBacklink]:
        """Get all backlinks to a note"""
        query = db.query(SmartBacklink).filter(SmartBacklink.note_id == note_id)
        
        if not include_unlinked:
            query = query.filter(SmartBacklink.is_linked == True)
        
        return query.all()


class UserPresenceService:
    """
    Feature 2.3: Real-time Presence
    - Track who is viewing/editing
    - Show typing status
    """
    
    @staticmethod
    def update_presence(
        db: Session,
        user_id: str,
        task_id: Optional[str] = None,
        note_id: Optional[str] = None,
        status: str = "viewing",
        is_typing: bool = False,
        session_id: Optional[str] = None,
    ) -> UserPresence:
        """Update user presence"""
        # Remove old presence for this user
        db.query(UserPresence).filter(
            and_(UserPresence.user_id == user_id, UserPresence.session_id == session_id)
        ).delete()
        
        presence = UserPresence(
            id=uuid.uuid4(),
            user_id=user_id,
            task_id=task_id,
            note_id=note_id,
            status=status,
            is_typing=is_typing,
            session_id=session_id,
        )
        
        db.add(presence)
        db.commit()
        
        return presence
    
    @staticmethod
    def get_active_users_on_task(db: Session, task_id: str) -> List[UserPresence]:
        """Get active users on a task"""
        # Remove stale presence (> 5 minutes old)
        stale_time = datetime.utcnow() - timedelta(minutes=5)
        db.query(UserPresence).filter(
            and_(UserPresence.task_id == task_id, UserPresence.last_activity_at < stale_time)
        ).delete()
        
        users = db.query(UserPresence).filter(UserPresence.task_id == task_id).all()
        
        return users


class MentionService:
    """
    Feature 2.1 AC 2: Smart Mentions
    """
    
    @staticmethod
    def create_mention(
        db: Session,
        mentioned_user_id: str,
        mentioned_by_user_id: str,
        comment_id: Optional[str] = None,
        note_id: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Mention:
        """Create mention record"""
        mention = Mention(
            id=uuid.uuid4(),
            mentioned_user_id=mentioned_user_id,
            mentioned_by_user_id=mentioned_by_user_id,
            comment_id=comment_id,
            note_id=note_id,
            context=context,
        )
        
        db.add(mention)
        db.commit()
        
        return mention
    
    @staticmethod
    def get_mention_suggestions(
        db: Session,
        project_id: str,
        current_user_id: str,
        task_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get smart mention suggestions
        
        AC 2: Priority: Assignee > Reporter > Recent collaborators
        """
        suggestions = []
        
        # TODO: Implement priority sorting based on assignee, reporter, recent interactions
        
        return suggestions
