"""
API endpoints for Subscription & Billing Management (Module 13)
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.db.models.users import User
from app.services.subscription import (
    PlanService,
    SubscriptionService,
    UsageService,
    ClientService,
    FreelancerInvoiceService,
)
from app.schemas.subscription import (
    PlanResponse,
    PlanCreate,
    PlanUpdate,
    WorkspaceSubscriptionResponse,
    WorkspaceSubscriptionCreate,
    UsageSummary,
    SubscriptionUsageResponse,
    ClientResponse,
    ClientCreate,
    ClientUpdate,
    FreelancerInvoiceResponse,
    FreelancerInvoiceCreate,
    FreelancerInvoiceUpdate,
    UpgradeRequest,
    CancelSubscriptionRequest,
)

router = APIRouter(prefix="/subscription", tags=["Subscription & Billing"])


# ======= Plan Endpoints =======

@router.get("/plans", response_model=List[PlanResponse])
def list_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all available subscription plans.
    Returns public plans for regular users, all plans for admins.
    """
    service = PlanService(db)
    
    # TODO: Check if user is admin
    is_admin = False  # Replace with actual admin check
    
    if is_admin:
        return service.list_all_plans()
    else:
        return service.list_public_plans()


@router.post("/plans", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new subscription plan (Admin only).
    """
    # TODO: Check if user is admin
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    service = PlanService(db)
    return service.create_plan(plan_data)


@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get plan details by ID"""
    service = PlanService(db)
    plan = service.get_plan(plan_id)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    return plan


@router.patch("/plans/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: UUID,
    plan_data: PlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update plan (Admin only)"""
    # TODO: Check if user is admin
    service = PlanService(db)
    return service.update_plan(plan_id, plan_data)


# ======= Subscription Endpoints =======

@router.get("/workspaces/{workspace_id}/subscription", response_model=WorkspaceSubscriptionResponse)
def get_workspace_subscription(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current subscription for workspace.
    Module 13 - Feature 13.1
    """
    service = SubscriptionService(db)
    subscription = service.get_workspace_subscription(workspace_id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return subscription


@router.post("/workspaces/{workspace_id}/subscription", response_model=WorkspaceSubscriptionResponse)
def create_subscription(
    workspace_id: UUID,
    subscription_data: WorkspaceSubscriptionCreate,
    is_trial: bool = Query(False, description="Create as trial subscription"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create subscription for workspace"""
    service = SubscriptionService(db)
    return service.create_subscription(workspace_id, subscription_data, is_trial)


@router.post("/workspaces/{workspace_id}/subscription/upgrade", response_model=WorkspaceSubscriptionResponse)
def upgrade_subscription(
    workspace_id: UUID,
    upgrade_data: UpgradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upgrade workspace subscription to a different plan.
    Module 13 - Feature 13.1 - AC 3: Instant Upgrade
    """
    service = SubscriptionService(db)
    return service.upgrade_subscription(workspace_id, upgrade_data, current_user.id)


@router.post("/workspaces/{workspace_id}/subscription/cancel", response_model=WorkspaceSubscriptionResponse)
def cancel_subscription(
    workspace_id: UUID,
    cancel_data: CancelSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel workspace subscription"""
    service = SubscriptionService(db)
    return service.cancel_subscription(workspace_id, cancel_data, current_user.id)


# ======= Usage Endpoints =======

@router.get("/workspaces/{workspace_id}/usage/summary", response_model=UsageSummary)
def get_usage_summary(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get usage summary with warnings.
    Module 13 - Feature 13.4 - AC 1: Resource Breakdown
    Module 13 - Feature 13.1 - AC 1: Soft Limit Warning
    """
    service = UsageService(db)
    return service.get_usage_summary(workspace_id)


@router.get("/workspaces/{workspace_id}/usage", response_model=SubscriptionUsageResponse)
def get_current_usage(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current usage period details"""
    service = UsageService(db)
    usage = service.get_current_usage(workspace_id)
    
    if not usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active usage period found"
        )
    
    return usage


# ======= Client Endpoints (Freelancer Feature) =======

@router.get("/workspaces/{workspace_id}/clients", response_model=List[ClientResponse])
def list_clients(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all clients for current user in workspace.
    Module 13 - Feature 13.3
    """
    service = ClientService(db)
    return service.list_clients(current_user.id, workspace_id)


@router.post("/workspaces/{workspace_id}/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    workspace_id: UUID,
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new client"""
    # Ensure workspace_id matches
    client_data.workspace_id = workspace_id
    service = ClientService(db)
    return service.create_client(client_data, current_user.id)


@router.get("/clients/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get client by ID"""
    service = ClientService(db)
    client = service.get_client(client_id, current_user.id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client


@router.patch("/clients/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update client"""
    service = ClientService(db)
    return service.update_client(client_id, client_data, current_user.id)


@router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete client (soft delete)"""
    service = ClientService(db)
    success = service.delete_client(client_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )


# ======= Freelancer Invoice Endpoints =======

@router.get("/workspaces/{workspace_id}/invoices", response_model=List[FreelancerInvoiceResponse])
def list_invoices(
    workspace_id: UUID,
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List invoices for current user.
    Module 13 - Feature 13.3 - AC 1
    """
    service = FreelancerInvoiceService(db)
    return service.list_invoices(workspace_id, current_user.id, status)


@router.post("/workspaces/{workspace_id}/invoices", response_model=FreelancerInvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    workspace_id: UUID,
    invoice_data: FreelancerInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create freelancer invoice from timesheet entries.
    Module 13 - Feature 13.3 - AC 1: Basic Invoicing
    Module 13 - Feature 13.3 - AC 2: Branded Invoicing (Pro)
    """
    # Ensure workspace_id matches
    invoice_data.workspace_id = workspace_id
    service = FreelancerInvoiceService(db)
    return service.create_invoice(invoice_data, current_user.id)


@router.get("/invoices/{invoice_id}", response_model=FreelancerInvoiceResponse)
def get_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get invoice by ID"""
    service = FreelancerInvoiceService(db)
    invoice = service.get_invoice(invoice_id)
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Check ownership
    if invoice.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return invoice


@router.patch("/invoices/{invoice_id}/status")
def update_invoice_status(
    invoice_id: UUID,
    new_status: str = Query(..., pattern="^(draft|sent|paid|overdue|cancelled)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update invoice status.
    Module 13 - Feature 13.3 - AC 3: Payment Tracking
    """
    service = FreelancerInvoiceService(db)
    return service.update_invoice_status(invoice_id, new_status, current_user.id)


@router.post("/invoices/{invoice_id}/generate-pdf")
def generate_invoice_pdf(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate PDF for invoice.
    Module 13 - Feature 13.3 - AC 2: Branded Invoicing
    """
    service = FreelancerInvoiceService(db)
    pdf_url = service.generate_pdf(invoice_id)
    
    return {"pdf_url": pdf_url}
