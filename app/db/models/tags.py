"""
Entity Models for Functional Module 4 & 15: Tag & Categorization System.
Provides Tag and related models for categorizing projects, tasks, and other entities.
Ref: docs/docs - PronaFlow React&FastAPI/02-Architeture/Entities/Tag.md
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Index, Table, Column, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin
from app.db.enums import TagEntityType

if TYPE_CHECKING:
    from app.db.models.workspaces import Workspace


# ======= Association Tables =======
project_tag_map = Table(
    'project_tag_map',
    Base.metadata,
    Column('project_id', UUID(as_uuid=True), ForeignKey('projects.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True),
)

task_tag_map = Table(
    'task_tag_map',
    Base.metadata,
    Column('task_id', UUID(as_uuid=True), ForeignKey('tasks.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True),
)


# ======= Entity Tables =======

class Tag(Base, TimestampMixin):
    """
    Tag Model - Categorization and classification.
    Manages tags for projects, tasks, and other entities within workspaces.
    Ref: Entities/Tag.md
    """
    __tablename__ = "tags"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for tag"
    )

    # Foreign Key
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to workspace"
    )

    # Tag Properties
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Tag name (Max 50 characters)"
    )

    color_code: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        comment="Hex color code (e.g., '#FF5733')"
    )

    # Entity Type Limit
    entity_type_limit: Mapped[TagEntityType] = mapped_column(
        SQLEnum(TagEntityType),
        default=TagEntityType.ALL,
        nullable=False,
        comment="Entity type limit (TASK / PROJECT / ALL)"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(foreign_keys=[workspace_id])

    # Indexes
    __table_args__ = (
        Index('ix_tags_workspace_id', 'workspace_id'),
        Index('ix_tags_name', 'name'),
    )
