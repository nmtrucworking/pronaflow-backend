"""
Alembic migration for Module 12: Integration Ecosystem.

Creates tables for API tokens, webhooks, OAuth, plugins, and governance.

Revision ID: module12_integration
Revises: module11_analytics
Create Date: 2026-02-03

Ref: Module 12 - Integration Ecosystem
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    """Create Module 12 tables for integration ecosystem."""
    
    # Create api_scopes table
    op.create_table(
        'api_scopes',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('scope_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('permission_type', sa.String(20), nullable=False),
        sa.Column('is_default', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('is_deprecated', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('scope_name', name='uq_api_scopes_scope_name'),
    )
    op.create_index('ix_api_scopes_scope_name', 'api_scopes', ['scope_name'])
    op.create_index('ix_api_scopes_resource_type', 'api_scopes', ['resource_type'])
    
    # Create api_tokens table
    op.create_table(
        'api_tokens',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('workspace_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('last_used_at', sa.DateTime, nullable=True),
        sa.Column('expires_at', sa.DateTime, nullable=True),
        sa.Column('created_by_user_id', sa.String(36), nullable=True),
        sa.Column('revoked_at', sa.DateTime, nullable=True),
        sa.Column('revoked_by_user_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['revoked_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash', name='uq_api_tokens_token_hash'),
    )
    op.create_index('ix_api_tokens_user_id', 'api_tokens', ['user_id'])
    op.create_index('ix_api_tokens_workspace_id', 'api_tokens', ['workspace_id'])
    op.create_index('ix_api_tokens_is_active', 'api_tokens', ['is_active'])
    
    # Create api_token_scopes table
    op.create_table(
        'api_token_scopes',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('api_token_id', sa.String(36), nullable=False),
        sa.Column('api_scope_id', sa.String(36), nullable=False),
        sa.ForeignKeyConstraint(['api_token_id'], ['api_tokens.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['api_scope_id'], ['api_scopes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('api_token_id', 'api_scope_id', name='uq_token_scope'),
    )
    op.create_index('ix_api_token_scopes_api_token_id', 'api_token_scopes', ['api_token_id'])
    
    # Create api_usage_logs table
    op.create_table(
        'api_usage_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('workspace_id', sa.String(36), nullable=False),
        sa.Column('api_token_id', sa.String(36), nullable=True),
        sa.Column('method', sa.String(20), nullable=False),
        sa.Column('endpoint', sa.String(500), nullable=False),
        sa.Column('status_code', sa.Integer, nullable=False),
        sa.Column('response_time_ms', sa.Integer, nullable=True),
        sa.Column('request_count_in_minute', sa.Integer, nullable=False, server_default='1'),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('logged_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['api_token_id'], ['api_tokens.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_api_usage_logs_workspace_id', 'api_usage_logs', ['workspace_id'])
    op.create_index('ix_api_usage_logs_api_token_id', 'api_usage_logs', ['api_token_id'])
    op.create_index('ix_api_usage_logs_logged_at', 'api_usage_logs', ['logged_at'])
    op.create_index('ix_api_usage_logs_status_code', 'api_usage_logs', ['status_code'])
    
    # Create webhook_endpoints table
    op.create_table(
        'webhook_endpoints',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('workspace_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('payload_url', sa.String(500), nullable=False),
        sa.Column('secret_key', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('max_retries', sa.Integer, nullable=False, server_default='5'),
        sa.Column('retry_backoff_seconds', sa.Integer, nullable=False, server_default='60'),
        sa.Column('timeout_seconds', sa.Integer, nullable=False, server_default='30'),
        sa.Column('created_by_user_id', sa.String(36), nullable=True),
        sa.Column('last_delivery_at', sa.DateTime, nullable=True),
        sa.Column('last_delivery_status', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_webhook_endpoints_workspace_id', 'webhook_endpoints', ['workspace_id'])
    op.create_index('ix_webhook_endpoints_is_active', 'webhook_endpoints', ['is_active'])
    
    # Create webhook_events table
    op.create_table(
        'webhook_events',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('webhook_endpoint_id', sa.String(36), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('is_subscribed', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['webhook_endpoint_id'], ['webhook_endpoints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('webhook_endpoint_id', 'event_type', name='uq_endpoint_event'),
    )
    op.create_index('ix_webhook_events_webhook_endpoint_id', 'webhook_events', ['webhook_endpoint_id'])
    
    # Create webhook_deliveries table
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('webhook_endpoint_id', sa.String(36), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('event_data', sa.JSON, nullable=False),
        sa.Column('attempt_number', sa.Integer, nullable=False, server_default='1'),
        sa.Column('status_code', sa.Integer, nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('request_headers', sa.JSON, nullable=True),
        sa.Column('request_body', sa.JSON, nullable=True),
        sa.Column('response_headers', sa.JSON, nullable=True),
        sa.Column('response_body', sa.Text, nullable=True),
        sa.Column('response_time_ms', sa.Integer, nullable=True),
        sa.Column('next_retry_at', sa.DateTime, nullable=True),
        sa.Column('last_error', sa.Text, nullable=True),
        sa.Column('delivered_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['webhook_endpoint_id'], ['webhook_endpoints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_webhook_deliveries_webhook_endpoint_id', 'webhook_deliveries', ['webhook_endpoint_id'])
    op.create_index('ix_webhook_deliveries_status', 'webhook_deliveries', ['status'])
    op.create_index('ix_webhook_deliveries_delivered_at', 'webhook_deliveries', ['delivered_at'])
    
    # Create oauth_apps table
    op.create_table(
        'oauth_apps',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('client_id', sa.String(255), nullable=False),
        sa.Column('client_secret', sa.String(255), nullable=False),
        sa.Column('authorize_url', sa.String(500), nullable=False),
        sa.Column('token_url', sa.String(500), nullable=False),
        sa.Column('redirect_uri', sa.String(500), nullable=False),
        sa.Column('required_scopes', sa.JSON, nullable=False),
        sa.Column('is_enabled', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('is_deprecated', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('documentation_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_oauth_apps_name'),
    )
    op.create_index('ix_oauth_apps_name', 'oauth_apps', ['name'])
    
    # Create oauth_connections table
    op.create_table(
        'oauth_connections',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('oauth_app_id', sa.String(36), nullable=False),
        sa.Column('workspace_id', sa.String(36), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('is_sync_enabled', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('access_token', sa.Text, nullable=False),
        sa.Column('refresh_token', sa.Text, nullable=True),
        sa.Column('token_expires_at', sa.DateTime, nullable=True),
        sa.Column('external_user_id', sa.String(255), nullable=False),
        sa.Column('external_user_email', sa.String(255), nullable=True),
        sa.Column('external_user_data', sa.JSON, nullable=True),
        sa.Column('last_sync_at', sa.DateTime, nullable=True),
        sa.Column('last_sync_status', sa.String(50), nullable=True),
        sa.Column('sync_error', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['oauth_app_id'], ['oauth_apps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'oauth_app_id', 'workspace_id', name='uq_user_app_workspace'),
    )
    op.create_index('ix_oauth_connections_user_id', 'oauth_connections', ['user_id'])
    op.create_index('ix_oauth_connections_oauth_app_id', 'oauth_connections', ['oauth_app_id'])
    op.create_index('ix_oauth_connections_workspace_id', 'oauth_connections', ['workspace_id'])
    
    # Create integration_bindings table
    op.create_table(
        'integration_bindings',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('oauth_connection_id', sa.String(36), nullable=False),
        sa.Column('local_resource_type', sa.String(50), nullable=False),
        sa.Column('local_resource_id', sa.String(36), nullable=False),
        sa.Column('external_resource_type', sa.String(50), nullable=False),
        sa.Column('external_resource_id', sa.String(255), nullable=False),
        sa.Column('field_mappings', sa.JSON, nullable=False),
        sa.Column('sync_direction', sa.String(20), nullable=False, server_default='bi'),
        sa.Column('created_by_user_id', sa.String(36), nullable=True),
        sa.Column('last_synced_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['oauth_connection_id'], ['oauth_connections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('oauth_connection_id', 'local_resource_type', 'local_resource_id', name='uq_connection_local_resource'),
    )
    op.create_index('ix_integration_bindings_oauth_connection_id', 'integration_bindings', ['oauth_connection_id'])
    
    # Create plugins table
    op.create_table(
        'plugins',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('developer_id', sa.String(36), nullable=True),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('documentation_url', sa.String(500), nullable=True),
        sa.Column('github_url', sa.String(500), nullable=True),
        sa.Column('manifest', sa.JSON, nullable=False),
        sa.Column('bundle_url', sa.String(500), nullable=False),
        sa.Column('required_permissions', sa.JSON, nullable=False),
        sa.Column('required_scopes', sa.JSON, nullable=False),
        sa.Column('is_public', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('is_verified', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('is_deprecated', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('rating_avg', sa.Integer, nullable=True),
        sa.Column('install_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['developer_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_plugins_name'),
    )
    op.create_index('ix_plugins_name', 'plugins', ['name'])
    op.create_index('ix_plugins_is_public', 'plugins', ['is_public'])
    
    # Create plugin_installations table
    op.create_table(
        'plugin_installations',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('workspace_id', sa.String(36), nullable=False),
        sa.Column('plugin_id', sa.String(36), nullable=False),
        sa.Column('is_enabled', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('configuration', sa.JSON, nullable=True),
        sa.Column('installed_by_user_id', sa.String(36), nullable=True),
        sa.Column('uninstalled_at', sa.DateTime, nullable=True),
        sa.Column('last_updated_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plugin_id'], ['plugins.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['installed_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id', 'plugin_id', name='uq_workspace_plugin'),
    )
    op.create_index('ix_plugin_installations_workspace_id', 'plugin_installations', ['workspace_id'])
    op.create_index('ix_plugin_installations_is_enabled', 'plugin_installations', ['is_enabled'])
    
    # Create consent_grants table
    op.create_table(
        'consent_grants',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('consent_type', sa.String(50), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(36), nullable=False),
        sa.Column('requested_permissions', sa.JSON, nullable=False),
        sa.Column('granted_permissions', sa.JSON, nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('revoked_at', sa.DateTime, nullable=True),
        sa.Column('granted_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'consent_type', 'entity_type', 'entity_id', name='uq_user_consent'),
    )
    op.create_index('ix_consent_grants_user_id', 'consent_grants', ['user_id'])
    op.create_index('ix_consent_grants_consent_type', 'consent_grants', ['consent_type'])


def downgrade() -> None:
    """Revert Module 12 tables."""
    
    # Drop tables in reverse order
    op.drop_index('ix_consent_grants_consent_type', table_name='consent_grants')
    op.drop_index('ix_consent_grants_user_id', table_name='consent_grants')
    op.drop_table('consent_grants')
    
    op.drop_index('ix_plugin_installations_is_enabled', table_name='plugin_installations')
    op.drop_index('ix_plugin_installations_workspace_id', table_name='plugin_installations')
    op.drop_table('plugin_installations')
    
    op.drop_index('ix_plugins_is_public', table_name='plugins')
    op.drop_index('ix_plugins_name', table_name='plugins')
    op.drop_table('plugins')
    
    op.drop_index('ix_integration_bindings_oauth_connection_id', table_name='integration_bindings')
    op.drop_table('integration_bindings')
    
    op.drop_index('ix_oauth_connections_workspace_id', table_name='oauth_connections')
    op.drop_index('ix_oauth_connections_oauth_app_id', table_name='oauth_connections')
    op.drop_index('ix_oauth_connections_user_id', table_name='oauth_connections')
    op.drop_table('oauth_connections')
    
    op.drop_index('ix_oauth_apps_name', table_name='oauth_apps')
    op.drop_table('oauth_apps')
    
    op.drop_index('ix_webhook_deliveries_delivered_at', table_name='webhook_deliveries')
    op.drop_index('ix_webhook_deliveries_status', table_name='webhook_deliveries')
    op.drop_index('ix_webhook_deliveries_webhook_endpoint_id', table_name='webhook_deliveries')
    op.drop_table('webhook_deliveries')
    
    op.drop_index('ix_webhook_events_webhook_endpoint_id', table_name='webhook_events')
    op.drop_table('webhook_events')
    
    op.drop_index('ix_webhook_endpoints_is_active', table_name='webhook_endpoints')
    op.drop_index('ix_webhook_endpoints_workspace_id', table_name='webhook_endpoints')
    op.drop_table('webhook_endpoints')
    
    op.drop_index('ix_api_usage_logs_status_code', table_name='api_usage_logs')
    op.drop_index('ix_api_usage_logs_logged_at', table_name='api_usage_logs')
    op.drop_index('ix_api_usage_logs_api_token_id', table_name='api_usage_logs')
    op.drop_index('ix_api_usage_logs_workspace_id', table_name='api_usage_logs')
    op.drop_table('api_usage_logs')
    
    op.drop_index('ix_api_token_scopes_api_token_id', table_name='api_token_scopes')
    op.drop_table('api_token_scopes')
    
    op.drop_index('ix_api_tokens_is_active', table_name='api_tokens')
    op.drop_index('ix_api_tokens_workspace_id', table_name='api_tokens')
    op.drop_index('ix_api_tokens_user_id', table_name='api_tokens')
    op.drop_table('api_tokens')
    
    op.drop_index('ix_api_scopes_resource_type', table_name='api_scopes')
    op.drop_index('ix_api_scopes_scope_name', table_name='api_scopes')
    op.drop_table('api_scopes')
