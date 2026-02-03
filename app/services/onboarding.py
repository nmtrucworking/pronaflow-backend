"""
Service layer for User Onboarding & Adoption (Module 16)
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.onboarding import (
    OnboardingSurvey,
    SurveyQuestion,
    SurveyResponse,
    PersonaProfile,
    OnboardingFlow,
    FlowStep,
    UserOnboardingStatus,
    ProductTour,
    TourStep,
    OnboardingChecklist,
    OnboardingChecklistItem,
    UserChecklistProgress,
    FeatureBeacon,
    UserBeaconState,
    OnboardingReward,
)
from app.schemas.onboarding import (
    OnboardingSurveyCreate,
    SurveyQuestionCreate,
    SurveyResponseCreate,
    PersonaProfileCreate,
    OnboardingFlowCreate,
    FlowStepCreate,
    UserOnboardingStatusUpdate,
    ProductTourCreate,
    TourStepCreate,
    OnboardingChecklistCreate,
    OnboardingChecklistItemCreate,
    UserChecklistProgressUpdate,
    OnboardingRewardCreate,
    FeatureBeaconCreate,
)
from app.db.enums import OnboardingStatus


class SurveyService:
    def __init__(self, db: Session):
        self.db = db

    def create_survey(self, data: OnboardingSurveyCreate) -> OnboardingSurvey:
        survey = OnboardingSurvey(**data.model_dump())
        self.db.add(survey)
        self.db.commit()
        self.db.refresh(survey)
        return survey

    def list_surveys(self, is_active: Optional[bool] = None) -> List[OnboardingSurvey]:
        query = self.db.query(OnboardingSurvey)
        if is_active is not None:
            query = query.filter(OnboardingSurvey.is_active == is_active)
        return query.all()

    def create_question(self, data: SurveyQuestionCreate) -> SurveyQuestion:
        question = SurveyQuestion(**data.model_dump())
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def submit_response(self, user_id: UUID, data: SurveyResponseCreate) -> SurveyResponse:
        response = SurveyResponse(user_id=user_id, **data.model_dump())
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        return response


class PersonaService:
    def __init__(self, db: Session):
        self.db = db

    def upsert_persona(self, user_id: UUID, data: PersonaProfileCreate) -> PersonaProfile:
        persona = self.db.query(PersonaProfile).filter(PersonaProfile.user_id == user_id).first()
        if persona:
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(persona, field, value)
        else:
            persona = PersonaProfile(user_id=user_id, **data.model_dump())
            self.db.add(persona)
        self.db.commit()
        self.db.refresh(persona)
        return persona


class FlowService:
    def __init__(self, db: Session):
        self.db = db

    def create_flow(self, data: OnboardingFlowCreate) -> OnboardingFlow:
        flow = OnboardingFlow(**data.model_dump())
        self.db.add(flow)
        self.db.commit()
        self.db.refresh(flow)
        return flow

    def create_step(self, data: FlowStepCreate) -> FlowStep:
        step = FlowStep(**data.model_dump())
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        return step

    def get_user_status(self, user_id: UUID) -> Optional[UserOnboardingStatus]:
        return self.db.query(UserOnboardingStatus).filter(UserOnboardingStatus.user_id == user_id).first()

    def update_user_status(self, user_id: UUID, data: UserOnboardingStatusUpdate) -> UserOnboardingStatus:
        status = self.get_user_status(user_id)
        if not status:
            status = UserOnboardingStatus(user_id=user_id, status=OnboardingStatus.NOT_STARTED)
            self.db.add(status)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(status, field, value)

        if data.status == OnboardingStatus.IN_PROGRESS and status.started_at is None:
            status.started_at = datetime.utcnow()
        if data.status == OnboardingStatus.COMPLETED:
            status.completed_at = datetime.utcnow()
        if data.status == OnboardingStatus.SKIPPED:
            status.skipped_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(status)
        return status


class TourService:
    def __init__(self, db: Session):
        self.db = db

    def create_tour(self, data: ProductTourCreate) -> ProductTour:
        tour = ProductTour(**data.model_dump())
        self.db.add(tour)
        self.db.commit()
        self.db.refresh(tour)
        return tour

    def create_tour_step(self, data: TourStepCreate) -> TourStep:
        step = TourStep(**data.model_dump())
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        return step


class ChecklistService:
    def __init__(self, db: Session):
        self.db = db

    def create_checklist(self, data: OnboardingChecklistCreate) -> OnboardingChecklist:
        checklist = OnboardingChecklist(**data.model_dump())
        self.db.add(checklist)
        self.db.commit()
        self.db.refresh(checklist)
        return checklist

    def create_item(self, data: OnboardingChecklistItemCreate) -> OnboardingChecklistItem:
        item = OnboardingChecklistItem(**data.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_progress(self, user_id: UUID, data: UserChecklistProgressUpdate) -> UserChecklistProgress:
        progress = (
            self.db.query(UserChecklistProgress)
            .filter(UserChecklistProgress.user_id == user_id, UserChecklistProgress.item_id == data.item_id)
            .first()
        )
        if progress:
            progress.is_completed = data.is_completed
            progress.completed_at = datetime.utcnow() if data.is_completed else None
        else:
            progress = UserChecklistProgress(
                user_id=user_id,
                item_id=data.item_id,
                is_completed=data.is_completed,
                completed_at=datetime.utcnow() if data.is_completed else None,
            )
            self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def create_reward(self, data: OnboardingRewardCreate) -> OnboardingReward:
        reward = OnboardingReward(**data.model_dump())
        self.db.add(reward)
        self.db.commit()
        self.db.refresh(reward)
        return reward


class FeatureBeaconService:
    def __init__(self, db: Session):
        self.db = db

    def create_beacon(self, data: FeatureBeaconCreate) -> FeatureBeacon:
        beacon = FeatureBeacon(**data.model_dump())
        self.db.add(beacon)
        self.db.commit()
        self.db.refresh(beacon)
        return beacon

    def list_beacons(self, is_active: Optional[bool] = None) -> List[FeatureBeacon]:
        query = self.db.query(FeatureBeacon)
        if is_active is not None:
            query = query.filter(FeatureBeacon.is_active == is_active)
        return query.all()

    def dismiss_beacon(self, user_id: UUID, beacon_id: UUID) -> UserBeaconState:
        state = (
            self.db.query(UserBeaconState)
            .filter(UserBeaconState.user_id == user_id, UserBeaconState.beacon_id == beacon_id)
            .first()
        )
        if state:
            state.is_dismissed = True
            state.dismissed_at = datetime.utcnow()
        else:
            state = UserBeaconState(
                user_id=user_id,
                beacon_id=beacon_id,
                is_dismissed=True,
                dismissed_at=datetime.utcnow(),
            )
            self.db.add(state)
        self.db.commit()
        self.db.refresh(state)
        return state
