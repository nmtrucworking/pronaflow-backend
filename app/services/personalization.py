"""
Module 9: User Experience Personalization Services

Business logic for managing user personalization preferences including:
- Theme and appearance settings
- Internationalization and localization
- Dashboard customization
- Notification preferences
- Accessibility profiles
- Keyboard shortcuts

Ref: Module 9 - User Experience Personalization
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, time

from app.db.models.personalization import (
    UserSettings,
    DashboardLayout,
    WidgetConfig,
    NotificationPreference,
    KeyboardShortcut,
    LocalizationString,
    AccessibilityProfile,
)
from app.schemas.personalization import (
    UserSettingsCreate,
    UserSettingsUpdate,
    UserSettingsRead,
    DashboardLayoutCreate,
    DashboardLayoutUpdate,
    DashboardLayoutRead,
    WidgetConfigCreate,
    WidgetConfigUpdate,
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
    KeyboardShortcutCreate,
    KeyboardShortcutUpdate,
    AccessibilityProfileCreate,
    AccessibilityProfileUpdate,
)
from app.db.enums import TemplateLocaleEnum, ThemeModeEnum
from app.core.config import settings


class PersonalizationService:
    """
    Central service for managing user personalization settings.
    Implements Features 2.1-2.8 of Module 9.
    
    Ref: Module 9 - Business Rule 3.1 (Dual-Layer Persistence)
    """

    @staticmethod
    def get_or_create_user_settings(db: Session, user_id: UUID) -> UserSettings:
        """
        Get user settings or create defaults.
        
        Ref: Module 9 - Business Rule 3.2 (Default Behavior)
        Auto-detect language from browser navigator.language and theme from prefers-color-scheme
        """
        settings_obj = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        
        if not settings_obj:
            settings_obj = UserSettings(
                user_id=user_id,
                theme_mode=ThemeModeEnum.SYSTEM.value,
                language=TemplateLocaleEnum.EN.value,
            )
            db.add(settings_obj)
            db.commit()
            db.refresh(settings_obj)
        
        return settings_obj

    @staticmethod
    def update_user_settings(db: Session, user_id: UUID, settings_update: UserSettingsUpdate) -> UserSettings:
        """
        Update user personalization settings.
        
        Ref: Module 9 - Feature 2.1-2.8 (Multiple settings types)
        """
        settings_obj = PersonalizationService.get_or_create_user_settings(db, user_id)
        
        update_data = settings_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(settings_obj, key, value)
        
        settings_obj.synced_to_client_at = datetime.utcnow()
        db.commit()
        db.refresh(settings_obj)
        
        return settings_obj

    @staticmethod
    def get_user_settings(db: Session, user_id: UUID) -> Optional[UserSettings]:
        """Retrieve user personalization settings."""
        return db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

    @staticmethod
    def validate_dnd_time_format(time_str: str) -> bool:
        """Validate Do Not Disturb time format (HH:MM)."""
        try:
            time.fromisoformat(time_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_in_dnd_window(user_settings: UserSettings) -> bool:
        """
        Check if current time is within Do Not Disturb window.
        
        Ref: Module 9 - Feature 2.6 - Notification Granularity (AC 2)
        """
        if not user_settings.dnd_enabled or not user_settings.dnd_start_time or not user_settings.dnd_end_time:
            return False
        
        current_time = datetime.utcnow().time()
        start_time = time.fromisoformat(user_settings.dnd_start_time)
        end_time = time.fromisoformat(user_settings.dnd_end_time)
        
        # Handle case where end time is next day (e.g., 22:00 to 08:00)
        if start_time < end_time:
            return start_time <= current_time <= end_time
        else:
            return current_time >= start_time or current_time <= end_time


class DashboardLayoutService:
    """
    Service for managing customizable dashboard layouts.
    
    Ref: Module 9 - Feature 2.3 - Customizable Dashboard
    Business Rule 3.1: Layout configuration persisted to database for sync
    """

    @staticmethod
    def create_layout(db: Session, user_id: UUID, layout_create: DashboardLayoutCreate) -> DashboardLayout:
        """
        Create new dashboard layout.
        
        Ref: Module 9 - Feature 2.3 (AC 2 - Persistence)
        """
        # Deactivate other layouts for this user+workspace if this is active
        if layout_create.is_active:
            db.query(DashboardLayout).filter(
                DashboardLayout.user_id == user_id,
                DashboardLayout.workspace_id == layout_create.workspace_id,
                DashboardLayout.is_active == True
            ).update({DashboardLayout.is_active: False})

        layout = DashboardLayout(
            user_id=user_id,
            name=layout_create.name,
            layout_config=layout_create.layout_config,
            is_active=layout_create.is_active if layout_create.is_active is not None else True,
            workspace_id=layout_create.workspace_id,
        )
        db.add(layout)
        db.commit()
        db.refresh(layout)
        return layout

    @staticmethod
    def get_active_layout(db: Session, user_id: UUID, workspace_id: UUID) -> Optional[DashboardLayout]:
        """Get active dashboard layout for user in workspace."""
        return db.query(DashboardLayout).filter(
            DashboardLayout.user_id == user_id,
            DashboardLayout.workspace_id == workspace_id,
            DashboardLayout.is_active == True
        ).first()

    @staticmethod
    def update_layout(db: Session, layout_id: UUID, user_id: UUID, layout_update: DashboardLayoutUpdate) -> DashboardLayout:
        """Update dashboard layout."""
        layout = db.query(DashboardLayout).filter(
            DashboardLayout.id == layout_id,
            DashboardLayout.user_id == user_id
        ).first()
        
        if not layout:
            return None
        
        update_data = layout_update.model_dump(exclude_unset=True)
        
        # If activating this layout, deactivate others
        if update_data.get("is_active") == True:
            db.query(DashboardLayout).filter(
                DashboardLayout.user_id == user_id,
                DashboardLayout.workspace_id == layout.workspace_id,
                DashboardLayout.is_active == True,
                DashboardLayout.id != layout_id
            ).update({DashboardLayout.is_active: False})
        
        for key, value in update_data.items():
            if value is not None:
                setattr(layout, key, value)
        
        db.commit()
        db.refresh(layout)
        return layout

    @staticmethod
    def list_layouts(db: Session, user_id: UUID, workspace_id: UUID, skip: int = 0, limit: int = 20) -> tuple:
        """List dashboard layouts for user in workspace."""
        query = db.query(DashboardLayout).filter(
            DashboardLayout.user_id == user_id,
            DashboardLayout.workspace_id == workspace_id
        )
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        
        return items, total

    @staticmethod
    def delete_layout(db: Session, layout_id: UUID, user_id: UUID) -> bool:
        """Delete dashboard layout."""
        layout = db.query(DashboardLayout).filter(
            DashboardLayout.id == layout_id,
            DashboardLayout.user_id == user_id
        ).first()
        
        if not layout:
            return False
        
        db.delete(layout)
        db.commit()
        return True


class WidgetConfigService:
    """
    Service for managing individual widget configurations.
    
    Ref: Module 9 - Feature 2.3 - Customizable Dashboard
    """

    @staticmethod
    def get_or_create_widget_config(db: Session, user_id: UUID, widget_id: str) -> WidgetConfig:
        """Get widget config or create with defaults."""
        config = db.query(WidgetConfig).filter(
            WidgetConfig.user_id == user_id,
            WidgetConfig.widget_id == widget_id
        ).first()
        
        if not config:
            config = WidgetConfig(
                user_id=user_id,
                widget_id=widget_id,
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        
        return config

    @staticmethod
    def update_widget_config(db: Session, user_id: UUID, widget_id: str, config_update: WidgetConfigUpdate) -> WidgetConfig:
        """Update widget configuration."""
        config = WidgetConfigService.get_or_create_widget_config(db, user_id, widget_id)
        
        update_data = config_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(config, key, value)
        
        db.commit()
        db.refresh(config)
        return config

    @staticmethod
    def list_widget_configs(db: Session, user_id: UUID) -> List[WidgetConfig]:
        """List all widget configs for user."""
        return db.query(WidgetConfig).filter(WidgetConfig.user_id == user_id).all()

    @staticmethod
    def toggle_widget_visibility(db: Session, user_id: UUID, widget_id: str) -> WidgetConfig:
        """Toggle widget visibility (AC 2.3 AC 1)."""
        config = WidgetConfigService.get_or_create_widget_config(db, user_id, widget_id)
        config.is_hidden = not config.is_hidden
        db.commit()
        db.refresh(config)
        return config


class NotificationPreferenceService:
    """
    Service for managing notification routing preferences.
    
    Ref: Module 9 - Feature 2.6 - Notification Granularity
    Implements multi-channel routing matrix (in-app, email, browser push)
    """

    @staticmethod
    def get_preference(db: Session, user_id: UUID, event_type: str) -> Optional[NotificationPreference]:
        """Get notification preference for specific event type."""
        return db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id,
            NotificationPreference.event_type == event_type
        ).first()

    @staticmethod
    def get_or_create_preference(db: Session, user_id: UUID, event_type: str) -> NotificationPreference:
        """Get preference or create with defaults."""
        pref = NotificationPreferenceService.get_preference(db, user_id, event_type)
        
        if not pref:
            pref = NotificationPreference(
                user_id=user_id,
                event_type=event_type,
                channels={"in_app": True, "email": False, "browser_push": True, "ignore_during_dnd": True},
            )
            db.add(pref)
            db.commit()
            db.refresh(pref)
        
        return pref

    @staticmethod
    def update_preference(db: Session, user_id: UUID, event_type: str, pref_update: NotificationPreferenceUpdate) -> NotificationPreference:
        """Update notification preference."""
        pref = NotificationPreferenceService.get_or_create_preference(db, user_id, event_type)
        
        update_data = pref_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(pref, key, value)
        
        db.commit()
        db.refresh(pref)
        return pref

    @staticmethod
    def list_preferences(db: Session, user_id: UUID, skip: int = 0, limit: int = 50) -> tuple:
        """List notification preferences for user."""
        query = db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def should_send_notification(db: Session, user_id: UUID, event_type: str, channel: str) -> bool:
        """
        Determine if notification should be sent on channel.
        
        Considers:
        1. Event type enabled
        2. Channel enabled
        3. Do Not Disturb status (for push/email channels)
        4. Exception rules
        
        Ref: Module 9 - Feature 2.6 (AC 1 & 2)
        """
        pref = NotificationPreferenceService.get_preference(db, user_id, event_type)
        
        # Default to True if no preference set
        if not pref:
            return True
        
        # Check if event type is globally enabled
        if not pref.is_enabled:
            return False
        
        # Check channel
        channels = pref.channels or {}
        if not channels.get(channel, True):
            return False
        
        # Check Do Not Disturb
        if channel in ["email", "browser_push"] and channels.get("ignore_during_dnd", True):
            user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            if user_settings and PersonalizationService.is_in_dnd_window(user_settings):
                # Check if this is urgent and sender is allowed
                exceptions = pref.exceptions or {}
                if not exceptions.get("urgent_only", False):
                    return False
        
        return True


class KeyboardShortcutService:
    """
    Service for managing keyboard shortcuts.
    
    Ref: Module 9 - Feature 2.7 - Keyboard Shortcuts & Power Usage
    """

    @staticmethod
    def create_shortcut(db: Session, user_id: UUID, shortcut_create: KeyboardShortcutCreate) -> KeyboardShortcut:
        """Create custom keyboard shortcut."""
        # Check if action already has a custom shortcut
        existing = db.query(KeyboardShortcut).filter(
            KeyboardShortcut.user_id == user_id,
            KeyboardShortcut.action_id == shortcut_create.action_id
        ).first()
        
        if existing:
            existing.key_combination = shortcut_create.key_combination
            db.commit()
            db.refresh(existing)
            return existing
        
        shortcut = KeyboardShortcut(
            user_id=user_id,
            action_id=shortcut_create.action_id,
            key_combination=shortcut_create.key_combination,
            is_custom=shortcut_create.is_custom,
        )
        db.add(shortcut)
        db.commit()
        db.refresh(shortcut)
        return shortcut

    @staticmethod
    def get_shortcut(db: Session, user_id: UUID, action_id: str) -> Optional[KeyboardShortcut]:
        """Get keyboard shortcut for action."""
        return db.query(KeyboardShortcut).filter(
            KeyboardShortcut.user_id == user_id,
            KeyboardShortcut.action_id == action_id
        ).first()

    @staticmethod
    def list_shortcuts(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> tuple:
        """List keyboard shortcuts for user."""
        query = db.query(KeyboardShortcut).filter(KeyboardShortcut.user_id == user_id)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def reset_to_defaults(db: Session, user_id: UUID) -> int:
        """
        Reset all custom shortcuts to defaults.
        
        Returns: Number of shortcuts deleted
        """
        result = db.query(KeyboardShortcut).filter(
            KeyboardShortcut.user_id == user_id,
            KeyboardShortcut.is_custom == True
        ).delete()
        db.commit()
        return result


class AccessibilityProfileService:
    """
    Service for managing comprehensive accessibility profiles.
    
    Ref: Module 9 - Features 2.2, 2.5, 2.8 (All accessibility features)
    """

    @staticmethod
    def get_or_create_profile(db: Session, user_id: UUID) -> AccessibilityProfile:
        """Get accessibility profile or create with defaults."""
        profile = db.query(AccessibilityProfile).filter(AccessibilityProfile.user_id == user_id).first()
        
        if not profile:
            profile = AccessibilityProfile(
                user_id=user_id,
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        return profile

    @staticmethod
    def update_profile(db: Session, user_id: UUID, profile_update: AccessibilityProfileUpdate) -> AccessibilityProfile:
        """Update accessibility profile."""
        profile = AccessibilityProfileService.get_or_create_profile(db, user_id)
        
        update_data = profile_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(profile, key, value)
        
        profile.last_reviewed_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def get_profile(db: Session, user_id: UUID) -> Optional[AccessibilityProfile]:
        """Get accessibility profile."""
        return db.query(AccessibilityProfile).filter(AccessibilityProfile.user_id == user_id).first()


class LocalizationService:
    """
    Service for managing localization strings and translations.
    
    Ref: Module 9 - Feature 2.1 - Internationalization & Localization
    Supports hot-swap language switching via i18next
    """

    @staticmethod
    def get_translation(db: Session, key: str, language: str, namespace: str = "common") -> Optional[str]:
        """
        Get translated string, with fallback to English.
        
        Ref: Module 9 - Feature 2.1 (AC 1) - Fallback mechanism
        """
        localization = db.query(LocalizationString).filter(
            LocalizationString.key == key,
            LocalizationString.language == language,
            LocalizationString.namespace == namespace
        ).first()
        
        if localization:
            return localization.value
        
        # Fallback to English (en-US) if not found
        if language != TemplateLocaleEnum.EN.value:
            localization = db.query(LocalizationString).filter(
                LocalizationString.key == key,
            LocalizationString.language == TemplateLocaleEnum.EN.value,
                LocalizationString.namespace == namespace
            ).first()
            
            if localization:
                return localization.value
        
        # Return key itself if no translation found
        return key

    @staticmethod
    def get_namespace_translations(db: Session, language: str, namespace: str = "common") -> Dict[str, str]:
        """
        Get all translations for namespace and language.
        Used for i18next hot-swap loading.
        """
        localizations = db.query(LocalizationString).filter(
            LocalizationString.language == language,
            LocalizationString.namespace == namespace
        ).all()
        
        return {l.key: l.value for l in localizations}

    @staticmethod
    def set_translation(db: Session, key: str, language: str, value: str, namespace: str = "common") -> LocalizationString:
        """Set or update translation."""
        localization = db.query(LocalizationString).filter(
            LocalizationString.key == key,
            LocalizationString.language == language,
            LocalizationString.namespace == namespace
        ).first()
        
        if localization:
            localization.value = value
        else:
            localization = LocalizationString(
                key=key,
                language=language,
                value=value,
                namespace=namespace,
            )
            db.add(localization)
        
        db.commit()
        db.refresh(localization)
        return localization

    @staticmethod
    def bulk_set_translations(db: Session, language: str, translations: Dict[str, str], namespace: str = "common") -> int:
        """
        Bulk set translations for language/namespace.
        
        Returns: Number of translations created/updated
        """
        count = 0
        for key, value in translations.items():
            LocalizationService.set_translation(db, key, language, value, namespace)
            count += 1
        
        return count

    @staticmethod
    def get_supported_languages(db: Session) -> List[str]:
        """Get list of supported languages."""
        languages = db.query(LocalizationString.language).distinct().all()
        return [lang[0] for lang in languages]
