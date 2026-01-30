> **Mục tiêu cốt lõi:** Giảm _Time-to-Value_ – dẫn người dùng đến **Aha Moment**  
> **Bản chất:** Behavioral orchestration (không phải notification, không phải analytics)

---

# Entity

| Domain            | Mục tiêu                    | Entity                                       |
| ----------------- | --------------------------- | -------------------------------------------- |
| Persona Intake    | Thu thập vai trò & mục tiêu | [[OnboardingSurvey]], [[PersonaProfile]]     |
| Flow Engine       | Điều phối onboarding        | [[OnboardingFlow]], [[FlowStep]]             |
| Progress Tracking | Theo dõi tiến độ            | [[UserOnboardingStatus]]                     |
| Interactive Tour  | Tour tương tác              | [[ProductTour]]<br>[[TourStep]]              |
| Checklist         | Gamification                | [[OnboardingChecklist]]<br>[[ChecklistItem]] |
| Feature Discovery | Beacon / Hotspot            | [[FeatureBeacon]]                            |
| Reward            | Khuyến khích                | [[OnboardingReward]]                         |

# ERD
```mermaid
erDiagram
    ONBOARDING_SURVEY ||--o{ SURVEY_QUESTION : contains
    SURVEY_QUESTION ||--o{ SURVEY_RESPONSE : answered_by
    USER ||--o{ SURVEY_RESPONSE : submits

    USER ||--|| PERSONA_PROFILE : mapped_as

    PERSONA_PROFILE ||--o{ ONBOARDING_FLOW : triggers
    ONBOARDING_FLOW ||--o{ FLOW_STEP : consists_of

    USER ||--o{ USER_ONBOARDING_STATUS : progresses

    PRODUCT_TOUR ||--o{ TOUR_STEP : includes

    ONBOARDING_CHECKLIST ||--o{ CHECKLIST_ITEM : has
    CHECKLIST_ITEM ||--o{ USER_CHECKLIST_PROGRESS : tracked_by

    FEATURE_BEACON ||--o{ USER_BEACON_STATE : dismissed_by

    ONBOARDING_REWARD ||--o{ ONBOARDING_CHECKLIST : grants

```
# Mapping
|AC|Entity|
|---|---|
|Welcome Survey|OnboardingSurvey, SurveyResponse|
|Persona Mapping|PersonaProfile|
|Interactive Tour|ProductTour, TourStep|
|Required Interaction|TourStep.required_action|
|Skip Logic|ProductTour.is_skippable|
|Progress Bar|UserOnboardingStatus|
|Checklist|OnboardingChecklist|
|Reward|OnboardingReward|
|Hotspot|FeatureBeacon|
|One-time Dismiss|UserBeaconState|
