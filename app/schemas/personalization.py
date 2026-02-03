"""
Module 9: User Experience Personalization Schemas

Pydantic models for validating and serializing personalization requests/responses.
Includes schemas for user settings, dashboard layouts, notification preferences, and accessibility.

Ref: Module 9 - User Experience Personalization
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.db.enums import (
    ThemeModeEnum,
    FontSizeEnum,
    FontFamilyEnum,
    InfoDensityModeEnum,
    ColorBlindnessModeEnum,
    NotificationChannelEnum,
    NotificationEventTypeEnum,
    TemplateLocaleEnum,
)


# ============ User Settings Schemas ============

class UserSettingsBase(BaseModel):
    """Base schema with common personalization fields"""
    theme_mode: Optional[str] = Field(default=ThemeModeEnum.SYSTEM.value, description="UI theme mode")
    font_size: Optional[str] = Field(default=FontSizeEnum.MEDIUM.value, description="Base font size")
    font_family: Optional[str] = Field(default=FontFamilyEnum.SYSTEM_DEFAULT.value, description="Font family")
    language: Optional[str] = Field(default=TemplateLocaleEnum.EN.value, description="Preferred language")
    info_density_mode: Optional[str] = Field(default=InfoDensityModeEnum.COMFORTABLE.value, description="Info density mode")
    sidebar_collapsed: Optional[bool] = Field(default=False, description="Sidebar collapsed state")
    color_blindness_mode: Optional[str] = Field(default=ColorBlindnessModeEnum.NORMAL.value, description="Color blindness support mode")
    dnd_enabled: Optional[bool] = Field(default=False, description="Do Not Disturb enabled")
    dnd_start_time: Optional[str] = Field(default=None, description="DND start time (HH:MM)")
    dnd_end_time: Optional[str] = Field(default=None, description="DND end time (HH:MM)")


class UserSettingsCreate(UserSettingsBase):
    """Schema for creating user settings"""
    pass


class UserSettingsUpdate(UserSettingsBase):
    """Schema for updating user settings - all fields optional"""
    pass


class UserSettingsRead(UserSettingsBase):
    """Schema for reading user settings"""
    id: UUID
    user_id: UUID
    keyboard_shortcuts: Optional[Dict[str, str]] = Field(default={}, description="Custom keyboard shortcuts")
    synced_to_client_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Dashboard Layout Schemas ============

class WidgetPosition(BaseModel):
    """Individual widget position in grid layout"""
    id: str = Field(..., description="Widget ID (e.g., 'my-tasks')")
    x: int = Field(..., ge=0, description="X position in grid")
    y: int = Field(..., ge=0, description="Y position in grid")
    w: int = Field(..., ge=1, le=12, description="Width in grid units")
    h: int = Field(..., ge=1, le=10, description="Height in grid units")
    visible: bool = Field(default=True, description="Widget visibility")


class DashboardLayoutBase(BaseModel):
    """Base dashboard layout schema"""
    name: str = Field(..., description="Layout name", max_length=255)
    layout_config: Dict[str, Any] = Field(..., description="Grid layout configuration")
    is_active: Optional[bool] = Field(default=True, description="Active layout flag")


class DashboardLayoutCreate(DashboardLayoutBase):
    """Schema for creating dashboard layout"""
    workspace_id: UUID


class DashboardLayoutUpdate(BaseModel):
    """Schema for updating dashboard layout"""
    name: Optional[str] = Field(default=None, max_length=255)
    layout_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DashboardLayoutRead(DashboardLayoutBase):
    """Schema for reading dashboard layout"""
    id: UUID
    user_id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DashboardLayoutListResponse(BaseModel):
    """Paginated list of dashboard layouts"""
    total: int
    page: int
    page_size: int
    has_more: bool
    items: List[DashboardLayoutRead]


# ============ Widget Config Schemas ============

class WidgetConfigBase(BaseModel):
    """Base widget configuration schema"""
    widget_id: str = Field(..., description="Widget identifier", max_length=100)
    config: Optional[Dict[str, Any]] = Field(default=None, description="Widget settings")
    is_hidden: Optional[bool] = Field(default=False, description="Widget hidden state")
    width: Optional[int] = None
    height: Optional[int] = None


class WidgetConfigCreate(WidgetConfigBase):
    """Schema for creating widget config"""
    pass


class WidgetConfigUpdate(BaseModel):
    """Schema for updating widget config"""
    config: Optional[Dict[str, Any]] = None
    is_hidden: Optional[bool] = None
    width: Optional[int] = None
    height: Optional[int] = None


class WidgetConfigRead(WidgetConfigBase):
    """Schema for reading widget config"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WidgetConfigListResponse(BaseModel):
    """List of widget configurations"""
    total: int
    items: List[WidgetConfigRead]


# ============ Notification Preference Schemas ============

class NotificationChannels(BaseModel):
    """Notification channel preferences"""
    in_app: bool = Field(default=True, description="In-app notifications enabled")
    email: bool = Field(default=False, description="Email notifications enabled")
    browser_push: bool = Field(default=True, description="Browser push notifications enabled")
    ignore_during_dnd: Optional[bool] = Field(default=True, description="Respect Do Not Disturb schedule")


class NotificationExceptions(BaseModel):
    """Exception rules for notification filtering"""
    urgent_only: Optional[bool] = Field(default=False, description="Only urgent notifications")
    allowed_senders: Optional[List[str]] = Field(default=None, description="List of allowed sender user IDs")


class NotificationPreferenceBase(BaseModel):
    """Base notification preference schema"""
    event_type: str = Field(..., description="Event type (mention, task_assigned, etc.)")
    channels: NotificationChannels
    is_enabled: Optional[bool] = Field(default=True, description="Event type enabled")
    exceptions: Optional[NotificationExceptions] = None


class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Schema for creating notification preference"""
    pass


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preference"""
    channels: Optional[NotificationChannels] = None
    is_enabled: Optional[bool] = None
    exceptions: Optional[NotificationExceptions] = None


class NotificationPreferenceRead(NotificationPreferenceBase):
    """Schema for reading notification preference"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferenceListResponse(BaseModel):
    """List of notification preferences"""
    total: int
    items: List[NotificationPreferenceRead]


# ============ Keyboard Shortcut Schemas ============

class KeyboardShortcutBase(BaseModel):
    """Base keyboard shortcut schema"""
    action_id: str = Field(..., description="Action identifier", max_length=100)
    key_combination: str = Field(..., description="Keyboard combination (e.g., Ctrl+K)", max_length=100)
    is_custom: Optional[bool] = Field(default=True, description="Custom override flag")


class KeyboardShortcutCreate(KeyboardShortcutBase):
    """Schema for creating keyboard shortcut"""
    pass


class KeyboardShortcutUpdate(BaseModel):
    """Schema for updating keyboard shortcut"""
    key_combination: Optional[str] = Field(default=None, max_length=100)


class KeyboardShortcutRead(KeyboardShortcutBase):
    """Schema for reading keyboard shortcut"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KeyboardShortcutListResponse(BaseModel):
    """List of keyboard shortcuts"""
    total: int
    items: List[KeyboardShortcutRead]


class KeyboardShortcutCheatsheet(BaseModel):
    """Keyboard shortcuts cheatsheet (Ref: AC 9.7 AC 1)"""
    shortcuts: List[Dict[str, str]] = Field(..., description="List of shortcuts with descriptions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "shortcuts": [
                    {"key": "Ctrl+K", "action": "Open Command Palette", "context": "Global"},
                    {"key": "C", "action": "Create Task", "context": "Dashboard"},
                    {"key": "?", "action": "Show Shortcuts", "context": "Global"},
                ]
            }
        }


# ============ Accessibility Profile Schemas ============

class VisualAccessibilitySettings(BaseModel):
    """Visual accessibility settings"""
    high_contrast_enabled: Optional[bool] = Field(default=False)
    reduce_motion_enabled: Optional[bool] = Field(default=False)
    scale_interface: Optional[float] = Field(default=1.0, ge=0.75, le=2.0)
    font_scaling: Optional[float] = Field(default=1.0, ge=0.75, le=2.0)


class AuditoryAccessibilitySettings(BaseModel):
    """Auditory accessibility settings"""
    captions_enabled: Optional[bool] = Field(default=False)
    sound_alerts_enabled: Optional[bool] = Field(default=True)
    volume_level: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)


class MotorAccessibilitySettings(BaseModel):
    """Motor accessibility settings"""
    large_click_targets: Optional[bool] = Field(default=False)
    sticky_keys_enabled: Optional[bool] = Field(default=False)
    pointer_speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0)


class CognitiveAccessibilitySettings(BaseModel):
    """Cognitive accessibility settings"""
    simplified_ui: Optional[bool] = Field(default=False)
    extra_reading_time: Optional[bool] = Field(default=False)
    focus_indicators_enhanced: Optional[bool] = Field(default=True)


class AccessibilityProfileBase(BaseModel):
    """Base accessibility profile schema"""
    visual_settings: Optional[VisualAccessibilitySettings] = Field(default=None)
    auditory_settings: Optional[AuditoryAccessibilitySettings] = Field(default=None)
    motor_settings: Optional[MotorAccessibilitySettings] = Field(default=None)
    cognitive_settings: Optional[CognitiveAccessibilitySettings] = Field(default=None)


class AccessibilityProfileCreate(AccessibilityProfileBase):
    """Schema for creating accessibility profile"""
    pass


class AccessibilityProfileUpdate(AccessibilityProfileBase):
    """Schema for updating accessibility profile"""
    pass


class AccessibilityProfileRead(AccessibilityProfileBase):
    """Schema for reading accessibility profile"""
    id: UUID
    user_id: UUID
    last_reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Localization Schemas ============

class LocalizationStringBase(BaseModel):
    """Base localization string schema"""
    key: str = Field(..., description="Translation key", max_length=255)
    language: str = Field(..., description="Language code (e.g., en-US, vi-VN)")
    value: str = Field(..., description="Translated text", max_length=2000)
    namespace: Optional[str] = Field(default="common", description="i18next namespace")


class LocalizationStringCreate(LocalizationStringBase):
    """Schema for creating localization string"""
    pass


class LocalizationStringRead(LocalizationStringBase):
    """Schema for reading localization string"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LocalizationStringListResponse(BaseModel):
    """List of localization strings"""
    total: int
    items: List[LocalizationStringRead]


class TranslationDictionary(BaseModel):
    """Complete translation dictionary for language"""
    language: str
    namespace: str
    translations: Dict[str, str] = Field(..., description="Key-value translation pairs")


# ============ Response Models ============

class PersonalizationActionResponse(BaseModel):
    """Generic response for personalization actions"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class PersonalizationSyncResponse(BaseModel):
    """Response for syncing personalization settings to client"""
    user_settings: UserSettingsRead
    dashboard_layouts: List[DashboardLayoutRead]
    accessibility_profile: Optional[AccessibilityProfileRead]
    keyboard_shortcuts: List[KeyboardShortcutRead]
    notification_preferences: List[NotificationPreferenceRead]
    last_synced_at: datetime


class PersonalizationPreferencesResponse(BaseModel):
    """Summary of all user personalization preferences"""
    theme: UserSettingsRead
    layout: Optional[DashboardLayoutRead]
    accessibility: Optional[AccessibilityProfileRead]
    notifications: Dict[str, NotificationPreferenceRead]
    shortcuts: Dict[str, KeyboardShortcutRead]
