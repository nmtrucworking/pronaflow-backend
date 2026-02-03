"""
Entity Models for Functional Module 16: User Onboarding & Adoption
Provides survey intake, persona mapping, flow orchestration, tours,
checklists, feature beacons, and rewards.
Ref: docs/01-Requirements/Functional-Modules/16 - User Onboarding and Adoption.md
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import (
    String, Text, Integer, Boolean, DateTime, ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.declarative_base import Base
from app.db.mixins import TimestampMixin
from app.db.enums import OnboardingStatus

if TYPE_CHECKING:
    from app.db.models.users import User


# ======= Survey & Persona =======

class OnboardingSurvey(Base, TimestampMixin):
    """Welcome Survey definition"""
    __tablename__ = "onboarding_surveys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    questions = relationship("SurveyQuestion", back_populates="survey", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_onboarding_surveys_active", "is_active"),
    )


class SurveyQuestion(Base, TimestampMixin):
    """Survey questions for onboarding"""
    __tablename__ = "survey_questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    survey_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_surveys.id", ondelete="CASCADE"))

    question_text: Mapped[str] = mapped_column(String(500), nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)  # single_choice, multi_choice, text
    options: Mapped[Optional[dict]] = mapped_column(JSONB)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    survey = relationship("OnboardingSurvey", back_populates="questions")
    responses = relationship("SurveyResponse", back_populates="question", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_survey_questions_survey", "survey_id"),
    )


class SurveyResponse(Base, TimestampMixin):
    """User responses to onboarding survey"""
    __tablename__ = "survey_responses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    question_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("survey_questions.id", ondelete="CASCADE"))

    answer_text: Mapped[Optional[str]] = mapped_column(Text)
    answer_choice: Mapped[Optional[str]] = mapped_column(String(255))
    answer_choices: Mapped[Optional[List[str]]] = mapped_column(JSONB)

    question = relationship("SurveyQuestion", back_populates="responses")

    __table_args__ = (
        Index("ix_survey_responses_user", "user_id"),
        Index("ix_survey_responses_question", "question_id"),
    )


class PersonaProfile(Base, TimestampMixin):
    """Persona mapped from survey responses"""
    __tablename__ = "persona_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    role: Mapped[str] = mapped_column(String(100), nullable=False)  # Project Manager, Developer, Stakeholder
    goal: Mapped[Optional[str]] = mapped_column(String(255))
    experience: Mapped[Optional[str]] = mapped_column(String(255))
    preferences: Mapped[Optional[dict]] = mapped_column(JSONB)

    __table_args__ = (
        Index("ix_persona_profiles_user", "user_id"),
    )


# ======= Onboarding Flow =======

class OnboardingFlow(Base, TimestampMixin):
    """Flow definition triggered by persona"""
    __tablename__ = "onboarding_flows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    persona_role: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    steps = relationship("FlowStep", back_populates="flow", cascade="all, delete-orphan")


class FlowStep(Base, TimestampMixin):
    """Steps in onboarding flow"""
    __tablename__ = "flow_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_flows.id", ondelete="CASCADE"))

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    route_path: Mapped[Optional[str]] = mapped_column(String(255))
    required_action: Mapped[Optional[str]] = mapped_column(String(255))
    step_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    flow = relationship("OnboardingFlow", back_populates="steps")

    __table_args__ = (
        Index("ix_flow_steps_flow", "flow_id"),
        Index("ix_flow_steps_order", "step_order"),
    )


class UserOnboardingStatus(Base, TimestampMixin):
    """Progress tracking for onboarding flow"""
    __tablename__ = "user_onboarding_status"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    flow_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_flows.id"))

    status: Mapped[OnboardingStatus] = mapped_column(SQLEnum(OnboardingStatus), default=OnboardingStatus.NOT_STARTED, nullable=False)
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_steps: Mapped[Optional[List[int]]] = mapped_column(JSONB)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    skipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_user_onboarding_status_user", "user_id"),
        Index("ix_user_onboarding_status_flow", "flow_id"),
    )


# ======= Product Tours =======

class ProductTour(Base, TimestampMixin):
    """Interactive product tour"""
    __tablename__ = "product_tours"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    route_path: Mapped[Optional[str]] = mapped_column(String(255))
    is_skippable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    steps = relationship("TourStep", back_populates="tour", cascade="all, delete-orphan")


class TourStep(Base, TimestampMixin):
    """Steps for interactive tour"""
    __tablename__ = "tour_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tour_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("product_tours.id", ondelete="CASCADE"))

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    target_selector: Mapped[str] = mapped_column(String(255), nullable=False)
    required_action: Mapped[Optional[str]] = mapped_column(String(255))
    step_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tour = relationship("ProductTour", back_populates="steps")

    __table_args__ = (
        Index("ix_tour_steps_tour", "tour_id"),
        Index("ix_tour_steps_order", "step_order"),
    )


class UserTourSession(Base, TimestampMixin):
    """
    Track tour sessions per user session to enforce frequency cap (1 tour/session).
    """
    __tablename__ = "user_tour_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    tour_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("product_tours.id", ondelete="CASCADE"))

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    skipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    tour = relationship("ProductTour")

    __table_args__ = (
        Index("ix_user_tour_sessions_user", "user_id"),
        Index("ix_user_tour_sessions_session", "session_id"),
        Index("ix_user_tour_sessions_tour", "tour_id"),
    )


# ======= Checklist & Reward =======

class OnboardingChecklist(Base, TimestampMixin):
    """Checklist for onboarding progress"""
    __tablename__ = "onboarding_checklists"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    items = relationship("OnboardingChecklistItem", back_populates="checklist", cascade="all, delete-orphan")
    reward = relationship("OnboardingReward", back_populates="checklist", uselist=False, cascade="all, delete-orphan")


class OnboardingChecklistItem(Base, TimestampMixin):
    """Checklist item"""
    __tablename__ = "onboarding_checklist_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    checklist_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_checklists.id", ondelete="CASCADE"))

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    route_path: Mapped[Optional[str]] = mapped_column(String(255))
    required_action: Mapped[Optional[str]] = mapped_column(String(255))
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    checklist = relationship("OnboardingChecklist", back_populates="items")
    progress = relationship("UserChecklistProgress", back_populates="item", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_onboarding_checklist_items_checklist", "checklist_id"),
        Index("ix_onboarding_checklist_items_order", "display_order"),
    )


class UserChecklistProgress(Base, TimestampMixin):
    """Track user progress per checklist item"""
    __tablename__ = "user_checklist_progress"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_checklist_items.id", ondelete="CASCADE"))

    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    item = relationship("OnboardingChecklistItem", back_populates="progress")

    __table_args__ = (
        Index("ix_user_checklist_progress_user", "user_id"),
        Index("ix_user_checklist_progress_item", "item_id"),
    )


class OnboardingReward(Base, TimestampMixin):
    """Reward granted after checklist completion"""
    __tablename__ = "onboarding_rewards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    checklist_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_checklists.id", ondelete="CASCADE"), unique=True)

    reward_type: Mapped[str] = mapped_column(String(100), nullable=False)  # trial_extension, badge, credit
    reward_value: Mapped[Optional[dict]] = mapped_column(JSONB)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    checklist = relationship("OnboardingChecklist", back_populates="reward")


class OnboardingRewardGrant(Base, TimestampMixin):
    """
    Record reward grants to prevent duplicate awarding.
    """
    __tablename__ = "onboarding_reward_grants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reward_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_rewards.id", ondelete="CASCADE"))
    checklist_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_checklists.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))

    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB)

    __table_args__ = (
        Index("ix_onboarding_reward_grants_user", "user_id"),
        Index("ix_onboarding_reward_grants_reward", "reward_id"),
        Index("ix_onboarding_reward_grants_checklist", "checklist_id"),
    )


# ======= Feature Discovery (Beacon) =======

class FeatureBeacon(Base, TimestampMixin):
    """Hotspot for new feature discovery"""
    __tablename__ = "feature_beacons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    route_path: Mapped[Optional[str]] = mapped_column(String(255))
    target_selector: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    states = relationship("UserBeaconState", back_populates="beacon", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_feature_beacons_key", "feature_key"),
        Index("ix_feature_beacons_active", "is_active"),
    )


class UserBeaconState(Base, TimestampMixin):
    """User-specific beacon dismissal state"""
    __tablename__ = "user_beacon_states"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    beacon_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("feature_beacons.id", ondelete="CASCADE"))

    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    beacon = relationship("FeatureBeacon", back_populates="states")

    __table_args__ = (
        Index("ix_user_beacon_states_user", "user_id"),
        Index("ix_user_beacon_states_beacon", "beacon_id"),
    )
