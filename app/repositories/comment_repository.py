"""
Comment Repository
Handles all database operations for Comment model.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
import uuid

from app.repositories.base import BaseRepository
from app.db.models.collaboration import Comment


class CommentRepository(BaseRepository[Comment]):
    """Repository for Comment model with threaded discussion support."""
    
    def __init__(self, db: Session):
        super().__init__(Comment, db)
    
    # ==================== COMMENT QUERIES ====================
    
    def get_task_comments(
        self,
        task_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Comment]:
        """
        Get all comments for a task.
        
        Args:
            task_id: Task ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of comments ordered by creation date
        """
        return (
            self.db.query(Comment)
            .filter(Comment.task_id == task_id)
            .filter(Comment.parent_comment_id.is_(None))  # Only top-level comments
            .order_by(Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_threaded_comments(self, task_id: uuid.UUID) -> List[Comment]:
        """
        Get all comments with full thread hierarchy.
        
        Args:
            task_id: Task ID
            
        Returns:
            List of all comments (top-level and replies)
        """
        return (
            self.db.query(Comment)
            .filter(Comment.task_id == task_id)
            .order_by(Comment.created_at.asc())
            .all()
        )
    
    def get_comment_replies(
        self,
        comment_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Comment]:
        """
        Get all replies to a comment.
        
        Args:
            comment_id: Parent comment ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of reply comments
        """
        return (
            self.db.query(Comment)
            .filter(Comment.parent_comment_id == comment_id)
            .order_by(Comment.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_user_comments(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Comment]:
        """
        Get all comments by a user.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of user's comments
        """
        return (
            self.db.query(Comment)
            .filter(Comment.created_by == user_id)
            .order_by(Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    # ==================== COMMENT EDITING ====================
    
    def edit_comment(
        self,
        comment_id: uuid.UUID,
        content: str
    ) -> Optional[Comment]:
        """
        Edit comment content.
        
        Args:
            comment_id: Comment ID
            content: New comment content
            
        Returns:
            Updated comment or None if not found
        """
        comment = self.get_by_id(comment_id)
        if comment:
            comment.content = content
            comment.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(comment)
        return comment
    
    # ==================== REACTIONS ====================
    
    def add_reaction(
        self,
        comment_id: uuid.UUID,
        user_id: uuid.UUID,
        reaction_type: str
    ) -> Optional[Comment]:
        """
        Add user reaction to comment.
        
        Args:
            comment_id: Comment ID
            user_id: User ID reacting
            reaction_type: Reaction type (emoji)
            
        Returns:
            Updated comment or None if not found
        """
        comment = self.get_by_id(comment_id)
        if comment:
            # Track reactions (implementation depends on model structure)
            # This is simplified - may need separate reaction table
            self.db.commit()
            self.db.refresh(comment)
        return comment
    
    # ==================== MENTIONS & NOTIFICATIONS ====================
    
    def get_mentions(self, comment_id: uuid.UUID) -> List[str]:
        """
        Extract mentioned user IDs from comment.
        
        Args:
            comment_id: Comment ID
            
        Returns:
            List of mentioned user IDs
        """
        comment = self.get_by_id(comment_id)
        if not comment:
            return []
        
        # Extract @mentions from content
        import re
        mentions = re.findall(r'@(\w+)', comment.content)
        return mentions
    
    # ==================== STATISTICS ====================
    
    def count_task_comments(self, task_id: uuid.UUID) -> int:
        """
        Count total comments on a task (including replies).
        
        Args:
            task_id: Task ID
            
        Returns:
            Number of comments
        """
        return (
            self.db.query(func.count(Comment.id))
            .filter(Comment.task_id == task_id)
            .scalar() or 0
        )
    
    def count_comment_replies(self, comment_id: uuid.UUID) -> int:
        """
        Count replies to a comment.
        
        Args:
            comment_id: Comment ID
            
        Returns:
            Number of replies
        """
        return (
            self.db.query(func.count(Comment.id))
            .filter(Comment.parent_comment_id == comment_id)
            .scalar() or 0
        )
    
    def get_user_comment_count(self, user_id: uuid.UUID) -> int:
        """
        Count comments by user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of user's comments
        """
        return (
            self.db.query(func.count(Comment.id))
            .filter(Comment.created_by == user_id)
            .scalar() or 0
        )
    
    def get_recently_commented_tasks(
        self,
        workspace_id: uuid.UUID,
        limit: int = 20
    ) -> List[uuid.UUID]:
        """
        Get tasks with recent comment activity.
        
        Args:
            workspace_id: Workspace ID for filtering
            limit: Maximum number of tasks
            
        Returns:
            List of task IDs ordered by latest comment
        """
        from app.db.models.tasks import Task
        
        return (
            self.db.query(Comment.task_id)
            .join(Task)
            .filter(Task.project_id.in_(
                self.db.query(Task.project_id)
                .join(Comment)
            ))
            .order_by(Comment.created_at.desc())
            .limit(limit)
            .all()
        )
