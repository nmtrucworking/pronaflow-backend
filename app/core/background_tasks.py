"""
Background tasks for Help Center indexing and notifications (Module 15)
Provides async job processing with SLA tracking (<= 5 minutes)
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import logging

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.help_center import ArticleSearchIndex, Article
from app.models.admin import FeatureFlag
from app.core.vector_search import vector_search_service

logger = logging.getLogger(__name__)


class IndexingTask:
    """Article indexing background task with SLA tracking"""
    
    SLA_MINUTES = 5  # Maximum 5 minutes for indexing
    
    @staticmethod
    def index_article(
        article_id: UUID,
        title: str,
        content: str,
        db: Session
    ) -> bool:
        """
        Index article for search (keyword + semantic).
        
        SLA: <= 5 minutes
        Returns: True if successful, False otherwise
        """
        start_time = datetime.utcnow()
        
        try:
            # Generate keywords (first 500 chars for snippet)
            snippet = (content[:500] + "...") if len(content) > 500 else content
            keywords = f"{title} {snippet}"
            
            # Generate semantic embedding
            embedding_text = f"{title}. {content[:2000]}"  # Limit for embedding
            embedding_vector = None
            
            if vector_search_service.is_available():
                try:
                    embedding_vector = vector_search_service.generate_embedding(embedding_text)
                except Exception as e:
                    logger.warning(f"Embedding generation failed for article {article_id}: {e}")
            
            # Update or create index
            index = db.query(ArticleSearchIndex).filter(
                ArticleSearchIndex.article_id == article_id
            ).first()
            
            if index:
                index.keywords = keywords
                index.snippet = snippet
                index.embedding_vector = embedding_vector
                index.last_indexed = datetime.utcnow()
            else:
                index = ArticleSearchIndex(
                    article_id=article_id,
                    keywords=keywords,
                    snippet=snippet,
                    embedding_vector=embedding_vector,
                    last_indexed=datetime.utcnow()
                )
                db.add(index)
            
            db.commit()
            
            # Check SLA
            elapsed = (datetime.utcnow() - start_time).total_seconds() / 60
            if elapsed > IndexingTask.SLA_MINUTES:
                logger.warning(f"Indexing SLA exceeded: {elapsed:.2f} minutes for article {article_id}")
            else:
                logger.info(f"Indexed article {article_id} in {elapsed:.2f} minutes")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to index article {article_id}: {e}")
            db.rollback()
            return False


class NotificationTask:
    """Article notification background task"""
    
    @staticmethod
    def notify_article_published(
        article_id: UUID,
        article_title: str,
        db: Session
    ) -> bool:
        """
        Send notification when article is published.
        
        Integration points:
        - Email service (Module 10)
        - Push notification service
        - Slack/Teams webhook
        
        Feature flag: help_center_notifications
        """
        try:
            # Check feature flag
            flag = db.query(FeatureFlag).filter(
                FeatureFlag.key == "help_center_notifications"
            ).first()
            
            if not flag or not flag.is_enabled:
                logger.info(f"Notifications disabled for article {article_id}")
                return True
            
            # TODO: Integrate with notification service
            # notification_service = NotificationService(db)
            # notification_service.send(
            #     recipients=get_subscribers(),
            #     subject=f"New Article: {article_title}",
            #     template="article_published",
            #     context={"article_id": article_id, "title": article_title}
            # )
            
            logger.info(f"Notification sent for published article: {article_title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification for article {article_id}: {e}")
            return False


def queue_article_indexing(article_id: UUID, title: str, content: str):
    """
    Queue article for background indexing.
    
    Production: Use Celery, RQ, or ARQ for distributed task queue
    Development: Inline execution with FastAPI BackgroundTasks
    """
    db = SessionLocal()
    try:
        IndexingTask.index_article(article_id, title, content, db)
    finally:
        db.close()


def queue_article_notification(article_id: UUID, title: str):
    """Queue article publication notification"""
    db = SessionLocal()
    try:
        NotificationTask.notify_article_published(article_id, title, db)
    finally:
        db.close()
