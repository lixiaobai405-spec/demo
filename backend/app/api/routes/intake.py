from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.intake import (
    IntakeCreateAssessmentRequest,
    IntakeCreateAssessmentResponse,
    IntakeImportRequest,
    IntakeImportResponse,
    IntakeSessionDetailResponse,
)
from app.services.intake_service import IntakeService

router = APIRouter(prefix="/api/intake", tags=["intake"])


@router.post(
    "/import",
    response_model=IntakeImportResponse,
    status_code=status.HTTP_200_OK,
)
def import_intake_content(
    payload: IntakeImportRequest,
    auto_create: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IntakeImportResponse:
    service = IntakeService()
    result = service.import_content(db, payload, current_user=current_user)
    if auto_create:
        result = service._auto_create_assessment(db, result, current_user=current_user)
    return result


@router.post(
    "/import/file",
    response_model=IntakeImportResponse,
    status_code=status.HTTP_200_OK,
)
async def import_intake_file(
    file: UploadFile = File(...),
    auto_create: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IntakeImportResponse:
    service = IntakeService()
    result = await service.import_file(db, file, current_user=current_user)
    if auto_create:
        result = service._auto_create_assessment(db, result, current_user=current_user)
    return result


@router.get(
    "/import/{import_session_id}",
    response_model=IntakeSessionDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_import_session_detail(
    import_session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IntakeSessionDetailResponse:
    return IntakeService().get_session_detail(db, import_session_id, current_user=current_user)


@router.post(
    "/import/{import_session_id}/assessment",
    response_model=IntakeCreateAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment_from_import(
    import_session_id: str,
    payload: IntakeCreateAssessmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IntakeCreateAssessmentResponse:
    return IntakeService().create_assessment_from_session(
        db,
        import_session_id,
        payload,
        current_user=current_user,
    )
