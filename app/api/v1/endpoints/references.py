from typing import Any, List
from fastapi import APIRouter, HTTPException
from app.core.referencer_loader import reference_loader

router = APIRouter()

@router.get("/project-priorities", response_model=List[dict])
def get_project_priorities() -> Any:
    """
    Fetch a list of project-priorities reference data.
    """
    priorities = reference_loader.get_project_priorities()
    if not priorities:
        # Fallback to default priorities if none are found
        raise HTTPException(status_code=404, detail="No project priorities found.")
    return priorities

@router.get("/project-status", response_model=List[dict])
def get_project_statuses() -> Any:
    """
    Fetch a list of project-status reference data.
    """
    status_list = reference_loader.get_project_statuses()
    if not status_list:
        # Fallback to default status if none are found
        raise HTTPException(status_code=404, detail="No project status found.")
    return status_list
