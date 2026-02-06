"""
Notification Repository
Handles all database operations for Notification model.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
import uuid

from app.repositories.base import BaseRepository
from app.models.notifications import Notification


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification model."""
    
    def __init__(self, db: Session):
        super().__init__(Notification, db)
    
    # ==================== USER NOTIFICATIONS ====================
    
    def get_user_notifications(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        """
        Get notifications for a user.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            unread_only: Only return unread notifications
            
        Returns:
            List of notifications
        """
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return (
            query.order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_unread_count(self, user_id: uuid.UUID) -> int:
        """
        Count unread notifications for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of unread notifications
        """
        return (
            self.db.query(func.count(Notification.id))
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
            .scalar() or 0
        )
    
    # ==================== READ/UNREAD MANAGEMENT ====================
    
    def mark_as_read(self, notification_id: uuid.UUID) -> Optional[Notification]:
        """
        Mark notification as read.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            Updated notification or None if not found
        """
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(notification)
        return notification
    
    def mark_as_unread(self, notification_id: uuid.UUID) -> Optional[Notification]:
        """
        Mark notification as unread.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            Updated notification or None if not found
        """
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_read = False
            notification.read_at = None
            self.db.commit()
            self.db.refresh(notification)
        return notification
    
    def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of notifications marked as read
        """
        count = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
            .count()
        )
        
        self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({
            Notification.is_read: True,
            Notification.read_at: datetime.utcnow()
        })
        
        self.db.commit()
        return count
    
    # ==================== PRIORITY FILTERING ====================
    
    def get_by_priority(
        self,
        user_id: uuid.UUID,
        priority: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Notification]:
        """
        Get notifications by priority.
        
        Args:
            user_id: User ID
            priority: Priority level (LOW, MEDIUM, HIGH, URGENT)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of notifications
        """
        return (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.priority == priority
                )
            )
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_urgent_notifications(self, user_id: uuid.UUID) -> List[Notification]:
        """
        Get urgent notifications.
        
        Args:
            user_id: User ID
            
        Returns:
            List of urgent notifications
        """
        return self.get_by_priority(user_id, 'URGENT', limit=100)
    
    # ==================== BULK OPERATIONS ====================
    
    def delete_old_read_notifications(self, days: int = 30) -> int:
        """
        Delete read notifications older than specified days.
        
        Args:
            days: Delete notifications older than this many days
            
        Returns:
            Number of deleted notifications
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        count = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.is_read == True,
                    Notification.read_at < cutoff_date
                )
            )
            .count()
        )
        
        self.db.query(Notification).filter(
            and_(
                Notification.is_read == True,
                Notification.read_at < cutoff_date
            )
        ).delete()
        
        self.db.commit()
        return count
    
    # ==================== STATISTICS ====================
    
    def get_user_stats(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get notification statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with notification statistics
        """
        return {
            "total": (
                self.db.query(func.count(Notification.id))
                .filter(Notification.user_id == user_id)
                .scalar() or 0
            ),
            "unread": self.get_unread_count(user_id),
            "urgent": (
                self.db.query(func.count(Notification.id))
                .filter(
                    and_(
                        Notification.user_id == user_id,
                        Notification.priority == 'URGENT'
                    )
                )
                .scalar() or 0
            )
        }
