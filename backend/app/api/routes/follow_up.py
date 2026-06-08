from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes.assessments import _get_assessment_or_404, _require_paid_workflow_access
from app.db.session import get_db
from app.models.user import User
from app.schemas.follow_up import FollowUpPlan, RecalibrateRequest, TaskUpdateRequest
from app.services.follow_up_service import FollowUpService

router = APIRouter(prefix="/api/assessments", tags=["follow-up"])


@router.get(
    "/{assessment_id}/follow-up",
    response_model=FollowUpPlan,
    status_code=status.HTTP_200_OK,
)
def get_follow_up_plan(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FollowUpPlan:
    assessment = _get_assessment_or_404(db, assessment_id)
    _require_paid_workflow_access(db, assessment, current_user)
    service = FollowUpService()
    return service.get_or_create_plan(db, assessment_id)


@router.patch(
    "/{assessment_id}/follow-up/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
)
def update_follow_up_task(
    assessment_id: str,
    task_id: str,
    payload: TaskUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assessment = _get_assessment_or_404(db, assessment_id)
    _require_paid_workflow_access(db, assessment, current_user)
    service = FollowUpService()
    result = service.update_task(db, task_id, payload)
    if result is None:
        return JSONResponse(
            status_code=404,
            content={"detail": "Task not found."},
        )
    return result


@router.post(
    "/{assessment_id}/follow-up/recalibrate",
    status_code=status.HTTP_200_OK,
)
def recalibrate_follow_up(
    assessment_id: str,
    payload: RecalibrateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FollowUpPlan:
    assessment = _get_assessment_or_404(db, assessment_id)
    _require_paid_workflow_access(db, assessment, current_user)
    service = FollowUpService()
    return service.recalibrate(
        db, assessment_id, payload.note, payload.updated_tasks,
    )
