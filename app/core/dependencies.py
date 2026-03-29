"""Compatibility dependency exports for legacy routes/tests.

Canonical auth dependencies are implemented in app.core.security.
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user as _get_current_user
from app.models.users import User


async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_workspace_id: Optional[UUID] = Header(None, alias="X-Workspace-Id"),
    db: Session = Depends(get_db),
) -> User:
    """Backward-compatible alias for current authenticated user dependency."""
    return await _get_current_user(authorization=authorization, x_workspace_id=x_workspace_id, db=db)


__all__ = ["get_db", "get_current_user"]
