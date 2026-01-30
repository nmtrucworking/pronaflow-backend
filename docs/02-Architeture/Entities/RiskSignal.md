> Cảnh bảo rủi ro dự án
> Kích hoạt sang Module 7 - [[7 - Even-Driven Notification System]]

# Module 10
|Field|Type|
|---|---|
|risk_id (PK)|UUID|
|project_id (FK)|UUID|
|signal_type|enum|
|severity|enum|
|detected_at|timestamp|
|is_acknowledged|boolean|
