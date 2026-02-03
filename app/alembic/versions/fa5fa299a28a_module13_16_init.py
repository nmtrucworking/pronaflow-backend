"""module13_16_init

Revision ID: fa5fa299a28a
Revises: 7196c8bd67fd
Create Date: 2026-02-03 12:30:07.533516

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fa5fa299a28a'
down_revision = '7196c8bd67fd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ===== Module 13: Subscription & Billing =====
    op.create_table(
        'plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Global unique UUID for plan'),
        sa.Column('name', sa.String(length=100), nullable=False, comment="Plan name (e.g., 'Free', 'Pro', 'Enterprise')"),
        sa.Column('display_name', sa.String(length=100), nullable=False, comment='Friendly display name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Plan description'),
        sa.Column('price_monthly', sa.Numeric(10, 2), nullable=False, comment='Monthly price in USD'),
        sa.Column('price_yearly', sa.Numeric(10, 2), nullable=False, comment='Yearly price in USD'),
        sa.Column('max_projects', sa.Integer(), nullable=False, comment='Maximum number of projects'),
        sa.Column('max_storage_gb', sa.Integer(), nullable=False, comment='Maximum storage in GB'),
        sa.Column('max_ai_tokens_monthly', sa.Integer(), nullable=False, comment='AI tokens quota per month'),
        sa.Column('max_users_per_workspace', sa.Integer(), nullable=False, comment='Maximum users per workspace'),
        sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Feature flags (SSO, Custom Fields, Advanced AI, etc.)'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='Whether plan is available for subscription'),
        sa.Column('is_public', sa.Boolean(), nullable=False, comment='Whether plan is publicly visible'),
        sa.Column('sort_order', sa.Integer(), nullable=False, comment='Display order (lower = shown first)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id', name='pk_plans'),
        sa.UniqueConstraint('name', name='uq_plans_name'),
    )
    op.create_index('ix_plans_is_active', 'plans', ['is_active'], unique=False)
    op.create_index('ix_plans_name', 'plans', ['name'], unique=False)

    op.create_table(
        'workspace_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Global unique UUID for subscription'),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Workspace reference'),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Plan reference'),
        sa.Column('billing_cycle', sa.String(length=20), nullable=False, comment="Billing cycle: 'monthly' or 'yearly'"),
        sa.Column('start_date', sa.Date(), nullable=False, comment='Subscription start date'),
        sa.Column('end_date', sa.Date(), nullable=True, comment='Subscription end date (null = ongoing)'),
        sa.Column('next_billing_date', sa.Date(), nullable=True, comment='Next billing date'),
        sa.Column('status', sa.String(length=20), nullable=False, comment="Status: 'trial', 'active', 'cancelled', 'expired', 'grace_period'"),
        sa.Column('is_trial', sa.Boolean(), nullable=False, comment='Whether this is a trial subscription'),
        sa.Column('trial_end_date', sa.Date(), nullable=True, comment='Trial end date'),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True, comment='Cancellation timestamp'),
        sa.Column('cancellation_reason', sa.Text(), nullable=True, comment='Reason for cancellation'),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True, comment='Stripe subscription ID'),
        sa.Column('auto_renew', sa.Boolean(), nullable=False, comment='Whether subscription auto-renews'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], name='fk_workspace_subscriptions_plan_id_plans', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_workspace_subscriptions_workspace_id_workspaces', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_workspace_subscriptions'),
        sa.UniqueConstraint('stripe_subscription_id', name='uq_workspace_subscriptions_stripe_subscription_id'),
    )
    op.create_index('ix_workspace_subscriptions_workspace_id', 'workspace_subscriptions', ['workspace_id'], unique=False)
    op.create_index('ix_workspace_subscriptions_plan_id', 'workspace_subscriptions', ['plan_id'], unique=False)
    op.create_index('ix_workspace_subscriptions_status', 'workspace_subscriptions', ['status'], unique=False)
    op.create_index('ix_workspace_subscriptions_next_billing_date', 'workspace_subscriptions', ['next_billing_date'], unique=False)

    op.create_table(
        'subscription_usages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Global unique UUID for usage record'),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Workspace reference'),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Subscription reference'),
        sa.Column('period_start', sa.Date(), nullable=False, comment='Usage period start'),
        sa.Column('period_end', sa.Date(), nullable=False, comment='Usage period end'),
        sa.Column('projects_count', sa.Integer(), nullable=False, comment='Number of active projects'),
        sa.Column('storage_used_bytes', sa.Integer(), nullable=False, comment='Storage used in bytes'),
        sa.Column('ai_tokens_used', sa.Integer(), nullable=False, comment='AI tokens consumed'),
        sa.Column('api_calls_count', sa.Integer(), nullable=False, comment='API calls made'),
        sa.Column('users_count', sa.Integer(), nullable=False, comment='Number of active users'),
        sa.Column('storage_breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Storage breakdown by category (files, database, backups)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['subscription_id'], ['workspace_subscriptions.id'], name='fk_subscription_usages_subscription_id_workspace_subscriptions', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_subscription_usages_workspace_id_workspaces', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_subscription_usages'),
    )
    op.create_index('ix_subscription_usages_workspace_id', 'subscription_usages', ['workspace_id'], unique=False)
    op.create_index('ix_subscription_usages_subscription_id', 'subscription_usages', ['subscription_id'], unique=False)
    op.create_index('ix_subscription_usages_period', 'subscription_usages', ['period_start', 'period_end'], unique=False)

    op.create_table(
        'invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Global unique UUID for invoice'),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Workspace reference'),
        sa.Column('invoice_number', sa.String(length=50), nullable=False, comment="Human-readable invoice number (e.g., 'INV-2026-001')"),
        sa.Column('issue_date', sa.Date(), nullable=False, comment='Invoice issue date'),
        sa.Column('due_date', sa.Date(), nullable=False, comment='Payment due date'),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False, comment='Subtotal before tax'),
        sa.Column('tax_amount', sa.Numeric(10, 2), nullable=False, comment='Tax amount'),
        sa.Column('tax_rate', sa.Numeric(5, 2), nullable=False, comment='Tax rate percentage'),
        sa.Column('total', sa.Numeric(10, 2), nullable=False, comment='Total amount (subtotal + tax)'),
        sa.Column('currency', sa.String(length=3), nullable=False, comment='Currency code (ISO 4217)'),
        sa.Column('status', sa.String(length=20), nullable=False, comment="Status: 'draft', 'sent', 'paid', 'overdue', 'void', 'cancelled'"),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True, comment='Payment timestamp'),
        sa.Column('is_locked', sa.Boolean(), nullable=False, comment='Whether invoice is locked (immutable)'),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True, comment='Lock timestamp'),
        sa.Column('stripe_invoice_id', sa.String(length=255), nullable=True, comment='Stripe invoice ID'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Invoice notes or terms'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Additional metadata'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_invoices_workspace_id_workspaces', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_invoices'),
        sa.UniqueConstraint('invoice_number', name='uq_invoices_invoice_number'),
        sa.UniqueConstraint('stripe_invoice_id', name='uq_invoices_stripe_invoice_id'),
    )
    op.create_index('ix_invoices_workspace_id', 'invoices', ['workspace_id'], unique=False)
    op.create_index('ix_invoices_invoice_number', 'invoices', ['invoice_number'], unique=False)
    op.create_index('ix_invoices_status', 'invoices', ['status'], unique=False)
    op.create_index('ix_invoices_due_date', 'invoices', ['due_date'], unique=False)

    op.create_table(
        'invoice_line_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Global unique UUID for line item'),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Invoice reference'),
        sa.Column('description', sa.Text(), nullable=False, comment='Line item description'),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False, comment='Quantity'),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False, comment='Unit price'),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False, comment='Total amount (quantity × unit_price)'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Additional metadata (e.g., timesheet_entry_ids)'),
        sa.Column('sort_order', sa.Integer(), nullable=False, comment='Display order'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], name='fk_invoice_line_items_invoice_id_invoices', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_invoice_line_items'),
    )
    op.create_index('ix_invoice_line_items_invoice_id', 'invoice_line_items', ['invoice_id'], unique=False)

    op.create_table(
        'billing_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Global unique UUID for transaction'),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Workspace reference'),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Related invoice'),
        sa.Column('transaction_type', sa.String(length=50), nullable=False, comment="Type: 'payment', 'refund', 'credit'"),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False, comment='Transaction amount in USD'),
        sa.Column('currency', sa.String(length=3), nullable=False, comment='Currency code (ISO 4217)'),
        sa.Column('status', sa.String(length=20), nullable=False, comment="Status: 'pending', 'succeeded', 'failed', 'refunded'"),
        sa.Column('payment_method', sa.String(length=50), nullable=False, comment="Payment method: 'stripe', 'paypal', 'bank_transfer'"),
        sa.Column('stripe_charge_id', sa.String(length=255), nullable=True, comment='Stripe charge ID'),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True, comment='Stripe payment intent ID'),
        sa.Column('idempotency_key', sa.String(length=255), nullable=False, comment='Idempotency key to prevent double charging'),
        sa.Column('description', sa.Text(), nullable=True, comment='Transaction description'),
        sa.Column('failure_reason', sa.Text(), nullable=True, comment="Failure reason if status is 'failed'"),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Additional metadata'),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True, comment='Transaction processing timestamp'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], name='fk_billing_transactions_invoice_id_invoices', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_billing_transactions_workspace_id_workspaces', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_billing_transactions'),
        sa.UniqueConstraint('idempotency_key', name='uq_billing_transactions_idempotency_key'),
        sa.UniqueConstraint('stripe_charge_id', name='uq_billing_transactions_stripe_charge_id'),
        sa.UniqueConstraint('stripe_payment_intent_id', name='uq_billing_transactions_stripe_payment_intent_id'),
    )
    op.create_index('ix_billing_transactions_workspace_id', 'billing_transactions', ['workspace_id'], unique=False)
    op.create_index('ix_billing_transactions_status', 'billing_transactions', ['status'], unique=False)
    op.create_index('ix_billing_transactions_created_at', 'billing_transactions', ['created_at'], unique=False)
    op.create_index('ix_billing_transactions_invoice_id', 'billing_transactions', ['invoice_id'], unique=False)

    op.create_table(
        'clients',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Global unique UUID for client'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Client owner (freelancer)'),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Workspace reference'),
        sa.Column('name', sa.String(length=200), nullable=False, comment='Client name or company name'),
        sa.Column('email', sa.String(length=255), nullable=False, comment='Client email'),
        sa.Column('phone', sa.String(length=50), nullable=True, comment='Client phone number'),
        sa.Column('address_line1', sa.String(length=255), nullable=True, comment='Address line 1'),
        sa.Column('address_line2', sa.String(length=255), nullable=True, comment='Address line 2'),
        sa.Column('city', sa.String(length=100), nullable=True, comment='City'),
        sa.Column('state', sa.String(length=100), nullable=True, comment='State/Province'),
        sa.Column('postal_code', sa.String(length=20), nullable=True, comment='Postal/ZIP code'),
        sa.Column('country', sa.String(length=2), nullable=True, comment='Country code (ISO 3166-1 alpha-2)'),
        sa.Column('tax_id', sa.String(length=100), nullable=True, comment='Tax ID or VAT number'),
        sa.Column('default_hourly_rate', sa.Numeric(10, 2), nullable=True, comment='Default hourly rate for freelancer invoices'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='Whether client is active'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Internal notes about client'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name='fk_clients_owner_id_users', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_clients_workspace_id_workspaces', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_clients'),
    )
    op.create_index('ix_clients_owner_id', 'clients', ['owner_id'], unique=False)
    op.create_index('ix_clients_workspace_id', 'clients', ['workspace_id'], unique=False)
    op.create_index('ix_clients_is_active', 'clients', ['is_active'], unique=False)

    op.create_table(
        'freelancer_invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Global unique UUID for freelancer invoice'),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Client reference'),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Workspace reference'),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Invoice creator (freelancer)'),
        sa.Column('invoice_number', sa.String(length=50), nullable=False, comment='Human-readable invoice number'),
        sa.Column('issue_date', sa.Date(), nullable=False, comment='Invoice issue date'),
        sa.Column('due_date', sa.Date(), nullable=False, comment='Payment due date'),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False, comment='Subtotal before tax'),
        sa.Column('hourly_rate', sa.Numeric(10, 2), nullable=True, comment='Hourly rate used for calculation'),
        sa.Column('tax_amount', sa.Numeric(10, 2), nullable=False, comment='Tax amount'),
        sa.Column('total', sa.Numeric(10, 2), nullable=False, comment='Total amount'),
        sa.Column('currency', sa.String(length=3), nullable=False, comment='Currency code'),
        sa.Column('status', sa.String(length=20), nullable=False, comment="Status: 'draft', 'sent', 'paid', 'overdue', 'cancelled'"),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True, comment='Sent timestamp'),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True, comment='Payment timestamp'),
        sa.Column('logo_url', sa.String(length=500), nullable=True, comment='Custom logo URL (Pro only)'),
        sa.Column('brand_color', sa.String(length=7), nullable=True, comment='Brand color hex code (Pro only)'),
        sa.Column('hide_branding', sa.Boolean(), nullable=False, comment="Hide 'Powered by PronaFlow' (Pro only)"),
        sa.Column('notes', sa.Text(), nullable=True, comment='Invoice notes or terms'),
        sa.Column('timesheet_entry_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='List of timesheet entry IDs included in this invoice'),
        sa.Column('pdf_url', sa.String(length=500), nullable=True, comment='Generated PDF URL'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], name='fk_freelancer_invoices_client_id_clients', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_freelancer_invoices_created_by_id_users', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_freelancer_invoices_workspace_id_workspaces', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_freelancer_invoices'),
        sa.UniqueConstraint('invoice_number', name='uq_freelancer_invoices_invoice_number'),
    )
    op.create_index('ix_freelancer_invoices_client_id', 'freelancer_invoices', ['client_id'], unique=False)
    op.create_index('ix_freelancer_invoices_workspace_id', 'freelancer_invoices', ['workspace_id'], unique=False)
    op.create_index('ix_freelancer_invoices_created_by_id', 'freelancer_invoices', ['created_by_id'], unique=False)
    op.create_index('ix_freelancer_invoices_status', 'freelancer_invoices', ['status'], unique=False)
    op.create_index('ix_freelancer_invoices_due_date', 'freelancer_invoices', ['due_date'], unique=False)

    # ===== Module 15: Help Center & Knowledge Base =====
    article_status_enum = postgresql.ENUM('DRAFT', 'PUBLISHED', 'ARCHIVED', name='articlestatus', create_type=False)
    article_visibility_enum = postgresql.ENUM('PUBLIC', 'INTERNAL', 'ROLE_BASED', name='articlevisibilityscope', create_type=False)
    article_status_enum.create(op.get_bind(), checkfirst=True)
    article_visibility_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=120), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], name='fk_categories_parent_id_categories'),
        sa.PrimaryKeyConstraint('id', name='pk_categories'),
    )
    op.create_index('ix_categories_name', 'categories', ['name'], unique=False)
    op.create_index('ix_categories_slug', 'categories', ['slug'], unique=True)
    op.create_index('ix_categories_parent', 'categories', ['parent_id'], unique=False)
    op.create_index('ix_categories_active', 'categories', ['is_active'], unique=False)

    op.create_table(
        'articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('status', article_status_enum, nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], name='fk_articles_author_id_users'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_articles_category_id_categories'),
        sa.PrimaryKeyConstraint('id', name='pk_articles'),
        sa.UniqueConstraint('slug', name='uq_articles_slug'),
    )
    op.create_index('ix_articles_status', 'articles', ['status'], unique=False)
    op.create_index('ix_articles_category', 'articles', ['category_id'], unique=False)
    op.create_index('ix_articles_slug', 'articles', ['slug'], unique=True)

    op.create_table(
        'article_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('version_label', sa.String(length=50), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content_raw', sa.Text(), nullable=False),
        sa.Column('content_rendered', sa.Text(), nullable=True),
        sa.Column('changelog_summary', sa.Text(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='fk_article_versions_article_id_articles', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_article_versions_created_by_id_users'),
        sa.PrimaryKeyConstraint('id', name='pk_article_versions'),
    )
    op.create_index('ix_article_versions_article', 'article_versions', ['article_id'], unique=False)
    op.create_index('ix_article_versions_current', 'article_versions', ['is_current'], unique=False)

    op.create_table(
        'article_translations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('locale', sa.String(length=10), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content_localized', sa.Text(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['version_id'], ['article_versions.id'], name='fk_article_translations_version_id_article_versions', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_article_translations'),
    )
    op.create_index('ix_article_translations_version', 'article_translations', ['version_id'], unique=False)
    op.create_index('ix_article_translations_locale', 'article_translations', ['locale'], unique=False)

    op.create_table(
        'route_mappings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('route_pattern', sa.String(length=255), nullable=False),
        sa.Column('element_selector', sa.String(length=255), nullable=True),
        sa.Column('context_description', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='fk_route_mappings_article_id_articles', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_route_mappings'),
    )
    op.create_index('ix_route_mappings_pattern', 'route_mappings', ['route_pattern'], unique=False)
    op.create_index('ix_route_mappings_priority', 'route_mappings', ['priority'], unique=False)
    op.create_index('ix_route_mappings_active', 'route_mappings', ['is_active'], unique=False)

    op.create_table(
        'article_visibility',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('access_scope', article_visibility_enum, nullable=False),
        sa.Column('allowed_roles', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='fk_article_visibility_article_id_articles', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_article_visibility'),
        sa.UniqueConstraint('article_id', name='uq_article_visibility_article_id'),
    )
    op.create_index('ix_article_visibility_scope', 'article_visibility', ['access_scope'], unique=False)

    op.create_table(
        'article_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_helpful', sa.Boolean(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('route_path', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='fk_article_feedback_article_id_articles', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_article_feedback_user_id_users', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='pk_article_feedback'),
    )
    op.create_index('ix_article_feedback_article', 'article_feedback', ['article_id'], unique=False)
    op.create_index('ix_article_feedback_user', 'article_feedback', ['user_id'], unique=False)

    op.create_table(
        'failed_searches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('query_text', sa.String(length=500), nullable=False),
        sa.Column('locale', sa.String(length=10), nullable=True),
        sa.Column('route_path', sa.String(length=255), nullable=True),
        sa.Column('searched_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_failed_searches_user_id_users', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='pk_failed_searches'),
    )
    op.create_index('ix_failed_searches_query', 'failed_searches', ['query_text'], unique=False)
    op.create_index('ix_failed_searches_searched_at', 'failed_searches', ['searched_at'], unique=False)

    op.create_table(
        'article_search_indexes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('embedding_vector', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('snippet', sa.String(length=500), nullable=True),
        sa.Column('last_indexed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='fk_article_search_indexes_article_id_articles', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_article_search_indexes'),
        sa.UniqueConstraint('article_id', name='uq_article_search_indexes_article_id'),
    )
    op.create_index('ix_article_search_indexes_article', 'article_search_indexes', ['article_id'], unique=False)

    op.create_table(
        'article_tag_map',
        sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='fk_article_tag_map_article_id_articles', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], name='fk_article_tag_map_tag_id_tags', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('article_id', 'tag_id', name='pk_article_tag_map'),
    )

    # ===== Module 16: User Onboarding & Adoption =====
    onboarding_status_enum = postgresql.ENUM('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', name='onboardingstatus', create_type=False)
    onboarding_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'onboarding_surveys',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id', name='pk_onboarding_surveys'),
    )
    op.create_index('ix_onboarding_surveys_active', 'onboarding_surveys', ['is_active'], unique=False)

    op.create_table(
        'survey_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('survey_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_text', sa.String(length=500), nullable=False),
        sa.Column('question_type', sa.String(length=50), nullable=False),
        sa.Column('options', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['survey_id'], ['onboarding_surveys.id'], name='fk_survey_questions_survey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_survey_questions'),
    )
    op.create_index('ix_survey_questions_survey', 'survey_questions', ['survey_id'], unique=False)

    op.create_table(
        'survey_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('answer_text', sa.Text(), nullable=True),
        sa.Column('answer_choice', sa.String(length=255), nullable=True),
        sa.Column('answer_choices', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['question_id'], ['survey_questions.id'], name='fk_survey_responses_question', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_survey_responses_user', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_survey_responses'),
    )
    op.create_index('ix_survey_responses_user', 'survey_responses', ['user_id'], unique=False)
    op.create_index('ix_survey_responses_question', 'survey_responses', ['question_id'], unique=False)

    op.create_table(
        'persona_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=False),
        sa.Column('goal', sa.String(length=255), nullable=True),
        sa.Column('experience', sa.String(length=255), nullable=True),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_persona_profiles_user', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_persona_profiles'),
        sa.UniqueConstraint('user_id', name='uq_persona_profiles_user_id'),
    )
    op.create_index('ix_persona_profiles_user', 'persona_profiles', ['user_id'], unique=False)

    op.create_table(
        'onboarding_flows',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('persona_role', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id', name='pk_onboarding_flows'),
    )

    op.create_table(
        'flow_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('flow_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('route_path', sa.String(length=255), nullable=True),
        sa.Column('required_action', sa.String(length=255), nullable=True),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['flow_id'], ['onboarding_flows.id'], name='fk_flow_steps_flow', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_flow_steps'),
    )
    op.create_index('ix_flow_steps_flow', 'flow_steps', ['flow_id'], unique=False)
    op.create_index('ix_flow_steps_order', 'flow_steps', ['step_order'], unique=False)

    op.create_table(
        'user_onboarding_status',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('flow_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', onboarding_status_enum, nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=False),
        sa.Column('completed_steps', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('skipped_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['flow_id'], ['onboarding_flows.id'], name='fk_user_onboarding_status_flow'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_onboarding_status_user', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_user_onboarding_status'),
        sa.UniqueConstraint('user_id', name='uq_user_onboarding_status_user_id'),
    )
    op.create_index('ix_user_onboarding_status_user', 'user_onboarding_status', ['user_id'], unique=False)
    op.create_index('ix_user_onboarding_status_flow', 'user_onboarding_status', ['flow_id'], unique=False)

    op.create_table(
        'product_tours',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('route_path', sa.String(length=255), nullable=True),
        sa.Column('is_skippable', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id', name='pk_product_tours'),
    )

    op.create_table(
        'tour_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tour_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('target_selector', sa.String(length=255), nullable=False),
        sa.Column('required_action', sa.String(length=255), nullable=True),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['tour_id'], ['product_tours.id'], name='fk_tour_steps_tour', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_tour_steps'),
    )
    op.create_index('ix_tour_steps_tour', 'tour_steps', ['tour_id'], unique=False)
    op.create_index('ix_tour_steps_order', 'tour_steps', ['step_order'], unique=False)

    op.create_table(
        'onboarding_checklists',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id', name='pk_onboarding_checklists'),
    )

    op.create_table(
        'onboarding_checklist_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('checklist_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('route_path', sa.String(length=255), nullable=True),
        sa.Column('required_action', sa.String(length=255), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['checklist_id'], ['onboarding_checklists.id'], name='fk_onb_checklist_items_checklist', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_onboarding_checklist_items'),
    )
    op.create_index('ix_onboarding_checklist_items_checklist', 'onboarding_checklist_items', ['checklist_id'], unique=False)
    op.create_index('ix_onboarding_checklist_items_order', 'onboarding_checklist_items', ['display_order'], unique=False)

    op.create_table(
        'user_checklist_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['item_id'], ['onboarding_checklist_items.id'], name='fk_user_checklist_progress_item', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_checklist_progress_user', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_user_checklist_progress'),
    )
    op.create_index('ix_user_checklist_progress_user', 'user_checklist_progress', ['user_id'], unique=False)
    op.create_index('ix_user_checklist_progress_item', 'user_checklist_progress', ['item_id'], unique=False)

    op.create_table(
        'onboarding_rewards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('checklist_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reward_type', sa.String(length=100), nullable=False),
        sa.Column('reward_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['checklist_id'], ['onboarding_checklists.id'], name='fk_onb_rewards_checklist', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_onboarding_rewards'),
        sa.UniqueConstraint('checklist_id', name='uq_onboarding_rewards_checklist_id'),
    )

    op.create_table(
        'feature_beacons',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('feature_key', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('route_path', sa.String(length=255), nullable=True),
        sa.Column('target_selector', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id', name='pk_feature_beacons'),
    )
    op.create_index('ix_feature_beacons_key', 'feature_beacons', ['feature_key'], unique=False)
    op.create_index('ix_feature_beacons_active', 'feature_beacons', ['is_active'], unique=False)

    op.create_table(
        'user_beacon_states',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('beacon_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_dismissed', sa.Boolean(), nullable=False),
        sa.Column('dismissed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['beacon_id'], ['feature_beacons.id'], name='fk_user_beacon_states_beacon', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_beacon_states_user', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_user_beacon_states'),
    )
    op.create_index('ix_user_beacon_states_user', 'user_beacon_states', ['user_id'], unique=False)
    op.create_index('ix_user_beacon_states_beacon', 'user_beacon_states', ['beacon_id'], unique=False)


def downgrade() -> None:
    # Drop Module 16
    op.drop_table('user_beacon_states')
    op.drop_table('feature_beacons')
    op.drop_table('onboarding_rewards')
    op.drop_table('user_checklist_progress')
    op.drop_table('onboarding_checklist_items')
    op.drop_table('onboarding_checklists')
    op.drop_table('tour_steps')
    op.drop_table('product_tours')
    op.drop_table('user_onboarding_status')
    op.drop_table('flow_steps')
    op.drop_table('onboarding_flows')
    op.drop_table('persona_profiles')
    op.drop_table('survey_responses')
    op.drop_table('survey_questions')
    op.drop_table('onboarding_surveys')
    op.execute('DROP TYPE IF EXISTS onboardingstatus')

    # Drop Module 15
    op.drop_table('article_tag_map')
    op.drop_table('article_search_indexes')
    op.drop_table('failed_searches')
    op.drop_table('article_feedback')
    op.drop_table('article_visibility')
    op.drop_table('article_translations')
    op.drop_table('article_versions')
    op.drop_table('route_mappings')
    op.drop_table('articles')
    op.drop_table('categories')
    op.execute('DROP TYPE IF EXISTS articlevisibilityscope')
    op.execute('DROP TYPE IF EXISTS articlestatus')

    # Drop Module 13
    op.drop_table('freelancer_invoices')
    op.drop_table('clients')
    op.drop_table('billing_transactions')
    op.drop_table('invoice_line_items')
    op.drop_table('invoices')
    op.drop_table('subscription_usages')
    op.drop_table('workspace_subscriptions')
    op.drop_table('plans')
