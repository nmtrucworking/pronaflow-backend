"""Add Module 9: User Experience Personalization tables

Revision ID: module9_personalization
Revises: module8_archiving
Create Date: 2026-02-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'module9_personalization'
down_revision = 'module8_archiving'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create Module 9 tables for personalization."""
    
    # Create user_settings table
    op.create_table(
        'user_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('theme_mode', sa.String(50), nullable=False, server_default='system'),
        sa.Column('font_size', sa.String(50), nullable=False, server_default='medium'),
        sa.Column('font_family', sa.String(50), nullable=False, server_default='system_default'),
        sa.Column('language', sa.String(10), nullable=False, server_default='en-US'),
        sa.Column('info_density_mode', sa.String(50), nullable=False, server_default='comfortable'),
        sa.Column('sidebar_collapsed', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('color_blindness_mode', sa.String(50), nullable=False, server_default='normal'),
        sa.Column('dnd_enabled', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('dnd_start_time', sa.String(5), nullable=True),
        sa.Column('dnd_end_time', sa.String(5), nullable=True),
        sa.Column('keyboard_shortcuts', postgresql.JSON, nullable=True),
        sa.Column('synced_to_client_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_settings_user_id')
    )
    op.create_index('ix_user_settings_user_id', 'user_settings', ['user_id'])
    
    # Create dashboard_layouts table
    op.create_table(
        'dashboard_layouts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, server_default='Default'),
        sa.Column('layout_config', postgresql.JSON, nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'workspace_id', 'name', name='uq_dashboard_layout_per_user_workspace')
    )
    op.create_index('ix_dashboard_layouts_user_id', 'dashboard_layouts', ['user_id'])
    op.create_index('ix_dashboard_layouts_workspace_id', 'dashboard_layouts', ['workspace_id'])
    op.create_index('ix_dashboard_layouts_is_active', 'dashboard_layouts', ['is_active'])
    
    # Create widget_configs table
    op.create_table(
        'widget_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('widget_id', sa.String(100), nullable=False),
        sa.Column('config', postgresql.JSON, nullable=True),
        sa.Column('is_hidden', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('width', sa.Integer, nullable=True),
        sa.Column('height', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'widget_id', name='uq_widget_config_per_user')
    )
    op.create_index('ix_widget_configs_user_id', 'widget_configs', ['user_id'])
    op.create_index('ix_widget_configs_widget_id', 'widget_configs', ['widget_id'])
    
    # Create notification_preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('channels', postgresql.JSON, nullable=False),
        sa.Column('is_enabled', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('exceptions', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'event_type', name='uq_notification_preference_per_user_event')
    )
    op.create_index('ix_notification_preferences_user_id', 'notification_preferences', ['user_id'])
    op.create_index('ix_notification_preferences_event_type', 'notification_preferences', ['event_type'])
    
    # Create keyboard_shortcuts table
    op.create_table(
        'keyboard_shortcuts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_id', sa.String(100), nullable=False),
        sa.Column('key_combination', sa.String(100), nullable=False),
        sa.Column('is_custom', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'action_id', name='uq_keyboard_shortcut_per_user_action')
    )
    op.create_index('ix_keyboard_shortcuts_user_id', 'keyboard_shortcuts', ['user_id'])
    op.create_index('ix_keyboard_shortcuts_action_id', 'keyboard_shortcuts', ['action_id'])
    
    # Create localization_strings table
    op.create_table(
        'localization_strings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('language', sa.String(10), nullable=False),
        sa.Column('value', sa.String(2000), nullable=False),
        sa.Column('namespace', sa.String(100), nullable=False, server_default='common'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key', 'language', 'namespace', name='uq_localization_string_per_language')
    )
    op.create_index('ix_localization_strings_key', 'localization_strings', ['key'])
    op.create_index('ix_localization_strings_language', 'localization_strings', ['language'])
    op.create_index('ix_localization_strings_namespace', 'localization_strings', ['namespace'])
    
    # Create accessibility_profiles table
    op.create_table(
        'accessibility_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('visual_settings', postgresql.JSON, nullable=False, server_default='{}'),
        sa.Column('auditory_settings', postgresql.JSON, nullable=False, server_default='{}'),
        sa.Column('motor_settings', postgresql.JSON, nullable=False, server_default='{}'),
        sa.Column('cognitive_settings', postgresql.JSON, nullable=False, server_default='{}'),
        sa.Column('last_reviewed_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_accessibility_profile_user_id')
    )
    op.create_index('ix_accessibility_profiles_user_id', 'accessibility_profiles', ['user_id'])


def downgrade() -> None:
    """Revert Module 9 tables."""
    
    op.drop_index('ix_accessibility_profiles_user_id', table_name='accessibility_profiles')
    op.drop_table('accessibility_profiles')
    
    op.drop_index('ix_localization_strings_namespace', table_name='localization_strings')
    op.drop_index('ix_localization_strings_language', table_name='localization_strings')
    op.drop_index('ix_localization_strings_key', table_name='localization_strings')
    op.drop_table('localization_strings')
    
    op.drop_index('ix_keyboard_shortcuts_action_id', table_name='keyboard_shortcuts')
    op.drop_index('ix_keyboard_shortcuts_user_id', table_name='keyboard_shortcuts')
    op.drop_table('keyboard_shortcuts')
    
    op.drop_index('ix_notification_preferences_event_type', table_name='notification_preferences')
    op.drop_index('ix_notification_preferences_user_id', table_name='notification_preferences')
    op.drop_table('notification_preferences')
    
    op.drop_index('ix_widget_configs_widget_id', table_name='widget_configs')
    op.drop_index('ix_widget_configs_user_id', table_name='widget_configs')
    op.drop_table('widget_configs')
    
    op.drop_index('ix_dashboard_layouts_is_active', table_name='dashboard_layouts')
    op.drop_index('ix_dashboard_layouts_workspace_id', table_name='dashboard_layouts')
    op.drop_index('ix_dashboard_layouts_user_id', table_name='dashboard_layouts')
    op.drop_table('dashboard_layouts')
    
    op.drop_index('ix_user_settings_user_id', table_name='user_settings')
    op.drop_table('user_settings')
