"""Add priority to projects and type to change requests

Revision ID: module3_enhancements
Revises: 37d437544626
Create Date: 2026-02-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'module3_enhancements'
down_revision = '37d437544626'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create new enum types
    op.execute("CREATE TYPE projectpriority AS ENUM ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')")
    op.execute("CREATE TYPE changerequesttype AS ENUM ('SCOPE', 'SCHEDULE', 'COST', 'RESOURCE')")
    op.execute("CREATE TYPE changerequeststatusv2 AS ENUM ('DRAFT', 'PENDING', 'APPROVED', 'REJECTED', 'IMPLEMENTED', 'CANCELLED')")
    op.execute("CREATE TYPE projecthealthstatus AS ENUM ('GREEN', 'AMBER', 'RED')")
    op.execute("CREATE TYPE projectrole AS ENUM ('MANAGER', 'PLANNER', 'MEMBER', 'VIEWER')")
    
    # Add priority column to projects table
    op.add_column('projects', 
        sa.Column('priority', sa.Enum('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', name='projectpriority'), 
                  nullable=False, 
                  server_default='MEDIUM',
                  comment='Project priority (CRITICAL / HIGH / MEDIUM / LOW)')
    )
    
    # Add type column to project_change_requests table
    op.add_column('project_change_requests',
        sa.Column('type', sa.Enum('SCOPE', 'SCHEDULE', 'COST', 'RESOURCE', name='changerequesttype'),
                  nullable=False,
                  server_default='SCOPE',
                  comment='Type of change request')
    )
    
    # Update the status enum for change requests to include new statuses
    # First, alter the column to accept NULL temporarily
    op.alter_column('project_change_requests', 'status', nullable=True)
    
    # Drop and recreate the enum type
    op.execute("ALTER TABLE project_change_requests ALTER COLUMN status TYPE varchar(50)")
    op.execute("DROP TYPE change_request_status")
    op.execute("ALTER TYPE changerequeststatusv2 RENAME TO change_request_status")
    op.execute("ALTER TABLE project_change_requests ALTER COLUMN status TYPE change_request_status USING status::change_request_status")
    op.alter_column('project_change_requests', 'status', nullable=False, server_default='PENDING')


def downgrade() -> None:
    # Remove priority from projects
    op.drop_column('projects', 'priority')
    
    # Remove type from project_change_requests
    op.drop_column('project_change_requests', 'type')
    
    # Revert status enum (simplified - may need adjustment based on data)
    op.execute("ALTER TABLE project_change_requests ALTER COLUMN status TYPE varchar(50)")
    op.execute("DROP TYPE change_request_status")
    op.execute("CREATE TYPE change_request_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'IMPLEMENTED')")
    op.execute("ALTER TABLE project_change_requests ALTER COLUMN status TYPE change_request_status USING status::change_request_status")
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS projectpriority")
    op.execute("DROP TYPE IF EXISTS changerequesttype")
    op.execute("DROP TYPE IF EXISTS changerequeststatusv2")
    op.execute("DROP TYPE IF EXISTS projecthealthstatus")
    op.execute("DROP TYPE IF EXISTS projectrole")
