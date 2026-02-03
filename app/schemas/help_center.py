"""
Pydantic schemas for Help Center & Knowledge Base (Module 15)
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.db.enums import ArticleStatus, ArticleVisibilityScope


# ======= Category Schemas =======

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=120)
    parent_id: Optional[UUID] = None
    display_order: int = 0
    description: Optional[str] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[UUID] = None
    display_order: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======= Article Schemas =======

class ArticleBase(BaseModel):
    slug: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=255)
    summary: Optional[str] = None
    category_id: Optional[UUID] = None
    status: ArticleStatus = ArticleStatus.DRAFT
    is_featured: bool = False


class ArticleCreate(ArticleBase):
    tag_ids: Optional[List[UUID]] = None


class ArticleUpdate(BaseModel):
    slug: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    category_id: Optional[UUID] = None
    status: Optional[ArticleStatus] = None
    is_featured: Optional[bool] = None
    tag_ids: Optional[List[UUID]] = None


class ArticleResponse(ArticleBase):
    id: UUID
    author_id: Optional[UUID]
    published_at: Optional[datetime]
    view_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======= Article Version Schemas =======

class ArticleVersionCreate(BaseModel):
    article_id: UUID
    version_number: int = 1
    version_label: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    content_raw: str = Field(..., min_length=1)
    content_rendered: Optional[str] = None
    changelog_summary: Optional[str] = None
    is_current: bool = True


class ArticleVersionResponse(BaseModel):
    id: UUID
    article_id: UUID
    version_number: int
    version_label: Optional[str]
    title: str
    content_raw: str
    content_rendered: Optional[str]
    changelog_summary: Optional[str]
    is_current: bool
    created_by_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======= Article Translation Schemas =======

class ArticleTranslationCreate(BaseModel):
    version_id: UUID
    locale: str = Field(..., min_length=2, max_length=10)
    title: str = Field(..., min_length=1, max_length=255)
    content_localized: str = Field(..., min_length=1)
    is_default: bool = False


class ArticleTranslationResponse(BaseModel):
    id: UUID
    version_id: UUID
    locale: str
    title: str
    content_localized: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======= Route Mapping Schemas =======

class RouteMappingCreate(BaseModel):
    article_id: UUID
    route_pattern: str = Field(..., min_length=1, max_length=255)
    element_selector: Optional[str] = None
    context_description: Optional[str] = None
    priority: int = 0
    is_active: bool = True


class RouteMappingResponse(BaseModel):
    id: UUID
    article_id: UUID
    route_pattern: str
    element_selector: Optional[str]
    context_description: Optional[str]
    priority: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======= Visibility Schemas =======

class ArticleVisibilityCreate(BaseModel):
    article_id: UUID
    access_scope: ArticleVisibilityScope = ArticleVisibilityScope.PUBLIC
    allowed_roles: Optional[Dict[str, Any]] = None


class ArticleVisibilityResponse(BaseModel):
    id: UUID
    article_id: UUID
    access_scope: ArticleVisibilityScope
    allowed_roles: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======= Feedback Schemas =======

class ArticleFeedbackCreate(BaseModel):
    article_id: UUID
    is_helpful: bool
    comment: Optional[str] = None
    route_path: Optional[str] = None


class ArticleFeedbackResponse(BaseModel):
    id: UUID
    article_id: UUID
    user_id: Optional[UUID]
    is_helpful: bool
    comment: Optional[str]
    route_path: Optional[str]
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======= Failed Search Schemas =======

class FailedSearchCreate(BaseModel):
    query_text: str = Field(..., min_length=1, max_length=500)
    locale: Optional[str] = None
    route_path: Optional[str] = None


class FailedSearchResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    query_text: str
    locale: Optional[str]
    route_path: Optional[str]
    searched_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======= Search Schemas =======

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1)
    locale: Optional[str] = None
    limit: int = Field(10, ge=1, le=50)


class SearchResult(BaseModel):
    article_id: UUID
    title: str
    snippet: Optional[str] = None
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]


# ======= Contextual Help Schemas =======

class ContextualSuggestion(BaseModel):
    article_id: UUID
    title: str
    route_pattern: str
    priority: int


class ContextualHelpResponse(BaseModel):
    route: str
    suggestions: List[ContextualSuggestion]
