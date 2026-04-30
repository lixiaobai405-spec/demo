from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.assessment import ReportDocumentResponse
from app.services.report_enrichment import ReportEnrichmentService
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


@router.get(
    "/{report_id}/export/pdf",
    status_code=status.HTTP_200_OK,
)
def export_report_pdf(
    report_id: str,
    db: Session = Depends(get_db),
) -> FileResponse:
    service = ReportService()
    record = service.get_report_or_404(db, report_id)
    path = service.ensure_pdf_export(db, record)
    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=path.name,
    )


@router.get(
    "/{report_id}/enrich",
    status_code=status.HTTP_200_OK,
)
def get_report_enrichment(
    report_id: str,
    db: Session = Depends(get_db),
):
    service = ReportService()
    record = service.get_report_or_404(db, report_id)
    return JSONResponse(content=service.get_enrichment(record))


@router.get(
    "/{report_id}/quality",
    status_code=status.HTTP_200_OK,
)
def get_report_quality(
    report_id: str,
    db: Session = Depends(get_db),
):
    service = ReportService()
    record = service.get_report_or_404(db, report_id)
    return JSONResponse(content=service.get_quality_report(record))


@router.get(
    "/{report_id}/share/{token}",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
def view_shared_report(
    report_id: str,
    token: str,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    service = ReportService()
    record = service.get_report_or_404(db, report_id)
    share_token = getattr(record, "share_token", None)
    if not share_token or share_token != token:
        return HTMLResponse(
            content="<html><body><h2>无效的分享链接</h2><p>该报告分享链接已过期或不存在。</p></body></html>",
            status_code=404,
        )
    return HTMLResponse(content=service.build_print_html(record))


@router.post(
    "/{report_id}/share",
    status_code=status.HTTP_200_OK,
)
def create_share_link(
    report_id: str,
    db: Session = Depends(get_db),
):
    service = ReportService()
    record = service.get_report_or_404(db, report_id)
    token = service.generate_share_token(db, record)
    return JSONResponse(content={
        "share_url": f"/api/reports/{report_id}/share/{token}",
        "token": token,
    })
