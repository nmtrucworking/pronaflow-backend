> Cấu hình #MFA (TOTP)

# Phân hệ 1.
|Field|Type|
|---|---|
|mfa_id (PK)|UUID|
|user_id (FK)|UUID|
|secret_key|varchar|
|enabled|boolean|
|created_at|timestamp|