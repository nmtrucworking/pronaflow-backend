**Project**: PronaFlow 
**Version**: 1.0
**State**: Draft 
_**Last updated:** Jan 11, 2026_

---

> Vai trò: **PronaFlow = Platform / Command Center**, không chỉ là app  
> Triết lý: **Loose Coupling – Secure by Design – API Economy**

# Entity

|Layer|Chức năng|Entity|
|---|---|---|
|API Access|REST API + PAT|ApiToken, ApiScope|
|Webhook|Outbound event|WebhookEndpoint, WebhookEvent, WebhookDelivery|
|OAuth|Native connectors|OAuthApp, OAuthConnection|
|Integration|Mapping dữ liệu|IntegrationBinding|
|Plugin|Marketplace & SDK|Plugin, PluginInstallation|
|Governance|Rate limit & consent|ApiUsageLog, ConsentGrant|

# ERD
```mermaid
erDiagram
    USER ||--o{ API_TOKEN : owns
    API_TOKEN ||--o{ API_TOKEN_SCOPE : grants
    API_SCOPE ||--o{ API_TOKEN_SCOPE : defines
    API_TOKEN ||--o{ API_USAGE_LOG : logs

    WORKSPACE ||--o{ WEBHOOK_ENDPOINT : registers
    WEBHOOK_ENDPOINT ||--o{ WEBHOOK_EVENT : subscribes
    WEBHOOK_ENDPOINT ||--o{ WEBHOOK_DELIVERY : delivers

    USER ||--o{ OAUTH_CONNECTION : connects
    OAUTH_APP ||--o{ OAUTH_CONNECTION : authorizes
    OAUTH_CONNECTION ||--o{ INTEGRATION_BINDING : maps

    PLUGIN ||--o{ PLUGIN_INSTALLATION : installed_as
    WORKSPACE ||--o{ PLUGIN_INSTALLATION : enables

    USER ||--o{ CONSENT_GRANT : grants

```