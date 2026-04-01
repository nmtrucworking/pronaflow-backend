"""add_workspace_audit_logs

Revision ID: 9f8d3f4b2a10
Revises: 2cc8dd3c96ed
Create Date: 2026-04-02 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "9f8d3f4b2a10"
down_revision = "2cc8dd3c96ed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "workspace_audit_logs" in inspector.get_table_names():
        return

    op.create_table(
        "workspace_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("resource_id", sa.String(length=255), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=50), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_workspace_audit_logs_workspace_id", "workspace_audit_logs", ["workspace_id"])
    op.create_index("ix_workspace_audit_logs_action", "workspace_audit_logs", ["action"])
    op.create_index("ix_workspace_audit_logs_created_at", "workspace_audit_logs", ["created_at"])
    op.create_index("ix_workspace_audit_logs_actor_id", "workspace_audit_logs", ["actor_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "workspace_audit_logs" not in inspector.get_table_names():
        return

    op.drop_index("ix_workspace_audit_logs_actor_id", table_name="workspace_audit_logs")
    op.drop_index("ix_workspace_audit_logs_created_at", table_name="workspace_audit_logs")
    op.drop_index("ix_workspace_audit_logs_action", table_name="workspace_audit_logs")
    op.drop_index("ix_workspace_audit_logs_workspace_id", table_name="workspace_audit_logs")
    op.drop_table("workspace_audit_logs")
