# Module 1 IAM Completion Checklist

Version: 1.0
Status: In Progress
Date: 2026-03-29
Scope: Functional Module 1 - Identity and Access Management (IAM)

---

## 1. Completion Goal

- [ ] All Module 1 user stories (1.1 -> 1.7) are implemented end-to-end.
- [ ] All acceptance criteria are covered by automated tests.
- [ ] No open critical/high issues in auth, MFA, session, password reset, OAuth flows.
- [ ] API docs and technical docs are synchronized with actual behavior.

---

## 2. Critical Gap Fixes (Priority P0)

### 2.1 Password reset flow
- [x] Fix request reset endpoint to resolve user by email before creating token.
- [x] Ensure reset token is one-time use and expires in 15 minutes.
- [x] Ensure password reset revokes all other active sessions immediately.
- [ ] Add negative tests: invalid token, expired token, reused token.

### 2.2 MFA login verification
- [x] Fix MFA verify endpoint to validate by user identity (not session_id as user_id).
- [x] Ensure OTP/backup code verification completes login correctly.
- [x] Return proper response model for MFA-required login state.
- [ ] Add integration tests for full MFA login sequence.

### 2.3 Session revoke/logout correctness
- [x] Implement real logout by revoking current session from JWT session_id.
- [x] Fix revoke-all to keep current session when required.
- [x] Ensure revoked session is blocked on next request.
- [ ] Add integration tests for logout, revoke single session, revoke all sessions.

### 2.4 Brute-force protection consistency
- [x] Enforce policy: 5 failed attempts within 10 minutes.
- [x] Apply lockout duration 15 minutes.
- [x] Send brute-force security alert email when lockout is triggered.
- [ ] Add tests for attempt window, lockout, and unlock behavior.

---

## 3. Feature Completion by User Story

### 3.1 User Story 1.1 - Registration + email verification
- [ ] Validate email format.
- [ ] Validate username: 3-30 chars, letters/numbers/underscore only.
- [ ] Validate password strength: >= 12 chars, upper/lower/digit/special.
- [ ] Create account in PENDING state after registration.
- [ ] Send verification email with 24-hour token.
- [ ] Activate account to ACTIVE after valid verification.
- [ ] Support resend verification for expired tokens.

### 3.2 User Story 1.2 - Secure login
- [x] Support login by email.
- [x] Support login by username.
- [ ] Return consistent auth error model.
- [ ] Ensure account status and email-verified checks are enforced.

### 3.3 User Story 1.3 - RBAC authorization
- [ ] Verify default roles: Owner, Admin, Member, Guest.
- [ ] Enforce permission checks on protected actions.
- [ ] Return standardized forbidden response for insufficient permission.
- [ ] Add coverage tests for allow/deny matrix on critical endpoints.

### 3.4 User Story 1.4 - Password recovery
- [x] Do not expose account existence in reset request response.
- [ ] Never send old password in email.
- [x] Ensure token is single-use and short-lived (15 minutes).
- [x] Force re-authentication by revoking active sessions after reset.

### 3.5 User Story 1.5 - MFA
- [ ] Enable MFA with TOTP app compatible setup (Google/Microsoft Authenticator).
- [ ] Confirm MFA only with valid 6-digit OTP.
- [ ] Require MFA second step during login when enabled.
- [x] Generate 10 backup codes and store only hashed values.
- [x] Ensure backup code verification checks all unused codes correctly.

### 3.6 User Story 1.6 - Session management
- [ ] List active sessions with device info, geo location, last activity.
- [ ] Correctly identify current session.
- [ ] Enforce max 5 concurrent sessions; revoke oldest on new login.
- [ ] Allow remote revoke by selected session.
- [ ] Implement impossible travel detection with alert + re-auth requirement.

### 3.7 User Story 1.7 - Social authentication
- [ ] Implement OAuth authorize flow for Google.
- [ ] Implement OAuth callback for Google.
- [ ] Implement OAuth authorize flow for GitHub.
- [ ] Implement OAuth callback for GitHub.
- [ ] Support account linking when email already exists.
- [ ] Auto-provision verified account for new social login.

---

## 4. Data and Security Rules

- [ ] Ensure email and username uniqueness at DB and service levels.
- [ ] Ensure all passwords/tokens are stored hashed (one-way).
- [ ] Ensure OTP/reset tokens are never returned in logs or API responses.
- [ ] Ensure audit log for login, password change/reset, MFA enable/disable.
- [ ] Ensure session timeout and cleanup policy is applied.

---

## 5. Testing Checklist

### 5.1 Unit tests
- [ ] Auth service tests aligned with current API contracts.
- [ ] MFA service tests include backup code edge cases.
- [ ] Session service tests include impossible travel and current-session logic.

### 5.2 Integration/API tests
- [ ] Fix route path mismatches to current auth prefix.
- [ ] Add tests for registration, login (email and username), MFA flow, password reset.
- [ ] Add tests for OAuth flows with mocked providers.
- [ ] Add tests for brute-force lockout and unlock window.

### 5.3 Regression and quality gates
- [ ] IAM test suite passes in CI.
- [ ] No new lint/type errors in IAM-related files.
- [ ] Coverage threshold for IAM module is met (set team target).

---

## 6. Documentation Sync

- [ ] Update API docs for all final auth/MFA/session/OAuth behaviors.
- [ ] Update deployment checklist only after completion checklist reaches done.
- [ ] Add release notes for FM1 functional changes and security fixes.

---

## 7. Definition of Done (FM1)

- [ ] All P0 items completed.
- [ ] All user stories 1.1 -> 1.7 completed or explicitly deferred with approval.
- [ ] All required tests implemented and passing.
- [ ] Security review completed for auth, token, and session flows.
- [ ] Product owner signs off FM1 against acceptance criteria.
