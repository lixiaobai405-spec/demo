from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.assessment import ReportDocumentResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get(
    "/{report_id}",
    response_model=ReportDocumentResponse,
    status_code=status.HTTP_200_OK,
)
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
) -> ReportDocumentResponse:
    service = ReportService()
    record = service.get_report_or_404(db, report_id)
    return service.to_document_response(record)


@router.get(
    "/{report_id}/export/markdown",
    status_code=status.HTTP_200_OK,
)
def export_report_markdown(
    report_id: str,
    db: Session = Depends(get_db),
) -> FileResponse:
    service = ReportService()
    record = service.get_report_or_404(db, report_id)
    path = service.ensure_markdown_export(db, record)
    return FileResponse(
        path=path,
        media_type="text/markdown; charset=utf-8",
        filename=path.name,
    )


@router.get(
    "/{report_id}/export/docx",
    status_code=status.HTTP_200_OK,
)
def export_report_docx(
    report_id: str,
    db: Session = Depends(get_db),
) -> FileResponse:
    service = ReportService()
    record = service.get_report_or_404(db, report_id)
    path = service.ensure_docx_export(db, record)
    return FileResponse(
        path=path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=path.name,
    )


@router.get(
    "/{report_id}/print",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
def get_report_print_view(
    report_id: str,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    service = ReportService()
    record = service.get_report_or_404(db, report_id)
    return HTMLResponse(content=service.build_print_html(record))
