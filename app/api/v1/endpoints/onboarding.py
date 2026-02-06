"""
API endpoints for User Onboarding & Adoption (Module 16)
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user, get_current_user_with_session
from app.models.users import User
from app.services.onboarding import (
    SurveyService,
    PersonaService,
    FlowService,
    TourService,
    ChecklistService,
    FeatureBeaconService,
)
from app.schemas.onboarding import (
    OnboardingSurveyResponse, OnboardingSurveyCreate,
    SurveyQuestionResponse, SurveyQuestionCreate,
    SurveyResponseResponse, SurveyResponseCreate,
    PersonaProfileResponse, PersonaProfileCreate,
    OnboardingFlowResponse, OnboardingFlowCreate,
    FlowStepResponse, FlowStepCreate,
    UserOnboardingStatusResponse, UserOnboardingStatusUpdate,
    ProductTourResponse, ProductTourCreate,
    TourStepResponse, TourStepCreate,
    TourSessionResponse,
    OnboardingChecklistResponse, OnboardingChecklistCreate,
    OnboardingChecklistItemResponse, OnboardingChecklistItemCreate,
    UserChecklistProgressResponse, UserChecklistProgressUpdate,
    OnboardingRewardResponse, OnboardingRewardCreate,
    FeatureBeaconResponse, FeatureBeaconCreate,
    UserBeaconStateResponse,
)

router = APIRouter(prefix="/onboarding", tags=["User Onboarding & Adoption"])


# ======= Survey Endpoints =======

@router.post("/surveys", response_model=OnboardingSurveyResponse, status_code=status.HTTP_201_CREATED)
def create_survey(
    data: OnboardingSurveyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SurveyService(db)
    return service.create_survey(data)


@router.get("/surveys", response_model=List[OnboardingSurveyResponse])
def list_surveys(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SurveyService(db)
    return service.list_surveys(is_active)


@router.post("/surveys/{survey_id}/questions", response_model=SurveyQuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    survey_id: UUID,
    data: SurveyQuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SurveyService(db)
    data.survey_id = survey_id
    return service.create_question(data)


@router.post("/responses", response_model=SurveyResponseResponse, status_code=status.HTTP_201_CREATED)
def submit_response(
    data: SurveyResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SurveyService(db)
    return service.submit_response(current_user.id, data)


# ======= Persona Endpoints =======

@router.post("/persona", response_model=PersonaProfileResponse)
def upsert_persona(
    data: PersonaProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PersonaService(db)
    return service.upsert_persona(current_user.id, data)


# ======= Flow Endpoints =======

@router.post("/flows", response_model=OnboardingFlowResponse, status_code=status.HTTP_201_CREATED)
def create_flow(
    data: OnboardingFlowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FlowService(db)
    return service.create_flow(data)


@router.post("/flows/{flow_id}/steps", response_model=FlowStepResponse, status_code=status.HTTP_201_CREATED)
def create_flow_step(
    flow_id: UUID,
    data: FlowStepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FlowService(db)
    data.flow_id = flow_id
    return service.create_step(data)


@router.get("/status", response_model=UserOnboardingStatusResponse)
def get_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FlowService(db)
    status_obj = service.get_user_status(current_user.id)
    if not status_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    return status_obj


@router.patch("/status", response_model=UserOnboardingStatusResponse)
def update_status(
    data: UserOnboardingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FlowService(db)
    return service.update_user_status(current_user.id, data)


# ======= Tour Endpoints =======

@router.post("/tours", response_model=ProductTourResponse, status_code=status.HTTP_201_CREATED)
def create_tour(
    data: ProductTourCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TourService(db)
    return service.create_tour(data)


@router.post("/tours/{tour_id}/steps", response_model=TourStepResponse, status_code=status.HTTP_201_CREATED)
def create_tour_step(
    tour_id: UUID,
    data: TourStepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TourService(db)
    data.tour_id = tour_id
    return service.create_tour_step(data)


@router.post("/tours/{tour_id}/start", response_model=TourSessionResponse)
def start_tour(
    tour_id: UUID,
    db: Session = Depends(get_db),
    current_user_session: tuple = Depends(get_current_user_with_session),
):
    user, session_id = current_user_session
    service = TourService(db)
    try:
        return service.start_tour(user.id, session_id, tour_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/tours/{tour_id}/skip", response_model=TourSessionResponse)
def skip_tour(
    tour_id: UUID,
    db: Session = Depends(get_db),
    current_user_session: tuple = Depends(get_current_user_with_session),
):
    user, session_id = current_user_session
    service = TourService(db)
    try:
        return service.skip_tour(user.id, session_id, tour_id)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# ======= Checklist Endpoints =======

@router.post("/checklists", response_model=OnboardingChecklistResponse, status_code=status.HTTP_201_CREATED)
def create_checklist(
    data: OnboardingChecklistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChecklistService(db)
    return service.create_checklist(data)


@router.post("/checklists/{checklist_id}/items", response_model=OnboardingChecklistItemResponse, status_code=status.HTTP_201_CREATED)
def create_checklist_item(
    checklist_id: UUID,
    data: OnboardingChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChecklistService(db)
    data.checklist_id = checklist_id
    return service.create_item(data)


@router.patch("/checklist-progress", response_model=UserChecklistProgressResponse)
def update_checklist_progress(
    data: UserChecklistProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChecklistService(db)
    return service.update_progress(current_user.id, data)


@router.post("/rewards", response_model=OnboardingRewardResponse, status_code=status.HTTP_201_CREATED)
def create_reward(
    data: OnboardingRewardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChecklistService(db)
    return service.create_reward(data)


# ======= Feature Beacon Endpoints =======

@router.post("/beacons", response_model=FeatureBeaconResponse, status_code=status.HTTP_201_CREATED)
def create_beacon(
    data: FeatureBeaconCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FeatureBeaconService(db)
    return service.create_beacon(data)


@router.get("/beacons", response_model=List[FeatureBeaconResponse])
def list_beacons(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FeatureBeaconService(db)
    return service.list_beacons(is_active)


@router.post("/beacons/{beacon_id}/dismiss", response_model=UserBeaconStateResponse)
def dismiss_beacon(
    beacon_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FeatureBeaconService(db)
    return service.dismiss_beacon(current_user.id, beacon_id)
