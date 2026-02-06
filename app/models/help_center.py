"""
Entity Models for Functional Module 15: Help Center & Knowledge Base
Provides Article, ArticleVersion, ArticleTranslation, Category, RouteMapping,
ArticleFeedback, FailedSearch, ArticleVisibility, and ArticleSearchIndex.
Ref: docs/01-Requirements/Functional-Modules/15 - Help Center and Knowledge Base.md
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import (
    String, Text, Integer, Boolean, DateTime, ForeignKey, Index, Table, Column, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin
from app.db.enums import ArticleStatus, ArticleVisibilityScope

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.tags import Tag


# ======= Association Tables =======

article_tag_map = Table(
    "article_tag_map",
    Base.metadata,
    Column("article_id", UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


# ======= Entity Tables =======

class Category(Base, TimestampMixin):
    """
    Category Model - Hierarchical taxonomy for articles.
    """
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"))
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    articles = relationship("Article", back_populates="category")

    __table_args__ = (
        Index("ix_categories_parent", "parent_id"),
        Index("ix_categories_active", "is_active"),
    )


class Article(Base, TimestampMixin):
    """
    Article core entity.
    """
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)

    status: Mapped[ArticleStatus] = mapped_column(
        SQLEnum(ArticleStatus), default=ArticleStatus.DRAFT, nullable=False, index=True
    )

    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"))
    author_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    category = relationship("Category", back_populates="articles")
    versions = relationship("ArticleVersion", back_populates="article", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=article_tag_map, backref="articles")
    route_mappings = relationship("RouteMapping", back_populates="article", cascade="all, delete-orphan")
    visibility = relationship("ArticleVisibility", back_populates="article", uselist=False, cascade="all, delete-orphan")
    feedback = relationship("ArticleFeedback", back_populates="article", cascade="all, delete-orphan")
    search_index = relationship("ArticleSearchIndex", back_populates="article", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_articles_status", "status"),
        Index("ix_articles_category", "category_id"),
    )


class ArticleVersion(Base, TimestampMixin):
    """
    Article versioning for CMS.
    """
    __tablename__ = "article_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"))

    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    version_label: Mapped[Optional[str]] = mapped_column(String(50))

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_raw: Mapped[str] = mapped_column(Text, nullable=False)
    content_rendered: Mapped[Optional[str]] = mapped_column(Text)
    changelog_summary: Mapped[Optional[str]] = mapped_column(Text)

    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    article = relationship("Article", back_populates="versions")
    translations = relationship("ArticleTranslation", back_populates="version", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_article_versions_article", "article_id"),
        Index("ix_article_versions_current", "is_current"),
    )


class ArticleTranslation(Base, TimestampMixin):
    """
    Localization for article versions.
    """
    __tablename__ = "article_translations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("article_versions.id", ondelete="CASCADE"))

    locale: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # e.g., vi-VN, en-US
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_localized: Mapped[str] = mapped_column(Text, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    version = relationship("ArticleVersion", back_populates="translations")

    __table_args__ = (
        Index("ix_article_translations_version", "version_id"),
        Index("ix_article_translations_locale", "locale"),
    )


class RouteMapping(Base, TimestampMixin):
    """
    Map UI route to suggested articles for contextual help widget.
    """
    __tablename__ = "route_mappings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"))

    route_pattern: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    element_selector: Mapped[Optional[str]] = mapped_column(String(255))
    context_description: Mapped[Optional[str]] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    article = relationship("Article", back_populates="route_mappings")

    __table_args__ = (
        Index("ix_route_mappings_pattern", "route_pattern"),
        Index("ix_route_mappings_priority", "priority"),
        Index("ix_route_mappings_active", "is_active"),
    )


class ArticleVisibility(Base, TimestampMixin):
    """
    Visibility scope for articles: Public, Internal, Role-based.
    """
    __tablename__ = "article_visibility"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), unique=True)

    access_scope: Mapped[ArticleVisibilityScope] = mapped_column(
        SQLEnum(ArticleVisibilityScope), default=ArticleVisibilityScope.PUBLIC, nullable=False
    )
    allowed_roles: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Relationships
    article = relationship("Article", back_populates="visibility")

    __table_args__ = (
        Index("ix_article_visibility_scope", "access_scope"),
    )


class ArticleFeedback(Base, TimestampMixin):
    """
    Helpfulness feedback for articles.
    """
    __tablename__ = "article_feedback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))

    is_helpful: Mapped[bool] = mapped_column(Boolean, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    route_path: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships
    article = relationship("Article", back_populates="feedback")

    __table_args__ = (
        Index("ix_article_feedback_article", "article_id"),
        Index("ix_article_feedback_user", "user_id"),
    )


class FailedSearch(Base, TimestampMixin):
    """
    Record failed searches for content gap analysis.
    """
    __tablename__ = "failed_searches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))

    query_text: Mapped[str] = mapped_column(String(500), nullable=False)
    locale: Mapped[Optional[str]] = mapped_column(String(10))
    route_path: Mapped[Optional[str]] = mapped_column(String(255))
    searched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_failed_searches_query", "query_text"),
        Index("ix_failed_searches_searched_at", "searched_at"),
    )


class ArticleSearchIndex(Base, TimestampMixin):
    """
    Search index for help center articles (keyword + semantic embedding).
    """
    __tablename__ = "article_search_indexes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), unique=True)

    keywords: Mapped[Optional[str]] = mapped_column(Text)
    embedding_vector: Mapped[Optional[List[float]]] = mapped_column(JSONB)
    snippet: Mapped[Optional[str]] = mapped_column(String(500))
    last_indexed: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    article = relationship("Article", back_populates="search_index")

    __table_args__ = (
        Index("ix_article_search_indexes_article", "article_id"),
    )
