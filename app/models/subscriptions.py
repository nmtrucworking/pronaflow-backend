"""
Entity Models for Functional Module 13: Subscription & Billing Management
Provides Plan, WorkspaceSubscription, SubscriptionUsage, BillingTransaction, 
Invoice, InvoiceLineItem, Client, FreelancerInvoice models.
Ref: docs/01-Requirements/Functional-Modules/13 - Subscription and Billing Management.md
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import String, DateTime, ForeignKey, Index, Boolean, Text, Integer, Numeric, Date, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.workspaces import Workspace
    from app.models.users import User


# ======= Entity Tables =======

class Plan(Base, TimestampMixin):
    """
    Plan Model - Subscription plans (Free, Pro, Enterprise).
    Defines pricing tiers and feature limits.
    Ref: Module 13 - Feature 13.1 - AC 1
    """
    __tablename__ = "plans"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for plan"
    )

    # Plan Information
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Plan name (e.g., 'Free', 'Pro', 'Enterprise')"
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Friendly display name"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Plan description"
    )

    # Pricing
    price_monthly: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="Monthly price in USD"
    )

    price_yearly: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="Yearly price in USD"
    )

    # Resource Limits (Quota)
    max_projects: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        comment="Maximum number of projects"
    )

    max_storage_gb: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Maximum storage in GB"
    )

    max_ai_tokens_monthly: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10000,
        comment="AI tokens quota per month"
    )

    max_users_per_workspace: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        comment="Maximum users per workspace"
    )

    # Feature Flags
    features: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Feature flags (SSO, Custom Fields, Advanced AI, etc.)"
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether plan is available for subscription"
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether plan is publicly visible"
    )

    # Sorting
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Display order (lower = shown first)"
    )

    # Relationships
    subscriptions: Mapped[List["WorkspaceSubscription"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index('ix_plans_name', 'name'),
        Index('ix_plans_is_active', 'is_active'),
    )


class WorkspaceSubscription(Base, TimestampMixin):
    """
    WorkspaceSubscription Model - Links workspace to a plan.
    Tracks subscription lifecycle (trial, active, expired).
    Ref: Module 13 - Feature 13.1
    """
    __tablename__ = "workspace_subscriptions"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for subscription"
    )

    # Foreign Keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Workspace reference"
    )

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('plans.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
        comment="Plan reference"
    )

    # Subscription Period
    billing_cycle: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='monthly',
        comment="Billing cycle: 'monthly' or 'yearly'"
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Subscription start date"
    )

    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Subscription end date (null = ongoing)"
    )

    next_billing_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Next billing date"
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='active',
        index=True,
        comment="Status: 'trial', 'active', 'cancelled', 'expired', 'grace_period'"
    )

    # Trial
    is_trial: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this is a trial subscription"
    )

    trial_end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Trial end date"
    )

    # Cancellation
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Cancellation timestamp"
    )

    cancellation_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for cancellation"
    )

    # Payment
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        comment="Stripe subscription ID"
    )

    auto_renew: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether subscription auto-renews"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="subscription")
    plan: Mapped["Plan"] = relationship(back_populates="subscriptions")
    usages: Mapped[List["SubscriptionUsage"]] = relationship(
        back_populates="subscription",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index('ix_workspace_subscriptions_workspace_id', 'workspace_id'),
        Index('ix_workspace_subscriptions_status', 'status'),
        Index('ix_workspace_subscriptions_next_billing_date', 'next_billing_date'),
    )


class SubscriptionUsage(Base, TimestampMixin):
    """
    SubscriptionUsage Model - Tracks resource consumption.
    Used for soft limit warnings and usage dashboard.
    Ref: Module 13 - Feature 13.4 - AC 1
    """
    __tablename__ = "subscription_usages"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for usage record"
    )

    # Foreign Keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Workspace reference"
    )

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspace_subscriptions.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Subscription reference"
    )

    # Period
    period_start: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Usage period start"
    )

    period_end: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Usage period end"
    )

    # Usage Metrics
    projects_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of active projects"
    )

    storage_used_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Storage used in bytes"
    )

    ai_tokens_used: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="AI tokens consumed"
    )

    api_calls_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="API calls made"
    )

    users_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of active users"
    )

    # Breakdown
    storage_breakdown: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Storage breakdown by category (files, database, backups)"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship()
    subscription: Mapped["WorkspaceSubscription"] = relationship(back_populates="usages")

    # Indexes
    __table_args__ = (
        Index('ix_subscription_usages_workspace_id', 'workspace_id'),
        Index('ix_subscription_usages_period', 'period_start', 'period_end'),
    )


class BillingTransaction(Base, TimestampMixin):
    """
    BillingTransaction Model - Payment transaction records.
    Tracks all payment attempts and their statuses.
    Ref: Module 13 - Feature 13.1 - AC 3
    """
    __tablename__ = "billing_transactions"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for transaction"
    )

    # Foreign Keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Workspace reference"
    )

    invoice_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('invoices.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="Related invoice"
    )

    # Transaction Details
    transaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type: 'payment', 'refund', 'credit'"
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Transaction amount in USD"
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default='USD',
        comment="Currency code (ISO 4217)"
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='pending',
        index=True,
        comment="Status: 'pending', 'succeeded', 'failed', 'refunded'"
    )

    # Payment Gateway
    payment_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Payment method: 'stripe', 'paypal', 'bank_transfer'"
    )

    stripe_charge_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        comment="Stripe charge ID"
    )

    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        comment="Stripe payment intent ID"
    )

    # Idempotency
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="Idempotency key to prevent double charging"
    )

    # Metadata
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Transaction description"
    )

    failure_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Failure reason if status is 'failed'"
    )

    metadata_: Mapped[Optional[dict]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Additional metadata"
    )

    # Timestamps
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Transaction processing timestamp"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship()
    invoice: Mapped[Optional["Invoice"]] = relationship(back_populates="transactions")

    # Indexes
    __table_args__ = (
        Index('ix_billing_transactions_workspace_id', 'workspace_id'),
        Index('ix_billing_transactions_status', 'status'),
        Index('ix_billing_transactions_created_at', 'created_at'),
    )


class Invoice(Base, TimestampMixin):
    """
    Invoice Model - Billing invoices for subscriptions.
    Immutable once sent (Financial Immutability).
    Ref: Module 13 - Business Rule 3.2
    """
    __tablename__ = "invoices"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for invoice"
    )

    # Foreign Keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Workspace reference"
    )

    # Invoice Number
    invoice_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Human-readable invoice number (e.g., 'INV-2026-001')"
    )

    # Dates
    issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Invoice issue date"
    )

    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Payment due date"
    )

    # Amounts
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Subtotal before tax"
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="Tax amount"
    )

    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=0,
        comment="Tax rate percentage"
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Total amount (subtotal + tax)"
    )

    # Currency
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default='USD',
        comment="Currency code (ISO 4217)"
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='draft',
        index=True,
        comment="Status: 'draft', 'sent', 'paid', 'overdue', 'void', 'cancelled'"
    )

    # Payment
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Payment timestamp"
    )

    # Immutability
    is_locked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether invoice is locked (immutable)"
    )

    locked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Lock timestamp"
    )

    # Stripe Integration
    stripe_invoice_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        comment="Stripe invoice ID"
    )

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Invoice notes or terms"
    )

    # Metadata
    metadata_: Mapped[Optional[dict]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Additional metadata"
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship()
    line_items: Mapped[List["InvoiceLineItem"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan"
    )
    transactions: Mapped[List["BillingTransaction"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index('ix_invoices_workspace_id', 'workspace_id'),
        Index('ix_invoices_invoice_number', 'invoice_number'),
        Index('ix_invoices_status', 'status'),
        Index('ix_invoices_due_date', 'due_date'),
    )


class InvoiceLineItem(Base, TimestampMixin):
    """
    InvoiceLineItem Model - Individual line items in an invoice.
    Ref: Module 13 - Feature 13.3 - AC 1
    """
    __tablename__ = "invoice_line_items"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for line item"
    )

    # Foreign Keys
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('invoices.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Invoice reference"
    )

    # Item Details
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Line item description"
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=1,
        comment="Quantity"
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Unit price"
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Total amount (quantity × unit_price)"
    )

    # Metadata
    metadata_: Mapped[Optional[dict]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Additional metadata (e.g., timesheet_entry_ids)"
    )

    # Sorting
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Display order"
    )

    # Relationships
    invoice: Mapped["Invoice"] = relationship(back_populates="line_items")

    # Indexes
    __table_args__ = (
        Index('ix_invoice_line_items_invoice_id', 'invoice_id'),
    )


class Client(Base, TimestampMixin):
    """
    Client Model - Client information for freelancer invoicing.
    Ref: Module 13 - Feature 13.3
    """
    __tablename__ = "clients"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for client"
    )

    # Foreign Keys
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Client owner (freelancer)"
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Workspace reference"
    )

    # Client Information
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Client name or company name"
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Client email"
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Client phone number"
    )

    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Address line 1"
    )

    address_line2: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Address line 2"
    )

    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="City"
    )

    state: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="State/Province"
    )

    postal_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Postal/ZIP code"
    )

    country: Mapped[Optional[str]] = mapped_column(
        String(2),
        nullable=True,
        comment="Country code (ISO 3166-1 alpha-2)"
    )

    # Tax
    tax_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Tax ID or VAT number"
    )

    default_hourly_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Default hourly rate for freelancer invoices"
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether client is active"
    )

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Internal notes about client"
    )

    # Relationships
    owner: Mapped["User"] = relationship()
    workspace: Mapped["Workspace"] = relationship()
    freelancer_invoices: Mapped[List["FreelancerInvoice"]] = relationship(
        back_populates="client",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index('ix_clients_owner_id', 'owner_id'),
        Index('ix_clients_workspace_id', 'workspace_id'),
        Index('ix_clients_is_active', 'is_active'),
    )


class FreelancerInvoice(Base, TimestampMixin):
    """
    FreelancerInvoice Model - Invoices created by freelancers for clients.
    Generated from timesheet entries.
    Ref: Module 13 - Feature 13.3 - AC 1, 2
    """
    __tablename__ = "freelancer_invoices"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Global unique UUID for freelancer invoice"
    )

    # Foreign Keys
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('clients.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Client reference"
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('workspaces.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Workspace reference"
    )

    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Invoice creator (freelancer)"
    )

    # Invoice Number
    invoice_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Human-readable invoice number"
    )

    # Dates
    issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Invoice issue date"
    )

    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Payment due date"
    )

    # Amounts
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Subtotal before tax"
    )

    hourly_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Hourly rate used for calculation"
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="Tax amount"
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Total amount"
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default='USD',
        comment="Currency code"
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='draft',
        index=True,
        comment="Status: 'draft', 'sent', 'paid', 'overdue', 'cancelled'"
    )

    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Sent timestamp"
    )

    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Payment timestamp"
    )

    # Branding (Pro feature)
    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Custom logo URL (Pro only)"
    )

    brand_color: Mapped[Optional[str]] = mapped_column(
        String(7),
        nullable=True,
        comment="Brand color hex code (Pro only)"
    )

    hide_branding: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Hide 'Powered by PronaFlow' (Pro only)"
    )

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Invoice notes or terms"
    )

    # Timesheet Entries
    timesheet_entry_ids: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="List of timesheet entry IDs included in this invoice"
    )

    # PDF
    pdf_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Generated PDF URL"
    )

    # Relationships
    client: Mapped["Client"] = relationship(back_populates="freelancer_invoices")
    workspace: Mapped["Workspace"] = relationship()
    created_by: Mapped["User"] = relationship()

    # Indexes
    __table_args__ = (
        Index('ix_freelancer_invoices_client_id', 'client_id'),
        Index('ix_freelancer_invoices_workspace_id', 'workspace_id'),
        Index('ix_freelancer_invoices_created_by_id', 'created_by_id'),
        Index('ix_freelancer_invoices_status', 'status'),
        Index('ix_freelancer_invoices_due_date', 'due_date'),
    )
