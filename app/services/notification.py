"""
Service layer for Module 7: Event-Driven Notification System.

Services:
- EventBusService: Pub/Sub event handling
- AggregationService: Debounce and batching logic
- RoutingService: Channel selection and presence-aware routing
- TemplateService: Template rendering with i18n
- NotificationService: Core notification management
- RetryService: Exponential backoff retry mechanism
- WatcherService: Entity watcher management
- PreferenceService: User notification preferences

Ref: Module 7 - Features 2.1-2.5 & Business Rules 3.1-3.5
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from string import Template
import redis
from redis import asyncio as aioredis

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func
from loguru import logger

from app.db.models.notifications import (
    Notification, NotificationTemplate, NotificationPreference,
    Watcher, EventLog, NotificationRetry, InteractionLog, DomainEvent
)
from app.db.models.users import User
from app.db.models.workspaces import Workspace
from app.db.enums import (
    NotificationTypeEnum, NotificationChannelEnum,
    NotificationPriorityEnum, NotificationStatusEnum,
    TemplateLocaleEnum
)
from app.schemas.notification import (
    NotificationCreate, NotificationRead, NotificationTemplateCreate,
    NotificationPreferenceCreate, NotificationPreferenceUpdate,
    WatcherCreate, InteractionTrackingRequest
)


# ============ Event Bus Service ============

class EventBusService:
    """
    Pub/Sub event bus for event-driven architecture.
    Handles event publishing and consumption via Redis or RabbitMQ.
    
    Ref: Module 7 - Business Overview - Event-Driven Architecture
    """
    
    def __init__(self, redis_client: redis.Redis = None):
        """Initialize event bus with Redis or RabbitMQ."""
        self.redis_client = redis_client
        self.subscribers = {}
        
    async def publish_event(
        self,
        event_id: str,
        event_type: NotificationTypeEnum,
        source_entity_type: str,
        source_entity_id: str,
        payload: Dict[str, Any],
        workspace_id: str,
        triggered_by_user_id: Optional[str] = None
    ) -> None:
        """
        Publish an event to the message broker.
        
        Ref: Module 7 - Mô hình Observer - GoF
        """
        event_message = {
            "event_id": event_id,
            "event_type": event_type.value,
            "source_entity_type": source_entity_type,
            "source_entity_id": source_entity_id,
            "payload": payload,
            "workspace_id": workspace_id,
            "triggered_by_user_id": triggered_by_user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to Redis channel
        channel = f"notifications:events"
        if self.redis_client:
            self.redis_client.publish(
                channel,
                json.dumps(event_message)
            )
        
        logger.info(f"Event published: {event_id} ({event_type.value})")
    
    async def subscribe(
        self,
        event_type: NotificationTypeEnum,
        callback
    ) -> None:
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    async def consume_events(self) -> None:
        """Consume events from message broker."""
        if not self.redis_client:
            return
        
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe("notifications:events")
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                event = json.loads(message['data'])
                await self._process_event(event)
    
    async def _process_event(self, event: Dict[str, Any]) -> None:
        """Process a consumed event."""
        event_type = NotificationTypeEnum(event["event_type"])
        
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Error processing event {event['event_id']}: {str(e)}")


# ============ Aggregation Service ============

class AggregationService:
    """
    Intelligent aggregation and debounce logic.
    Combines related events within a time window.
    
    Ref: Module 7 - Feature 2.1 - AC 1 (Debounce) & AC 2 (Batching)
    """
    
    DEBOUNCE_WINDOW_MS = {
        NotificationPriorityEnum.HIGH: 0,        # No debounce for high priority
        NotificationPriorityEnum.MEDIUM: 5000,   # 5 seconds for medium
        NotificationPriorityEnum.LOW: 30000      # 30 seconds for low
    }
    
    def __init__(self, db: Session):
        """Initialize aggregation service."""
        self.db = db
        self._aggregation_keys = {}
    
    async def should_debounce(
        self,
        entity_type: str,
        entity_id: str,
        event_type: NotificationTypeEnum,
        priority: NotificationPriorityEnum
    ) -> tuple[bool, Optional[str]]:
        """
        Check if event should be debounced.
        Returns (should_debounce, aggregation_group_id)
        
        Ref: Module 7 - Feature 2.1 - AC 1 - Debounce Logic
        """
        debounce_ms = self.DEBOUNCE_WINDOW_MS.get(priority, 5000)
        
        # High priority events are never debounced
        if priority == NotificationPriorityEnum.HIGH:
            return False, None
        
        # Create aggregation key
        agg_key = f"{entity_type}:{entity_id}:{event_type.value}"
        
        # Check if we have recent aggregations
        if agg_key in self._aggregation_keys:
            last_time, agg_group_id = self._aggregation_keys[agg_key]
            elapsed = (datetime.utcnow() - last_time).total_seconds() * 1000
            
            if elapsed < debounce_ms:
                return True, agg_group_id
        
        # Create new aggregation group
        agg_group_id = str(uuid.uuid4())
        self._aggregation_keys[agg_key] = (datetime.utcnow(), agg_group_id)
        
        return False, agg_group_id
    
    def batch_notifications(
        self,
        notifications: List[NotificationRead],
        group_by: str = "event_type"
    ) -> Dict[str, List[NotificationRead]]:
        """
        Batch notifications for display.
        
        Ref: Module 7 - Feature 2.1 - AC 2 - Batching
        
        Example:
            "A, B, và C đã thích bình luận của bạn"
            instead of 3 separate notifications
        """
        batches = {}
        
        for notification in notifications:
            if group_by == "event_type":
                key = notification.event_type.value
            elif group_by == "entity_type":
                key = notification.related_entity_type or "unknown"
            else:
                key = "all"
            
            if key not in batches:
                batches[key] = []
            batches[key].append(notification)
        
        return batches


# ============ Routing Service ============

class RoutingService:
    """
    Smart routing and presence-aware channel selection.
    
    Ref: Module 7 - Feature 2.2 - Real-time Delivery & Fallback
    """
    
    def __init__(self, db: Session):
        """Initialize routing service."""
        self.db = db
        self.online_users = set()  # Track online users via WebSocket
    
    async def determine_channels(
        self,
        user_id: str,
        workspace_id: str,
        event_priority: NotificationPriorityEnum
    ) -> List[NotificationChannelEnum]:
        """
        Determine delivery channels based on user presence and preferences.
        
        Logic:
        - IF user is online: WebSocket only (no email spam)
        - IF user is offline: Email + Push (persistent channels)
        - High priority: Always email + push
        
        Ref: Module 7 - Feature 2.2 - AC 1 - Presence Awareness Routing
        """
        # Get user preferences
        preference = self.db.execute(
            select(NotificationPreference).where(
                and_(
                    NotificationPreference.user_id == user_id,
                    NotificationPreference.workspace_id == workspace_id
                )
            )
        ).scalar_one_or_none()
        
        if not preference:
            # Default channels
            return [NotificationChannelEnum.IN_APP, NotificationChannelEnum.EMAIL]
        
        channels = []
        
        # Check if user is online
        is_online = user_id in self.online_users
        
        if is_online and preference.in_app_enabled:
            # User is online: Send only in-app notification
            channels.append(NotificationChannelEnum.IN_APP)
        else:
            # User is offline or preference not enabled
            if preference.email_enabled:
                channels.append(NotificationChannelEnum.EMAIL)
            if preference.push_enabled:
                channels.append(NotificationChannelEnum.MOBILE_PUSH)
        
        # High priority always includes persistent channels
        if event_priority == NotificationPriorityEnum.HIGH:
            if preference.email_enabled and NotificationChannelEnum.EMAIL not in channels:
                channels.append(NotificationChannelEnum.EMAIL)
            if preference.push_enabled and NotificationChannelEnum.MOBILE_PUSH not in channels:
                channels.append(NotificationChannelEnum.MOBILE_PUSH)
        
        return channels
    
    def mark_user_online(self, user_id: str) -> None:
        """Mark user as online (called on WebSocket connect)."""
        self.online_users.add(user_id)
    
    def mark_user_offline(self, user_id: str) -> None:
        """Mark user as offline (called on WebSocket disconnect)."""
        self.online_users.discard(user_id)


# ============ Template Service ============

class TemplateService:
    """
    Notification template rendering with i18n support.
    
    Ref: Module 7 - Feature 2.4 - Notification Templating Engine
    """
    
    def __init__(self, db: Session):
        """Initialize template service."""
        self.db = db
    
    def render_template(
        self,
        template: NotificationTemplate,
        variables: Dict[str, Any]
    ) -> tuple[str, str]:
        """
        Render template with variable injection.
        
        Ref: Module 7 - Feature 2.4 - AC 1 - Variable Injection
        
        Returns: (rendered_subject, rendered_body)
        """
        # Use Python's Template for simple substitution
        subject_template = Template(template.subject)
        body_template = Template(template.body_template)
        
        try:
            subject = subject_template.substitute(**variables)
            body = body_template.substitute(**variables)
            return subject, body
        except KeyError as e:
            logger.error(f"Missing variable in template: {str(e)}")
            raise ValueError(f"Missing required variable: {str(e)}")
    
    def get_template(
        self,
        workspace_id: str,
        template_key: str,
        locale: TemplateLocaleEnum = TemplateLocaleEnum.EN
    ) -> Optional[NotificationTemplate]:
        """
        Get template with locale fallback.
        
        Ref: Module 7 - Feature 2.4 - AC 2 - Localization Support
        
        Fallback order: Requested locale -> EN (default)
        """
        # Try to find template in requested locale
        template = self.db.execute(
            select(NotificationTemplate).where(
                and_(
                    NotificationTemplate.workspace_id == workspace_id,
                    NotificationTemplate.template_key == template_key,
                    NotificationTemplate.locale == locale,
                    NotificationTemplate.is_active == True
                )
            )
        ).scalar_one_or_none()
        
        if template:
            return template
        
        # Fallback to English
        if locale != TemplateLocaleEnum.EN:
            template = self.db.execute(
                select(NotificationTemplate).where(
                    and_(
                        NotificationTemplate.workspace_id == workspace_id,
                        NotificationTemplate.template_key == template_key,
                        NotificationTemplate.locale == TemplateLocaleEnum.EN,
                        NotificationTemplate.is_active == True
                    )
                )
            ).scalar_one_or_none()
        
        return template
    
    def create_template(
        self,
        workspace_id: str,
        template_data: NotificationTemplateCreate
    ) -> NotificationTemplate:
        """Create a new notification template."""
        template = NotificationTemplate(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            template_key=template_data.template_key,
            locale=template_data.locale,
            subject=template_data.subject,
            body_template=template_data.body_template,
            required_variables=[v.dict() for v in template_data.required_variables],
            email_enabled=template_data.email_enabled,
            push_enabled=template_data.push_enabled,
            in_app_enabled=template_data.in_app_enabled,
            priority=template_data.priority,
            is_active=template_data.is_active
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        return template


# ============ Retry Service ============

class RetryService:
    """
    Exponential backoff retry mechanism for failed deliveries.
    
    Ref: Module 7 - Business Rule 3.1 - Retry Mechanism & Exponential Backoff
    
    Retry strategy:
    - Max retries: 3
    - Backoff: 1s -> 5s -> 25s
    """
    
    RETRY_DELAYS = [1, 5, 25]  # Seconds: 1s, 5s, 25s
    MAX_RETRIES = 3
    
    def __init__(self, db: Session):
        """Initialize retry service."""
        self.db = db
    
    async def should_retry(
        self,
        notification_id: str,
        channel: NotificationChannelEnum
    ) -> bool:
        """Check if a failed notification should be retried."""
        retry_count = self.db.execute(
            select(func.count(NotificationRetry.id)).where(
                and_(
                    NotificationRetry.notification_id == notification_id,
                    NotificationRetry.channel == channel,
                    NotificationRetry.status == "failed"
                )
            )
        ).scalar()
        
        return retry_count < self.MAX_RETRIES
    
    async def schedule_retry(
        self,
        notification_id: str,
        channel: NotificationChannelEnum,
        error_message: str
    ) -> None:
        """Schedule a retry with exponential backoff."""
        # Count previous failures for this channel
        retry_count = self.db.execute(
            select(func.count(NotificationRetry.id)).where(
                and_(
                    NotificationRetry.notification_id == notification_id,
                    NotificationRetry.channel == channel
                )
            )
        ).scalar()
        
        if retry_count >= self.MAX_RETRIES:
            # Max retries exceeded, mark as failed
            notification = self.db.query(Notification).get(notification_id)
            notification.status = NotificationStatusEnum.FAILED
            self.db.commit()
            logger.error(f"Max retries exceeded for notification {notification_id}")
            return
        
        # Calculate next retry time
        delay = self.RETRY_DELAYS[retry_count]
        next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
        
        # Create retry record
        retry = NotificationRetry(
            id=str(uuid.uuid4()),
            notification_id=notification_id,
            attempt_number=retry_count + 1,
            channel=channel,
            status="pending",
            error_message=error_message,
            scheduled_at=datetime.utcnow(),
            next_retry_at=next_retry_at
        )
        
        self.db.add(retry)
        self.db.commit()
        
        logger.info(f"Retry scheduled for notification {notification_id}, attempt {retry_count + 1}, delay {delay}s")


# ============ Notification Service ============

class NotificationService:
    """
    Core notification management service.
    Orchestrates all notification operations.
    """
    
    def __init__(
        self,
        db: Session,
        event_bus: EventBusService,
        aggregation: AggregationService,
        routing: RoutingService,
        template: TemplateService,
        retry: RetryService
    ):
        """Initialize notification service with dependencies."""
        self.db = db
        self.event_bus = event_bus
        self.aggregation = aggregation
        self.routing = routing
        self.template = template
        self.retry = retry
    
    async def create_notification(
        self,
        data: NotificationCreate
    ) -> NotificationRead:
        """
        Create a new notification with intelligent routing.
        
        Process:
        1. Check for idempotency (event_id)
        2. Apply debounce logic
        3. Determine delivery channels
        4. Create notification record
        5. Publish to message queue
        """
        # Check idempotency
        existing = self.db.execute(
            select(Notification).where(
                Notification.event_id == data.event_id
            )
        ).scalar_one_or_none()
        
        if existing:
            return NotificationRead.from_orm(existing)
        
        # Apply debounce logic
        should_debounce, agg_group_id = await self.aggregation.should_debounce(
            entity_type=data.related_entity_type or "unknown",
            entity_id=data.related_entity_id or "",
            event_type=data.event_type,
            priority=data.priority
        )
        
        # Determine delivery channels
        channels = await self.routing.determine_channels(
            user_id=data.recipient_id,
            workspace_id=data.workspace_id,
            event_priority=data.priority
        )
        
        # Create notification record
        notification = Notification(
            id=str(uuid.uuid4()),
            workspace_id=data.workspace_id,
            recipient_id=data.recipient_id,
            event_id=data.event_id,
            event_type=data.event_type,
            title=data.title,
            body=data.body,
            action_url=data.action_url,
            channels_used=channels,
            priority=data.priority,
            status=NotificationStatusEnum.PENDING,
            aggregation_group_id=agg_group_id,
            related_entity_type=data.related_entity_type,
            related_entity_id=data.related_entity_id,
            metadata=data.metadata,
            scheduled_at=data.scheduled_at
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # Publish to event bus
        await self.event_bus.publish_event(
            event_id=data.event_id,
            event_type=data.event_type,
            source_entity_type=data.related_entity_type or "notification",
            source_entity_id=notification.id,
            payload={
                "notification_id": notification.id,
                "channels": [c.value for c in channels]
            },
            workspace_id=data.workspace_id
        )
        
        return NotificationRead.from_orm(notification)
    
    async def get_notifications(
        self,
        user_id: str,
        workspace_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[NotificationRead], int]:
        """Get user's notifications with pagination."""
        query = select(Notification).where(
            and_(
                Notification.recipient_id == user_id,
                Notification.workspace_id == workspace_id
            )
        )
        
        if unread_only:
            query = query.where(Notification.read_at.is_(None))
        
        total = self.db.execute(
            select(func.count(Notification.id)).where(
                and_(
                    Notification.recipient_id == user_id,
                    Notification.workspace_id == workspace_id
                )
            )
        ).scalar()
        
        notifications = self.db.execute(
            query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        ).scalars().all()
        
        return [NotificationRead.from_orm(n) for n in notifications], total
    
    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str
    ) -> NotificationRead:
        """Mark notification as read."""
        notification = self.db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.recipient_id == user_id
                )
            )
        ).scalar_one_or_none()
        
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")
        
        notification.read_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(notification)
        
        # Track interaction
        interaction = InteractionLog(
            id=str(uuid.uuid4()),
            notification_id=notification_id,
            user_id=user_id,
            interaction_type="read",
            source_channel=NotificationChannelEnum.IN_APP
        )
        self.db.add(interaction)
        self.db.commit()
        
        return NotificationRead.from_orm(notification)
    
    async def track_interaction(
        self,
        data: InteractionTrackingRequest,
        user_id: str
    ) -> None:
        """Track user interactions with notifications."""
        interaction = InteractionLog(
            id=str(uuid.uuid4()),
            notification_id=data.notification_id,
            user_id=user_id,
            interaction_type=data.interaction_type,
            action_label=data.action_label,
            action_url_clicked=data.action_url_clicked,
            source_channel=data.source_channel,
            user_agent=data.user_agent,
            ip_address=data.ip_address
        )
        
        self.db.add(interaction)
        self.db.commit()
        
        # If it's a read action, also update notification status
        if data.interaction_type == "read":
            notification = self.db.query(Notification).get(data.notification_id)
            if notification:
                notification.read_at = datetime.utcnow()
                self.db.commit()


# ============ Watcher Service ============

class WatcherService:
    """
    Entity watcher management for granular subscriptions.
    
    Ref: Module 7 - Feature 2.3 - Unsubscribe Strategy
    """
    
    def __init__(self, db: Session):
        """Initialize watcher service."""
        self.db = db
    
    async def add_watcher(
        self,
        user_id: str,
        workspace_id: str,
        data: WatcherCreate
    ) -> None:
        """Add a user as watcher of an entity."""
        # Check if already watching
        existing = self.db.execute(
            select(Watcher).where(
                and_(
                    Watcher.workspace_id == workspace_id,
                    Watcher.entity_type == data.entity_type,
                    Watcher.entity_id == data.entity_id,
                    Watcher.user_id == user_id
                )
            )
        ).scalar_one_or_none()
        
        if existing:
            existing.is_watching = True
            self.db.commit()
            return
        
        watcher = Watcher(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            user_id=user_id,
            is_watching=True,
            custom_channels=data.custom_channels,
            notify_on_types=data.notify_on_types
        )
        
        self.db.add(watcher)
        self.db.commit()
    
    async def remove_watcher(
        self,
        user_id: str,
        workspace_id: str,
        entity_type: str,
        entity_id: str
    ) -> None:
        """Remove watcher from an entity."""
        watcher = self.db.execute(
            select(Watcher).where(
                and_(
                    Watcher.workspace_id == workspace_id,
                    Watcher.entity_type == entity_type,
                    Watcher.entity_id == entity_id,
                    Watcher.user_id == user_id
                )
            )
        ).scalar_one_or_none()
        
        if watcher:
            watcher.is_watching = False
            self.db.commit()
    
    async def get_watchers(
        self,
        entity_type: str,
        entity_id: str,
        workspace_id: str
    ) -> List[Watcher]:
        """Get all watchers of an entity."""
        watchers = self.db.execute(
            select(Watcher).where(
                and_(
                    Watcher.workspace_id == workspace_id,
                    Watcher.entity_type == entity_type,
                    Watcher.entity_id == entity_id,
                    Watcher.is_watching == True
                )
            )
        ).scalars().all()
        
        return watchers
    
    async def should_notify_watcher(
        self,
        watcher: Watcher,
        event_type: NotificationTypeEnum
    ) -> bool:
        """Check if watcher should be notified of this event."""
        # If notify_on_types is specified, check if event matches
        if watcher.notify_on_types:
            return event_type.value in watcher.notify_on_types
        
        # Otherwise, notify for all events
        return True


# ============ Preference Service ============

class PreferenceService:
    """
    User notification preference management.
    """
    
    def __init__(self, db: Session):
        """Initialize preference service."""
        self.db = db
    
    async def get_or_create_preferences(
        self,
        user_id: str,
        workspace_id: str
    ) -> NotificationPreference:
        """Get or create user notification preferences."""
        preference = self.db.execute(
            select(NotificationPreference).where(
                and_(
                    NotificationPreference.user_id == user_id,
                    NotificationPreference.workspace_id == workspace_id
                )
            )
        ).scalar_one_or_none()
        
        if preference:
            return preference
        
        # Create default preferences
        preference = NotificationPreference(
            id=str(uuid.uuid4()),
            user_id=user_id,
            workspace_id=workspace_id,
            notifications_enabled=True,
            email_enabled=True,
            push_enabled=True,
            in_app_enabled=True,
            enable_digest_batching=True,
            digest_frequency="hourly"
        )
        
        self.db.add(preference)
        self.db.commit()
        self.db.refresh(preference)
        
        return preference
    
    async def update_preferences(
        self,
        user_id: str,
        workspace_id: str,
        data: NotificationPreferenceUpdate
    ) -> NotificationPreference:
        """Update user notification preferences."""
        preference = await self.get_or_create_preferences(user_id, workspace_id)
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preference, field, value)
        
        self.db.commit()
        self.db.refresh(preference)
        
        return preference
