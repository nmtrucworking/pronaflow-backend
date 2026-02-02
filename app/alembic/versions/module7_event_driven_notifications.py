"""Add Module 7: Event-Driven Notification System tables

Revision ID: module7_notifications
Revises: cd6041d7e8ce
Create Date: 2026-02-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'module7_notifications'
down_revision = 'cd6041d7e8ce'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create Module 7 new tables.
    
    Note: notification_templates and notification_preferences tables already exist
    from Module 6, so we only create the 4 missing tables.
    """
    
    # Create watchers table
    op.create_table(
        'watchers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_watching', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('custom_channels', postgresql.JSON, nullable=True),
        sa.Column('notify_on_types', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id', 'entity_type', 'entity_id', 'user_id', name='uq_watcher')
    )
    op.create_index('ix_watchers_entity', 'watchers', ['workspace_id', 'entity_type', 'entity_id'])
    op.create_index('ix_watchers_user', 'watchers', ['user_id', 'is_watching'])
    
    # Create event_logs table
    op.create_table(
        'event_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('source_entity_type', sa.String(50), nullable=False),
        sa.Column('source_entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_payload', postgresql.JSON, nullable=False),
        sa.Column('is_processed', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('processed_at', sa.DateTime, nullable=True),
        sa.Column('triggered_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['triggered_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', name='uq_event_log_event_id')
    )
    op.create_index('ix_event_logs_workspace_id', 'event_logs', ['workspace_id'])
    op.create_index('ix_event_logs_event_type', 'event_logs', ['event_type'])
    op.create_index('ix_event_logs_is_processed', 'event_logs', ['is_processed', 'created_at'])
    
    # Create notification_retries table
    op.create_table(
        'notification_retries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notification_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attempt_number', sa.Integer, nullable=False),
        sa.Column('channel', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('scheduled_at', sa.DateTime, nullable=False),
        sa.Column('executed_at', sa.DateTime, nullable=True),
        sa.Column('next_retry_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notification_retries_status_scheduled', 'notification_retries', ['status', 'scheduled_at'])
    
    # Create interaction_logs table
    op.create_table(
        'interaction_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notification_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interaction_type', sa.String(50), nullable=False),
        sa.Column('action_label', sa.String(100), nullable=True),
        sa.Column('action_url_clicked', sa.String(500), nullable=True),
        sa.Column('source_channel', sa.String(50), nullable=False),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_interaction_logs_notification_id', 'interaction_logs', ['notification_id', 'interaction_type'])
    op.create_index('ix_interaction_logs_user_id', 'interaction_logs', ['user_id', 'interaction_type'])


def downgrade() -> None:
    """Revert Module 7 tables - only drop the 4 new tables we created."""
    
    # Drop indexes first
    op.drop_index('ix_interaction_logs_user_id', table_name='interaction_logs')
    op.drop_index('ix_interaction_logs_notification_id', table_name='interaction_logs')
    op.drop_table('interaction_logs')
    
    op.drop_index('ix_notification_retries_status_scheduled', table_name='notification_retries')
    op.drop_table('notification_retries')
    
    op.drop_index('ix_event_logs_is_processed', table_name='event_logs')
    op.drop_index('ix_event_logs_event_type', table_name='event_logs')
    op.drop_index('ix_event_logs_workspace_id', table_name='event_logs')
    op.drop_table('event_logs')
    
    op.drop_index('ix_watchers_user', table_name='watchers')
    op.drop_index('ix_watchers_entity', table_name='watchers')
    op.drop_table('watchers')
