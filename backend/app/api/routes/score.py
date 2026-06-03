from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.score import (
    ScoreCreateResponse,
    ScoreDetailResponse,
    ScoreExportFormat,
    ScoreSubmissionInput,
)
from app.services.score_service import ScoreService

router = APIRouter(prefix="/api/score", tags=["score"])


@router.post(
    "",
    response_model=ScoreCreateResponse,
    status_code=status.HTTP_200_OK,
)
async def create_score(
    name: str = Form(...),
    org: str = Form(...),
    report_type: str = Form(...),
    date: str = Form(...),
    note: str | None = Form(default=None),
    transcript: str = Form(default=""),
    pdf_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScoreCreateResponse:
    submission = ScoreSubmissionInput.model_validate(
        {
            "name": name,
            "org": org,
            "report_type": report_type,
            "date": date,
            "note": note,
            "transcript": transcript,
        }
    )
    return await ScoreService().create_score(
        db=db,
        current_user=current_user,
        submission=submission,
        pdf_file=pdf_file,
    )


@router.get(
    "/{score_id}",
    response_model=ScoreDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_score_detail(
    score_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScoreDetailResponse:
    service = ScoreService()
    record = service.get_score_or_404(db, score_id, current_user)
    return service.to_detail_response(record)


@router.get(
    "/{score_id}/export",
    status_code=status.HTTP_200_OK,
)
def export_score(
    score_id: str,
    format: ScoreExportFormat = Query(ScoreExportFormat.MARKDOWN),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    service = ScoreService()
    record = service.get_score_or_404(db, score_id, current_user)
    path, metadata = service.ensure_export(db, record, format)
    return FileResponse(
        path=path,
        media_type=metadata.media_type,
        filename=metadata.file_name,
    )
