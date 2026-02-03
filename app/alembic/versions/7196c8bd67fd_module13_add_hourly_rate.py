"""module13_add_hourly_rate

Revision ID: 7196c8bd67fd
Revises: module12_integration
Create Date: 2026-02-03 12:25:55.579631

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '7196c8bd67fd'
down_revision = 'module12_integration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if 'clients' in tables:
        op.add_column(
            'clients',
            sa.Column('default_hourly_rate', sa.Numeric(10, 2), nullable=True)
        )

    if 'freelancer_invoices' in tables:
        op.add_column(
            'freelancer_invoices',
            sa.Column('hourly_rate', sa.Numeric(10, 2), nullable=True)
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if 'freelancer_invoices' in tables:
        op.drop_column('freelancer_invoices', 'hourly_rate')

    if 'clients' in tables:
        op.drop_column('clients', 'default_hourly_rate')
