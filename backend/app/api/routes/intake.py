from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
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
    db: Session = Depends(get_db),
) -> IntakeImportResponse:
    return IntakeService().import_content(db, payload)


@router.post(
    "/import/file",
    response_model=IntakeImportResponse,
    status_code=status.HTTP_200_OK,
)
async def import_intake_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> IntakeImportResponse:
    return await IntakeService().import_file(db, file)


@router.get(
    "/import/{import_session_id}",
    response_model=IntakeSessionDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_import_session_detail(
    import_session_id: str,
    db: Session = Depends(get_db),
) -> IntakeSessionDetailResponse:
    return IntakeService().get_session_detail(db, import_session_id)


@router.post(
    "/import/{import_session_id}/assessment",
    response_model=IntakeCreateAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment_from_import(
    import_session_id: str,
    payload: IntakeCreateAssessmentRequest,
    db: Session = Depends(get_db),
) -> IntakeCreateAssessmentResponse:
    return IntakeService().create_assessment_from_session(db, import_session_id, payload)
