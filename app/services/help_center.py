"""
Service layer for Help Center & Knowledge Base (Module 15)
"""
from datetime import datetime
from fnmatch import fnmatch
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload

from app.db.models.help_center import (
    Article,
    ArticleVersion,
    ArticleTranslation,
    Category,
    RouteMapping,
    ArticleFeedback,
    FailedSearch,
    ArticleVisibility,
    ArticleSearchIndex,
)
from app.db.models.tags import Tag
from app.db.enums import ArticleStatus
from app.schemas.help_center import (
    CategoryCreate,
    CategoryUpdate,
    ArticleCreate,
    ArticleUpdate,
    ArticleVersionCreate,
    ArticleTranslationCreate,
    RouteMappingCreate,
    ArticleVisibilityCreate,
    ArticleFeedbackCreate,
    FailedSearchCreate,
    SearchQuery,
)


class CategoryService:
    """Manage article categories"""

    def __init__(self, db: Session):
        self.db = db

    def create_category(self, data: CategoryCreate) -> Category:
        category = Category(**data.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_category(self, category_id: UUID) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def list_categories(self, is_active: Optional[bool] = None) -> List[Category]:
        query = self.db.query(Category)
        if is_active is not None:
            query = query.filter(Category.is_active == is_active)
        return query.order_by(Category.display_order.asc()).all()

    def update_category(self, category_id: UUID, data: CategoryUpdate) -> Category:
        category = self.get_category(category_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        self.db.commit()
        self.db.refresh(category)
        return category


class ArticleService:
    """Manage articles and versions"""

    def __init__(self, db: Session):
        self.db = db

    def create_article(self, data: ArticleCreate, author_id: Optional[UUID]) -> Article:
        article = Article(
            slug=data.slug,
            title=data.title,
            summary=data.summary,
            category_id=data.category_id,
            status=data.status,
            is_featured=data.is_featured,
            author_id=author_id,
        )

        if data.tag_ids:
            tags = self.db.query(Tag).filter(Tag.id.in_(data.tag_ids)).all()
            article.tags = tags

        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def get_article(self, article_id: UUID) -> Optional[Article]:
        return (
            self.db.query(Article)
            .options(joinedload(Article.versions), joinedload(Article.tags))
            .filter(Article.id == article_id)
            .first()
        )

    def get_article_by_slug(self, slug: str) -> Optional[Article]:
        return self.db.query(Article).filter(Article.slug == slug).first()

    def list_articles(self, status: Optional[str] = None, category_id: Optional[UUID] = None) -> List[Article]:
        query = self.db.query(Article)
        if status:
            try:
                status_enum = ArticleStatus(status)
                query = query.filter(Article.status == status_enum)
            except ValueError:
                query = query.filter(Article.status == status)
        if category_id:
            query = query.filter(Article.category_id == category_id)
        return query.order_by(Article.updated_at.desc()).all()

    def update_article(self, article_id: UUID, data: ArticleUpdate) -> Article:
        article = self.get_article(article_id)
        for field, value in data.model_dump(exclude_unset=True, exclude={"tag_ids"}).items():
            setattr(article, field, value)

        if data.tag_ids is not None:
            tags = self.db.query(Tag).filter(Tag.id.in_(data.tag_ids)).all()
            article.tags = tags

        if data.status == ArticleStatus.PUBLISHED and article.published_at is None:
            article.published_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(article)
        return article

    def add_version(self, data: ArticleVersionCreate, created_by_id: Optional[UUID]) -> ArticleVersion:
        if data.is_current:
            self.db.query(ArticleVersion).filter(ArticleVersion.article_id == data.article_id).update(
                {"is_current": False}
            )

        version = ArticleVersion(
            article_id=data.article_id,
            version_number=data.version_number,
            version_label=data.version_label,
            title=data.title,
            content_raw=data.content_raw,
            content_rendered=data.content_rendered,
            changelog_summary=data.changelog_summary,
            is_current=data.is_current,
            created_by_id=created_by_id,
        )

        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def get_current_version(self, article_id: UUID) -> Optional[ArticleVersion]:
        return (
            self.db.query(ArticleVersion)
            .filter(ArticleVersion.article_id == article_id, ArticleVersion.is_current == True)
            .first()
        )

    def add_translation(self, data: ArticleTranslationCreate) -> ArticleTranslation:
        translation = ArticleTranslation(**data.model_dump())
        self.db.add(translation)
        self.db.commit()
        self.db.refresh(translation)
        return translation

    def get_reader_content(self, article_id: UUID, locale: Optional[str] = None) -> Optional[ArticleTranslation]:
        version = self.get_current_version(article_id)
        if not version:
            return None

        query = self.db.query(ArticleTranslation).filter(ArticleTranslation.version_id == version.id)
        if locale:
            query = query.filter(ArticleTranslation.locale == locale)
        translation = query.order_by(ArticleTranslation.is_default.desc()).first()
        return translation


class RouteMappingService:
    """Manage contextual help route mappings"""

    def __init__(self, db: Session):
        self.db = db

    def create_mapping(self, data: RouteMappingCreate) -> RouteMapping:
        mapping = RouteMapping(**data.model_dump())
        self.db.add(mapping)
        self.db.commit()
        self.db.refresh(mapping)
        return mapping

    def list_mappings(self, is_active: Optional[bool] = None) -> List[RouteMapping]:
        query = self.db.query(RouteMapping)
        if is_active is not None:
            query = query.filter(RouteMapping.is_active == is_active)
        return query.order_by(RouteMapping.priority.desc()).all()

    def get_contextual_suggestions(self, route: str, limit: int = 5) -> List[RouteMapping]:
        mappings = self.db.query(RouteMapping).filter(RouteMapping.is_active == True).all()
        matched = []
        for mapping in mappings:
            pattern = mapping.route_pattern
            if fnmatch(route.lower(), pattern.lower()):
                matched.append(mapping)
        matched.sort(key=lambda m: m.priority, reverse=True)
        return matched[:limit]


class VisibilityService:
    """Manage article visibility"""

    def __init__(self, db: Session):
        self.db = db

    def set_visibility(self, data: ArticleVisibilityCreate) -> ArticleVisibility:
        visibility = self.db.query(ArticleVisibility).filter(ArticleVisibility.article_id == data.article_id).first()
        if visibility:
            visibility.access_scope = data.access_scope
            visibility.allowed_roles = data.allowed_roles
        else:
            visibility = ArticleVisibility(**data.model_dump())
            self.db.add(visibility)
        self.db.commit()
        self.db.refresh(visibility)
        return visibility


class FeedbackService:
    """Manage article feedback"""

    def __init__(self, db: Session):
        self.db = db

    def submit_feedback(self, data: ArticleFeedbackCreate, user_id: Optional[UUID]) -> ArticleFeedback:
        feedback = ArticleFeedback(
            article_id=data.article_id,
            user_id=user_id,
            is_helpful=data.is_helpful,
            comment=data.comment,
            route_path=data.route_path,
            submitted_at=datetime.utcnow(),
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback


class FailedSearchService:
    """Track failed searches"""

    def __init__(self, db: Session):
        self.db = db

    def record_failed_search(self, data: FailedSearchCreate, user_id: Optional[UUID]) -> FailedSearch:
        record = FailedSearch(
            user_id=user_id,
            query_text=data.query_text,
            locale=data.locale,
            route_path=data.route_path,
            searched_at=datetime.utcnow(),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record


class SearchService:
    """Search for articles using keyword + semantic index (placeholder)"""

    def __init__(self, db: Session):
        self.db = db

    def search(self, query: SearchQuery) -> List[ArticleSearchIndex]:
        q = f"%{query.query.lower()}%"
        return (
            self.db.query(ArticleSearchIndex)
            .join(Article)
            .filter(Article.status == ArticleStatus.PUBLISHED)
            .filter(
                or_(
                    func.lower(ArticleSearchIndex.keywords).like(q),
                    func.lower(Article.title).like(q),
                )
            )
            .limit(query.limit)
            .all()
        )

    def update_index(self, article_id: UUID, keywords: Optional[str], snippet: Optional[str]) -> ArticleSearchIndex:
        index = self.db.query(ArticleSearchIndex).filter(ArticleSearchIndex.article_id == article_id).first()
        if index:
            index.keywords = keywords
            index.snippet = snippet
            index.last_indexed = datetime.utcnow()
        else:
            index = ArticleSearchIndex(
                article_id=article_id,
                keywords=keywords,
                snippet=snippet,
                last_indexed=datetime.utcnow(),
            )
            self.db.add(index)
        self.db.commit()
        self.db.refresh(index)
        return index
