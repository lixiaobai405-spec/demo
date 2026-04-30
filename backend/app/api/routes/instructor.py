from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.assessment import (
    BatchCommentRequest,
    BatchCommentResponse,
    InstructorDashboardResponse,
    InstructorExportResponse,
)
from app.services.instructor_service import InstructorService

router = APIRouter(prefix="/api/instructor", tags=["instructor"])


@router.get(
    "/dashboard",
    response_model=InstructorDashboardResponse,
    status_code=status.HTTP_200_OK,
)
def get_instructor_dashboard(
    db: Session = Depends(get_db),
) -> InstructorDashboardResponse:
    service = InstructorService()
    return service.get_dashboard(db)


@router.post(
    "/batch-comment",
    response_model=BatchCommentResponse,
    status_code=status.HTTP_200_OK,
)
def batch_comment(
    payload: BatchCommentRequest,
    db: Session = Depends(get_db),
) -> BatchCommentResponse:
    service = InstructorService()
    return service.batch_comment(db, payload)


@router.get(
    "/export",
    status_code=status.HTTP_200_OK,
)
def export_students(
    format: str = Query("csv", pattern="^(csv|json)$"),
    db: Session = Depends(get_db),
):
    service = InstructorService()
    if format == "csv":
        result = service.export_csv(db)
        return JSONResponse(content=result.model_dump())
    else:
        dashboard = service.get_dashboard(db)
        return JSONResponse(content=dashboard.model_dump())
