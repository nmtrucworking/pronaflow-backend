"""
Service layer for Help Center & Knowledge Base (Module 15)
"""
from datetime import datetime
from fnmatch import fnmatch
from typing import List, Optional
from uuid import UUID
import logging

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload

from app.models.help_center import (
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
from app.models.tags import Tag
from app.models.admin import FeatureFlag
from app.db.enums import ArticleStatus, ArticleVisibilityScope
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
from app.core.vector_search import vector_search_service

logger = logging.getLogger(__name__)


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

    def get_article(
        self,
        article_id: UUID,
        user_id: Optional[UUID] = None,
        user_roles: Optional[List[str]] = None
    ) -> Optional[Article]:
        """Get article with visibility check"""
        query = (
            self.db.query(Article)
            .options(
                joinedload(Article.versions),
                joinedload(Article.tags),
                joinedload(Article.visibility)
            )
            .filter(Article.id == article_id)
        )
        
        # Apply visibility filter
        query = self._apply_visibility_filter(query, user_id, user_roles or [])
        
        return query.first()

    def get_article_by_slug(self, slug: str) -> Optional[Article]:
        return self.db.query(Article).filter(Article.slug == slug).first()

    def list_articles(
        self,
        status: Optional[str] = None,
        category_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        user_roles: Optional[List[str]] = None
    ) -> List[Article]:
        """List articles with visibility rule enforcement"""
        query = self.db.query(Article).options(joinedload(Article.visibility))
        
        if status:
            try:
                status_enum = ArticleStatus(status)
                query = query.filter(Article.status == status_enum)
            except ValueError:
                query = query.filter(Article.status == status)
        
        if category_id:
            query = query.filter(Article.category_id == category_id)
        
        # Apply visibility filtering
        query = self._apply_visibility_filter(query, user_id, user_roles or [])
        
        return query.order_by(Article.updated_at.desc()).all()
    
    def _apply_visibility_filter(
        self,
        query,
        user_id: Optional[UUID],
        user_roles: List[str]
    ):
        """Apply visibility rules to article query"""
        # Get all visibility rules
        visibility_subquery = self.db.query(ArticleVisibility).subquery()
        
        query = query.outerjoin(
            visibility_subquery,
            Article.id == visibility_subquery.c.article_id
        )
        
        # Build visibility conditions
        conditions = []
        
        # 1. No visibility rule = PUBLIC by default
        conditions.append(visibility_subquery.c.article_id.is_(None))
        
        # 2. Explicitly PUBLIC articles
        conditions.append(visibility_subquery.c.access_scope == ArticleVisibilityScope.PUBLIC)
        
        # 3. INTERNAL articles (user must be authenticated)
        if user_id:
            conditions.append(visibility_subquery.c.access_scope == ArticleVisibilityScope.INTERNAL)
            
            # 4. ROLE_BASED articles (check user roles)
            if user_roles:
                # Check if any user role matches allowed_roles
                role_based_condition = and_(
                    visibility_subquery.c.access_scope == ArticleVisibilityScope.ROLE_BASED,
                    or_(
                        visibility_subquery.c.allowed_roles.is_(None),
                        # JSONB contains check - any user role in allowed_roles
                        *[visibility_subquery.c.allowed_roles.op('?')(role) for role in user_roles]
                    )
                )
                conditions.append(role_based_condition)
        
        return query.filter(or_(*conditions))

    def update_article(
        self,
        article_id: UUID,
        data: ArticleUpdate,
        auto_publish: bool = False
    ) -> Article:
        """Update article with feature flag support for auto-publish"""
        article = self.get_article(article_id, user_id=None, user_roles=[])
        
        for field, value in data.model_dump(exclude_unset=True, exclude={"tag_ids"}).items():
            setattr(article, field, value)

        if data.tag_ids is not None:
            tags = self.db.query(Tag).filter(Tag.id.in_(data.tag_ids)).all()
            article.tags = tags
        
        # Check auto-publish feature flag
        if auto_publish:
            flag = self.db.query(FeatureFlag).filter(
                FeatureFlag.key == "help_center_auto_publish"
            ).first()
            
            if flag and flag.is_enabled:
                article.status = ArticleStatus.PUBLISHED
                logger.info(f"Auto-publishing article {article_id} via feature flag")

        if article.status == ArticleStatus.PUBLISHED and article.published_at is None:
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
    """Search for articles using keyword + semantic vector search"""

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        query: SearchQuery,
        use_semantic: bool = True,
        user_id: Optional[UUID] = None,
        user_roles: Optional[List[str]] = None
    ) -> List[ArticleSearchIndex]:
        """Hybrid search: keyword + semantic similarity"""
        
        # Try semantic search first if enabled and available
        if use_semantic and vector_search_service.is_available():
            try:
                return self._semantic_search(query, user_id, user_roles)
            except Exception as e:
                logger.warning(f"Semantic search failed, falling back to keyword: {e}")
        
        # Keyword search fallback
        return self._keyword_search(query, user_id, user_roles)
    
    def _keyword_search(
        self,
        query: SearchQuery,
        user_id: Optional[UUID],
        user_roles: Optional[List[str]]
    ) -> List[ArticleSearchIndex]:
        """Traditional keyword-based search"""
        q = f"%{query.query.lower()}%"
        
        search_query = (
            self.db.query(ArticleSearchIndex)
            .join(Article)
            .filter(Article.status == ArticleStatus.PUBLISHED)
            .filter(
                or_(
                    func.lower(ArticleSearchIndex.keywords).like(q),
                    func.lower(Article.title).like(q),
                )
            )
        )
        
        # Apply visibility filtering
        article_service = ArticleService(self.db)
        search_query = article_service._apply_visibility_filter(
            search_query.join(Article, ArticleSearchIndex.article_id == Article.id),
            user_id,
            user_roles or []
        )
        
        return search_query.limit(query.limit).all()
    
    def _semantic_search(
        self,
        query: SearchQuery,
        user_id: Optional[UUID],
        user_roles: Optional[List[str]]
    ) -> List[ArticleSearchIndex]:
        """Semantic similarity search using embeddings"""
        # Generate query embedding
        query_embedding = vector_search_service.generate_embedding(query.query)
        
        # Get all indexed articles with embeddings
        indexed_articles = (
            self.db.query(ArticleSearchIndex)
            .join(Article)
            .filter(Article.status == ArticleStatus.PUBLISHED)
            .filter(ArticleSearchIndex.embedding_vector.isnot(None))
            .all()
        )
        
        if not indexed_articles:
            # Fallback to keyword search
            return self._keyword_search(query, user_id, user_roles)
        
        # Calculate similarities
        article_embeddings = [
            (str(idx.article_id), idx.embedding_vector)
            for idx in indexed_articles
            if idx.embedding_vector
        ]
        
        similar_articles = vector_search_service.search_similar(
            query_embedding,
            article_embeddings,
            limit=query.limit,
            threshold=0.3  # Minimum similarity score
        )
        
        # Retrieve full index objects in similarity order
        article_id_map = {str(idx.article_id): idx for idx in indexed_articles}
        results = []
        
        for article_id_str, score in similar_articles:
            if article_id_str in article_id_map:
                idx = article_id_map[article_id_str]
                # Check visibility
                article = idx.article
                if self._check_visibility(article, user_id, user_roles or []):
                    results.append(idx)
        
        return results[:query.limit]
    
    def _check_visibility(
        self,
        article: Article,
        user_id: Optional[UUID],
        user_roles: List[str]
    ) -> bool:
        """Check if user can access article based on visibility rules"""
        if not article.visibility:
            return True  # No rule = public
        
        scope = article.visibility.access_scope
        
        if scope == ArticleVisibilityScope.PUBLIC:
            return True
        
        if scope == ArticleVisibilityScope.INTERNAL:
            return user_id is not None
        
        if scope == ArticleVisibilityScope.ROLE_BASED:
            if not user_id:
                return False
            
            allowed_roles = article.visibility.allowed_roles or {}
            if not allowed_roles:
                return True  # No role restriction
            
            # Check if any user role matches
            return any(role in allowed_roles for role in user_roles)
        
        return False

    def update_index(
        self,
        article_id: UUID,
        keywords: Optional[str],
        snippet: Optional[str],
        content: Optional[str] = None
    ) -> ArticleSearchIndex:
        """Update search index with keywords and semantic embedding"""
        index = self.db.query(ArticleSearchIndex).filter(
            ArticleSearchIndex.article_id == article_id
        ).first()
        
        # Generate embedding if content provided
        embedding_vector = None
        if content and vector_search_service.is_available():
            try:
                embedding_text = content[:2000]  # Limit for embedding API
                embedding_vector = vector_search_service.generate_embedding(embedding_text)
            except Exception as e:
                logger.warning(f"Failed to generate embedding for article {article_id}: {e}")
        
        if index:
            index.keywords = keywords
            index.snippet = snippet
            if embedding_vector:
                index.embedding_vector = embedding_vector
            index.last_indexed = datetime.utcnow()
        else:
            index = ArticleSearchIndex(
                article_id=article_id,
                keywords=keywords,
                snippet=snippet,
                embedding_vector=embedding_vector,
                last_indexed=datetime.utcnow(),
            )
            self.db.add(index)
        
        self.db.commit()
        self.db.refresh(index)
        return index
