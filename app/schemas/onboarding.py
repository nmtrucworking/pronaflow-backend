"""
Pydantic schemas for User Onboarding & Adoption (Module 16)
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.db.enums import OnboardingStatus


# ======= Survey Schemas =======

class OnboardingSurveyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: bool = True


class OnboardingSurveyCreate(OnboardingSurveyBase):
    pass


class OnboardingSurveyResponse(OnboardingSurveyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SurveyQuestionBase(BaseModel):
    survey_id: UUID
    question_text: str = Field(..., min_length=1, max_length=500)
    question_type: str = Field(..., min_length=1, max_length=50)
    options: Optional[Dict[str, Any]] = None
    display_order: int = 0
    is_required: bool = True


class SurveyQuestionCreate(SurveyQuestionBase):
    pass


class SurveyQuestionResponse(SurveyQuestionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SurveyResponseCreate(BaseModel):
    question_id: UUID
    answer_text: Optional[str] = None
    answer_choice: Optional[str] = None
    answer_choices: Optional[List[str]] = None


class SurveyResponseResponse(BaseModel):
    id: UUID
    user_id: UUID
    question_id: UUID
    answer_text: Optional[str]
    answer_choice: Optional[str]
    answer_choices: Optional[List[str]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======= Persona Schemas =======

class PersonaProfileCreate(BaseModel):
    role: str = Field(..., min_length=1, max_length=100)
    goal: Optional[str] = None
    experience: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class PersonaProfileResponse(PersonaProfileCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======= Flow Schemas =======

class OnboardingFlowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    persona_role: Optional[str] = None
    is_active: bool = True


class OnboardingFlowCreate(OnboardingFlowBase):
    pass


class OnboardingFlowResponse(OnboardingFlowBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FlowStepBase(BaseModel):
    flow_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    route_path: Optional[str] = None
    required_action: Optional[str] = None
    step_order: int = 0
    is_required: bool = True


class FlowStepCreate(FlowStepBase):
    pass


class FlowStepResponse(FlowStepBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserOnboardingStatusResponse(BaseModel):
    id: UUID
    user_id: UUID
    flow_id: Optional[UUID]
    status: OnboardingStatus
    current_step: int
    completed_steps: Optional[List[int]]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    skipped_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserOnboardingStatusUpdate(BaseModel):
    status: Optional[OnboardingStatus] = None
    current_step: Optional[int] = None
    completed_steps: Optional[List[int]] = None


# ======= Tour Schemas =======

class ProductTourBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    route_path: Optional[str] = None
    is_skippable: bool = True
    is_active: bool = True


class ProductTourCreate(ProductTourBase):
    pass


class ProductTourResponse(ProductTourBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TourStepBase(BaseModel):
    tour_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    target_selector: str = Field(..., min_length=1, max_length=255)
    required_action: Optional[str] = None
    step_order: int = 0
    is_required: bool = True


class TourStepCreate(TourStepBase):
    pass


class TourStepResponse(TourStepBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======= Checklist Schemas =======

class OnboardingChecklistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: bool = True


class OnboardingChecklistCreate(OnboardingChecklistBase):
    pass


class OnboardingChecklistResponse(OnboardingChecklistBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OnboardingChecklistItemBase(BaseModel):
    checklist_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    route_path: Optional[str] = None
    required_action: Optional[str] = None
    display_order: int = 0
    is_required: bool = True


class OnboardingChecklistItemCreate(OnboardingChecklistItemBase):
    pass


class OnboardingChecklistItemResponse(OnboardingChecklistItemBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserChecklistProgressUpdate(BaseModel):
    item_id: UUID
    is_completed: bool


class UserChecklistProgressResponse(BaseModel):
    id: UUID
    user_id: UUID
    item_id: UUID
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OnboardingRewardCreate(BaseModel):
    checklist_id: UUID
    reward_type: str = Field(..., min_length=1, max_length=100)
    reward_value: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    is_active: bool = True


class OnboardingRewardResponse(OnboardingRewardCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======= Feature Beacon Schemas =======

class FeatureBeaconBase(BaseModel):
    feature_key: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    route_path: Optional[str] = None
    target_selector: Optional[str] = None
    is_active: bool = True


class FeatureBeaconCreate(FeatureBeaconBase):
    pass


class FeatureBeaconResponse(FeatureBeaconBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBeaconStateResponse(BaseModel):
    id: UUID
    user_id: UUID
    beacon_id: UUID
    is_dismissed: bool
    dismissed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
