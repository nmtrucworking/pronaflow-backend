"""
Module 9: User Experience Personalization Models

This module defines the database models for managing user personalization preferences,
including theme settings, language/localization, dashboard layouts, and notification preferences.

Features Implemented:
- Internationalization (i18n) & Localization (l10n) - AC 2.1
- Theme & Appearance customization - AC 2.2
- Customizable Dashboard layouts - AC 2.3
- Workspace layout optimization - AC 2.4
- Typographic accessibility - AC 2.5
- Notification granularity - AC 2.6
- Keyboard shortcuts management - AC 2.7
- Color vision deficiency support - AC 2.8

Ref: Module 9 - User Experience Personalization
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, JSON, Index, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base_class import Base
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
from app.db.mixins import TimestampMixin


class UserSettings(Base, TimestampMixin):
    """
    Central repository for user personalization preferences.
    Stores theme, language, accessibility, and workspace layout settings.
    
    Ref: Module 9 - Feature 2.1 to 2.8
    Business Rule 3.1: Dual-Layer Persistence (Local Storage + Database)
    """
    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Feature 2.2: Theme & Appearance (AC 1)
    theme_mode = Column(String(50), nullable=False, default=ThemeModeEnum.SYSTEM.value)
    # Feature 2.5: Typographic Accessibility (AC 1)
    font_size = Column(String(50), nullable=False, default=FontSizeEnum.MEDIUM.value)
    # Feature 2.5: Typographic Accessibility (AC 2)
    font_family = Column(String(50), nullable=False, default=FontFamilyEnum.SYSTEM_DEFAULT.value)

    # Feature 2.1: Internationalization & Localization (AC 1)
    language = Column(String(10), nullable=False, default=TemplateLocaleEnum.EN.value)
    
    # Feature 2.4: Workspace Layout Optimization (AC 2)
    info_density_mode = Column(String(50), nullable=False, default=InfoDensityModeEnum.COMFORTABLE.value)
    
    # Feature 2.4: Workspace Layout Optimization (AC 1) - Sidebar state
    sidebar_collapsed = Column(Boolean, nullable=False, default=False)
    
    # Feature 2.8: Color Vision Deficiency Support (AC 1)
    color_blindness_mode = Column(String(50), nullable=False, default=ColorBlindnessModeEnum.NORMAL.value)

    # Feature 2.6: Notification Granularity (AC 2) - Do Not Disturb settings
    dnd_enabled = Column(Boolean, nullable=False, default=False)
    dnd_start_time = Column(String(5), nullable=True)  # Format: "HH:MM"
    dnd_end_time = Column(String(5), nullable=True)    # Format: "HH:MM"

    # Feature 2.7: Keyboard Shortcuts - Custom keyboard shortcuts (JSON)
    keyboard_shortcuts = Column(JSON, nullable=True, default={})

    # Metadata for dual-layer persistence
    synced_to_client_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="personalization_settings", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_user_settings_user_id", "user_id"),
    )


class DashboardLayout(Base, TimestampMixin):
    """
    Stores custom dashboard layout configuration for each user and workspace.
    Implements Feature 2.3: Customizable Dashboard (AC 2 - Persistence)
    
    Ref: Module 9 - Feature 2.3 - Customizable Dashboard
    Business Rule: layout_config must be persisted to database for sync across devices
    """
    __tablename__ = "dashboard_layouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)

    # Layout name (e.g., "Default", "Manager View", "Developer View")
    name = Column(String(255), nullable=False, default="Default")

    # Feature 2.3: Widget Library (AC 1) - Layout configuration
    # Structure: {
    #   "grid": [
    #     {"id": "my-tasks", "x": 0, "y": 0, "w": 6, "h": 4, "visible": true},
    #     {"id": "project-progress", "x": 6, "y": 0, "w": 6, "h": 4, "visible": true},
    #     {"id": "calendar", "x": 0, "y": 4, "w": 6, "h": 5, "visible": false}
    #   ]
    # }
    layout_config = Column(JSON, nullable=False)

    # Whether this is the active layout
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    workspace = relationship("Workspace", foreign_keys=[workspace_id])

    __table_args__ = (
        Index("ix_dashboard_layouts_user_id", "user_id"),
        Index("ix_dashboard_layouts_workspace_id", "workspace_id"),
        Index("ix_dashboard_layouts_is_active", "is_active"),
        UniqueConstraint("user_id", "workspace_id", "name", name="uq_dashboard_layout_per_user_workspace"),
    )


class WidgetConfig(Base, TimestampMixin):
    """
    Individual widget configuration and preferences.
    Stores settings for specific widgets (My Tasks, Project Progress, Calendar, etc.)
    
    Ref: Module 9 - Feature 2.3 - Customizable Dashboard
    """
    __tablename__ = "widget_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Widget identifier (e.g., "my-tasks", "project-progress", "calendar")
    widget_id = Column(String(100), nullable=False)

    # Widget customization settings (JSON)
    # Example: {"refresh_interval": 300, "sort_by": "priority", "limit": 10}
    config = Column(JSON, nullable=True)

    # Whether widget is hidden (false = visible, true = hidden)
    is_hidden = Column(Boolean, nullable=False, default=False)

    # Widget size (for resizable widgets)
    width = Column(Integer, nullable=True)   # in grid units
    height = Column(Integer, nullable=True)  # in grid units

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_widget_configs_user_id", "user_id"),
        Index("ix_widget_configs_widget_id", "widget_id"),
        UniqueConstraint("user_id", "widget_id", name="uq_widget_config_per_user"),
    )


class NotificationPreference(Base, TimestampMixin):
    """
    Stores notification routing preferences per event type.
    Implements Feature 2.6: Notification Granularity (AC 1 - Multi-Channel Routing)
    
    Allows users to configure which channels (in-app, email, browser push) receive
    notifications for specific event types.
    
    Ref: Module 9 - Feature 2.6 - Notification Granularity
    """
    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Type of event (mention, task_assigned, etc.)
    event_type = Column(String(50), nullable=False)

    # Notification channel preferences (JSON)
    # Structure: {
    #   "in_app": true,
    #   "email": false,
    #   "browser_push": true,
    #   "ignore_during_dnd": true
    # }
    channels = Column(JSON, nullable=False)

    # Whether this event type is globally enabled
    is_enabled = Column(Boolean, nullable=False, default=True)

    # Exception rules for high-priority senders (e.g., only notify if from Project Manager)
    # Structure: {
    #   "urgent_only": false,
    #   "allowed_senders": ["project_manager_id", "team_lead_id"]
    # }
    exceptions = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_notification_preferences_user_id", "user_id"),
        Index("ix_notification_preferences_event_type", "event_type"),
        UniqueConstraint("user_id", "event_type", name="uq_notification_preference_per_user_event"),
    )


class KeyboardShortcut(Base, TimestampMixin):
    """
    Stores custom keyboard shortcut mappings.
    Implements Feature 2.7: Keyboard Shortcuts & Power Usage (AC 1)
    
    Allows power users to customize or override default keyboard shortcuts.
    
    Ref: Module 9 - Feature 2.7 - Keyboard Shortcuts & Power Usage
    """
    __tablename__ = "keyboard_shortcuts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Action identifier (e.g., "open_command_palette", "create_task")
    action_id = Column(String(100), nullable=False)

    # Keyboard combination (e.g., "Ctrl+K", "Cmd+Shift+P")
    key_combination = Column(String(100), nullable=False)

    # Whether this is a custom override of the default
    is_custom = Column(Boolean, nullable=False, default=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_keyboard_shortcuts_user_id", "user_id"),
        Index("ix_keyboard_shortcuts_action_id", "action_id"),
        UniqueConstraint("user_id", "action_id", name="uq_keyboard_shortcut_per_user_action"),
    )


class LocalizationString(Base, TimestampMixin):
    """
    Stores localized strings for UI labels, messages, and notifications.
    Implements Feature 2.1: Internationalization & Localization (AC 1)
    
    Supports hot-swap language switching without page reload via i18next.
    
    Ref: Module 9 - Feature 2.1 - Internationalization & Localization
    Business Rule: Fallback to English if translation unavailable
    """
    __tablename__ = "localization_strings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Translation key (e.g., "common.save_button", "errors.invalid_email")
    key = Column(String(255), nullable=False)

    # Language code (e.g., "en-US", "vi-VN")
    language = Column(String(10), nullable=False)

    # Translated text
    value = Column(String(2000), nullable=False)

    # Namespace for i18next (e.g., "common", "errors", "dashboard")
    namespace = Column(String(100), nullable=False, default="common")

    __table_args__ = (
        Index("ix_localization_strings_key", "key"),
        Index("ix_localization_strings_language", "language"),
        Index("ix_localization_strings_namespace", "namespace"),
        UniqueConstraint("key", "language", "namespace", name="uq_localization_string_per_language"),
    )


class AccessibilityProfile(Base, TimestampMixin):
    """
    Stores comprehensive accessibility settings grouped by category.
    Centralizes Features 2.2, 2.5, and 2.8 accessibility configurations.
    
    Ref: Module 9 - Features 2.2, 2.5, 2.8
    Design: Allows future expansion for additional accessibility features
    """
    __tablename__ = "accessibility_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Visual accessibility settings
    # Structure: {
    #   "high_contrast_enabled": false,
    #   "reduce_motion_enabled": false,
    #   "scale_interface": 1.0,
    #   "font_scaling": 1.0
    # }
    visual_settings = Column(JSON, nullable=False, default={})

    # Auditory accessibility settings
    # Structure: {
    #   "captions_enabled": false,
    #   "sound_alerts_enabled": true,
    #   "volume_level": 0.8
    # }
    auditory_settings = Column(JSON, nullable=False, default={})

    # Motor accessibility settings
    # Structure: {
    #   "large_click_targets": false,
    #   "sticky_keys_enabled": false,
    #   "pointer_speed": 1.0
    # }
    motor_settings = Column(JSON, nullable=False, default={})

    # Cognitive accessibility settings
    # Structure: {
    #   "simplified_ui": false,
    #   "extra_reading_time": false,
    #   "focus_indicators_enhanced": true
    # }
    cognitive_settings = Column(JSON, nullable=False, default={})

    # Last accessibility audit/review date
    last_reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="accessibility_profile", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_accessibility_profiles_user_id", "user_id"),
    )
