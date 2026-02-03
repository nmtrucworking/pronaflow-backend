"""
Pagination utilities for PronaFlow API
"""
from typing import TypeVar, Generic, List, Optional, Any, Dict
from pydantic import BaseModel, Field
from math import ceil

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination request parameters."""
    
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum items per page")
    
    @property
    def page(self) -> int:
        """Calculate page number (1-based)."""
        return (self.skip // self.limit) + 1 if self.skip > 0 else 1
    
    @property
    def offset(self) -> int:
        """Alias for skip."""
        return self.skip


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    
    items: List[T]
    total: int
    skip: int
    limit: int
    
    @property
    def page(self) -> int:
        """Calculate current page number."""
        return (self.skip // self.limit) + 1 if self.skip > 0 else 1
    
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return ceil(self.total / self.limit) if self.limit > 0 else 0
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.skip + self.limit < self.total
    
    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.skip > 0


class Paginator:
    """Helper class for pagination."""
    
    @staticmethod
    def paginate(
        items: List[T],
        total: int,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Create pagination metadata.
        
        Args:
            items: List of items for current page
            total: Total number of items
            skip: Number of items skipped
            limit: Maximum items per page
            
        Returns:
            Dictionary with pagination metadata
        """
        page = (skip // limit) + 1 if skip > 0 else 1
        total_pages = ceil(total / limit) if limit > 0 else 0
        
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "page": page,
            "total_pages": total_pages,
            "has_next": skip + limit < total,
            "has_previous": skip > 0,
        }
    
    @staticmethod
    def get_offset_limit(page: int, per_page: int = 20) -> tuple[int, int]:
        """
        Convert page number to offset/limit.
        
        Args:
            page: Page number (1-based)
            per_page: Items per page
            
        Returns:
            Tuple of (skip, limit)
        """
        if page < 1:
            page = 1
        
        skip = (page - 1) * per_page
        return skip, per_page
