**Triết lý:** Context-aware • Self-service • PLG-ready  
**Bản chất:** Knowledge Management + Search + Feedback (KHÔNG phải ticketing)

---

# Entity

| Domain          | Mục tiêu            | Entity                                  |
| --------------- | ------------------- | --------------------------------------- |
| Content Core    | Bài viết & cấu trúc | [[Article]], [[ArticleVersion]]         |
| Taxonomy        | Phân loại           | [[Category]]<br>[[Tag]]                 |
| Localization    | Đa ngôn ngữ         | [[ArticleTranslation]]                  |
| Contextual Help | Gợi ý theo ngữ cảnh | [[RouteMapping]]                        |
| Search          | Semantic + Keyword  | [[SearchIndex]]                         |
| Feedback        | Helpfulness & gap   | [[ArticleFeedback]]<br>[[FailedSearch]] |
| Visibility      | Public / Private    | [[ArticleVisibility]]                   |

# ERD
```mermaid
erDiagram
    ARTICLE ||--o{ ARTICLE_VERSION : has
    ARTICLE_VERSION ||--o{ ARTICLE_TRANSLATION : localized_as

    ARTICLE ||--o{ ARTICLE_TAG : classified_by
    TAG ||--o{ ARTICLE_TAG : labels

    CATEGORY ||--o{ ARTICLE : groups

    ARTICLE ||--o{ ROUTE_MAPPING : suggested_on

    ARTICLE ||--|| SEARCH_INDEX : indexed_as

    ARTICLE ||--o{ ARTICLE_FEEDBACK : reviewed_by
    USER ||--o{ ARTICLE_FEEDBACK : submits

    ARTICLE ||--o{ ARTICLE_VISIBILITY : constrained_by

```

# Mapping
|Tài liệu|Entity|
|---|---|
|Contextual Help Widget|RouteMapping|
|Embedded Reader|ArticleVersion|
|Semantic Search|SearchIndex.embedding_vector|
|Keyword Search|SearchIndex.keywords|
|Versioning|ArticleVersion|
|Localization|ArticleTranslation|
|Yes/No feedback|ArticleFeedback|
|Failed searches|FailedSearch|
|Public vs Private KB|ArticleVisibility|
