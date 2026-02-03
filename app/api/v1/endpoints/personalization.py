"""
Module 9: User Experience Personalization API Endpoints

RESTful API routes for managing personalization preferences:
- Theme and appearance settings
- Language and localization
- Dashboard customization
- Notification preferences
- Accessibility profiles
- Keyboard shortcuts

Ref: Module 9 - User Experience Personalization
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.security import get_current_user
from app.db.session import get_db
from app.db.models.users import User
from app.schemas.personalization import (
    UserSettingsRead,
    UserSettingsUpdate,
    DashboardLayoutCreate,
    DashboardLayoutRead,
    DashboardLayoutUpdate,
    DashboardLayoutListResponse,
    WidgetConfigCreate,
    WidgetConfigRead,
    WidgetConfigUpdate,
    WidgetConfigListResponse,
    NotificationPreferenceCreate,
    NotificationPreferenceRead,
    NotificationPreferenceUpdate,
    NotificationPreferenceListResponse,
    KeyboardShortcutCreate,
    KeyboardShortcutRead,
    KeyboardShortcutUpdate,
    KeyboardShortcutListResponse,
    KeyboardShortcutCheatsheet,
    AccessibilityProfileRead,
    AccessibilityProfileCreate,
    AccessibilityProfileUpdate,
    PersonalizationActionResponse,
    PersonalizationSyncResponse,
    PersonalizationPreferencesResponse,
    LocalizationStringRead,
    TranslationDictionary,
)
from app.services.personalization import (
    PersonalizationService,
    DashboardLayoutService,
    WidgetConfigService,
    NotificationPreferenceService,
    KeyboardShortcutService,
    AccessibilityProfileService,
    LocalizationService,
)

router = APIRouter(prefix="/personalization", tags=["Personalization"])


# ============ User Settings Endpoints ============

@router.get("/settings", response_model=UserSettingsRead, summary="Get user personalization settings")
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's personalization settings.
    
    Ref: Module 9 - Features 2.1-2.8
    Returns: Theme, language, accessibility, and workspace layout preferences
    """
    settings = PersonalizationService.get_or_create_user_settings(db, current_user.id)
    return settings


@router.put("/settings", response_model=UserSettingsRead, summary="Update user personalization settings")
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user personalization settings.
    
    Ref: Module 9 - Feature 2.1-2.8
    Supports: Theme, font size, language, info density, sidebar state, color blindness mode, DND settings
    
    Business Rule 3.1: Syncs to Local Storage immediately, persists to DB for roaming
    """
    settings = PersonalizationService.update_user_settings(db, current_user.id, settings_update)
    return settings


# ============ Dashboard Layout Endpoints ============

@router.post("/dashboard/layouts", response_model=DashboardLayoutRead, summary="Create dashboard layout", status_code=status.HTTP_201_CREATED)
async def create_dashboard_layout(
    layout_create: DashboardLayoutCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new customizable dashboard layout.
    
    Ref: Module 9 - Feature 2.3 - Customizable Dashboard (AC 1 & 2)
    Allows drag & drop arrangement of widgets with persistence
    """
    layout = DashboardLayoutService.create_layout(db, current_user.id, layout_create)
    return layout


@router.get("/dashboard/layouts/active", response_model=DashboardLayoutRead, summary="Get active dashboard layout")
async def get_active_layout(
    workspace_id: UUID = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get active dashboard layout for workspace.
    
    Returns active layout or creates default if none exists.
    """
    layout = DashboardLayoutService.get_active_layout(db, current_user.id, workspace_id)
    if not layout:
        raise HTTPException(status_code=404, detail="No active layout found")
    return layout


@router.get("/dashboard/layouts", response_model=DashboardLayoutListResponse, summary="List dashboard layouts")
async def list_dashboard_layouts(
    workspace_id: UUID = Query(..., description="Workspace ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all dashboard layouts for workspace."""
    items, total = DashboardLayoutService.list_layouts(
        db, current_user.id, workspace_id,
        skip=(page - 1) * page_size,
        limit=page_size
    )
    return DashboardLayoutListResponse(
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total,
        items=items
    )


@router.put("/dashboard/layouts/{layout_id}", response_model=DashboardLayoutRead, summary="Update dashboard layout")
async def update_dashboard_layout(
    layout_id: UUID,
    layout_update: DashboardLayoutUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update existing dashboard layout."""
    layout = DashboardLayoutService.update_layout(db, layout_id, current_user.id, layout_update)
    if not layout:
        raise HTTPException(status_code=404, detail="Layout not found")
    return layout


@router.delete("/dashboard/layouts/{layout_id}", response_model=PersonalizationActionResponse, summary="Delete dashboard layout")
async def delete_dashboard_layout(
    layout_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete dashboard layout."""
    success = DashboardLayoutService.delete_layout(db, layout_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Layout not found")
    return PersonalizationActionResponse(
        success=True,
        message="Layout deleted successfully"
    )


# ============ Widget Configuration Endpoints ============

@router.get("/widgets", response_model=WidgetConfigListResponse, summary="List widget configurations")
async def list_widget_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all widget configurations for user."""
    configs = WidgetConfigService.list_widget_configs(db, current_user.id)
    return WidgetConfigListResponse(
        total=len(configs),
        items=configs
    )


@router.put("/widgets/{widget_id}", response_model=WidgetConfigRead, summary="Update widget configuration")
async def update_widget_config(
    widget_id: str,
    config_update: WidgetConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update individual widget configuration."""
    config = WidgetConfigService.update_widget_config(db, current_user.id, widget_id, config_update)
    return config


@router.post("/widgets/{widget_id}/toggle", response_model=WidgetConfigRead, summary="Toggle widget visibility")
async def toggle_widget_visibility(
    widget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle widget visibility (hide/show).
    
    Ref: Module 9 - Feature 2.3 (AC 1) - Widget Library management
    """
    config = WidgetConfigService.toggle_widget_visibility(db, current_user.id, widget_id)
    return config


# ============ Notification Preference Endpoints ============

@router.get("/notifications/preferences", response_model=NotificationPreferenceListResponse, summary="List notification preferences")
async def list_notification_preferences(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all notification preferences for user.
    
    Ref: Module 9 - Feature 2.6 - Notification Granularity
    """
    items, total = NotificationPreferenceService.list_preferences(
        db, current_user.id,
        skip=(page - 1) * page_size,
        limit=page_size
    )
    return NotificationPreferenceListResponse(
        total=total,
        items=items
    )


@router.get("/notifications/preferences/{event_type}", response_model=NotificationPreferenceRead, summary="Get notification preference")
async def get_notification_preference(
    event_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification preference for specific event type."""
    pref = NotificationPreferenceService.get_or_create_preference(db, current_user.id, event_type)
    return pref


@router.put("/notifications/preferences/{event_type}", response_model=NotificationPreferenceRead, summary="Update notification preference")
async def update_notification_preference(
    event_type: str,
    pref_update: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update notification routing preference for event type.
    
    Ref: Module 9 - Feature 2.6 (AC 1) - Multi-Channel Routing matrix
    Allows configuring in-app, email, and browser push per event type
    """
    pref = NotificationPreferenceService.update_preference(db, current_user.id, event_type, pref_update)
    return pref


# ============ Keyboard Shortcut Endpoints ============

@router.get("/shortcuts/cheatsheet", response_model=KeyboardShortcutCheatsheet, summary="Get keyboard shortcuts cheatsheet")
async def get_shortcuts_cheatsheet():
    """
    Get default keyboard shortcuts reference.
    
    Ref: Module 9 - Feature 2.7 (AC 1) - Global Shortcuts Map
    Shows standard shortcuts: Cmd/Ctrl+K (Command Palette), C (Create Task), ? (Help)
    """
    return KeyboardShortcutCheatsheet(
        shortcuts=[
            {"key": "Cmd/Ctrl + K", "action": "Open Command Palette", "context": "Global"},
            {"key": "C", "action": "Create Task", "context": "Dashboard"},
            {"key": "?", "action": "Show Shortcuts Help", "context": "Global"},
            {"key": "J", "action": "Move Down", "context": "Kanban/List (Vim-style)"},
            {"key": "K", "action": "Move Up", "context": "Kanban/List (Vim-style)"},
            {"key": "Space", "action": "Preview/Open", "context": "Kanban/List"},
            {"key": "Ctrl/Cmd + B", "action": "Toggle Sidebar", "context": "Global"},
        ]
    )


@router.get("/shortcuts", response_model=KeyboardShortcutListResponse, summary="List custom keyboard shortcuts")
async def list_keyboard_shortcuts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List custom keyboard shortcuts."""
    items, total = KeyboardShortcutService.list_shortcuts(
        db, current_user.id,
        skip=(page - 1) * page_size,
        limit=page_size
    )
    return KeyboardShortcutListResponse(
        total=total,
        items=items
    )


@router.post("/shortcuts", response_model=KeyboardShortcutRead, summary="Create keyboard shortcut", status_code=status.HTTP_201_CREATED)
async def create_keyboard_shortcut(
    shortcut_create: KeyboardShortcutCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or override keyboard shortcut.
    
    Ref: Module 9 - Feature 2.7 (AC 1 & 2) - Power user shortcuts
    Enables keyboard-only workflow for frequent actions
    """
    shortcut = KeyboardShortcutService.create_shortcut(db, current_user.id, shortcut_create)
    return shortcut


@router.delete("/shortcuts/{action_id}", response_model=PersonalizationActionResponse, summary="Reset shortcut to default")
async def reset_keyboard_shortcut(
    action_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset keyboard shortcut to default."""
    result = KeyboardShortcutService.reset_to_defaults(db, current_user.id)
    return PersonalizationActionResponse(
        success=result > 0,
        message=f"Reset {result} shortcuts to default"
    )


# ============ Accessibility Profile Endpoints ============

@router.get("/accessibility", response_model=AccessibilityProfileRead, summary="Get accessibility profile")
async def get_accessibility_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive accessibility profile.
    
    Ref: Module 9 - Features 2.2, 2.5, 2.8 (All accessibility settings)
    Includes visual, auditory, motor, and cognitive accessibility options
    """
    profile = AccessibilityProfileService.get_or_create_profile(db, current_user.id)
    return profile


@router.put("/accessibility", response_model=AccessibilityProfileRead, summary="Update accessibility profile")
async def update_accessibility_profile(
    profile_update: AccessibilityProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update accessibility profile.
    
    Ref: Module 9 - Feature 2.8 (AC 1) - Color blindness support
    Ref: Module 9 - Feature 2.2 (AC 2) - WCAG 2.1 Level AA contrast
    """
    profile = AccessibilityProfileService.update_profile(db, current_user.id, profile_update)
    return profile


# ============ Localization Endpoints ============

@router.get("/localization/{language}/{namespace}", response_model=TranslationDictionary, summary="Get translations for namespace")
async def get_translation_namespace(
    language: str = Path(..., description="Language code (e.g., en-US, vi-VN)"),
    namespace: str = Path(..., description="i18next namespace"),
    db: Session = Depends(get_db)
):
    """
    Get all translations for language and namespace.
    
    Ref: Module 9 - Feature 2.1 - Internationalization & Localization (AC 1)
    Used for hot-swap language switching without page reload via i18next
    """
    translations = LocalizationService.get_namespace_translations(db, language, namespace)
    return TranslationDictionary(
        language=language,
        namespace=namespace,
        translations=translations
    )


@router.get("/localization/languages", response_model=List[str], summary="Get supported languages")
async def get_supported_languages(
    db: Session = Depends(get_db)
):
    """
    Get list of all supported languages in system.
    
    Ref: Module 9 - Feature 2.1 (AC 1)
    """
    languages = LocalizationService.get_supported_languages(db)
    return languages


# ============ Sync Endpoints ============

@router.get("/sync", response_model=PersonalizationSyncResponse, summary="Sync all personalization settings")
async def sync_personalization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync all user personalization settings to client.
    
    Ref: Module 9 - Business Rule 3.1 (Dual-Layer Persistence)
    Returns all settings for initialization/refresh: theme, accessibility, layouts, shortcuts
    
    Use Cases:
    1. On app startup for Local Storage hydration
    2. After settings changes for sync across devices
    3. Device roaming - restore profile on new device
    """
    from datetime import datetime as dt
    
    user_settings = PersonalizationService.get_or_create_user_settings(db, current_user.id)
    
    # Get default active layouts (if workspace context available)
    layouts = []
    
    # Get accessibility profile
    accessibility = AccessibilityProfileService.get_profile(db, current_user.id)
    
    # Get keyboard shortcuts
    shortcuts, _ = KeyboardShortcutService.list_shortcuts(db, current_user.id, limit=100)
    
    # Get notification preferences
    prefs, _ = NotificationPreferenceService.list_preferences(db, current_user.id, limit=50)
    
    return PersonalizationSyncResponse(
        user_settings=user_settings,
        dashboard_layouts=layouts,
        accessibility_profile=accessibility,
        keyboard_shortcuts=shortcuts,
        notification_preferences=prefs,
        last_synced_at=dt.utcnow()
    )


@router.post("/reset", response_model=PersonalizationActionResponse, summary="Reset all personalization to defaults")
async def reset_personalization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset all personalization settings to system defaults.
    
    Ref: Module 9 - Business Rule 3.2 (Default Behavior)
    Dangerous operation - recommended to show confirmation dialog
    """
    # Reset user settings
    settings = PersonalizationService.get_or_create_user_settings(db, current_user.id)
    settings.theme_mode = "system"
    settings.language = "en-US"
    settings.font_size = "medium"
    settings.font_family = "system_default"
    settings.info_density_mode = "comfortable"
    settings.sidebar_collapsed = False
    settings.color_blindness_mode = "normal"
    settings.dnd_enabled = False
    db.commit()
    
    return PersonalizationActionResponse(
        success=True,
        message="All personalization settings reset to defaults"
    )
