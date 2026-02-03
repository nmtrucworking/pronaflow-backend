"""
Pydantic schemas for System Administration (Module 14)
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict


# ======= AdminUser Schemas =======

class AdminUserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    employee_id: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)


class AdminUserCreate(AdminUserBase):
    password: str = Field(..., min_length=8)
    mfa_enabled: bool = False


class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    mfa_enabled: Optional[bool] = None
    is_active: Optional[bool] = None


class AdminUserResponse(AdminUserBase):
    id: UUID
    mfa_enabled: bool
    is_active: bool
    is_locked: bool
    failed_login_attempts: int
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ======= AdminRole Schemas =======

class AdminRoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field(..., pattern="^(technical|security|business|audit)$")


class AdminRoleCreate(AdminRoleBase):
    requires_mfa: bool = True
    max_session_duration: int = Field(28800, ge=1800, le=86400)  # 30min to 24hrs


class AdminRoleUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    requires_mfa: Optional[bool] = None
    max_session_duration: Optional[int] = Field(None, ge=1800, le=86400)


class AdminRoleResponse(AdminRoleBase):
    id: UUID
    is_system_role: bool
    is_active: bool
    requires_mfa: bool
    max_session_duration: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ======= AdminPermission Schemas =======

class AdminPermissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    resource: str = Field(..., min_length=1, max_length=100)
    action: str = Field(..., min_length=1, max_length=50)


class AdminPermissionCreate(AdminPermissionBase):
    is_dangerous: bool = False


class AdminPermissionUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_dangerous: Optional[bool] = None
    is_active: Optional[bool] = None


class AdminPermissionResponse(AdminPermissionBase):
    id: UUID
    is_dangerous: bool
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ======= AdminUserRole Schemas =======

class AdminUserRoleCreate(BaseModel):
    admin_user_id: UUID
    role_id: UUID
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    approval_reason: Optional[str] = None


class AdminUserRoleResponse(BaseModel):
    id: UUID
    admin_user_id: UUID
    role_id: UUID
    valid_from: datetime
    valid_until: Optional[datetime]
    is_approved: bool
    approved_by_id: Optional[UUID]
    approved_at: Optional[datetime]
    assigned_at: datetime
    revoked_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class RoleAssignmentRequest(BaseModel):
    role_id: UUID
    valid_until: Optional[datetime] = None
    reason: str = Field(..., min_length=10)


class RoleApprovalRequest(BaseModel):
    assignment_id: UUID
    approve: bool
    notes: Optional[str] = None


# ======= SystemConfig Schemas =======

class SystemConfigBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    value: Dict[str, Any]
    data_type: str = Field(..., pattern="^(string|integer|boolean|json)$")
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_sensitive: bool = False


class SystemConfigCreate(SystemConfigBase):
    is_editable: bool = True


class SystemConfigUpdate(BaseModel):
    value: Dict[str, Any]
    description: Optional[str] = None


class SystemConfigResponse(SystemConfigBase):
    id: UUID
    is_editable: bool
    version: int
    created_at: datetime
    updated_at: datetime
    updated_by_id: Optional[UUID]
    
    model_config = ConfigDict(from_attributes=True)


# ======= FeatureFlag Schemas =======

class FeatureFlagBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class FeatureFlagCreate(FeatureFlagBase):
    is_enabled: bool = False
    rollout_percentage: int = Field(0, ge=0, le=100)
    environment: str = "production"
    expires_at: Optional[datetime] = None


class FeatureFlagUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    rollout_percentage: Optional[int] = Field(None, ge=0, le=100)
    target_workspaces: Optional[List[UUID]] = None
    target_users: Optional[List[UUID]] = None
    targeting_rules: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class FeatureFlagResponse(FeatureFlagBase):
    id: UUID
    is_enabled: bool
    rollout_percentage: int
    target_workspaces: Optional[List[UUID]]
    target_users: Optional[List[UUID]]
    targeting_rules: Optional[Dict[str, Any]]
    environment: str
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[UUID]
    updated_by_id: Optional[UUID]
    
    model_config = ConfigDict(from_attributes=True)


# ======= AdminAuditLog Schemas =======

class AdminAuditLogCreate(BaseModel):
    admin_user_id: UUID
    action: str
    resource_type: str
    resource_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    status: str = "success"
    error_message: Optional[str] = None


class AdminAuditLogResponse(BaseModel):
    id: UUID
    admin_user_id: UUID
    action: str
    resource_type: str
    resource_id: Optional[UUID]
    ip_address: Optional[str]
    user_agent: Optional[str]
    session_id: Optional[str]
    changes: Optional[Dict[str, Any]]
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    status: str
    error_message: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AuditLogQuery(BaseModel):
    admin_user_id: Optional[UUID] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


# ======= SecurityIncident Schemas =======

class SecurityIncidentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    severity: str = Field(..., pattern="^(critical|high|medium|low)$")
    category: str = Field(..., min_length=1, max_length=100)


class SecurityIncidentCreate(SecurityIncidentBase):
    affected_user_id: Optional[UUID] = None
    affected_workspace_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None


class SecurityIncidentUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(open|investigating|resolved|closed)$")
    assigned_to_id: Optional[UUID] = None
    actions_taken: Optional[List[str]] = None
    resolution_notes: Optional[str] = None


class SecurityIncidentResponse(SecurityIncidentBase):
    id: UUID
    status: str
    assigned_to_id: Optional[UUID]
    affected_user_id: Optional[UUID]
    affected_workspace_id: Optional[UUID]
    ip_address: Optional[str]
    evidence: Optional[Dict[str, Any]]
    actions_taken: Optional[List[str]]
    resolution_notes: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    reported_by_id: Optional[UUID]
    
    model_config = ConfigDict(from_attributes=True)


# ======= ChangeRequest Schemas =======

class ChangeRequestBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    change_type: str = Field(..., pattern="^(release|config|hotfix|rollback)$")
    risk_level: str = Field(..., pattern="^(critical|high|medium|low)$")
    affected_systems: List[str] = Field(..., min_items=1)


class ChangeRequestCreate(ChangeRequestBase):
    rollback_plan: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class ChangeRequestUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(draft|pending|approved|rejected|deployed|rolled_back)$")
    scheduled_at: Optional[datetime] = None
    rollback_plan: Optional[str] = None
    deployment_notes: Optional[str] = None
    was_successful: Optional[bool] = None


class ChangeRequestApproval(BaseModel):
    approve: bool
    approval_notes: Optional[str] = None


class ChangeRequestResponse(ChangeRequestBase):
    id: UUID
    status: str
    scheduled_at: Optional[datetime]
    deployed_at: Optional[datetime]
    rollback_plan: Optional[str]
    approved_by_id: Optional[UUID]
    approved_at: Optional[datetime]
    approval_notes: Optional[str]
    deployment_notes: Optional[str]
    was_successful: Optional[bool]
    created_at: datetime
    updated_at: datetime
    requester_id: UUID
    
    model_config = ConfigDict(from_attributes=True)


# ======= AccessReview Schemas =======

class AccessReviewBase(BaseModel):
    review_period: str = Field(..., min_length=1, max_length=50)
    review_type: str = Field(..., pattern="^(quarterly|annual|ad-hoc)$")
    admin_user_id: UUID
    roles_reviewed: List[UUID] = Field(..., min_items=1)


class AccessReviewCreate(AccessReviewBase):
    pass


class AccessReviewDecision(BaseModel):
    decision: str = Field(..., pattern="^(approve_all|revoke_some|revoke_all)$")
    revoked_roles: Optional[List[UUID]] = None
    review_notes: Optional[str] = None
    
    @validator('revoked_roles')
    def validate_revoked_roles(cls, v, values):
        if values.get('decision') in ['revoke_some', 'revoke_all'] and not v:
            raise ValueError("revoked_roles required when decision is revoke_some or revoke_all")
        return v


class AccessReviewResponse(AccessReviewBase):
    id: UUID
    status: str
    reviewer_id: UUID
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]
    decision: Optional[str]
    revoked_roles: Optional[List[UUID]]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ======= Helper Schemas =======

class AdminLoginRequest(BaseModel):
    username: str
    password: str
    mfa_token: Optional[str] = None


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_user: AdminUserResponse
    roles: List[AdminRoleResponse]
    permissions: List[str]  # List of permission names


class RolePermissionAssignment(BaseModel):
    role_id: UUID
    permission_ids: List[UUID] = Field(..., min_items=1)


class BulkRoleAssignment(BaseModel):
    admin_user_id: UUID
    role_ids: List[UUID] = Field(..., min_items=1)
    valid_until: Optional[datetime] = None
    reason: str = Field(..., min_length=10)


class AdminStats(BaseModel):
    total_admin_users: int
    active_admin_users: int
    total_roles: int
    total_permissions: int
    pending_change_requests: int
    open_security_incidents: int
    pending_access_reviews: int
