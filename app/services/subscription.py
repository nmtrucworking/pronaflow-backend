"""
Service layer for Subscription & Billing Management (Module 13)
Handles subscription lifecycle, usage tracking, and invoicing
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
try:
    import stripe
except ImportError:  # pragma: no cover - optional dependency
    stripe = None
try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen import canvas
except ImportError:  # pragma: no cover - optional dependency
    LETTER = None
    canvas = None

from app.models.subscriptions import (
    Plan,
    WorkspaceSubscription,
    SubscriptionUsage,
    BillingTransaction,
    Invoice,
    InvoiceLineItem,
    Client,
    FreelancerInvoice,
)
from app.models.tasks import TimeEntry
from app.models.workspaces import Workspace
from app.core.config import settings
from app.schemas.subscription import (
    PlanCreate,
    PlanUpdate,
    WorkspaceSubscriptionCreate,
    UsageSummary,
    InvoiceCreate,
    ClientCreate,
    ClientUpdate,
    FreelancerInvoiceCreate,
    UpgradeRequest,
    CancelSubscriptionRequest,
)


class PlanService:
    """Service for managing subscription plans"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_plan(self, plan_data: PlanCreate) -> Plan:
        """Create a new subscription plan"""
        plan = Plan(**plan_data.model_dump())
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan
    
    def get_plan(self, plan_id: UUID) -> Optional[Plan]:
        """Get plan by ID"""
        return self.db.query(Plan).filter(Plan.id == plan_id).first()
    
    def get_plan_by_name(self, name: str) -> Optional[Plan]:
        """Get plan by name"""
        return self.db.query(Plan).filter(Plan.name == name).first()
    
    def list_public_plans(self) -> List[Plan]:
        """List all public active plans"""
        return self.db.query(Plan).filter(
            and_(
                Plan.is_active == True,
                Plan.is_public == True
            )
        ).order_by(Plan.sort_order).all()
    
    def list_all_plans(self) -> List[Plan]:
        """List all plans (admin only)"""
        return self.db.query(Plan).order_by(Plan.sort_order).all()
    
    def update_plan(self, plan_id: UUID, plan_data: PlanUpdate) -> Plan:
        """Update a plan"""
        plan = self.get_plan(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        update_data = plan_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(plan, key, value)
        
        self.db.commit()
        self.db.refresh(plan)
        return plan
    
    def delete_plan(self, plan_id: UUID) -> bool:
        """Delete a plan (soft delete by deactivating)"""
        plan = self.get_plan(plan_id)
        if not plan:
            return False
        
        # Check if any active subscriptions exist
        active_subs = self.db.query(WorkspaceSubscription).filter(
            and_(
                WorkspaceSubscription.plan_id == plan_id,
                WorkspaceSubscription.status.in_(['active', 'trial'])
            )
        ).first()
        
        if active_subs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete plan with active subscriptions"
            )
        
        plan.is_active = False
        self.db.commit()
        return True


class SubscriptionService:
    """Service for managing workspace subscriptions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_subscription(
        self,
        workspace_id: UUID,
        subscription_data: WorkspaceSubscriptionCreate,
        is_trial: bool = False
    ) -> WorkspaceSubscription:
        """Create a new subscription for workspace"""
        # Check if workspace already has active subscription
        existing = self.db.query(WorkspaceSubscription).filter(
            and_(
                WorkspaceSubscription.workspace_id == workspace_id,
                WorkspaceSubscription.status.in_(['active', 'trial'])
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace already has an active subscription"
            )
        
        # Verify plan exists
        plan = self.db.query(Plan).filter(Plan.id == subscription_data.plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        # Calculate dates
        start_date = date.today()
        if is_trial:
            trial_end_date = start_date + timedelta(days=14)  # 14-day trial
            next_billing_date = trial_end_date
            sub_status = 'trial'
        else:
            trial_end_date = None
            if subscription_data.billing_cycle == 'monthly':
                next_billing_date = start_date + timedelta(days=30)
            else:  # yearly
                next_billing_date = start_date + timedelta(days=365)
            sub_status = 'active'
        
        subscription = WorkspaceSubscription(
            workspace_id=workspace_id,
            plan_id=subscription_data.plan_id,
            billing_cycle=subscription_data.billing_cycle,
            start_date=start_date,
            next_billing_date=next_billing_date,
            status=sub_status,
            is_trial=is_trial,
            trial_end_date=trial_end_date,
            auto_renew=subscription_data.auto_renew,
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        # Create initial usage record
        self._create_usage_period(subscription.id, workspace_id)
        
        return subscription
    
    def get_workspace_subscription(self, workspace_id: UUID) -> Optional[WorkspaceSubscription]:
        """Get active subscription for workspace"""
        return self.db.query(WorkspaceSubscription).filter(
            and_(
                WorkspaceSubscription.workspace_id == workspace_id,
                WorkspaceSubscription.status.in_(['active', 'trial', 'grace_period'])
            )
        ).options(joinedload(WorkspaceSubscription.plan)).first()

    def extend_trial(self, workspace_id: UUID, additional_days: int) -> Optional[WorkspaceSubscription]:
        """
        Extend trial period for a workspace (Module 16 reward integration).
        """
        if additional_days <= 0:
            return None

        subscription = self.get_workspace_subscription(workspace_id)
        if not subscription or not subscription.is_trial or not subscription.trial_end_date:
            return None

        subscription.trial_end_date = subscription.trial_end_date + timedelta(days=additional_days)
        subscription.next_billing_date = subscription.trial_end_date
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    def upgrade_subscription(
        self,
        workspace_id: UUID,
        upgrade_data: UpgradeRequest,
        user_id: UUID
    ) -> WorkspaceSubscription:
        """Upgrade workspace to a different plan (Module 13 - Feature 13.1 - AC 3)"""
        current_sub = self.get_workspace_subscription(workspace_id)
        
        # Verify new plan
        new_plan = self.db.query(Plan).filter(Plan.id == upgrade_data.plan_id).first()
        if not new_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        if current_sub:
            # Cancel current subscription
            current_sub.status = 'cancelled'
            current_sub.cancelled_at = datetime.utcnow()
            current_sub.end_date = date.today()
        
        # Create new subscription
        new_sub_data = WorkspaceSubscriptionCreate(
            plan_id=upgrade_data.plan_id,
            billing_cycle=upgrade_data.billing_cycle,
            auto_renew=True
        )
        
        new_sub = self.create_subscription(workspace_id, new_sub_data, is_trial=False)

        if upgrade_data.payment_method_id:
            amount = self._calculate_plan_amount(new_plan, upgrade_data.billing_cycle)
            self._process_payment(
                workspace_id=workspace_id,
                amount=amount,
                currency=settings.STRIPE_CURRENCY,
                payment_method_id=upgrade_data.payment_method_id,
                description=f"Subscription upgrade to {new_plan.name}",
            )
        
        return new_sub
    
    def cancel_subscription(
        self,
        workspace_id: UUID,
        cancel_data: CancelSubscriptionRequest,
        user_id: UUID
    ) -> WorkspaceSubscription:
        """Cancel workspace subscription"""
        subscription = self.get_workspace_subscription(workspace_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        subscription.cancellation_reason = cancel_data.reason
        subscription.cancelled_at = datetime.utcnow()
        
        if cancel_data.immediate:
            subscription.status = 'cancelled'
            subscription.end_date = date.today()
        else:
            # Cancel at period end
            subscription.auto_renew = False
            subscription.end_date = subscription.next_billing_date
        
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def _calculate_plan_amount(self, plan: Plan, billing_cycle: str) -> Decimal:
        if billing_cycle == "yearly":
            return plan.price_yearly
        return plan.price_monthly

    def _process_payment(
        self,
        workspace_id: UUID,
        amount: Decimal,
        currency: str,
        payment_method_id: str,
        description: str,
    ) -> BillingTransaction:
        if stripe is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stripe SDK is not installed"
            )
        if not settings.STRIPE_SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stripe is not configured"
            )

        stripe.api_key = settings.STRIPE_SECRET_KEY
        idempotency_key = str(uuid4())

        transaction = BillingTransaction(
            workspace_id=workspace_id,
            transaction_type="payment",
            amount=amount,
            currency=currency.upper(),
            status="pending",
            payment_method="stripe",
            idempotency_key=idempotency_key,
            description=description,
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency=currency.lower(),
                payment_method=payment_method_id,
                confirm=True,
                description=description,
                metadata={
                    "workspace_id": str(workspace_id),
                    "transaction_id": str(transaction.id),
                },
                idempotency_key=idempotency_key,
            )
            transaction.stripe_payment_intent_id = intent.id
            transaction.status = "succeeded" if intent.status == "succeeded" else "failed"
            transaction.processed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(transaction)
            return transaction
        except stripe.error.StripeError as exc:
            transaction.status = "failed"
            transaction.failure_reason = str(exc)
            transaction.processed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(transaction)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment processing failed"
            )
    
    def _create_usage_period(self, subscription_id: UUID, workspace_id: UUID):
        """Create a new usage tracking period"""
        today = date.today()
        period_end = today + timedelta(days=30)
        
        usage = SubscriptionUsage(
            workspace_id=workspace_id,
            subscription_id=subscription_id,
            period_start=today,
            period_end=period_end,
        )
        
        self.db.add(usage)
        self.db.commit()


class UsageService:
    """Service for tracking subscription usage (Module 13 - Feature 13.4)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_current_usage(self, workspace_id: UUID) -> Optional[SubscriptionUsage]:
        """Get current usage period for workspace"""
        today = date.today()
        return self.db.query(SubscriptionUsage).filter(
            and_(
                SubscriptionUsage.workspace_id == workspace_id,
                SubscriptionUsage.period_start <= today,
                SubscriptionUsage.period_end >= today
            )
        ).first()
    
    def update_usage(
        self,
        workspace_id: UUID,
        **metrics: Dict[str, int]
    ) -> SubscriptionUsage:
        """Update usage metrics"""
        usage = self.get_current_usage(workspace_id)
        if not usage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active usage period found"
            )
        
        for key, value in metrics.items():
            if hasattr(usage, key):
                setattr(usage, key, value)
        
        self.db.commit()
        self.db.refresh(usage)
        return usage
    
    def get_usage_summary(self, workspace_id: UUID) -> UsageSummary:
        """Get usage summary with limits (Module 13 - Feature 13.4 - AC 1)"""
        subscription = self.db.query(WorkspaceSubscription).filter(
            and_(
                WorkspaceSubscription.workspace_id == workspace_id,
                WorkspaceSubscription.status.in_(['active', 'trial', 'grace_period'])
            )
        ).options(joinedload(WorkspaceSubscription.plan)).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        plan = subscription.plan
        usage = self.get_current_usage(workspace_id)
        
        if not usage:
            # Create default usage
            usage = SubscriptionUsage(
                workspace_id=workspace_id,
                subscription_id=subscription.id,
                period_start=date.today(),
                period_end=date.today() + timedelta(days=30),
            )
        
        # Calculate percentages
        projects_pct = int((usage.projects_count / plan.max_projects) * 100) if plan.max_projects > 0 else 0
        storage_gb = usage.storage_used_bytes / (1024 ** 3)
        storage_pct = int((storage_gb / plan.max_storage_gb) * 100) if plan.max_storage_gb > 0 else 0
        ai_tokens_pct = int((usage.ai_tokens_used / plan.max_ai_tokens_monthly) * 100) if plan.max_ai_tokens_monthly > 0 else 0
        users_pct = int((usage.users_count / plan.max_users_per_workspace) * 100) if plan.max_users_per_workspace > 0 else 0
        
        # Generate warnings (Module 13 - Feature 13.1 - AC 1)
        warnings = []
        if projects_pct >= 80:
            warnings.append(f"Projects usage at {projects_pct}% ({usage.projects_count}/{plan.max_projects})")
        if storage_pct >= 80:
            warnings.append(f"Storage usage at {storage_pct}% ({storage_gb:.2f}GB/{plan.max_storage_gb}GB)")
        if ai_tokens_pct >= 80:
            warnings.append(f"AI tokens usage at {ai_tokens_pct}% ({usage.ai_tokens_used}/{plan.max_ai_tokens_monthly})")
        if users_pct >= 80:
            warnings.append(f"Users at {users_pct}% ({usage.users_count}/{plan.max_users_per_workspace})")
        
        return UsageSummary(
            projects={
                'used': usage.projects_count,
                'limit': plan.max_projects,
                'percentage': projects_pct
            },
            storage={
                'used_gb': round(storage_gb, 2),
                'limit_gb': plan.max_storage_gb,
                'percentage': storage_pct
            },
            ai_tokens={
                'used': usage.ai_tokens_used,
                'limit': plan.max_ai_tokens_monthly,
                'percentage': ai_tokens_pct
            },
            users={
                'used': usage.users_count,
                'limit': plan.max_users_per_workspace,
                'percentage': users_pct
            },
            warnings=warnings
        )
    
    def check_limit(self, workspace_id: UUID, resource: str) -> bool:
        """Check if workspace can use more of a resource (Module 13 - Feature 13.1 - AC 2)"""
        summary = self.get_usage_summary(workspace_id)
        
        resource_map = {
            'projects': summary.projects,
            'storage': summary.storage,
            'ai_tokens': summary.ai_tokens,
            'users': summary.users,
        }
        
        if resource not in resource_map:
            return True
        
        resource_data = resource_map[resource]
        return resource_data['used'] < resource_data['limit']


class ClientService:
    """Service for managing freelancer clients (Module 13 - Feature 13.3)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_client(self, client_data: ClientCreate, owner_id: UUID) -> Client:
        """Create a new client"""
        client = Client(
            **client_data.model_dump(),
            owner_id=owner_id
        )
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client
    
    def get_client(self, client_id: UUID, owner_id: UUID) -> Optional[Client]:
        """Get client by ID (must be owned by user)"""
        return self.db.query(Client).filter(
            and_(
                Client.id == client_id,
                Client.owner_id == owner_id
            )
        ).first()
    
    def list_clients(self, owner_id: UUID, workspace_id: UUID) -> List[Client]:
        """List all clients for user in workspace"""
        return self.db.query(Client).filter(
            and_(
                Client.owner_id == owner_id,
                Client.workspace_id == workspace_id,
                Client.is_active == True
            )
        ).order_by(Client.name).all()
    
    def update_client(
        self,
        client_id: UUID,
        client_data: ClientUpdate,
        owner_id: UUID
    ) -> Client:
        """Update client"""
        client = self.get_client(client_id, owner_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        update_data = client_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(client, key, value)
        
        self.db.commit()
        self.db.refresh(client)
        return client
    
    def delete_client(self, client_id: UUID, owner_id: UUID) -> bool:
        """Delete client (soft delete)"""
        client = self.get_client(client_id, owner_id)
        if not client:
            return False
        
        client.is_active = False
        self.db.commit()
        return True


class FreelancerInvoiceService:
    """Service for freelancer invoicing (Module 13 - Feature 13.3)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_invoice(
        self,
        invoice_data: FreelancerInvoiceCreate,
        user_id: UUID
    ) -> FreelancerInvoice:
        """Create freelancer invoice from timesheet entries (Module 13 - Feature 13.3 - AC 1)"""
        # Verify client
        client = self.db.query(Client).filter(Client.id == invoice_data.client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )

        if not invoice_data.timesheet_entry_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="timesheet_entry_ids is required"
            )

        entries = (
            self.db.query(TimeEntry)
            .filter(TimeEntry.id.in_(invoice_data.timesheet_entry_ids))
            .all()
        )

        if len(entries) != len(invoice_data.timesheet_entry_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more time entries not found"
            )

        hourly_rate = invoice_data.hourly_rate or client.default_hourly_rate
        if hourly_rate is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hourly rate is required for invoice calculation"
            )

        total_hours = sum(Decimal(str(entry.hours_spent)) for entry in entries)
        subtotal = (total_hours * hourly_rate).quantize(Decimal("0.01"))
        tax_amount = (subtotal * (invoice_data.tax_rate / Decimal("100"))).quantize(Decimal("0.01"))
        total = (subtotal + tax_amount).quantize(Decimal("0.01"))
        
        # Generate invoice number
        today = date.today()
        count = self.db.query(func.count(FreelancerInvoice.id)).filter(
            FreelancerInvoice.workspace_id == invoice_data.workspace_id
        ).scalar() or 0
        invoice_number = f"FI-{today.year}-{count + 1:04d}"
        
        invoice = FreelancerInvoice(
            client_id=invoice_data.client_id,
            workspace_id=invoice_data.workspace_id,
            created_by_id=user_id,
            invoice_number=invoice_number,
            issue_date=today,
            due_date=invoice_data.due_date,
            subtotal=subtotal,
            hourly_rate=hourly_rate,
            tax_amount=tax_amount,
            total=total,
            currency=(invoice_data.currency or "USD").upper(),
            notes=invoice_data.notes,
            logo_url=invoice_data.logo_url,
            brand_color=invoice_data.brand_color,
            hide_branding=invoice_data.hide_branding,
            timesheet_entry_ids=invoice_data.timesheet_entry_ids,
        )
        
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
    
    def get_invoice(self, invoice_id: UUID) -> Optional[FreelancerInvoice]:
        """Get invoice by ID"""
        return self.db.query(FreelancerInvoice).filter(
            FreelancerInvoice.id == invoice_id
        ).options(joinedload(FreelancerInvoice.client)).first()
    
    def list_invoices(
        self,
        workspace_id: UUID,
        user_id: UUID,
        status: Optional[str] = None
    ) -> List[FreelancerInvoice]:
        """List invoices for user"""
        query = self.db.query(FreelancerInvoice).filter(
            and_(
                FreelancerInvoice.workspace_id == workspace_id,
                FreelancerInvoice.created_by_id == user_id
            )
        )
        
        if status:
            query = query.filter(FreelancerInvoice.status == status)
        
        return query.order_by(desc(FreelancerInvoice.created_at)).all()
    
    def update_invoice_status(
        self,
        invoice_id: UUID,
        new_status: str,
        user_id: UUID
    ) -> FreelancerInvoice:
        """Update invoice status (Module 13 - Feature 13.3 - AC 3)"""
        invoice = self.db.query(FreelancerInvoice).filter(
            and_(
                FreelancerInvoice.id == invoice_id,
                FreelancerInvoice.created_by_id == user_id
            )
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Validate status transition
        if invoice.status == 'paid' and new_status != 'paid':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change status of paid invoice"
            )
        
        invoice.status = new_status
        
        if new_status == 'sent' and not invoice.sent_at:
            invoice.sent_at = datetime.utcnow()
        elif new_status == 'paid' and not invoice.paid_at:
            invoice.paid_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
    
    def generate_pdf(self, invoice_id: UUID) -> str:
        """Generate PDF for invoice (Module 13 - Feature 13.3 - AC 2)"""
        if canvas is None or LETTER is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ReportLab is not installed"
            )
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        storage_dir = Path(settings.INVOICE_STORAGE_DIR)
        storage_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"freelancer_invoice_{invoice.invoice_number}_{invoice.id}.pdf"
        file_path = storage_dir / file_name

        c = canvas.Canvas(str(file_path), pagesize=LETTER)
        width, height = LETTER

        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height - 50, "Freelancer Invoice")

        c.setFont("Helvetica", 10)
        c.drawString(40, height - 80, f"Invoice #: {invoice.invoice_number}")
        c.drawString(40, height - 95, f"Issue Date: {invoice.issue_date}")
        c.drawString(40, height - 110, f"Due Date: {invoice.due_date}")

        y = height - 150
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, "Time Entries")
        y -= 15
        c.setFont("Helvetica", 9)

        entries = (
            self.db.query(TimeEntry)
            .filter(TimeEntry.id.in_(invoice.timesheet_entry_ids))
            .all()
        )

        for entry in entries:
            if y < 80:
                c.showPage()
                y = height - 50
            task_title = entry.task.title if entry.task else "Task"
            c.drawString(40, y, f"{entry.date_logged.date()} - {task_title}")
            c.drawRightString(550, y, f"{entry.hours_spent:.2f} hrs")
            y -= 12

        y -= 10
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(550, y, f"Subtotal: {invoice.subtotal} {invoice.currency}")
        y -= 12
        c.drawRightString(550, y, f"Tax: {invoice.tax_amount} {invoice.currency}")
        y -= 12
        c.drawRightString(550, y, f"Total: {invoice.total} {invoice.currency}")

        c.showPage()
        c.save()

        pdf_url = f"{settings.INVOICE_BASE_URL}/{file_name}"
        invoice.pdf_url = pdf_url
        self.db.commit()

        return pdf_url
