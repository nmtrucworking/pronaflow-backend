"""Add Module 8: Data Archiving and Compliance tables

Revision ID: module8_archiving
Revises: module7_notifications
Create Date: 2026-02-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'module8_archiving'
down_revision = 'module7_notifications'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create Module 8 tables for archiving and compliance."""
    
    # Create archive_policies table
    op.create_table(
        'archive_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inactive_days', sa.Integer, nullable=False, server_default='180'),
        sa.Column('is_enabled', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('trash_retention_days', sa.Integer, nullable=False, server_default='30'),
        sa.Column('auto_purge_enabled', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('export_link_expiry_hours', sa.Integer, nullable=False, server_default='24'),
        sa.Column('max_export_file_size_mb', sa.Integer, nullable=False, server_default='500'),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('last_modified_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['last_modified_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id', name='uq_archive_policy_per_workspace')
    )
    op.create_index('ix_archive_policies_workspace_id', 'archive_policies', ['workspace_id'])
    
    # Create deleted_items table
    op.create_table(
        'deleted_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deleted_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('original_data', postgresql.JSON, nullable=False),
        sa.Column('deletion_reason', sa.String(255), nullable=True),
        sa.Column('restored_at', sa.DateTime, nullable=True),
        sa.Column('restored_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_restored', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['deleted_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['restored_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_deleted_items_workspace_id', 'deleted_items', ['workspace_id'])
    op.create_index('ix_deleted_items_entity_type', 'deleted_items', ['entity_type'])
    op.create_index('ix_deleted_items_deleted_at', 'deleted_items', ['deleted_at'])
    op.create_index('ix_deleted_items_is_restored', 'deleted_items', ['is_restored'])
    
    # Create archived_snapshots table
    op.create_table(
        'archived_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('archived_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('archived_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('project_data', postgresql.JSON, nullable=False),
        sa.Column('task_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_time_logged', sa.Integer, nullable=True),
        sa.Column('comment_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('file_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('archive_reason', sa.String(255), nullable=True),
        sa.Column('storage_location', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['archived_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_archived_snapshots_workspace_id', 'archived_snapshots', ['workspace_id'])
    op.create_index('ix_archived_snapshots_project_id', 'archived_snapshots', ['project_id'])
    op.create_index('ix_archived_snapshots_archived_at', 'archived_snapshots', ['archived_at'])
    
    # Create data_export_requests table
    op.create_table(
        'data_export_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requested_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('export_format', sa.String(20), nullable=False, server_default='json'),
        sa.Column('scope', sa.String(50), nullable=False),
        sa.Column('scope_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('progress_percent', sa.Integer, nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('file_size_bytes', sa.Integer, nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('download_token', sa.String(255), nullable=True),
        sa.Column('download_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requested_by_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_data_export_requests_workspace_id', 'data_export_requests', ['workspace_id'])
    op.create_index('ix_data_export_requests_requested_by_user_id', 'data_export_requests', ['requested_by_user_id'])
    op.create_index('ix_data_export_requests_status', 'data_export_requests', ['status'])
    op.create_index('ix_data_export_requests_expires_at', 'data_export_requests', ['expires_at'])
    
    # Create data_retention_logs table
    op.create_table(
        'data_retention_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('data_retention_type', sa.String(50), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_count', sa.Integer, nullable=False, server_default='1'),
        sa.Column('retention_days', sa.Integer, nullable=True),
        sa.Column('executed_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('executed_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', postgresql.JSON, nullable=True),
        sa.Column('rows_affected', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['executed_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_data_retention_logs_workspace_id', 'data_retention_logs', ['workspace_id'])
    op.create_index('ix_data_retention_logs_action_type', 'data_retention_logs', ['action_type'])
    op.create_index('ix_data_retention_logs_executed_at', 'data_retention_logs', ['executed_at'])
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('changes', postgresql.JSON, nullable=True),
        sa.Column('status_code', sa.String(20), nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('logged_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_workspace_id', 'audit_logs', ['workspace_id'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('ix_audit_logs_logged_at', 'audit_logs', ['logged_at'])


def downgrade() -> None:
    """Revert Module 8 tables."""
    
    # Drop indexes and tables in reverse order
    op.drop_index('ix_audit_logs_logged_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_resource_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_workspace_id', table_name='audit_logs')
    op.drop_table('audit_logs')
    
    op.drop_index('ix_data_retention_logs_executed_at', table_name='data_retention_logs')
    op.drop_index('ix_data_retention_logs_action_type', table_name='data_retention_logs')
    op.drop_index('ix_data_retention_logs_workspace_id', table_name='data_retention_logs')
    op.drop_table('data_retention_logs')
    
    op.drop_index('ix_data_export_requests_expires_at', table_name='data_export_requests')
    op.drop_index('ix_data_export_requests_status', table_name='data_export_requests')
    op.drop_index('ix_data_export_requests_requested_by_user_id', table_name='data_export_requests')
    op.drop_index('ix_data_export_requests_workspace_id', table_name='data_export_requests')
    op.drop_table('data_export_requests')
    
    op.drop_index('ix_archived_snapshots_archived_at', table_name='archived_snapshots')
    op.drop_index('ix_archived_snapshots_project_id', table_name='archived_snapshots')
    op.drop_index('ix_archived_snapshots_workspace_id', table_name='archived_snapshots')
    op.drop_table('archived_snapshots')
    
    op.drop_index('ix_deleted_items_is_restored', table_name='deleted_items')
    op.drop_index('ix_deleted_items_deleted_at', table_name='deleted_items')
    op.drop_index('ix_deleted_items_entity_type', table_name='deleted_items')
    op.drop_index('ix_deleted_items_workspace_id', table_name='deleted_items')
    op.drop_table('deleted_items')
    
    op.drop_index('ix_archive_policies_workspace_id', table_name='archive_policies')
    op.drop_table('archive_policies')
