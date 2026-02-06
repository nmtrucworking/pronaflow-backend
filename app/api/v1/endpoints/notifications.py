"""
API Endpoints for Module 7: Event-Driven Notification System.

Endpoints:
- GET /notifications - List user notifications
- POST /notifications/{id}/read - Mark notification as read
- POST /notifications/interactions - Track interactions
- GET /notifications/preferences - Get user preferences
- PUT /notifications/preferences - Update preferences
- GET /notifications/templates - List templates
- POST /notifications/templates - Create template
- POST /watchers - Add watcher
- DELETE /watchers - Remove watcher
- GET /watchers - List watchers

Ref: Module 7 - Features 2.1-2.5
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.services.notification import (
    NotificationService, AggregationService, RoutingService,
    TemplateService, RetryService, PreferenceService, WatcherService,
    EventBusService
)
from app.schemas.notification import (
    NotificationListResponse, NotificationRead, MarkAsReadRequest,
    NotificationTemplateCreate, NotificationTemplateRead,
    NotificationPreferenceRead, NotificationPreferenceUpdate,
    WatcherCreate, WatcherRead, InteractionTrackingRequest,
    NotificationTemplateListResponse, WatcherListResponse,
    NotificationStatistics, InteractionLogListResponse
)
from app.db.enums import NotificationPriorityEnum
from sqlalchemy import select, and_
from app.models.notifications import (
    Notification, NotificationTemplate, NotificationPreference,
    EventConsumer, DomainEvent
)
from functools import lru_cache
import redis
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


# ============ Dependency Injection ============

@lru_cache()
def get_redis_client():
    """Get Redis client for event bus."""
    return redis.Redis(host='localhost', port=6379, db=0)


def get_services(db: Session = Depends(get_db)):
    """Get all notification services."""
    redis_client = get_redis_client()
    
    event_bus = EventBusService(redis_client)
    aggregation = AggregationService(db)
    routing = RoutingService(db)
    template = TemplateService(db)
    retry = RetryService(db)
    
    notification_service = NotificationService(
        db=db,
        event_bus=event_bus,
        aggregation=aggregation,
        routing=routing,
        template=template,
        retry=retry
    )
    
    preference_service = PreferenceService(db)
    watcher_service = WatcherService(db)
    
    return {
        "notification": notification_service,
        "preference": preference_service,
        "watcher": watcher_service,
        "routing": routing,
        "template": template
    }


# ============ Notification Endpoints ============

@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    workspace_id: str = Query(..., description="Workspace ID"),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    limit: int = Query(50, ge=1, le=100),
    page: int = Query(1, ge=1)
):
    """
    List user's notifications.
    
    Ref: Module 7 - Feature 2.1 - Intelligent Aggregation
    """
    services = get_services(db)
    
    # Check workspace membership
    from app.models.workspaces import WorkspaceMember
    membership = db.execute(
        select(WorkspaceMember).where(
            and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == str(current_user.id)
            )
        )
    ).scalar_one_or_none()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    offset = (page - 1) * limit
    notifications, total = await services["notification"].get_notifications(
        user_id=str(current_user.id),
        workspace_id=workspace_id,
        unread_only=unread_only,
        limit=limit,
        offset=offset
    )
    
    # Batch notifications by type
    batched = services["notification"].aggregation.batch_notifications(notifications)
    
    return NotificationListResponse(
        items=notifications,
        total=total,
        page=page,
        page_size=limit,
        has_more=(offset + limit) < total
    )


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> NotificationRead:
    """
    Mark notification as read.
    
    Ref: Module 7 - Feature 2.5 - AC 1 - Read Receipts
    """
    services = get_services(db)
    
    notification = await services["notification"].mark_as_read(
        notification_id=notification_id,
        user_id=str(current_user.id)
    )
    
    return notification


@router.post("/interactions")
async def track_interaction(
    data: InteractionTrackingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track user interaction with notification.
    
    Ref: Module 7 - Feature 2.5 - Interaction Tracking
    """
    services = get_services(db)
    
    await services["notification"].track_interaction(
        data=data,
        user_id=str(current_user.id)
    )
    
    return {"status": "ok", "message": "Interaction tracked"}


@router.get("/interactions", response_model=InteractionLogListResponse)
async def list_interactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    workspace_id: str = Query(...),
    notification_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    page: int = Query(1, ge=1)
):
    """
    List user's notification interactions for analytics.
    
    Ref: Module 7 - Feature 2.5 - Interaction Tracking
    """
    offset = (page - 1) * limit
    
    query = select(InteractionLog).where(
        InteractionLog.user_id == str(current_user.id)
    )
    
    if notification_id:
        query = query.where(InteractionLog.notification_id == notification_id)
    
    total = db.execute(
        select(func.count(InteractionLog.id)).where(
            InteractionLog.user_id == str(current_user.id)
        )
    ).scalar()
    
    logs = db.execute(
        query.order_by(InteractionLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).scalars().all()
    
    return InteractionLogListResponse(
        items=[InteractionLogRead.from_orm(log) for log in logs],
        total=total,
        page=page,
        page_size=limit
    )


# ============ Preference Endpoints ============

@router.get("/preferences", response_model=NotificationPreferenceRead)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    workspace_id: str = Query(..., description="Workspace ID")
) -> NotificationPreferenceRead:
    """
    Get user's notification preferences.
    
    Ref: Module 7 - Feature 2.3 - Unsubscribe Strategy
    """
    services = get_services(db)
    
    preference = await services["preference"].get_or_create_preferences(
        user_id=str(current_user.id),
        workspace_id=workspace_id
    )
    
    return NotificationPreferenceRead.from_orm(preference)


@router.put("/preferences")
async def update_preferences(
    workspace_id: str = Query(...),
    data: NotificationPreferenceUpdate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> NotificationPreferenceRead:
    """
    Update user's notification preferences.
    
    Ref: Module 7 - Feature 2.3 - Unsubscribe Strategy
    """
    services = get_services(db)
    
    preference = await services["preference"].update_preferences(
        user_id=str(current_user.id),
        workspace_id=workspace_id,
        data=data
    )
    
    return NotificationPreferenceRead.from_orm(preference)


# ============ Template Endpoints ============

@router.get("/templates", response_model=NotificationTemplateListResponse)
async def list_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    workspace_id: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1)
):
    """
    List notification templates.
    
    Ref: Module 7 - Feature 2.4 - Notification Templating Engine
    """
    offset = (page - 1) * limit
    
    query = select(NotificationTemplate).where(
        and_(
            NotificationTemplate.workspace_id == workspace_id,
            NotificationTemplate.is_active == True
        )
    )
    
    total = db.execute(
        select(func.count(NotificationTemplate.id)).where(
            NotificationTemplate.workspace_id == workspace_id
        )
    ).scalar()
    
    templates = db.execute(
        query.order_by(NotificationTemplate.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).scalars().all()
    
    return NotificationTemplateListResponse(
        items=[NotificationTemplateRead.from_orm(t) for t in templates],
        total=total,
        page=page,
        page_size=limit
    )


@router.post("/templates", response_model=NotificationTemplateRead)
async def create_template(
    data: NotificationTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new notification template.
    
    Requires: Admin or Owner role
    
    Ref: Module 7 - Feature 2.4 - Notification Templating Engine
    """
    services = get_services(db)
    
    # Check admin permission
    from app.models.workspaces import WorkspaceMember
    from app.db.enums import WorkspaceRole
    
    membership = db.execute(
        select(WorkspaceMember).where(
            and_(
                WorkspaceMember.workspace_id == data.workspace_id,
                WorkspaceMember.user_id == str(current_user.id)
            )
        )
    ).scalar_one_or_none()
    
    if not membership or membership.role not in [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only admins can create templates")
    
    template = services["template"].create_template(
        workspace_id=data.workspace_id,
        template_data=data
    )
    
    return NotificationTemplateRead.from_orm(template)


# ============ Watcher Endpoints ============

@router.post("/watchers")
async def add_watcher(
    data: WatcherCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add watcher to an entity (task, project, etc.).
    
    Ref: Module 7 - Feature 2.3 - Granular Subscription
    """
    services = get_services(db)
    
    await services["watcher"].add_watcher(
        user_id=str(current_user.id),
        workspace_id=data.workspace_id,
        data=data
    )
    
    return {"status": "ok", "message": f"Now watching {data.entity_type} {data.entity_id}"}


@router.delete("/watchers")
async def remove_watcher(
    entity_type: str = Query(...),
    entity_id: str = Query(...),
    workspace_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove watcher from an entity.
    
    Ref: Module 7 - Feature 2.3 - Granular Subscription
    """
    services = get_services(db)
    
    await services["watcher"].remove_watcher(
        user_id=str(current_user.id),
        workspace_id=workspace_id,
        entity_type=entity_type,
        entity_id=entity_id
    )
    
    return {"status": "ok", "message": "Unwatched successfully"}


@router.get("/watchers", response_model=WatcherListResponse)
async def list_watchers(
    entity_type: str = Query(...),
    entity_id: str = Query(...),
    workspace_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List watchers of an entity.
    """
    services = get_services(db)
    
    watchers = await services["watcher"].get_watchers(
        entity_type=entity_type,
        entity_id=entity_id,
        workspace_id=workspace_id
    )
    
    return WatcherListResponse(
        items=[WatcherRead.from_orm(w) for w in watchers],
        total=len(watchers)
    )


# ============ Statistics Endpoints ============

@router.get("/statistics", response_model=NotificationStatistics)
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    workspace_id: str = Query(...),
    period: str = Query("week", regex="today|week|month|all")
):
    """
    Get notification statistics for analytics.
    
    Ref: Module 7 - Feature 2.5 - Interaction Tracking
    """
    from datetime import timedelta, datetime
    from sqlalchemy import func
    
    # Determine time range
    if period == "today":
        days = 1
    elif period == "week":
        days = 7
    elif period == "month":
        days = 30
    else:
        days = None
    
    query_filter = []
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query_filter.append(Notification.created_at >= cutoff)
    
    query_filter.extend([
        Notification.recipient_id == str(current_user.id),
        Notification.workspace_id == workspace_id
    ])
    
    # Total sent
    total_sent = db.execute(
        select(func.count(Notification.id)).where(*query_filter)
    ).scalar()
    
    # Total read
    total_read = db.execute(
        select(func.count(Notification.id)).where(
            *query_filter,
            Notification.read_at.isnot(None)
        )
    ).scalar() or 0
    
    # Calculate rates
    open_rate = (total_read / total_sent * 100) if total_sent > 0 else 0
    
    # Event type distribution
    top_types = db.execute(
        select(Notification.event_type, func.count(Notification.id)).where(
            *query_filter
        ).group_by(Notification.event_type).order_by(func.count(Notification.id).desc()).limit(5)
    ).all()
    
    top_event_types = {str(t[0]): t[1] for t in top_types}
    
    # Channel distribution
    top_channels = {}
    notifications = db.execute(
        select(Notification).where(*query_filter)
    ).scalars().all()
    
    for notif in notifications:
        for channel in notif.channels_used:
            channel_str = str(channel)
            top_channels[channel_str] = top_channels.get(channel_str, 0) + 1
    
    return NotificationStatistics(
        total_sent=total_sent,
        total_read=total_read,
        open_rate=open_rate,
        click_through_rate=0,  # TODO: Calculate from interaction logs
        top_event_types=top_event_types,
        top_channels=top_channels,
        period=period
    )


# ============ WebSocket Integration (Stub) ============

@router.post("/websocket/connect")
async def websocket_connect(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark user as online for presence-aware routing.
    Called when user connects via WebSocket.
    
    Ref: Module 7 - Feature 2.2 - Presence Awareness Routing
    """
    services = get_services(db)
    services["routing"].mark_user_online(str(current_user.id))
    
    return {"status": "online"}


@router.post("/websocket/disconnect")
async def websocket_disconnect(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark user as offline.
    Called when user disconnects from WebSocket.
    
    Ref: Module 7 - Feature 2.2 - Presence Awareness Routing
    """
    services = get_services(db)
    services["routing"].mark_user_offline(str(current_user.id))
    
    return {"status": "offline"}
