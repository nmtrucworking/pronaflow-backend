> Metadata cho Search Engine (Elastic / Vectore DB)

# Module 15

| Filde            | Type      |     |
| ---------------- | --------- | --- |
| index_id         | UUID      | PK  |
| article_id       | UUID      | FK  |
| embedding_vector | vector    |     |
| keywords         | text      |     |
| indexed_at       | timestamp |     |

- Vector generation có thể dùng Module 10 
- Những ownership vẫn là Module 15
- 