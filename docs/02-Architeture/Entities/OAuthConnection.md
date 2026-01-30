> User ↔ App
# Module 12

|Field|Type|
|---|---|
|connection_id (PK)|UUID|
|user_id (FK)|UUID|
|app_id (FK)|UUID|
|access_token|text|
|refresh_token|text|
|expires_at|timestamp|
|connected_at|timestamp|
|revoked_at|timestamp|