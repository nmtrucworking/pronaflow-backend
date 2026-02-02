"""Add Module 11: Advanced Analytics and Reporting tables

Revision ID: module11_analytics
Revises: module9_personalization, module8_archiving
Create Date: 2026-02-03 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'module11_analytics'
down_revision = ('module9_personalization', 'module8_archiving')
branch_labels = None
depends_on = None


def upgrade():
    """Create Module 11 tables"""
    
    # sprint_metrics table
    op.create_table(
        'sprint_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sprint_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('total_story_points', sa.Integer(), nullable=False),
        sa.Column('initial_story_points', sa.Integer(), nullable=False),
        sa.Column('completed_story_points', sa.Integer(), nullable=False),
        sa.Column('remaining_story_points', sa.Integer(), nullable=False),
        sa.Column('added_story_points', sa.Integer(), nullable=False),
        sa.Column('removed_story_points', sa.Integer(), nullable=False),
        sa.Column('sprint_start_date', sa.DateTime(), nullable=False),
        sa.Column('sprint_end_date', sa.DateTime(), nullable=False),
        sa.Column('days_elapsed', sa.Integer(), nullable=False),
        sa.Column('total_sprint_days', sa.Integer(), nullable=False),
        sa.Column('planned_value', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('earned_value', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('actual_cost', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('cost_performance_index', sa.Float(), nullable=True),
        sa.Column('schedule_performance_index', sa.Float(), nullable=True),
        sa.Column('is_on_track', sa.Boolean(), nullable=False),
        sa.Column('risk_level', sa.String(20), nullable=False),
        sa.Column('last_updated_by', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    )
    op.create_index('ix_sprint_metric_sprint', 'sprint_metrics', ['sprint_id'])
    op.create_index('ix_sprint_metric_project', 'sprint_metrics', ['project_id'])
    op.create_index('ix_sprint_metric_dates', 'sprint_metrics', ['sprint_start_date', 'sprint_end_date'])

    # velocity_metrics table
    op.create_table(
        'velocity_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sprint_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('commitment', sa.Integer(), nullable=False),
        sa.Column('completed', sa.Integer(), nullable=False),
        sa.Column('velocity', sa.Float(), nullable=False),
        sa.Column('team_size', sa.Integer(), nullable=False),
        sa.Column('avg_velocity_3_sprints', sa.Float(), nullable=True),
        sa.Column('avg_velocity_6_sprints', sa.Float(), nullable=True),
        sa.Column('trend', sa.String(20), nullable=False),
        sa.Column('sprint_number', sa.Integer(), nullable=False),
        sa.Column('sprint_start_date', sa.DateTime(), nullable=False),
        sa.Column('sprint_end_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.UniqueConstraint('sprint_id'),
    )
    op.create_index('ix_velocity_metric_project', 'velocity_metrics', ['project_id'])
    op.create_index('ix_velocity_metric_sprint_number', 'velocity_metrics', ['project_id', 'sprint_number'])

    # resource_allocations table
    op.create_table(
        'resource_allocations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('working_capacity_hours', sa.Float(), nullable=False),
        sa.Column('assigned_hours', sa.Float(), nullable=False),
        sa.Column('utilization_percentage', sa.Float(), nullable=False),
        sa.Column('capacity_status', sa.String(20), nullable=False),
        sa.Column('allocation_date', sa.DateTime(), nullable=False),
        sa.Column('is_overloaded', sa.Boolean(), nullable=False),
        sa.Column('is_underutilized', sa.Boolean(), nullable=False),
        sa.Column('in_progress_hours', sa.Float(), nullable=False),
        sa.Column('completed_hours', sa.Float(), nullable=False),
        sa.Column('blocked_hours', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    )
    op.create_index('ix_resource_alloc_user', 'resource_allocations', ['user_id'])
    op.create_index('ix_resource_alloc_project', 'resource_allocations', ['project_id'])
    op.create_index('ix_resource_alloc_date', 'resource_allocations', ['allocation_date'])
    op.create_index('ix_resource_alloc_user_date', 'resource_allocations', ['user_id', 'allocation_date'])

    # time_entries table
    op.create_table(
        'time_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('task_id', sa.String(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.Column('duration_hours', sa.Float(), nullable=False),
        sa.Column('entry_type', sa.String(20), nullable=False),
        sa.Column('is_billable', sa.Boolean(), nullable=False),
        sa.Column('billable_status', sa.String(), nullable=False),
        sa.Column('hourly_rate', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('billable_amount', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('daily_warning_exceeded', sa.Boolean(), nullable=False),
        sa.Column('daily_max_exceeded', sa.Boolean(), nullable=False),
        sa.Column('edit_count', sa.Integer(), nullable=False),
        sa.Column('edit_history', postgresql.JSON(), nullable=True),
        sa.Column('manually_edited', sa.Boolean(), nullable=False),
        sa.Column('edit_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    )
    op.create_index('ix_time_entry_user', 'time_entries', ['user_id'])
    op.create_index('ix_time_entry_task', 'time_entries', ['task_id'])
    op.create_index('ix_time_entry_project', 'time_entries', ['project_id'])
    op.create_index('ix_time_entry_date', 'time_entries', ['start_time'])
    op.create_index('ix_time_entry_billable', 'time_entries', ['is_billable'])
    op.create_index('ix_time_entry_user_date', 'time_entries', ['user_id', 'start_time'])

    # timesheets table
    op.create_table(
        'timesheets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('approved_by', sa.String(), nullable=True),
        sa.Column('period_start_date', sa.DateTime(), nullable=False),
        sa.Column('period_end_date', sa.DateTime(), nullable=False),
        sa.Column('period_type', sa.String(20), nullable=False),
        sa.Column('total_hours', sa.Float(), nullable=False),
        sa.Column('billable_hours', sa.Float(), nullable=False),
        sa.Column('non_billable_hours', sa.Float(), nullable=False),
        sa.Column('total_cost', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('billable_amount', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('time_entries_count', sa.Integer(), nullable=False),
        sa.Column('time_entries_json', postgresql.JSON(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['approved_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    )
    op.create_index('ix_timesheet_user', 'timesheets', ['user_id'])
    op.create_index('ix_timesheet_project', 'timesheets', ['project_id'])
    op.create_index('ix_timesheet_period', 'timesheets', ['period_start_date', 'period_end_date'])
    op.create_index('ix_timesheet_status', 'timesheets', ['status'])
    op.create_index('ix_timesheet_user_status', 'timesheets', ['user_id', 'status'])

    # custom_reports table
    op.create_table(
        'custom_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dimensions', postgresql.JSON(), nullable=False),
        sa.Column('metrics', postgresql.JSON(), nullable=False),
        sa.Column('filters', postgresql.JSON(), nullable=True),
        sa.Column('report_type', sa.String(), nullable=False),
        sa.Column('visualization_type', sa.String(50), nullable=False),
        sa.Column('sort_by', postgresql.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('shared_with_users', postgresql.JSON(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('last_run_result_size', sa.Integer(), nullable=True),
        sa.Column('is_template', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    )
    op.create_index('ix_custom_report_creator', 'custom_reports', ['created_by'])
    op.create_index('ix_custom_report_project', 'custom_reports', ['project_id'])

    # report_schedules table
    op.create_table(
        'report_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('custom_report_id', sa.String(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('frequency', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('next_run_at', sa.DateTime(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('execution_days', postgresql.JSON(), nullable=True),
        sa.Column('execution_time', sa.String(5), nullable=True),
        sa.Column('recipient_emails', postgresql.JSON(), nullable=False),
        sa.Column('export_format', sa.String(), nullable=False),
        sa.Column('include_charts', sa.Boolean(), nullable=False),
        sa.Column('total_runs', sa.Integer(), nullable=False),
        sa.Column('success_runs', sa.Integer(), nullable=False),
        sa.Column('failed_runs', sa.Integer(), nullable=False),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['custom_report_id'], ['custom_reports.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    )
    op.create_index('ix_report_schedule_report', 'report_schedules', ['custom_report_id'])
    op.create_index('ix_report_schedule_creator', 'report_schedules', ['created_by'])
    op.create_index('ix_report_schedule_next_run', 'report_schedules', ['next_run_at'])
    
    
    # metric_snapshots table (NEW)
    op.create_table(
        'metric_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('sprint_id', sa.String(), nullable=True),
        sa.Column('snapshot_date', sa.DateTime(), nullable=False),
        sa.Column('planned_value', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('earned_value', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('actual_cost', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('cost_performance_index', sa.Float(), nullable=True),
        sa.Column('schedule_performance_index', sa.Float(), nullable=True),
        sa.Column('cost_variance', sa.DECIMAL(12, 2), nullable=True),
        sa.Column('schedule_variance', sa.DECIMAL(12, 2), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=False),
        sa.Column('on_track', sa.Boolean(), nullable=False),
        sa.Column('health_status', sa.String(20), nullable=False),
        sa.Column('recorded_by', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.ForeignKeyConstraint(['sprint_id'], ['sprint.id'], ),
        sa.ForeignKeyConstraint(['recorded_by'], ['user.id'], )
    )
    op.create_index('ix_metric_snapshot_project', 'metric_snapshots', ['project_id'], unique=False)
    op.create_index('ix_metric_snapshot_sprint', 'metric_snapshots', ['sprint_id'], unique=False)
    op.create_index('ix_metric_snapshot_date', 'metric_snapshots', ['snapshot_date'], unique=False)
    op.create_index('ix_metric_snapshot_project_date', 'metric_snapshots', ['project_id', 'snapshot_date'], unique=False)
    
    
    # kpis table (NEW)
    op.create_table(
        'kpis',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('sprint_id', sa.String(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('kpi_type', sa.String(50), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('target_value', sa.Float(), nullable=False),
        sa.Column('actual_value', sa.Float(), nullable=True),
        sa.Column('current_value', sa.Float(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('achieved', sa.Boolean(), nullable=False),
        sa.Column('green_threshold', sa.Float(), nullable=False),
        sa.Column('amber_threshold', sa.Float(), nullable=False),
        sa.Column('red_threshold', sa.Float(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('target_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.ForeignKeyConstraint(['sprint_id'], ['sprint.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], )
    )
    op.create_index('ix_kpi_project', 'kpis', ['project_id'], unique=False)
    op.create_index('ix_kpi_sprint', 'kpis', ['sprint_id'], unique=False)
    op.create_index('ix_kpi_status', 'kpis', ['status'], unique=False)
    
    
    # timesheet_approvals table (NEW)
    op.create_table(
        'timesheet_approvals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timesheet_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approver_id', sa.String(), nullable=True),
        sa.Column('rejected_by', sa.String(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('validation_passed', sa.Boolean(), nullable=False),
        sa.Column('validation_errors', postgresql.JSON(), nullable=True),
        sa.Column('is_compliant', sa.Boolean(), nullable=False),
        sa.Column('requires_escalation', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['timesheet_id'], ['timesheet.id'], ),
        sa.ForeignKeyConstraint(['approver_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['rejected_by'], ['user.id'], ),
        sa.UniqueConstraint('timesheet_id', name='uq_timesheet_approval_timesheet')
    )
    op.create_index('ix_timesheet_approval_status', 'timesheet_approvals', ['status'], unique=False)
    op.create_index('ix_timesheet_approval_approver', 'timesheet_approvals', ['approver_id'], unique=False)
    
    
    # report_permissions table (NEW)
    op.create_table(
        'report_permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('granted_by', sa.String(), nullable=False),
        sa.Column('revoked_by', sa.String(), nullable=True),
        sa.Column('permission_level', sa.String(20), nullable=False),
        sa.Column('scope_type', sa.String(50), nullable=True),
        sa.Column('scope_id', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('granted_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('grant_reason', sa.Text(), nullable=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['report_id'], ['custom_reports.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['granted_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['revoked_by'], ['user.id'], ),
        sa.UniqueConstraint('report_id', 'user_id', name='uq_report_permission_report_user')
    )
    op.create_index('ix_report_permission_report', 'report_permissions', ['report_id'], unique=False)
    op.create_index('ix_report_permission_user', 'report_permissions', ['user_id'], unique=False)
    op.create_index('ix_report_permission_active', 'report_permissions', ['is_active'], unique=False)
    op.create_index('ix_report_permission_report_user', 'report_permissions', ['report_id', 'user_id'], unique=False)


def downgrade():
    """Drop Module 11 tables"""
    op.drop_index('ix_report_schedule_next_run', table_name='report_schedules')
    op.drop_index('ix_report_schedule_creator', table_name='report_schedules')
    op.drop_index('ix_report_schedule_report', table_name='report_schedules')
    op.drop_table('report_schedules')
    
    op.drop_index('ix_custom_report_project', table_name='custom_reports')
    op.drop_index('ix_custom_report_creator', table_name='custom_reports')
    op.drop_table('custom_reports')
    
    op.drop_index('ix_timesheet_user_status', table_name='timesheets')
    op.drop_index('ix_timesheet_status', table_name='timesheets')
    op.drop_index('ix_timesheet_period', table_name='timesheets')
    op.drop_index('ix_timesheet_project', table_name='timesheets')
    op.drop_index('ix_timesheet_user', table_name='timesheets')
    op.drop_table('timesheets')
    
    op.drop_index('ix_time_entry_user_date', table_name='time_entries')
    op.drop_index('ix_time_entry_billable', table_name='time_entries')
    op.drop_index('ix_time_entry_date', table_name='time_entries')
    op.drop_index('ix_time_entry_project', table_name='time_entries')
    op.drop_index('ix_time_entry_task', table_name='time_entries')
    op.drop_index('ix_time_entry_user', table_name='time_entries')
    op.drop_table('time_entries')
    
    op.drop_index('ix_resource_alloc_user_date', table_name='resource_allocations')
    op.drop_index('ix_resource_alloc_date', table_name='resource_allocations')
    op.drop_index('ix_resource_alloc_project', table_name='resource_allocations')
    op.drop_index('ix_resource_alloc_user', table_name='resource_allocations')
    op.drop_table('resource_allocations')
    
    op.drop_index('ix_report_permission_report_user', table_name='report_permissions')
    op.drop_index('ix_report_permission_active', table_name='report_permissions')
    op.drop_index('ix_report_permission_user', table_name='report_permissions')
    op.drop_index('ix_report_permission_report', table_name='report_permissions')
    op.drop_table('report_permissions')
    
    op.drop_index('ix_timesheet_approval_approver', table_name='timesheet_approvals')
    op.drop_index('ix_timesheet_approval_status', table_name='timesheet_approvals')
    op.drop_table('timesheet_approvals')
    
    op.drop_index('ix_kpi_status', table_name='kpis')
    op.drop_index('ix_kpi_sprint', table_name='kpis')
    op.drop_index('ix_kpi_project', table_name='kpis')
    op.drop_table('kpis')
    
    op.drop_index('ix_metric_snapshot_project_date', table_name='metric_snapshots')
    op.drop_index('ix_metric_snapshot_date', table_name='metric_snapshots')
    op.drop_index('ix_metric_snapshot_sprint', table_name='metric_snapshots')
    op.drop_index('ix_metric_snapshot_project', table_name='metric_snapshots')
    op.drop_table('metric_snapshots')
    
    op.drop_index('ix_velocity_metric_sprint_number', table_name='velocity_metrics')
    op.drop_index('ix_velocity_metric_project', table_name='velocity_metrics')
    op.drop_table('velocity_metrics')
    
    op.drop_index('ix_sprint_metric_dates', table_name='sprint_metrics')
    op.drop_index('ix_sprint_metric_project', table_name='sprint_metrics')
    op.drop_index('ix_sprint_metric_sprint', table_name='sprint_metrics')
    op.drop_table('sprint_metrics')
