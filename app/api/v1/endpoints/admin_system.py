"""
API endpoints for System Administration (Module 14)
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.admin_security import (
    get_current_admin_user,
    require_admin_roles,
    create_admin_access_token,
)
from app.db.models.admin import AdminUser
from app.services.admin import (
    AdminUserService,
    AdminRoleService,
    AdminPermissionService,
    AdminRoleAssignmentService,
    SystemConfigService,
    FeatureFlagService,
    AuditLogService,
    SecurityIncidentService,
    ChangeRequestService,
    AccessReviewService,
)
from app.schemas.admin import (
    AdminUserResponse, AdminUserCreate, AdminUserUpdate,
    AdminRoleResponse, AdminRoleCreate, AdminRoleUpdate,
    AdminPermissionResponse, AdminPermissionCreate, AdminPermissionUpdate,
    AdminUserRoleResponse, RoleAssignmentRequest, RoleApprovalRequest,
    SystemConfigResponse, SystemConfigCreate, SystemConfigUpdate,
    FeatureFlagResponse, FeatureFlagCreate, FeatureFlagUpdate,
    AdminAuditLogResponse, AdminAuditLogCreate, AuditLogQuery,
    SecurityIncidentResponse, SecurityIncidentCreate, SecurityIncidentUpdate,
    ChangeRequestResponse, ChangeRequestCreate, ChangeRequestUpdate, ChangeRequestApproval,
    AccessReviewResponse, AccessReviewCreate, AccessReviewDecision,
    AdminLoginRequest, AdminLoginResponse,
    RolePermissionAssignment, BulkRoleAssignment, AdminStats,
)

router = APIRouter(prefix="/admin-system", tags=["System Administration"])


# ======= Admin Auth =======

@router.post("/auth/login", response_model=AdminLoginResponse)
def admin_login(
    credentials: AdminLoginRequest,
    db: Session = Depends(get_db),
):
    """Admin login (separate from regular users)."""
    user_service = AdminUserService(db)
    role_service = AdminRoleAssignmentService(db)

    admin_user = user_service.get_admin_user_by_username(credentials.username)
    if not admin_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if admin_user.is_locked or not admin_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin account locked or inactive")

    if not user_service.verify_password(admin_user, credentials.password):
        user_service.record_failed_login(admin_user.id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user_service.record_successful_login(admin_user.id)

    roles = role_service.get_user_roles(admin_user.id)
    permissions = role_service.get_user_permissions(admin_user.id)
    token = create_admin_access_token(admin_user.id, [role.name for role in roles], permissions)

    return AdminLoginResponse(
        access_token=token,
        admin_user=admin_user,
        roles=roles,
        permissions=permissions,
    )


# ======= Admin User Endpoints =======

@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    user_data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin")),
):
    """
    Create new admin user (Super Admin only).
    Module 14 - Admin Identity
    """
    service = AdminUserService(db)
    return service.create_admin_user(user_data, created_by_id=current_admin.id)


@router.get("/users", response_model=List[AdminUserResponse])
def list_admin_users(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "iam_admin")),
):
    """List all admin users"""
    service = AdminUserService(db)
    return service.list_admin_users(is_active)


@router.get("/users/{admin_user_id}", response_model=AdminUserResponse)
def get_admin_user(
    admin_user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "iam_admin")),
):
    """Get admin user by ID"""
    service = AdminUserService(db)
    admin_user = service.get_admin_user(admin_user_id)
    
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    return admin_user


@router.patch("/users/{admin_user_id}", response_model=AdminUserResponse)
def update_admin_user(
    admin_user_id: UUID,
    user_data: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "iam_admin")),
):
    """Update admin user"""
    service = AdminUserService(db)
    return service.update_admin_user(admin_user_id, user_data)


@router.post("/users/{admin_user_id}/lock")
def lock_admin_user(
    admin_user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "security_admin")),
):
    """Lock admin user account (Security Admin)"""
    service = AdminUserService(db)
    return service.lock_admin_user(admin_user_id, current_admin.id)


@router.post("/users/{admin_user_id}/unlock")
def unlock_admin_user(
    admin_user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "security_admin")),
):
    """Unlock admin user account (Security Admin)"""
    service = AdminUserService(db)
    return service.unlock_admin_user(admin_user_id)


# ======= Admin Role Endpoints =======

@router.post("/roles", response_model=AdminRoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: AdminRoleCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "iam_admin")),
):
    """
    Create admin role (Super Admin only).
    Module 14 - 18 Specialized Roles
    """
    service = AdminRoleService(db)
    return service.create_role(role_data)


@router.get("/roles", response_model=List[AdminRoleResponse])
def list_roles(
    category: Optional[str] = Query(None, pattern="^(technical|security|business|audit)$"),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    List admin roles by category.
    Categories: technical, security, business, audit
    """
    service = AdminRoleService(db)
    return service.list_roles(category, is_active)


@router.get("/roles/{role_id}", response_model=AdminRoleResponse)
def get_role(
    role_id: UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Get role by ID"""
    service = AdminRoleService(db)
    role = service.get_role(role_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return role


@router.patch("/roles/{role_id}", response_model=AdminRoleResponse)
def update_role(
    role_id: UUID,
    role_data: AdminRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "iam_admin")),
):
    """Update role"""
    service = AdminRoleService(db)
    return service.update_role(role_id, role_data)


@router.get("/roles/{role_id}/permissions", response_model=List[AdminPermissionResponse])
def get_role_permissions(
    role_id: UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Get all permissions for a role"""
    service = AdminRoleService(db)
    return service.get_role_permissions(role_id)


@router.post("/roles/{role_id}/permissions")
def assign_permission_to_role(
    role_id: UUID,
    assignment: RolePermissionAssignment,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "iam_admin")),
):
    """
    Assign permissions to role (IAM Admin).
    Module 14 - Permission Assignment
    """
    service = AdminRoleService(db)
    
    results = []
    for permission_id in assignment.permission_ids:
        result = service.assign_permission_to_role(role_id, permission_id, current_admin.id)
        results.append(result)
    
    return {"assigned_count": len(results)}


# ======= Permission Endpoints =======

@router.post("/permissions", response_model=AdminPermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission_data: AdminPermissionCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "iam_admin")),
):
    """Create permission (Super Admin only)"""
    service = AdminPermissionService(db)
    return service.create_permission(permission_data)


@router.get("/permissions", response_model=List[AdminPermissionResponse])
def list_permissions(
    resource: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """List all permissions"""
    service = AdminPermissionService(db)
    return service.list_permissions(resource)


@router.patch("/permissions/{permission_id}", response_model=AdminPermissionResponse)
def update_permission(
    permission_id: UUID,
    permission_data: AdminPermissionUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "iam_admin")),
):
    """Update permission"""
    service = AdminPermissionService(db)
    return service.update_permission(permission_id, permission_data)


# ======= Role Assignment Endpoints =======

@router.post("/users/{admin_user_id}/roles", response_model=AdminUserRoleResponse)
def assign_role_to_user(
    admin_user_id: UUID,
    request: RoleAssignmentRequest,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "iam_admin")),
):
    """
    Assign role to admin user (IAM Admin).
    Module 14 - Least Privilege with Time-bound assignments
    """
    service = AdminRoleAssignmentService(db)
    return service.assign_role(admin_user_id, request, current_admin.id)


@router.post("/role-assignments/{assignment_id}/approve")
def approve_role_assignment(
    assignment_id: UUID,
    approval: RoleApprovalRequest,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "iam_admin")),
):
    """Approve or reject role assignment (IAM Admin)"""
    service = AdminRoleAssignmentService(db)
    return service.approve_role_assignment(assignment_id, current_admin.id, approval.approve, approval.notes)


@router.delete("/role-assignments/{assignment_id}")
def revoke_role_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "iam_admin")),
):
    """Revoke role assignment (IAM Admin)"""
    service = AdminRoleAssignmentService(db)
    return service.revoke_role(assignment_id, current_admin.id)


@router.get("/users/{admin_user_id}/roles", response_model=List[AdminRoleResponse])
def get_user_roles(
    admin_user_id: UUID,
    include_expired: bool = Query(False),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "iam_admin")),
):
    """Get active roles for admin user"""
    service = AdminRoleAssignmentService(db)
    return service.get_user_roles(admin_user_id, include_expired)


# ======= System Config Endpoints =======

@router.post("/config", response_model=SystemConfigResponse, status_code=status.HTTP_201_CREATED)
def create_system_config(
    config_data: SystemConfigCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin")),
):
    """
    Create system config (Super Admin only).
    Module 14 - System Configuration
    """
    service = SystemConfigService(db)
    return service.create_config(config_data, current_admin.id)


@router.get("/config", response_model=List[SystemConfigResponse])
def list_system_configs(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "system_admin")),
):
    """List system configs"""
    service = SystemConfigService(db)
    return service.list_configs(category)


@router.get("/config/{key}", response_model=SystemConfigResponse)
def get_system_config(
    key: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "system_admin")),
):
    """Get config by key"""
    service = SystemConfigService(db)
    config = service.get_config(key)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    return config


@router.patch("/config/{key}", response_model=SystemConfigResponse)
def update_system_config(
    key: str,
    config_data: SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin")),
):
    """
    Update config with audit trail (Super Admin).
    Module 14 - Immutable Audit for Config Changes
    """
    service = SystemConfigService(db)
    return service.update_config(key, config_data, current_admin.id)


# ======= Feature Flag Endpoints =======

@router.post("/feature-flags", response_model=FeatureFlagResponse, status_code=status.HTTP_201_CREATED)
def create_feature_flag(
    flag_data: FeatureFlagCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "ai_admin")),
):
    """
    Create feature flag (Super Admin / AI Admin).
    Module 14 - Feature Control / Kill Switch
    """
    service = FeatureFlagService(db)
    return service.create_flag(flag_data, current_admin.id)


@router.get("/feature-flags", response_model=List[FeatureFlagResponse])
def list_feature_flags(
    environment: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """List feature flags"""
    service = FeatureFlagService(db)
    return service.list_flags(environment)


@router.get("/feature-flags/{key}", response_model=FeatureFlagResponse)
def get_feature_flag(
    key: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Get feature flag by key"""
    service = FeatureFlagService(db)
    flag = service.get_flag(key)
    
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature flag not found"
        )
    
    return flag


@router.patch("/feature-flags/{key}", response_model=FeatureFlagResponse)
def update_feature_flag(
    key: str,
    flag_data: FeatureFlagUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "ai_admin")),
):
    """
    Update feature flag (Super Admin / AI Admin).
    Module 14 - Gradual Rollout Control
    """
    service = FeatureFlagService(db)
    return service.update_flag(key, flag_data, current_admin.id)


@router.get("/feature-flags/{key}/check/{user_id}")
def check_feature_flag(
    key: str,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Check if feature is enabled for specific user"""
    service = FeatureFlagService(db)
    is_enabled = service.is_enabled_for_user(key, user_id)
    
    return {"enabled": is_enabled}


# ======= Audit Log Endpoints =======

@router.post("/audit-logs", response_model=AdminAuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_audit_log(
    log_data: AdminAuditLogCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "audit_admin")),
):
    """
    Create audit log (System use only).
    Module 14 - Audit-first / Write-protected Logs
    """
    service = AuditLogService(db)
    return service.create_log(log_data)


@router.get("/audit-logs", response_model=List[AdminAuditLogResponse])
def query_audit_logs(
    admin_user_id: Optional[UUID] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "audit_admin", "compliance_admin")),
):
    """
    Query audit logs (Audit-only Admin / Compliance Admin).
    Module 14 - Immutable Audit Trail
    """
    query_params = AuditLogQuery(
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        status=status,
        limit=limit,
        offset=offset
    )
    
    service = AuditLogService(db)
    return service.query_logs(query_params)


# ======= Security Incident Endpoints =======

@router.post("/security-incidents", response_model=SecurityIncidentResponse, status_code=status.HTTP_201_CREATED)
def create_security_incident(
    incident_data: SecurityIncidentCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "security_admin")),
):
    """
    Create security incident.
    Module 14 - Security Operations
    """
    service = SecurityIncidentService(db)
    return service.create_incident(incident_data, current_admin.id)


@router.get("/security-incidents", response_model=List[SecurityIncidentResponse])
def list_security_incidents(
    status: Optional[str] = Query(None, pattern="^(open|investigating|resolved|closed)$"),
    severity: Optional[str] = Query(None, pattern="^(critical|high|medium|low)$"),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "security_admin")),
):
    """List security incidents (Security Admin)"""
    service = SecurityIncidentService(db)
    return service.list_incidents(status, severity)


@router.get("/security-incidents/{incident_id}", response_model=SecurityIncidentResponse)
def get_security_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "security_admin")),
):
    """Get security incident by ID"""
    service = SecurityIncidentService(db)
    incident = service.get_incident(incident_id)
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    return incident


@router.patch("/security-incidents/{incident_id}", response_model=SecurityIncidentResponse)
def update_security_incident(
    incident_id: UUID,
    incident_data: SecurityIncidentUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "security_admin")),
):
    """Update security incident (Security Admin)"""
    service = SecurityIncidentService(db)
    return service.update_incident(incident_id, incident_data)


# ======= Change Request Endpoints =======

@router.post("/change-requests", response_model=ChangeRequestResponse, status_code=status.HTTP_201_CREATED)
def create_change_request(
    change_data: ChangeRequestCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "release_admin")),
):
    """
    Create change request.
    Module 14 - Release / Change Management
    """
    service = ChangeRequestService(db)
    return service.create_change_request(change_data, current_admin.id)


@router.get("/change-requests", response_model=List[ChangeRequestResponse])
def list_change_requests(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "release_admin")),
):
    """List change requests (Release Admin)"""
    service = ChangeRequestService(db)
    return service.list_change_requests(status)


@router.get("/change-requests/{change_id}", response_model=ChangeRequestResponse)
def get_change_request(
    change_id: UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "release_admin")),
):
    """Get change request by ID"""
    service = ChangeRequestService(db)
    change = service.get_change_request(change_id)
    
    if not change:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Change request not found"
        )
    
    return change


@router.patch("/change-requests/{change_id}", response_model=ChangeRequestResponse)
def update_change_request(
    change_id: UUID,
    change_data: ChangeRequestUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "release_admin")),
):
    """Update change request (Release Admin)"""
    service = ChangeRequestService(db)
    return service.update_change_request(change_id, change_data)


@router.post("/change-requests/{change_id}/approve", response_model=ChangeRequestResponse)
def approve_change_request(
    change_id: UUID,
    approval: ChangeRequestApproval,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "release_admin")),
):
    """
    Approve or reject change request (Release Admin).
    Module 14 - Change Approval Workflow
    """
    service = ChangeRequestService(db)
    return service.approve_change_request(change_id, approval, current_admin.id)


# ======= Access Review Endpoints =======

@router.post("/access-reviews", response_model=AccessReviewResponse, status_code=status.HTTP_201_CREATED)
def create_access_review(
    review_data: AccessReviewCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "privacy_admin")),
):
    """
    Create access review.
    Module 14 - Periodic Access Review
    """
    service = AccessReviewService(db)
    return service.create_access_review(review_data, current_admin.id)


@router.get("/access-reviews", response_model=List[AccessReviewResponse])
def list_access_reviews(
    status: Optional[str] = Query(None, pattern="^(pending|approved|revoked)$"),
    review_period: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "privacy_admin")),
):
    """List access reviews (Privacy/DPO)"""
    service = AccessReviewService(db)
    return service.list_access_reviews(status, review_period)


@router.get("/access-reviews/{review_id}", response_model=AccessReviewResponse)
def get_access_review(
    review_id: UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "privacy_admin")),
):
    """Get access review by ID"""
    service = AccessReviewService(db)
    review = service.get_access_review(review_id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access review not found"
        )
    
    return review


@router.post("/access-reviews/{review_id}/complete", response_model=AccessReviewResponse)
def complete_access_review(
    review_id: UUID,
    decision: AccessReviewDecision,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "privacy_admin")),
):
    """
    Complete access review with decision (Privacy/DPO).
    Module 14 - Access Review Workflow
    """
    service = AccessReviewService(db)
    return service.complete_access_review(review_id, decision, current_admin.id)


# ======= Statistics =======

@router.get("/stats", response_model=AdminStats)
def get_admin_stats(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_admin_roles("super_admin", "system_admin")),
):
    """Get admin system statistics"""
    from app.db.models.admin import AdminUser, AdminRole, AdminPermission, ChangeRequest, SecurityIncident, AccessReview
    
    total_admin_users = db.query(AdminUser).count()
    active_admin_users = db.query(AdminUser).filter(AdminUser.is_active == True).count()
    total_roles = db.query(AdminRole).count()
    total_permissions = db.query(AdminPermission).count()
    pending_change_requests = db.query(ChangeRequest).filter(ChangeRequest.status == "pending").count()
    open_security_incidents = db.query(SecurityIncident).filter(SecurityIncident.status == "open").count()
    pending_access_reviews = db.query(AccessReview).filter(AccessReview.status == "pending").count()
    
    return AdminStats(
        total_admin_users=total_admin_users,
        active_admin_users=active_admin_users,
        total_roles=total_roles,
        total_permissions=total_permissions,
        pending_change_requests=pending_change_requests,
        open_security_incidents=open_security_incidents,
        pending_access_reviews=pending_access_reviews
    )
