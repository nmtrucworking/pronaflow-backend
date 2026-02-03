"""module16_onboarding_sessions_rewards

Revision ID: 2cc8dd3c96ed
Revises: fa5fa299a28a
Create Date: 2026-02-03 13:25:08.171970

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
"""module16_onboarding_sessions_rewards

Revision ID: 2cc8dd3c96ed
Revises: fa5fa299a28a
Create Date: 2026-02-03 13:25:08.171970

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2cc8dd3c96ed"
down_revision = "fa5fa299a28a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Module 16 onboarding additions only
    op.create_table(
        "user_tour_sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("tour_id", sa.UUID(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("skipped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="Timestamp when the record was created"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="Timestamp when the record was last updated"),
        sa.ForeignKeyConstraint(["tour_id"], ["product_tours.id"], name=op.f("fk_user_tour_sessions_tour_id_product_tours"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_user_tour_sessions_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_tour_sessions")),
    )
    op.create_index("ix_user_tour_sessions_session", "user_tour_sessions", ["session_id"], unique=False)
    op.create_index("ix_user_tour_sessions_tour", "user_tour_sessions", ["tour_id"], unique=False)
    op.create_index("ix_user_tour_sessions_user", "user_tour_sessions", ["user_id"], unique=False)

    op.create_table(
        "onboarding_reward_grants",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("reward_id", sa.UUID(), nullable=False),
        sa.Column("checklist_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="Timestamp when the record was created"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="Timestamp when the record was last updated"),
        sa.ForeignKeyConstraint(["checklist_id"], ["onboarding_checklists.id"], name=op.f("fk_onboarding_reward_grants_checklist_id_onboarding_checklists"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reward_id"], ["onboarding_rewards.id"], name=op.f("fk_onboarding_reward_grants_reward_id_onboarding_rewards"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_onboarding_reward_grants_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_onboarding_reward_grants")),
    )
    op.create_index("ix_onboarding_reward_grants_checklist", "onboarding_reward_grants", ["checklist_id"], unique=False)
    op.create_index("ix_onboarding_reward_grants_reward", "onboarding_reward_grants", ["reward_id"], unique=False)
    op.create_index("ix_onboarding_reward_grants_user", "onboarding_reward_grants", ["user_id"], unique=False)


def downgrade() -> None:
    # Module 16 onboarding rollback only
    op.drop_index("ix_onboarding_reward_grants_user", table_name="onboarding_reward_grants")
    op.drop_index("ix_onboarding_reward_grants_reward", table_name="onboarding_reward_grants")
    op.drop_index("ix_onboarding_reward_grants_checklist", table_name="onboarding_reward_grants")
    op.drop_table("onboarding_reward_grants")

    op.drop_index("ix_user_tour_sessions_user", table_name="user_tour_sessions")
    op.drop_index("ix_user_tour_sessions_tour", table_name="user_tour_sessions")
    op.drop_index("ix_user_tour_sessions_session", table_name="user_tour_sessions")
    op.drop_table("user_tour_sessions")
    op.drop_table('user_tour_sessions')
    op.drop_index(op.f('ix_plugins_name'), table_name='plugins')
    op.drop_index(op.f('ix_plugins_is_enabled'), table_name='plugins')
    op.drop_table('plugins')
    op.drop_index(op.f('ix_oauth_apps_provider_name'), table_name='oauth_apps')
    op.drop_index(op.f('ix_oauth_apps_is_enabled'), table_name='oauth_apps')
    op.drop_table('oauth_apps')
    # ### end Alembic commands ###
