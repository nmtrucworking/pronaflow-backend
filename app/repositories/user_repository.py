"""
User Repository
Handles all database operations for User model.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import uuid

from app.repositories.base import BaseRepository
from app.models.users import User, Role, Permission
from app.db.enums import UserStatus


class UserRepository(BaseRepository[User]):
    """Repository for User model with specialized queries."""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    # ==================== AUTHENTICATION ====================
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.email == email.lower()).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: User's username
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """
        Get user by email or username.
        
        Args:
            identifier: Email or username
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(
            or_(
                User.email == identifier.lower(),
                User.username == identifier
            )
        ).first()
    
    def email_exists(self, email: str, exclude_user_id: Optional[uuid.UUID] = None) -> bool:
        """
        Check if email already exists.
        
        Args:
            email: Email to check
            exclude_user_id: Optional user ID to exclude from check
            
        Returns:
            True if email exists, False otherwise
        """
        query = self.db.query(User).filter(User.email == email.lower())
        
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        
        return self.db.query(query.exists()).scalar()
    
    def username_exists(self, username: str, exclude_user_id: Optional[uuid.UUID] = None) -> bool:
        """
        Check if username already exists.
        
        Args:
            username: Username to check
            exclude_user_id: Optional user ID to exclude from check
            
        Returns:
            True if username exists, False otherwise
        """
        query = self.db.query(User).filter(User.username == username)
        
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        
        return self.db.query(query.exists()).scalar()
    
    # ==================== USER STATUS ====================
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all active users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active users
        """
        return (
            self.db.query(User)
            .filter(User.status == UserStatus.ACTIVE)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_pending_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get users with pending status (not verified).
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of pending users
        """
        return (
            self.db.query(User)
            .filter(User.status == UserStatus.PENDING)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_suspended_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get suspended users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of suspended users
        """
        return (
            self.db.query(User)
            .filter(User.status == UserStatus.SUSPENDED)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def activate_user(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Activate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user instance or None if not found
        """
        user = self.get_by_id(user_id)
        if user:
            user.status = UserStatus.ACTIVE
            if not user.email_verified_at:
                user.email_verified_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def suspend_user(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Suspend a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user instance or None if not found
        """
        user = self.get_by_id(user_id)
        if user:
            user.status = UserStatus.SUSPENDED
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def verify_email(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Mark user's email as verified.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user instance or None if not found
        """
        user = self.get_by_id(user_id)
        if user:
            user.email_verified_at = datetime.utcnow()
            if user.status == UserStatus.PENDING:
                user.status = UserStatus.ACTIVE
            self.db.commit()
            self.db.refresh(user)
        return user
    
    # ==================== USER SEARCH ====================
    
    def search_users(
        self,
        query: str,
        status: Optional[UserStatus] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[User]:
        """
        Search users by email, username, or full name.
        
        Args:
            query: Search query string
            status: Optional status filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching users
        """
        search_filter = or_(
            User.email.ilike(f"%{query}%"),
            User.username.ilike(f"%{query}%"),
            User.full_name.ilike(f"%{query}%")
        )
        
        db_query = self.db.query(User).filter(search_filter)
        
        if status:
            db_query = db_query.filter(User.status == status)
        
        return db_query.offset(skip).limit(limit).all()
    
    # ==================== ROLE MANAGEMENT ====================
    
    def add_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> Optional[User]:
        """
        Add a role to user.
        
        Args:
            user_id: User ID
            role_id: Role ID
            
        Returns:
            Updated user instance or None if not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if role and role not in user.roles:
            user.roles.append(role)
            self.db.commit()
            self.db.refresh(user)
        
        return user
    
    def remove_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> Optional[User]:
        """
        Remove a role from user.
        
        Args:
            user_id: User ID
            role_id: Role ID
            
        Returns:
            Updated user instance or None if not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if role and role in user.roles:
            user.roles.remove(role)
            self.db.commit()
            self.db.refresh(user)
        
        return user
    
    def get_user_roles(self, user_id: uuid.UUID) -> List[Role]:
        """
        Get all roles for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of role instances
        """
        user = self.get_by_id(user_id)
        return user.roles if user else []
    
    def get_user_permissions(self, user_id: uuid.UUID) -> List[Permission]:
        """
        Get all permissions for a user (through roles).
        
        Args:
            user_id: User ID
            
        Returns:
            List of permission instances
        """
        user = self.get_by_id(user_id)
        if not user:
            return []
        
        permissions = []
        for role in user.roles:
            permissions.extend(role.permissions)
        
        # Remove duplicates
        return list({perm.id: perm for perm in permissions}.values())
    
    def has_permission(self, user_id: uuid.UUID, permission_name: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user_id: User ID
            permission_name: Permission name to check
            
        Returns:
            True if user has permission, False otherwise
        """
        permissions = self.get_user_permissions(user_id)
        return any(perm.permission_name == permission_name for perm in permissions)
    
    # ==================== STATISTICS ====================
    
    def count_by_status(self, status: UserStatus) -> int:
        """
        Count users by status.
        
        Args:
            status: User status
            
        Returns:
            Number of users with given status
        """
        return self.db.query(func.count(User.id)).filter(User.status == status).scalar()
    
    def count_verified_users(self) -> int:
        """
        Count users with verified email.
        
        Returns:
            Number of verified users
        """
        return (
            self.db.query(func.count(User.id))
            .filter(User.email_verified_at.isnot(None))
            .scalar()
        )
    
    def get_recently_created_users(self, days: int = 7, limit: int = 100) -> List[User]:
        """
        Get users created in the last N days.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of records to return
            
        Returns:
            List of recently created users
        """
        since_date = datetime.utcnow() - timedelta(days=days)
        return (
            self.db.query(User)
            .filter(User.created_at >= since_date)
            .order_by(User.created_at.desc())
            .limit(limit)
            .all()
        )
    
    # ==================== PASSWORD MANAGEMENT ====================
    
    def update_password(self, user_id: uuid.UUID, password_hash: str) -> Optional[User]:
        """
        Update user's password hash.
        
        Args:
            user_id: User ID
            password_hash: New password hash
            
        Returns:
            Updated user instance or None if not found
        """
        user = self.get_by_id(user_id)
        if user:
            user.password_hash = password_hash
            self.db.commit()
            self.db.refresh(user)
        return user
