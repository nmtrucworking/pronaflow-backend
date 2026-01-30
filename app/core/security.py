"""
Security utilities for authentication and authorization.
"""
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.users import User


async def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = None,
) -> User:
    """
    Get the current authenticated user.
    
    TODO: Implement actual JWT token verification
    For now, this is a placeholder that raises an exception.
    """
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Please implement JWT token verification in security module.",
    )
