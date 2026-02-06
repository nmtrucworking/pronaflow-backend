"""
Service layer for System Administration (Module 14)

Core Principles:
- Separation of Duties
- Least Privilege  
- Audit-first
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.admin import (
    AdminUser, AdminRole, AdminPermission, AdminRolePermission,
    AdminUserRole, SystemConfig, FeatureFlag, AdminAuditLog,
    SecurityIncident, ChangeRequest, AccessReview
)
from app.schemas.admin import (
    AdminUserCreate, AdminUserUpdate,
    AdminRoleCreate, AdminRoleUpdate,
    AdminPermissionCreate, AdminPermissionUpdate,
    AdminUserRoleCreate, RoleAssignmentRequest,
    SystemConfigCreate, SystemConfigUpdate,
    FeatureFlagCreate, FeatureFlagUpdate,
    AdminAuditLogCreate,
    SecurityIncidentCreate, SecurityIncidentUpdate,
    ChangeRequestCreate, ChangeRequestUpdate, ChangeRequestApproval,
    AccessReviewCreate, AccessReviewDecision,
    AuditLogQuery
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminUserService:
    """Manage admin users (separate from regular users)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_admin_user(self, admin_data: AdminUserCreate, created_by_id: Optional[UUID] = None) -> AdminUser:
        """Create new admin user"""
        hashed_password = pwd_context.hash(admin_data.password)
        
        admin_user = AdminUser(
            username=admin_data.username,
            email=admin_data.email,
            hashed_password=hashed_password,
            full_name=admin_data.full_name,
            employee_id=admin_data.employee_id,
            department=admin_data.department,
            mfa_enabled=admin_data.mfa_enabled,
            created_by_id=created_by_id
        )
        
        self.db.add(admin_user)
        self.db.commit()
        self.db.refresh(admin_user)
        return admin_user
    
    def get_admin_user(self, admin_user_id: UUID) -> Optional[AdminUser]:
        """Get admin user by ID"""
        return self.db.query(AdminUser).filter(AdminUser.id == admin_user_id).first()
    
    def get_admin_user_by_username(self, username: str) -> Optional[AdminUser]:
        """Get admin user by username"""
        return self.db.query(AdminUser).filter(AdminUser.username == username).first()
    
    def list_admin_users(self, is_active: Optional[bool] = None) -> List[AdminUser]:
        """List all admin users"""
        query = self.db.query(AdminUser)
        
        if is_active is not None:
            query = query.filter(AdminUser.is_active == is_active)
        
        return query.all()
    
    def update_admin_user(self, admin_user_id: UUID, admin_data: AdminUserUpdate) -> AdminUser:
        """Update admin user"""
        admin_user = self.get_admin_user(admin_user_id)
        
        for field, value in admin_data.model_dump(exclude_unset=True).items():
            setattr(admin_user, field, value)
        
        self.db.commit()
        self.db.refresh(admin_user)
        return admin_user
    
    def verify_password(self, admin_user: AdminUser, password: str) -> bool:
        """Verify admin password"""
        return pwd_context.verify(password, admin_user.hashed_password)
    
    def lock_admin_user(self, admin_user_id: UUID, locked_by_id: UUID) -> AdminUser:
        """Lock admin user account"""
        admin_user = self.get_admin_user(admin_user_id)
        admin_user.is_locked = True
        
        self.db.commit()
        self.db.refresh(admin_user)
        return admin_user
    
    def unlock_admin_user(self, admin_user_id: UUID) -> AdminUser:
        """Unlock admin user account"""
        admin_user = self.get_admin_user(admin_user_id)
        admin_user.is_locked = False
        admin_user.failed_login_attempts = 0
        
        self.db.commit()
        self.db.refresh(admin_user)
        return admin_user
    
    def record_failed_login(self, admin_user_id: UUID) -> AdminUser:
        """Record failed login attempt"""
        admin_user = self.get_admin_user(admin_user_id)
        admin_user.failed_login_attempts += 1
        
        # Auto-lock after 5 failed attempts
        if admin_user.failed_login_attempts >= 5:
            admin_user.is_locked = True
        
        self.db.commit()
        self.db.refresh(admin_user)
        return admin_user
    
    def record_successful_login(self, admin_user_id: UUID) -> AdminUser:
        """Record successful login"""
        admin_user = self.get_admin_user(admin_user_id)
        admin_user.last_login_at = datetime.utcnow()
        admin_user.failed_login_attempts = 0
        
        self.db.commit()
        self.db.refresh(admin_user)
        return admin_user


class AdminRoleService:
    """Manage 18 specialized admin roles"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_role(self, role_data: AdminRoleCreate) -> AdminRole:
        """Create new admin role"""
        role = AdminRole(
            name=role_data.name,
            display_name=role_data.display_name,
            description=role_data.description,
            category=role_data.category,
            requires_mfa=role_data.requires_mfa,
            max_session_duration=role_data.max_session_duration
        )
        
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def get_role(self, role_id: UUID) -> Optional[AdminRole]:
        """Get role by ID"""
        return self.db.query(AdminRole).filter(AdminRole.id == role_id).first()
    
    def get_role_by_name(self, name: str) -> Optional[AdminRole]:
        """Get role by name"""
        return self.db.query(AdminRole).filter(AdminRole.name == name).first()
    
    def list_roles(self, category: Optional[str] = None, is_active: Optional[bool] = None) -> List[AdminRole]:
        """List all roles"""
        query = self.db.query(AdminRole)
        
        if category:
            query = query.filter(AdminRole.category == category)
        if is_active is not None:
            query = query.filter(AdminRole.is_active == is_active)
        
        return query.all()
    
    def update_role(self, role_id: UUID, role_data: AdminRoleUpdate) -> AdminRole:
        """Update role"""
        role = self.get_role(role_id)
        
        for field, value in role_data.model_dump(exclude_unset=True).items():
            setattr(role, field, value)
        
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def assign_permission_to_role(self, role_id: UUID, permission_id: UUID, granted_by_id: UUID) -> AdminRolePermission:
        """Assign permission to role"""
        assignment = AdminRolePermission(
            role_id=role_id,
            permission_id=permission_id,
            granted_by_id=granted_by_id
        )
        
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def get_role_permissions(self, role_id: UUID) -> List[AdminPermission]:
        """Get all permissions for a role"""
        return (
            self.db.query(AdminPermission)
            .join(AdminRolePermission)
            .filter(AdminRolePermission.role_id == role_id)
            .all()
        )


class AdminPermissionService:
    """Manage granular permissions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_permission(self, permission_data: AdminPermissionCreate) -> AdminPermission:
        """Create new permission"""
        permission = AdminPermission(
            name=permission_data.name,
            display_name=permission_data.display_name,
            description=permission_data.description,
            resource=permission_data.resource,
            action=permission_data.action,
            is_dangerous=permission_data.is_dangerous
        )
        
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission
    
    def get_permission(self, permission_id: UUID) -> Optional[AdminPermission]:
        """Get permission by ID"""
        return self.db.query(AdminPermission).filter(AdminPermission.id == permission_id).first()
    
    def list_permissions(self, resource: Optional[str] = None) -> List[AdminPermission]:
        """List all permissions"""
        query = self.db.query(AdminPermission)
        
        if resource:
            query = query.filter(AdminPermission.resource == resource)
        
        return query.all()
    
    def update_permission(self, permission_id: UUID, permission_data: AdminPermissionUpdate) -> AdminPermission:
        """Update permission"""
        permission = self.get_permission(permission_id)
        
        for field, value in permission_data.model_dump(exclude_unset=True).items():
            setattr(permission, field, value)
        
        self.db.commit()
        self.db.refresh(permission)
        return permission


class AdminRoleAssignmentService:
    """Manage role assignments with time-bound and approval"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def assign_role(self, admin_user_id: UUID, request: RoleAssignmentRequest, assigned_by_id: UUID) -> AdminUserRole:
        """Assign role to admin user (requires approval for sensitive roles)"""
        assignment = AdminUserRole(
            admin_user_id=admin_user_id,
            role_id=request.role_id,
            valid_until=request.valid_until,
            approval_reason=request.reason,
            assigned_by_id=assigned_by_id
        )
        
        # Auto-approve for non-sensitive roles
        role = self.db.query(AdminRole).filter(AdminRole.id == request.role_id).first()
        if role and role.category in ["business", "audit"]:
            assignment.is_approved = True
            assignment.approved_by_id = assigned_by_id
            assignment.approved_at = datetime.utcnow()
        
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def approve_role_assignment(self, assignment_id: UUID, approved_by_id: UUID, approve: bool, notes: Optional[str] = None) -> AdminUserRole:
        """Approve or reject role assignment"""
        assignment = self.db.query(AdminUserRole).filter(AdminUserRole.id == assignment_id).first()
        
        assignment.is_approved = approve
        assignment.approved_by_id = approved_by_id
        assignment.approved_at = datetime.utcnow()
        assignment.approval_reason = notes or assignment.approval_reason
        
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def revoke_role(self, assignment_id: UUID, revoked_by_id: UUID) -> AdminUserRole:
        """Revoke role assignment"""
        assignment = self.db.query(AdminUserRole).filter(AdminUserRole.id == assignment_id).first()
        
        assignment.revoked_at = datetime.utcnow()
        assignment.revoked_by_id = revoked_by_id
        
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def get_user_roles(self, admin_user_id: UUID, include_expired: bool = False) -> List[AdminRole]:
        """Get active roles for admin user"""
        query = (
            self.db.query(AdminRole)
            .join(AdminUserRole)
            .filter(AdminUserRole.admin_user_id == admin_user_id)
            .filter(AdminUserRole.is_approved == True)
            .filter(AdminUserRole.revoked_at.is_(None))
        )
        
        if not include_expired:
            now = datetime.utcnow()
            query = query.filter(
                or_(
                    AdminUserRole.valid_until.is_(None),
                    AdminUserRole.valid_until > now
                )
            )
        
        return query.all()
    
    def get_user_permissions(self, admin_user_id: UUID) -> List[str]:
        """Get all effective permissions for admin user"""
        roles = self.get_user_roles(admin_user_id)
        role_ids = [role.id for role in roles]
        
        permissions = (
            self.db.query(AdminPermission.name)
            .join(AdminRolePermission)
            .filter(AdminRolePermission.role_id.in_(role_ids))
            .filter(AdminPermission.is_active == True)
            .distinct()
            .all()
        )
        
        return [p[0] for p in permissions]


class SystemConfigService:
    """Manage system configuration with audit trail"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_config(self, config_data: SystemConfigCreate, created_by_id: UUID) -> SystemConfig:
        """Create new config"""
        config = SystemConfig(
            key=config_data.key,
            value=config_data.value,
            data_type=config_data.data_type,
            category=config_data.category,
            description=config_data.description,
            is_sensitive=config_data.is_sensitive,
            is_editable=config_data.is_editable,
            updated_by_id=created_by_id
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def get_config(self, key: str) -> Optional[SystemConfig]:
        """Get config by key"""
        return self.db.query(SystemConfig).filter(SystemConfig.key == key).first()
    
    def list_configs(self, category: Optional[str] = None) -> List[SystemConfig]:
        """List all configs"""
        query = self.db.query(SystemConfig)
        
        if category:
            query = query.filter(SystemConfig.category == category)
        
        return query.all()
    
    def update_config(self, key: str, config_data: SystemConfigUpdate, updated_by_id: UUID) -> SystemConfig:
        """Update config with version tracking"""
        config = self.get_config(key)
        
        # Store previous value
        config.previous_value = config.value
        config.version += 1
        
        # Update with new value
        config.value = config_data.value
        if config_data.description:
            config.description = config_data.description
        config.updated_by_id = updated_by_id
        
        self.db.commit()
        self.db.refresh(config)
        return config


class FeatureFlagService:
    """Manage feature flags and gradual rollout"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_flag(self, flag_data: FeatureFlagCreate, created_by_id: UUID) -> FeatureFlag:
        """Create new feature flag"""
        flag = FeatureFlag(
            key=flag_data.key,
            name=flag_data.name,
            description=flag_data.description,
            is_enabled=flag_data.is_enabled,
            rollout_percentage=flag_data.rollout_percentage,
            environment=flag_data.environment,
            expires_at=flag_data.expires_at,
            created_by_id=created_by_id
        )
        
        self.db.add(flag)
        self.db.commit()
        self.db.refresh(flag)
        return flag
    
    def get_flag(self, key: str) -> Optional[FeatureFlag]:
        """Get flag by key"""
        return self.db.query(FeatureFlag).filter(FeatureFlag.key == key).first()
    
    def list_flags(self, environment: Optional[str] = None) -> List[FeatureFlag]:
        """List all flags"""
        query = self.db.query(FeatureFlag)
        
        if environment:
            query = query.filter(FeatureFlag.environment == environment)
        
        return query.all()
    
    def update_flag(self, key: str, flag_data: FeatureFlagUpdate, updated_by_id: UUID) -> FeatureFlag:
        """Update feature flag"""
        flag = self.get_flag(key)
        
        for field, value in flag_data.model_dump(exclude_unset=True).items():
            setattr(flag, field, value)
        
        flag.updated_by_id = updated_by_id
        
        self.db.commit()
        self.db.refresh(flag)
        return flag
    
    def is_enabled_for_user(self, key: str, user_id: UUID) -> bool:
        """Check if feature is enabled for specific user"""
        flag = self.get_flag(key)
        
        if not flag or not flag.is_enabled:
            return False
        
        # Check targeted users
        if flag.target_users and user_id in flag.target_users:
            return True
        
        # Check rollout percentage (simple hash-based)
        if flag.rollout_percentage == 100:
            return True
        elif flag.rollout_percentage == 0:
            return False
        else:
            # Simple deterministic hash
            hash_value = hash(str(user_id) + key) % 100
            return hash_value < flag.rollout_percentage


class AuditLogService:
    """Immutable audit logging"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_log(self, log_data: AdminAuditLogCreate) -> AdminAuditLog:
        """Create audit log entry (immutable)"""
        log = AdminAuditLog(
            admin_user_id=log_data.admin_user_id,
            action=log_data.action,
            resource_type=log_data.resource_type,
            resource_id=log_data.resource_id,
            ip_address=log_data.ip_address,
            user_agent=log_data.user_agent,
            session_id=log_data.session_id,
            changes=log_data.changes,
            metadata_=log_data.metadata_,
            status=log_data.status,
            error_message=log_data.error_message
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def query_logs(self, query: AuditLogQuery) -> List[AdminAuditLog]:
        """Query audit logs with filters"""
        db_query = self.db.query(AdminAuditLog)
        
        if query.admin_user_id:
            db_query = db_query.filter(AdminAuditLog.admin_user_id == query.admin_user_id)
        if query.action:
            db_query = db_query.filter(AdminAuditLog.action == query.action)
        if query.resource_type:
            db_query = db_query.filter(AdminAuditLog.resource_type == query.resource_type)
        if query.status:
            db_query = db_query.filter(AdminAuditLog.status == query.status)
        if query.start_date:
            db_query = db_query.filter(AdminAuditLog.created_at >= query.start_date)
        if query.end_date:
            db_query = db_query.filter(AdminAuditLog.created_at <= query.end_date)
        
        return db_query.order_by(AdminAuditLog.created_at.desc()).limit(query.limit).offset(query.offset).all()


class SecurityIncidentService:
    """Manage security incidents"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_incident(self, incident_data: SecurityIncidentCreate, reported_by_id: UUID) -> SecurityIncident:
        """Create security incident"""
        incident = SecurityIncident(
            title=incident_data.title,
            description=incident_data.description,
            severity=incident_data.severity,
            category=incident_data.category,
            affected_user_id=incident_data.affected_user_id,
            affected_workspace_id=incident_data.affected_workspace_id,
            ip_address=incident_data.ip_address,
            evidence=incident_data.evidence,
            status="open",
            reported_by_id=reported_by_id
        )
        
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident
    
    def get_incident(self, incident_id: UUID) -> Optional[SecurityIncident]:
        """Get incident by ID"""
        return self.db.query(SecurityIncident).filter(SecurityIncident.id == incident_id).first()
    
    def list_incidents(self, status: Optional[str] = None, severity: Optional[str] = None) -> List[SecurityIncident]:
        """List incidents"""
        query = self.db.query(SecurityIncident)
        
        if status:
            query = query.filter(SecurityIncident.status == status)
        if severity:
            query = query.filter(SecurityIncident.severity == severity)
        
        return query.order_by(SecurityIncident.created_at.desc()).all()
    
    def update_incident(self, incident_id: UUID, incident_data: SecurityIncidentUpdate) -> SecurityIncident:
        """Update incident"""
        incident = self.get_incident(incident_id)
        
        for field, value in incident_data.model_dump(exclude_unset=True).items():
            setattr(incident, field, value)
        
        if incident.status == "resolved":
            incident.resolved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(incident)
        return incident


class ChangeRequestService:
    """Manage change/release requests"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_change_request(self, change_data: ChangeRequestCreate, requester_id: UUID) -> ChangeRequest:
        """Create change request"""
        change = ChangeRequest(
            title=change_data.title,
            description=change_data.description,
            change_type=change_data.change_type,
            risk_level=change_data.risk_level,
            affected_systems=change_data.affected_systems,
            rollback_plan=change_data.rollback_plan,
            scheduled_at=change_data.scheduled_at,
            status="draft",
            requester_id=requester_id
        )
        
        self.db.add(change)
        self.db.commit()
        self.db.refresh(change)
        return change
    
    def get_change_request(self, change_id: UUID) -> Optional[ChangeRequest]:
        """Get change request by ID"""
        return self.db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
    
    def list_change_requests(self, status: Optional[str] = None) -> List[ChangeRequest]:
        """List change requests"""
        query = self.db.query(ChangeRequest)
        
        if status:
            query = query.filter(ChangeRequest.status == status)
        
        return query.order_by(ChangeRequest.created_at.desc()).all()
    
    def update_change_request(self, change_id: UUID, change_data: ChangeRequestUpdate) -> ChangeRequest:
        """Update change request"""
        change = self.get_change_request(change_id)
        
        for field, value in change_data.model_dump(exclude_unset=True).items():
            setattr(change, field, value)
        
        if change.status == "deployed":
            change.deployed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(change)
        return change
    
    def approve_change_request(self, change_id: UUID, approval: ChangeRequestApproval, approver_id: UUID) -> ChangeRequest:
        """Approve or reject change request"""
        change = self.get_change_request(change_id)
        
        if approval.approve:
            change.status = "approved"
        else:
            change.status = "rejected"
        
        change.approved_by_id = approver_id
        change.approved_at = datetime.utcnow()
        change.approval_notes = approval.approval_notes
        
        self.db.commit()
        self.db.refresh(change)
        return change


class AccessReviewService:
    """Manage periodic access reviews"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_access_review(self, review_data: AccessReviewCreate, reviewer_id: UUID) -> AccessReview:
        """Create access review"""
        review = AccessReview(
            review_period=review_data.review_period,
            review_type=review_data.review_type,
            admin_user_id=review_data.admin_user_id,
            roles_reviewed=review_data.roles_reviewed,
            status="pending",
            reviewer_id=reviewer_id
        )
        
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review
    
    def get_access_review(self, review_id: UUID) -> Optional[AccessReview]:
        """Get access review by ID"""
        return self.db.query(AccessReview).filter(AccessReview.id == review_id).first()
    
    def list_access_reviews(self, status: Optional[str] = None, review_period: Optional[str] = None) -> List[AccessReview]:
        """List access reviews"""
        query = self.db.query(AccessReview)
        
        if status:
            query = query.filter(AccessReview.status == status)
        if review_period:
            query = query.filter(AccessReview.review_period == review_period)
        
        return query.all()
    
    def complete_access_review(self, review_id: UUID, decision: AccessReviewDecision, reviewer_id: UUID) -> AccessReview:
        """Complete access review with decision"""
        review = self.get_access_review(review_id)
        
        review.decision = decision.decision
        review.revoked_roles = decision.revoked_roles
        review.review_notes = decision.review_notes
        review.reviewed_at = datetime.utcnow()
        review.reviewer_id = reviewer_id
        
        if decision.decision == "approve_all":
            review.status = "approved"
        else:
            review.status = "revoked"
            
            # Revoke role assignments
            if decision.revoked_roles:
                for role_id in decision.revoked_roles:
                    assignment = (
                        self.db.query(AdminUserRole)
                        .filter(AdminUserRole.admin_user_id == review.admin_user_id)
                        .filter(AdminUserRole.role_id == role_id)
                        .filter(AdminUserRole.revoked_at.is_(None))
                        .first()
                    )
                    if assignment:
                        assignment.revoked_at = datetime.utcnow()
                        assignment.revoked_by_id = reviewer_id
        
        self.db.commit()
        self.db.refresh(review)
        return review
