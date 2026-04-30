from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.push import PushCycleResult, RecalibratePlanRequest
from app.services.push_service import PushService

router = APIRouter(prefix="/api/assessments", tags=["push-recalibrate"])


@router.post(
    "/{assessment_id}/push",
    response_model=PushCycleResult,
    status_code=status.HTTP_200_OK,
)
def trigger_case_push(
    assessment_id: str,
    db: Session = Depends(get_db),
):
    from app.api.routes.assessments import (
        _get_assessment_or_404,
        _require_canvas,
        _require_scenarios,
    )

    assessment = _get_assessment_or_404(db, assessment_id)
    canvas = _require_canvas(db, assessment_id)
    scenarios = _require_scenarios(db, assessment_id)

    service = PushService()
    return service.get_next_push(db, assessment, canvas, scenarios)


@router.get(
    "/{assessment_id}/push/history",
    status_code=status.HTTP_200_OK,
)
def get_push_history(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> list[PushCycleResult]:
    service = PushService()
    return service.get_push_history(db, assessment_id)


@router.post(
    "/{assessment_id}/recalibrate",
    status_code=status.HTTP_200_OK,
)
def recalibrate_plan(
    assessment_id: str,
    payload: RecalibratePlanRequest,
    db: Session = Depends(get_db),
):
    service = PushService()
    result = service.recalibrate_plan(db, assessment_id, payload)
    return JSONResponse(content=result)
