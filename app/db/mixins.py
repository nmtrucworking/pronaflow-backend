"""
Reusable SQLAlchemy model mixins for common functionality.
Provides timestamp tracking, audit logging, and soft delete functionality.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID


class UUIDPrimaryKeyMixin:
    """
    Mixin that provides a UUID primary key column named `id`.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Primary key UUID"
    )


class TimestampMixin:
    """
    Mixin that automatically tracks record creation and modification timestamps.
    
    Provides:
    - created_at: Automatically set to current time on insert
    - updated_at: Automatically set to current time on insert/update
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the record was created"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the record was last updated"
    )


class AuditMixin(TimestampMixin):
    """
    Mixin for audit trail tracking with timestamps and user tracking.
    
    Extends TimestampMixin and adds:
    - created_by: UUID reference to the user who created the record
    
    Note: Uses @declared_attr to ensure proper inheritance behavior
    """

    @declared_attr
    def created_by(cls) -> Mapped[Optional[uuid.UUID]]:
        """Reference to the user who created this record"""
        return mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            comment="UUID of the user who created the record"
        )


class SoftDeleteMixin:
    """
    Mixin that implements soft delete functionality.
    Records are marked as deleted but not physically removed from the database.
    
    Provides:
    - is_deleted: Boolean flag indicating soft deletion status
    - deleted_at: Timestamp when the record was soft deleted
    - soft_delete(): Helper method to mark record as deleted
    - restore(): Helper method to restore a soft-deleted record
    """
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Flag indicating soft deletion status"
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when the record was soft deleted"
    )

    def soft_delete(self) -> None:
        """Mark this record as deleted without removing it from the database."""
        self.is_deleted = True
        self.deleted_at = datetime.now(datetime.UTC)

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
