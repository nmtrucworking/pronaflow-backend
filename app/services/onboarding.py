"""
Service layer for User Onboarding & Adoption (Module 16)
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.onboarding import (
    OnboardingSurvey,
    SurveyQuestion,
    SurveyResponse,
    PersonaProfile,
    OnboardingFlow,
    FlowStep,
    UserOnboardingStatus,
    ProductTour,
    TourStep,
    UserTourSession,
    OnboardingChecklist,
    OnboardingChecklistItem,
    UserChecklistProgress,
    FeatureBeacon,
    UserBeaconState,
    OnboardingReward,
    OnboardingRewardGrant,
)
from app.models.workspaces import WorkspaceMember
from app.models.admin import FeatureFlag
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
from app.services.personalization import PersonalizationService
from app.schemas.personalization import UserSettingsUpdate
from app.services.subscription import SubscriptionService
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
        self._apply_persona_preferences(user_id, data.preferences or {})
        return persona

    def _apply_persona_preferences(self, user_id: UUID, preferences: dict) -> None:
        """
        Map persona preferences to UI settings and feature toggles.

        Expected preferences schema:
        {
            "ui_settings": {"theme_mode": "dark", "language": "vi-VN", ...},
            "feature_toggles": {"new_dashboard": true, "ai_assistant": false}
        }
        """
        ui_settings = preferences.get("ui_settings", {})
        feature_toggles = preferences.get("feature_toggles", {})

        if ui_settings:
            allowed_fields = set(UserSettingsUpdate.model_fields.keys())
            filtered_settings = {k: v for k, v in ui_settings.items() if k in allowed_fields}
            if filtered_settings:
                settings_update = UserSettingsUpdate(**filtered_settings)
                PersonalizationService.update_user_settings(self.db, user_id, settings_update)

        if feature_toggles:
            for key, enabled in feature_toggles.items():
                flag = self.db.query(FeatureFlag).filter(FeatureFlag.key == key).first()
                if not flag:
                    continue
                target_users = flag.target_users or []
                user_id_str = str(user_id)
                if enabled and user_id_str not in target_users:
                    target_users.append(user_id_str)
                if not enabled and user_id_str in target_users:
                    target_users.remove(user_id_str)
                flag.target_users = target_users
            self.db.commit()


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

    def start_tour(self, user_id: UUID, session_id: UUID, tour_id: UUID) -> UserTourSession:
        tour = self.db.query(ProductTour).filter(ProductTour.id == tour_id, ProductTour.is_active == True).first()
        if not tour:
            raise ValueError("Tour not found or inactive")

        existing_session = self.db.query(UserTourSession).filter(
            UserTourSession.session_id == session_id,
            UserTourSession.user_id == user_id,
        ).first()

        if existing_session:
            raise ValueError("Only one tour is allowed per session")

        session = UserTourSession(
            user_id=user_id,
            session_id=session_id,
            tour_id=tour_id,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def skip_tour(self, user_id: UUID, session_id: UUID, tour_id: UUID) -> UserTourSession:
        tour = self.db.query(ProductTour).filter(ProductTour.id == tour_id).first()
        if not tour:
            raise ValueError("Tour not found")
        if not tour.is_skippable:
            raise PermissionError("Tour is not skippable")

        session = self.db.query(UserTourSession).filter(
            UserTourSession.user_id == user_id,
            UserTourSession.session_id == session_id,
            UserTourSession.tour_id == tour_id,
            UserTourSession.completed_at == None,
            UserTourSession.skipped_at == None,
        ).first()

        if not session:
            session = UserTourSession(
                user_id=user_id,
                session_id=session_id,
                tour_id=tour_id,
            )
            self.db.add(session)

        session.skipped_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        return session


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

        self._grant_reward_if_eligible(user_id, data.item_id)
        return progress

    def create_reward(self, data: OnboardingRewardCreate) -> OnboardingReward:
        reward = OnboardingReward(**data.model_dump())
        self.db.add(reward)
        self.db.commit()
        self.db.refresh(reward)
        return reward

    def _grant_reward_if_eligible(self, user_id: UUID, item_id: UUID) -> None:
        item = self.db.query(OnboardingChecklistItem).filter(OnboardingChecklistItem.id == item_id).first()
        if not item:
            return

        checklist = self.db.query(OnboardingChecklist).filter(OnboardingChecklist.id == item.checklist_id).first()
        if not checklist:
            return

        # Check all required items completed
        required_items = self.db.query(OnboardingChecklistItem).filter(
            OnboardingChecklistItem.checklist_id == checklist.id,
            OnboardingChecklistItem.is_required == True
        ).all()

        if not required_items:
            return

        required_item_ids = [i.id for i in required_items]
        completed_count = self.db.query(UserChecklistProgress).filter(
            UserChecklistProgress.user_id == user_id,
            UserChecklistProgress.item_id.in_(required_item_ids),
            UserChecklistProgress.is_completed == True
        ).count()

        if completed_count < len(required_item_ids):
            return

        reward = self.db.query(OnboardingReward).filter(
            OnboardingReward.checklist_id == checklist.id,
            OnboardingReward.is_active == True
        ).first()

        if not reward:
            return

        existing_grant = self.db.query(OnboardingRewardGrant).filter(
            OnboardingRewardGrant.user_id == user_id,
            OnboardingRewardGrant.reward_id == reward.id
        ).first()

        if existing_grant:
            return

        applied = True

        # Apply reward to Module 13 (trial extension)
        if reward.reward_type == "trial_extension":
            reward_value = reward.reward_value or {}
            trial_days = int(reward_value.get("days", 7))
            workspace_id = reward_value.get("workspace_id")

            if not workspace_id:
                membership = self.db.query(WorkspaceMember).filter(
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.is_active == True
                ).first()
                workspace_id = membership.workspace_id if membership else None

            if workspace_id:
                subscription_service = SubscriptionService(self.db)
                applied = subscription_service.extend_trial(workspace_id, trial_days) is not None
            else:
                applied = False

        if applied:
            grant = OnboardingRewardGrant(
                reward_id=reward.id,
                checklist_id=checklist.id,
                user_id=user_id,
                metadata_={"reward_type": reward.reward_type, "reward_value": reward.reward_value},
            )
            self.db.add(grant)
            self.db.commit()


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
