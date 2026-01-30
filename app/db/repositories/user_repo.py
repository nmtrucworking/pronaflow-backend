"""
User Repository - Database access for User model.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.users import User
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model with specialized queries."""

    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.session.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users."""
        from app.db.enums import UserStatus
        return self.session.execute(
            select(User)
            .where(User.status == UserStatus.ACTIVE)
            .offset(skip)
            .limit(limit)
        ).scalars().all()

    def get_by_email_or_username(self, credential: str) -> Optional[User]:
        """Get user by either email or username."""
        return self.session.execute(
            select(User).where(
                (User.email == credential) | (User.username == credential)
            )
        ).scalar_one_or_none()

    def email_exists(self, email: str, exclude_user_id: Optional[str] = None) -> bool:
        """Check if email already exists."""
        query = select(User).where(User.email == email)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        return self.session.execute(query).scalar_one_or_none() is not None

    def username_exists(self, username: str, exclude_user_id: Optional[str] = None) -> bool:
        """Check if username already exists."""
        query = select(User).where(User.username == username)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        return self.session.execute(query).scalar_one_or_none() is not None
