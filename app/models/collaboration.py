"""
Module 6: Unified Collaboration Hub - Database Models

This module contains all database models for collaboration features including:
- Contextual comments and threaded discussions
- Digital asset management with file versioning
- Project and personal notes with hierarchy
- Formal approval workflows
- Real-time presence tracking
- Collaborative search and smart backlinks
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin
from app.db.enums import ApprovalStatusEnum, NoteAccessEnum, PublicLinkStatusEnum


class Note(Base, TimestampMixin):
    """
    Project and personal notes with hierarchy
    
    Feature 2.6: Project Notes (Wiki)
    Feature 2.7: Personal Notes
    - Rich text content
    - Nested hierarchy (parent-child)
    - Access control (public, private, project)
    """
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # Hierarchy (Feature 2.6 AC 2: Nested structure)
    parent_note_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Access control (Feature 2.7 AC 1: Privacy, Feature 2.6 for project notes)
    access_level: Mapped[NoteAccessEnum] = mapped_column(
        SQLEnum(NoteAccessEnum), default=NoteAccessEnum.PRIVATE, nullable=False
    )

    # Template support (Feature 2.8: Note Templates)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    template_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    template_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    template_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Hierarchy tracking
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Statistics
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="notes", foreign_keys=[project_id])
    user = relationship("User", foreign_keys=[user_id])
    children = relationship("Note", back_populates="parent", remote_side=[id])
    parent = relationship("Note", back_populates="children", remote_side=[parent_note_id])
    versions = relationship("NoteVersion", back_populates="note", cascade="all, delete-orphan")
    public_links = relationship("PublicLink", back_populates="note", cascade="all, delete-orphan")
    backlinks = relationship("SmartBacklink", back_populates="note", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_notes_project_created", "project_id", "created_at"),
        Index("ix_notes_project_title", "project_id", "title"),
        Index("ix_notes_user_created", "user_id", "created_at"),
        Index("ix_notes_access_level", "access_level"),
        Index("ix_notes_is_template", "is_template"),
    )


class NoteVersion(Base, TimestampMixin):
    """
    Document versioning system
    
    Feature 2.10: Document Versioning
    - Auto-snapshots on save
    - Diff tracking (added/removed content)
    - Restore capability
    """
    __tablename__ = "note_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # Version information (Feature 2.10 AC 1: Auto-Snapshot)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    change_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Content snapshot
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Diff information (Feature 2.10 AC 2: Diff View)
    added_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    removed_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    note = relationship("Note", back_populates="versions", foreign_keys=[note_id])
    user = relationship("User", foreign_keys=[created_by])

    __table_args__ = (
        UniqueConstraint("note_id", "version_number", name="uq_note_version_number"),
        Index("ix_note_versions_created", "created_at"),
    )


class SmartBacklink(Base, TimestampMixin):
    """
    Smart backlinks system
    
    Feature 2.11: Smart Backlinks
    - Track references to this note from other notes/tasks
    - Detect unlinked mentions for suggestion
    """
    __tablename__ = "smart_backlinks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # What references this note
    source_note_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=True
    )
    source_task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True
    )

    # Mention details
    mention_text: Mapped[str] = mapped_column(String(255), nullable=False)
    is_linked: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    note = relationship("Note", back_populates="backlinks", foreign_keys=[note_id])
    source_note = relationship("Note", foreign_keys=[source_note_id])
    source_task = relationship("Task", foreign_keys=[source_task_id])

    __table_args__ = (
        Index("ix_smart_backlinks_note", "note_id"),
        Index("ix_smart_backlinks_source_note", "source_note_id"),
    )


class PublicLink(Base, TimestampMixin):
    """
    Public publishing for notes
    
    Feature 2.9: Public Publishing
    - Generate public URL for read-only access
    - Password protection (optional)
    - Expiration dates
    - Live updates to published content
    """
    __tablename__ = "public_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # Link configuration (Feature 2.9 AC 1: Generate Public Link)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    link_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Access control (Feature 2.9 AC 2: Access Control)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_password_protected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expiration_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Status
    status: Mapped[PublicLinkStatusEnum] = mapped_column(
        SQLEnum(PublicLinkStatusEnum), default=PublicLinkStatusEnum.ACTIVE, nullable=False
    )
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Auto-update setting (Feature 2.9 AC 3: Live Update)
    auto_update: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    note = relationship("Note", back_populates="public_links", foreign_keys=[note_id])
    user = relationship("User", foreign_keys=[created_by])

    __table_args__ = (
        Index("ix_public_links_note", "note_id"),
        Index("ix_public_links_status", "status"),
        Index("ix_public_links_expiration", "expiration_date"),
    )


class Mention(Base, TimestampMixin):
    """
    Track @mentions in comments and notes
    
    Feature 2.1 AC 2: Smart Mentions
    - Trigger notifications
    - Track mention frequency
    """
    __tablename__ = "mentions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentioned_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mentioned_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Mention context
    comment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    note_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=True
    )

    # Mention reason (for filtering suggestions)
    mention_priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    mentioned_user = relationship("User", foreign_keys=[mentioned_user_id])
    mentioned_by_user = relationship("User", foreign_keys=[mentioned_by_user_id])
    comment = relationship("Comment", foreign_keys=[comment_id])
    note = relationship("Note", foreign_keys=[note_id])

    __table_args__ = (
        Index("ix_mentions_mentioned_user", "mentioned_user_id"),
        Index("ix_mentions_mentioned_by_user", "mentioned_by_user_id"),
        Index("ix_mentions_comment", "comment_id"),
    )


class UserPresence(Base, TimestampMixin):
    """
    Real-time presence tracking
    
    Feature 2.3: Real-time Presence
    - Track who is viewing/editing a task or note
    - Show typing status
    """
    __tablename__ = "user_presence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Presence context
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True
    )
    note_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Presence status
    status: Mapped[str] = mapped_column(String(50), default="viewing", nullable=False)
    is_typing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timing
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    task = relationship("Task", foreign_keys=[task_id])
    note = relationship("Note", foreign_keys=[note_id])

    __table_args__ = (
        Index("ix_user_presence_task", "task_id"),
        Index("ix_user_presence_note", "note_id"),
        Index("ix_user_presence_user", "user_id"),
    )


class ApprovalRecord(Base, TimestampMixin):
    """
    Formal approval workflow
    
    Feature 2.4: Formal Approval Workflow
    - Decision state machine (Pending → Approved/Changes Requested)
    - Digital signature audit trail
    - File/Task approval with locking
    """
    __tablename__ = "approval_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Approval context (can approve tasks or files)
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True
    )
    file_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=True, index=True
    )

    approver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    requestor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )

    # Decision (Feature 2.4 AC 1: Decision State Machine)
    status: Mapped[ApprovalStatusEnum] = mapped_column(
        SQLEnum(ApprovalStatusEnum), default=ApprovalStatusEnum.PENDING, nullable=False
    )
    decision_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decision_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Digital signature audit (Feature 2.4 AC 2: Digital Signature Audit)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    signature: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Audit trail
    invalidation_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    invalidated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    invalidation_checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    task = relationship("Task", back_populates="approvals", foreign_keys=[task_id])
    file = relationship("File", back_populates="approvals", foreign_keys=[file_id])
    approver = relationship("User", foreign_keys=[approver_id])
    requestor = relationship("User", foreign_keys=[requestor_id])

    __table_args__ = (
        Index("ix_approval_records_task", "task_id"),
        Index("ix_approval_records_file", "file_id"),
        Index("ix_approval_records_approver", "approver_id"),
        Index("ix_approval_records_status", "status"),
    )


class SearchIndex(Base, TimestampMixin):
    """
    Search index for collaboration content
    
    Feature 2.5: Collaborative Search
    - Full-text search across comments, notes, files
    - Contextual result highlighting
    """
    __tablename__ = "search_indexes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Content type
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Project context for permissions
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True
    )

    # Searchable content
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Snippet for display
    snippet: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Metadata
    url_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    original_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("Project", foreign_keys=[project_id])

    __table_args__ = (
        Index("ix_search_indexes_entity", "entity_type", "entity_id"),
        Index("ix_search_indexes_project", "project_id"),
    )


class CollaborationNotification(Base, TimestampMixin):
    """
    Track collaboration notifications
    
    Integration point with Module 7 (Event-Driven Notification System)
    - Mentions
    - Approvals
    - Comments on tasks
    - Note sharing
    """
    __tablename__ = "collaboration_notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Notification trigger
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Related entities
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True
    )
    note_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=True
    )
    comment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    triggered_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # Notification content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    recipient = relationship("User", foreign_keys=[recipient_user_id])
    triggered_by = relationship("User", foreign_keys=[triggered_by_user_id])
    task = relationship("Task", foreign_keys=[task_id])
    note = relationship("Note", foreign_keys=[note_id])
    comment = relationship("Comment", foreign_keys=[comment_id])

    __table_args__ = (
        Index("ix_collaboration_notifications_recipient", "recipient_user_id"),
        Index("ix_collaboration_notifications_is_read", "is_read"),
        Index("ix_collaboration_notifications_created", "created_at"),
    )


# Update Task model to include collaboration relationships
# These backrefs are used in the relationships above
