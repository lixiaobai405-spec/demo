"""D3: Instructor Service — 讲师仪表盘 / 批量点评 / 成果导出"""
import json
from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.generated_report import GeneratedReport
from app.schemas.assessment import (
    BatchCommentRequest,
    BatchCommentResponse,
    InstructorDashboardResponse,
    InstructorExportResponse,
    StudentSummary,
)


class InstructorService:
    def get_dashboard(self, db: Session) -> InstructorDashboardResponse:
        assessments = db.query(Assessment).order_by(Assessment.created_at.desc()).all()
        students: list[StudentSummary] = []
        group_counts: dict[str, int] = defaultdict(int)

        for a in assessments:
            report = self._get_latest_report(db, a.id)
            student = StudentSummary(
                assessment_id=a.id,
                company_name=a.company_name,
                industry=a.industry,
                company_size=a.company_size,
                class_group=a.class_group,
                instructor_comment=a.instructor_comment,
                has_profile=bool(a.profile_payload),
                has_canvas=bool(a.profile_payload),
                has_breakthrough=False,
                has_directions=False,
                has_competitiveness=False,
                has_scenarios=False,
                has_cases=False,
                has_report=report is not None,
                ready_for_report=report is not None,
                canvas_score=None,
                report_id=report.id if report else None,
                created_at=a.created_at.isoformat() if a.created_at else None,
                updated_at=a.updated_at.isoformat() if a.updated_at else None,
            )

            group = a.class_group or "未分组"
            group_counts[group] += 1
            students.append(student)

        groups = sorted(group_counts.keys())
        completed = sum(1 for s in students if s.has_report)
        pct = int(completed / max(len(students), 1) * 100)

        return InstructorDashboardResponse(
            total_students=len(students),
            groups=groups,
            students=students,
            summary_by_group=dict(group_counts),
            overall_completion_pct=pct,
        )

    def batch_comment(
        self,
        db: Session,
        request: BatchCommentRequest,
    ) -> BatchCommentResponse:
        assessments = (
            db.query(Assessment)
            .filter(Assessment.id.in_(request.assessment_ids))
            .all()
        )
        for a in assessments:
            a.instructor_comment = request.comment
            db.add(a)
        db.commit()

        return BatchCommentResponse(
            updated_count=len(assessments),
            comment=request.comment,
        )

    def export_csv(self, db: Session) -> InstructorExportResponse:
        assessments = db.query(Assessment).order_by(Assessment.created_at.desc()).all()

        rows = [
            ["assessment_id", "company_name", "industry", "company_size",
             "class_group", "instructor_comment", "has_profile", "has_report",
             "created_at"]
        ]
        for a in assessments:
            report = self._get_latest_report(db, a.id)
            rows.append([
                a.id, a.company_name, a.industry, a.company_size,
                a.class_group or "", a.instructor_comment or "",
                "是" if a.profile_payload else "否",
                "是" if report else "否",
                a.created_at.isoformat() if a.created_at else "",
            ])

        csv_content = "\n".join(",".join(str(c) for c in row) for row in rows)
        return InstructorExportResponse(
            export_format="csv",
            content=csv_content,
            student_count=len(assessments),
        )

    @staticmethod
    def _get_latest_report(db: Session, assessment_id: str) -> GeneratedReport | None:
        return (
            db.query(GeneratedReport)
            .filter(GeneratedReport.assessment_id == assessment_id)
            .order_by(GeneratedReport.created_at.desc())
            .first()
        )
