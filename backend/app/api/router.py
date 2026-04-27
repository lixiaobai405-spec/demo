from fastapi import APIRouter

from app.api.routes.assessments import router as assessment_router
from app.api.routes.health import router as health_router
from app.api.routes.rag import router as rag_router
from app.api.routes.reports import router as report_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(assessment_router)
api_router.include_router(report_router)
api_router.include_router(rag_router)
