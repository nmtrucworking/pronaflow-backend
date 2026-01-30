> Mapping trực tiếp từ Module 9 (User Locale)
# Module 15

| Field              | Type     | Note |
| ------------------ | -------- | ---- |
| translation_id     | UUID     | PK   |
| version_id         | UUID     | FK   |
| locale             | varchar  |      |
| translated_content | richtext |      |
| is_default         | boolean  |      |
