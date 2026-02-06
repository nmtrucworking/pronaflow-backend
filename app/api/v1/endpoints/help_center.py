"""
API endpoints for Help Center & Knowledge Base (Module 15)
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.models.workspaces import WorkspaceMember
from app.db.enums import WorkspaceRole
from app.services.help_center import (
    CategoryService,
    ArticleService,
    RouteMappingService,
    VisibilityService,
    FeedbackService,
    FailedSearchService,
    SearchService,
)
from app.core.background_tasks import IndexingTask, NotificationTask
from app.schemas.help_center import (
    CategoryResponse, CategoryCreate, CategoryUpdate,
    ArticleResponse, ArticleCreate, ArticleUpdate,
    ArticleVersionResponse, ArticleVersionCreate,
    ArticleTranslationResponse, ArticleTranslationCreate,
    RouteMappingResponse, RouteMappingCreate,
    ArticleVisibilityResponse, ArticleVisibilityCreate,
    ArticleFeedbackResponse, ArticleFeedbackCreate,
    FailedSearchResponse, FailedSearchCreate,
    SearchResponse, SearchResult, SearchQuery,
    ContextualHelpResponse, ContextualSuggestion,
)

router = APIRouter(prefix="/help-center", tags=["Help Center & Knowledge Base"])


# ======= Category Endpoints =======

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db)
    return service.create_category(data)


@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db)
    return service.list_categories(is_active)


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db)
    category = service.update_category(category_id, data)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


# ======= Article Endpoints =======

@router.post("/articles", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ArticleService(db)
    return service.create_article(data, current_user.id)


@router.get("/articles", response_model=List[ArticleResponse])
def list_articles(
    status: Optional[str] = Query(None),
    category_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List articles with visibility filtering based on user context"""
    service = ArticleService(db)
    
    # Get user roles from workspace memberships
    user_roles = (
        db.query(WorkspaceMember.role)
        .filter(WorkspaceMember.user_id == current_user.id)
        .distinct()
        .all()
    )
    role_names = [role[0].value if isinstance(role[0], WorkspaceRole) else role[0] for role in user_roles]
    
    return service.list_articles(
        status=status,
        category_id=category_id,
        user_id=current_user.id,
        user_roles=role_names
    )


@router.get("/articles/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get article with visibility rule enforcement"""
    service = ArticleService(db)
    
    # Get user roles
    user_roles = (
        db.query(WorkspaceMember.role)
        .filter(WorkspaceMember.user_id == current_user.id)
        .distinct()
        .all()
    )
    role_names = [role[0].value if isinstance(role[0], WorkspaceRole) else role[0] for role in user_roles]
    
    article = service.get_article(
        article_id,
        user_id=current_user.id,
        user_roles=role_names
    )
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found or access denied"
        )
    return article


@router.patch("/articles/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: UUID,
    data: ArticleUpdate,
    auto_publish: bool = Query(False, description="Trigger auto-publish if feature flag enabled"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update article with feature flag support for auto-publish and notifications"""
    service = ArticleService(db)
    article = service.update_article(article_id, data, auto_publish=auto_publish)
    
    # Queue notification if article was published
    if article.status.value == "published" and background_tasks:
        background_tasks.add_task(
            NotificationTask.notify_article_published,
            article.id,
            article.title,
            db
        )
    
    return article


@router.post("/articles/{article_id}/versions", response_model=ArticleVersionResponse, status_code=status.HTTP_201_CREATED)
def create_article_version(
    article_id: UUID,
    data: ArticleVersionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new article version with background indexing (<= 5 min SLA)"""
    service = ArticleService(db)
    data.article_id = article_id
    version = service.add_version(data, current_user.id)

    # Queue background indexing task with SLA tracking
    background_tasks.add_task(
        IndexingTask.index_article,
        article_id=article_id,
        title=data.title,
        content=data.content_raw,
        db=db
    )

    return version


@router.post("/versions/{version_id}/translations", response_model=ArticleTranslationResponse, status_code=status.HTTP_201_CREATED)
def create_translation(
    version_id: UUID,
    data: ArticleTranslationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ArticleService(db)
    data.version_id = version_id
    return service.add_translation(data)


@router.get("/articles/{article_id}/reader", response_model=ArticleTranslationResponse)
def get_reader_content(
    article_id: UUID,
    locale: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ArticleService(db)
    translation = service.get_reader_content(article_id, locale)
    if not translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    return translation


# ======= Route Mapping Endpoints =======

@router.post("/route-mappings", response_model=RouteMappingResponse, status_code=status.HTTP_201_CREATED)
def create_route_mapping(
    data: RouteMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RouteMappingService(db)
    return service.create_mapping(data)


@router.get("/route-mappings", response_model=List[RouteMappingResponse])
def list_route_mappings(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RouteMappingService(db)
    return service.list_mappings(is_active)


@router.get("/contextual", response_model=ContextualHelpResponse)
def get_contextual_help(
    route: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RouteMappingService(db)
    mappings = service.get_contextual_suggestions(route, limit)
    suggestions = [
        ContextualSuggestion(
            article_id=mapping.article_id,
            title=mapping.article.title if mapping.article else "",
            route_pattern=mapping.route_pattern,
            priority=mapping.priority,
        )
        for mapping in mappings
    ]
    return ContextualHelpResponse(route=route, suggestions=suggestions)


# ======= Visibility Endpoints =======

@router.post("/articles/{article_id}/visibility", response_model=ArticleVisibilityResponse)
def set_visibility(
    article_id: UUID,
    data: ArticleVisibilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = VisibilityService(db)
    data.article_id = article_id
    return service.set_visibility(data)


# ======= Feedback Endpoints =======

@router.post("/articles/{article_id}/feedback", response_model=ArticleFeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    article_id: UUID,
    data: ArticleFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FeedbackService(db)
    data.article_id = article_id
    return service.submit_feedback(data, current_user.id)


# ======= Search Endpoints =======

@router.get("/search", response_model=SearchResponse)
def search_articles(
    query: str = Query(..., min_length=1),
    locale: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    use_semantic: bool = Query(True, description="Use semantic vector search if available"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search articles with semantic vector search + keyword fallback"""
    service = SearchService(db)
    
    # Get user roles for visibility filtering
    user_roles = (
        db.query(WorkspaceMember.role)
        .filter(WorkspaceMember.user_id == current_user.id)
        .distinct()
        .all()
    )
    role_names = [role[0].value if isinstance(role[0], WorkspaceRole) else role[0] for role in user_roles]
    
    results = service.search(
        SearchQuery(query=query, locale=locale, limit=limit),
        use_semantic=use_semantic,
        user_id=current_user.id,
        user_roles=role_names
    )

    formatted = [
        SearchResult(
            article_id=item.article_id,
            title=item.article.title if item.article else "",
            snippet=item.snippet,
            score=1.0,
        )
        for item in results
    ]

    return SearchResponse(query=query, results=formatted)


@router.post("/search/failed", response_model=FailedSearchResponse, status_code=status.HTTP_201_CREATED)
def record_failed_search(
    data: FailedSearchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FailedSearchService(db)
    return service.record_failed_search(data, current_user.id)
