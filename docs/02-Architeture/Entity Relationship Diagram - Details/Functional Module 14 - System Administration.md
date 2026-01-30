> **Nguyên tắc cốt lõi**
> - **Separation of Duties (SoD)**
> - **Least Privilege**
> - **Audit-first / Write-protected logs**
> - **Admin ≠ User**

---

# Entity

| Domain          | Mục tiêu               | Entity                                     |
| --------------- | ---------------------- | ------------------------------------------ |
| Admin Identity  | Định danh admin        | [[AdminUser]]                              |
| Admin Roles     | 18 vai trò chuyên biệt | [[AdminRole]]                              |
| Permission      | Quyền thao tác         | [[AdminPermission]]                        |
| Assignment      | Gán quyền              | [[AdminRolePermission]], [[AdminUserRole]] |
| System Config   | Cấu hình hệ thống      | [[SystemConfig]]                           |
| Feature Control | Kill switch / rollout  | [[FeatureFlag]]                            |
| Audit Logging   | Nhật ký bất biến       | [[AdminAuditLog]]                          |
| Security Ops    | Sự kiện bảo mật        | [[SecurityIncident]]                       |
| Change Mgmt     | Release / Change       | [[ChangeRequest]]                          |
| Access Review   | Kiểm toán định kỳ      | [[AccessReview]]                           |
# ERD
```mermaid
erDiagram
    ADMIN_USER ||--o{ ADMIN_USER_ROLE : assigned
    ADMIN_ROLE ||--o{ ADMIN_USER_ROLE : grants

    ADMIN_ROLE ||--o{ ADMIN_ROLE_PERMISSION : defines
    ADMIN_PERMISSION ||--o{ ADMIN_ROLE_PERMISSION : allows

    ADMIN_USER ||--o{ AUDIT_LOG : generates

    ADMIN_USER ||--o{ SECURITY_INCIDENT : manages

    ADMIN_USER ||--o{ CHANGE_REQUEST : requests
    CHANGE_REQUEST ||--|| ADMIN_USER : approved_by

    ADMIN_USER ||--o{ ACCESS_REVIEW : reviewed_in

```
# Mapping
| Role             | Entity liên quan              |
| ---------------- | ----------------------------- |
| Super Admin      | FeatureFlag, SystemConfig     |
| SRE Admin        | SystemConfig (READ), AuditLog |
| Release Admin    | ChangeRequest                 |
| Security Admin   | SecurityIncident              |
| IAM Admin        | AdminUserRole                 |
| Compliance Admin | AdminAuditLog                 |
| Privacy / DPO    | AccessReview                  |
| Finance Admin    | Billing (READ)                |
| AI Admin         | FeatureFlag (AI)              |
| Data Admin       | Analytics (READ)              |
| Support Admin    | Ticket (Module khác)          |
| Audit-only       | AuditLog (READ ONLY)          |
