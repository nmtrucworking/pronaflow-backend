"""
Event Bus configuration for Module 7: Event-Driven Notification System.

Provides Redis Pub/Sub connection and initialization.

Ref: Module 7 - Business Overview - Event-Driven Architecture (EDA)
"""

import redis
from typing import Optional
from loguru import logger
from app.core.config import settings


class EventBusConfig:
    """Configuration for event bus (Redis Pub/Sub)."""
    
    _instance: Optional[redis.Redis] = None
    
    @classmethod
    def get_redis_client(cls) -> redis.Redis:
        """
        Get or create Redis client singleton.
        
        Returns:
            redis.Redis: Connected Redis client
        """
        if cls._instance is None:
            cls._instance = cls._create_client()
        
        return cls._instance
    
    @classmethod
    def _create_client(cls) -> redis.Redis:
        """Create a new Redis client."""
        try:
            client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            
            # Test connection
            client.ping()
            logger.info(f"Redis connected: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
            return client
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            logger.warning("Event bus disabled - notifications will be stored but not delivered in real-time")
            return None
    
    @classmethod
    def close(cls) -> None:
        """Close Redis connection."""
        if cls._instance:
            cls._instance.close()
            cls._instance = None
    
    @classmethod
    def is_connected(cls) -> bool:
        """Check if Redis is connected."""
        client = cls.get_redis_client()
        return client is not None


# Event channels
class EventChannels:
    """Standard event channels for Pub/Sub."""
    
    # Main event channel
    NOTIFICATIONS = "notifications:events"
    
    # Priority channels
    CRITICAL = "notifications:critical"
    TRANSACTIONAL = "notifications:transactional"
    PROMOTIONAL = "notifications:promotional"
    
    # User-specific channels
    @staticmethod
    def user_channel(user_id: str) -> str:
        """Get user-specific notification channel."""
        return f"notifications:user:{user_id}"
    
    @staticmethod
    def workspace_channel(workspace_id: str) -> str:
        """Get workspace-specific event channel."""
        return f"notifications:workspace:{workspace_id}"
    
    @staticmethod
    def entity_channel(entity_type: str, entity_id: str) -> str:
        """Get entity-specific event channel."""
        return f"notifications:{entity_type}:{entity_id}"


# Event types for routing
class EventPriorityChannels:
    """Map event types to priority channels."""
    
    CRITICAL_EVENTS = {
        "security_alert",
        "system_error",
        "sla_breached"
    }
    
    TRANSACTIONAL_EVENTS = {
        "task_assigned",
        "task_updated",
        "user_mentioned",
        "approval_requested"
    }
    
    PROMOTIONAL_EVENTS = {
        "weekly_digest",
        "general_reminder"
    }
    
    @classmethod
    def get_channel(cls, event_type: str) -> str:
        """Get priority channel for event type."""
        if event_type in cls.CRITICAL_EVENTS:
            return EventChannels.CRITICAL
        elif event_type in cls.TRANSACTIONAL_EVENTS:
            return EventChannels.TRANSACTIONAL
        elif event_type in cls.PROMOTIONAL_EVENTS:
            return EventChannels.PROMOTIONAL
        else:
            return EventChannels.NOTIFICATIONS


# Redis Key patterns for caching
class RedisKeys:
    """Redis key patterns for event bus operations."""
    
    @staticmethod
    def event_id_processed(event_id: str) -> str:
        """Key for tracking processed event IDs (idempotency)."""
        return f"event:processed:{event_id}"
    
    @staticmethod
    def aggregation_key(entity_type: str, entity_id: str, event_type: str) -> str:
        """Key for debounce/aggregation tracking."""
        return f"agg:{entity_type}:{entity_id}:{event_type}"
    
    @staticmethod
    def retry_queue(channel: str) -> str:
        """Key for retry queue per channel."""
        return f"retry:{channel}"
    
    @staticmethod
    def user_online(user_id: str) -> str:
        """Key for tracking online users."""
        return f"online:user:{user_id}"
    
    @staticmethod
    def notification_cache(notification_id: str) -> str:
        """Key for caching notification data."""
        return f"notif:{notification_id}"
