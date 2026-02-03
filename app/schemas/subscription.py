"""
Pydantic schemas for Subscription & Billing Management (Module 13)
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, validator


# ======= Plan Schemas =======

class PlanBase(BaseModel):
    """Base schema for Plan"""
    name: str = Field(..., max_length=100)
    display_name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price_monthly: Decimal = Field(default=Decimal('0.00'), ge=0)
    price_yearly: Decimal = Field(default=Decimal('0.00'), ge=0)
    max_projects: int = Field(default=3, ge=0)
    max_storage_gb: int = Field(default=1, ge=0)
    max_ai_tokens_monthly: int = Field(default=10000, ge=0)
    max_users_per_workspace: int = Field(default=5, ge=1)
    features: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    is_public: bool = True
    sort_order: int = 0


class PlanCreate(PlanBase):
    """Schema for creating a plan"""
    pass


class PlanUpdate(BaseModel):
    """Schema for updating a plan"""
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    price_monthly: Optional[Decimal] = Field(None, ge=0)
    price_yearly: Optional[Decimal] = Field(None, ge=0)
    max_projects: Optional[int] = Field(None, ge=0)
    max_storage_gb: Optional[int] = Field(None, ge=0)
    max_ai_tokens_monthly: Optional[int] = Field(None, ge=0)
    max_users_per_workspace: Optional[int] = Field(None, ge=1)
    features: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    sort_order: Optional[int] = None


class PlanResponse(PlanBase):
    """Schema for plan response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ======= Workspace Subscription Schemas =======

class WorkspaceSubscriptionBase(BaseModel):
    """Base schema for WorkspaceSubscription"""
    billing_cycle: str = Field(default='monthly', pattern='^(monthly|yearly)$')
    auto_renew: bool = True


class WorkspaceSubscriptionCreate(WorkspaceSubscriptionBase):
    """Schema for creating a workspace subscription"""
    plan_id: UUID


class WorkspaceSubscriptionUpdate(BaseModel):
    """Schema for updating a workspace subscription"""
    billing_cycle: Optional[str] = Field(None, pattern='^(monthly|yearly)$')
    auto_renew: Optional[bool] = None
    cancellation_reason: Optional[str] = None


class WorkspaceSubscriptionResponse(WorkspaceSubscriptionBase):
    """Schema for workspace subscription response"""
    id: UUID
    workspace_id: UUID
    plan_id: UUID
    start_date: date
    end_date: Optional[date]
    next_billing_date: Optional[date]
    status: str
    is_trial: bool
    trial_end_date: Optional[date]
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Nested
    plan: Optional[PlanResponse] = None

    class Config:
        from_attributes = True


# ======= Subscription Usage Schemas =======

class SubscriptionUsageBase(BaseModel):
    """Base schema for SubscriptionUsage"""
    projects_count: int = 0
    storage_used_bytes: int = 0
    ai_tokens_used: int = 0
    api_calls_count: int = 0
    users_count: int = 0
    storage_breakdown: Optional[Dict[str, Any]] = None


class SubscriptionUsageResponse(SubscriptionUsageBase):
    """Schema for subscription usage response"""
    id: UUID
    workspace_id: UUID
    subscription_id: UUID
    period_start: date
    period_end: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UsageSummary(BaseModel):
    """Summary of current usage vs limits"""
    projects: Dict[str, int] = Field(
        ...,
        description="{'used': 2, 'limit': 3, 'percentage': 66}"
    )
    storage: Dict[str, Any] = Field(
        ...,
        description="{'used_gb': 0.8, 'limit_gb': 1, 'percentage': 80}"
    )
    ai_tokens: Dict[str, int] = Field(
        ...,
        description="{'used': 7500, 'limit': 10000, 'percentage': 75}"
    )
    users: Dict[str, int] = Field(
        ...,
        description="{'used': 3, 'limit': 5, 'percentage': 60}"
    )
    warnings: List[str] = Field(default_factory=list)


# ======= Billing Transaction Schemas =======

class BillingTransactionBase(BaseModel):
    """Base schema for BillingTransaction"""
    transaction_type: str = Field(..., pattern='^(payment|refund|credit)$')
    amount: Decimal = Field(..., ge=0)
    currency: str = Field(default='USD', max_length=3)
    payment_method: str
    description: Optional[str] = None


class BillingTransactionCreate(BillingTransactionBase):
    """Schema for creating a billing transaction"""
    workspace_id: UUID
    invoice_id: Optional[UUID] = None
    idempotency_key: str


class BillingTransactionResponse(BillingTransactionBase):
    """Schema for billing transaction response"""
    id: UUID
    workspace_id: UUID
    invoice_id: Optional[UUID]
    status: str
    stripe_charge_id: Optional[str]
    stripe_payment_intent_id: Optional[str]
    idempotency_key: str
    failure_reason: Optional[str]
    metadata: Optional[Dict[str, Any]]
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ======= Invoice Schemas =======

class InvoiceLineItemBase(BaseModel):
    """Base schema for InvoiceLineItem"""
    description: str
    quantity: Decimal = Field(default=Decimal('1.00'), gt=0)
    unit_price: Decimal = Field(..., ge=0)
    metadata: Optional[Dict[str, Any]] = None


class InvoiceLineItemCreate(InvoiceLineItemBase):
    """Schema for creating an invoice line item"""
    pass


class InvoiceLineItemResponse(InvoiceLineItemBase):
    """Schema for invoice line item response"""
    id: UUID
    invoice_id: UUID
    amount: Decimal
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    """Base schema for Invoice"""
    due_date: date
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    """Schema for creating an invoice"""
    line_items: List[InvoiceLineItemCreate]
    tax_rate: Decimal = Field(default=Decimal('0.00'), ge=0, le=100)


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice (only for drafts)"""
    due_date: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[str] = Field(None, pattern='^(draft|sent|paid|overdue|void|cancelled)$')


class InvoiceResponse(InvoiceBase):
    """Schema for invoice response"""
    id: UUID
    workspace_id: UUID
    invoice_number: str
    issue_date: date
    subtotal: Decimal
    tax_amount: Decimal
    tax_rate: Decimal
    total: Decimal
    currency: str
    status: str
    paid_at: Optional[datetime]
    is_locked: bool
    locked_at: Optional[datetime]
    stripe_invoice_id: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    # Nested
    line_items: List[InvoiceLineItemResponse] = []

    class Config:
        from_attributes = True


# ======= Client Schemas =======

class ClientBase(BaseModel):
    """Base schema for Client"""
    name: str = Field(..., max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=2)
    tax_id: Optional[str] = Field(None, max_length=100)
    default_hourly_rate: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    """Schema for creating a client"""
    workspace_id: UUID


class ClientUpdate(BaseModel):
    """Schema for updating a client"""
    name: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=2)
    tax_id: Optional[str] = Field(None, max_length=100)
    default_hourly_rate: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ClientResponse(ClientBase):
    """Schema for client response"""
    id: UUID
    owner_id: UUID
    workspace_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ======= Freelancer Invoice Schemas =======

class FreelancerInvoiceBase(BaseModel):
    """Base schema for FreelancerInvoice"""
    due_date: date
    notes: Optional[str] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    brand_color: Optional[str] = Field(None, max_length=7, pattern='^#[0-9A-Fa-f]{6}$')
    hide_branding: bool = False


class FreelancerInvoiceCreate(FreelancerInvoiceBase):
    """Schema for creating a freelancer invoice"""
    client_id: UUID
    workspace_id: UUID
    timesheet_entry_ids: List[UUID]
    tax_rate: Decimal = Field(default=Decimal('0.00'), ge=0, le=100)
    hourly_rate: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(default='USD', max_length=3)


class FreelancerInvoiceUpdate(BaseModel):
    """Schema for updating a freelancer invoice (only for drafts)"""
    due_date: Optional[date] = None
    notes: Optional[str] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    brand_color: Optional[str] = Field(None, max_length=7, pattern='^#[0-9A-Fa-f]{6}$')
    hide_branding: Optional[bool] = None
    status: Optional[str] = Field(None, pattern='^(draft|sent|paid|overdue|cancelled)$')


class FreelancerInvoiceResponse(FreelancerInvoiceBase):
    """Schema for freelancer invoice response"""
    id: UUID
    client_id: UUID
    workspace_id: UUID
    created_by_id: UUID
    invoice_number: str
    issue_date: date
    subtotal: Decimal
    hourly_rate: Optional[Decimal]
    tax_amount: Decimal
    total: Decimal
    currency: str
    status: str
    sent_at: Optional[datetime]
    paid_at: Optional[datetime]
    timesheet_entry_ids: List[UUID]
    pdf_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Nested
    client: Optional[ClientResponse] = None

    class Config:
        from_attributes = True


# ======= Upgrade/Downgrade Schemas =======

class UpgradeRequest(BaseModel):
    """Schema for upgrade request"""
    plan_id: UUID
    billing_cycle: str = Field(..., pattern='^(monthly|yearly)$')
    payment_method_id: Optional[str] = None  # Stripe payment method


class CancelSubscriptionRequest(BaseModel):
    """Schema for cancellation request"""
    reason: Optional[str] = None
    immediate: bool = Field(
        default=False,
        description="If true, cancel immediately. Otherwise, cancel at period end."
    )
