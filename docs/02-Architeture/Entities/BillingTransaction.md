> áp dụng Idenpotency + Financial Audit

# Module 13
|Field|Type|
|---|---|
|id|UUID|
|workspace_id|UUID|
|amount|decimal|
|currency|varchar|
|provider|enum (STRIPE / PAYPAL)|
|provider_tx_id|varchar|
|status|enum (SUCCESS / FAILED / REFUNDED)|
|idempotency_key|UUID|
|created_at|timestamp|
