# Module 9
|Field|Type|Ghi chú|
|---|---|---|
|id|UUID|PK|
|user_id|UUID|FK → users|
|language|varchar|en-US, vi-VN|
|theme_mode|enum|light / dark / system|
|base_font_size|int|12 / 14 / 16 / 18|
|font_family|enum|system / dyslexic / monospace|
|density_mode|enum|comfortable / compact|
|color_blind_mode|enum|none / deuter / protan / tritan|
|created_at|timestamp||
|updated_at|timestamp||