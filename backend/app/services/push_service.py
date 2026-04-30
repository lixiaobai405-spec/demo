"""D2: Push Service — 双周案例推送 + 方案再校准"""
import json

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.follow_up import FollowUpTask
from app.models.push_record import PushRecord
from app.schemas.follow_up import DEFAULT_FOLLOW_UP_TASKS
from app.schemas.push import (
    PushCycleResult,
    PushedCase,
    RecalibrateActionItem,
    RecalibratePlanRequest,
    _build_cycle_note,
)
from app.services.case_matcher import load_case_library
from app.services.layered_retriever import LayeredRetriever


class PushService:
    def get_next_push(
        self,
        db: Session,
        assessment: Assessment,
        canvas_diagnosis,
        scenario_recommendation,
    ) -> PushCycleResult:
        library = load_case_library()
        all_cases = library.cases

        pushed_records = (
            db.query(PushRecord)
            .filter(PushRecord.assessment_id == assessment.id)
            .order_by(PushRecord.cycle.desc())
            .all()
        )

        seen_ids: set[str] = set()
        for pr in pushed_records:
            try:
                ids = json.loads(pr.case_ids_json)
                seen_ids.update(ids)
            except (json.JSONDecodeError, TypeError):
                pass

        next_cycle = (pushed_records[0].cycle + 1) if pushed_records else 1

        unseen_cases = [c for c in all_cases if c.id not in seen_ids]

        if not unseen_cases:
            unseen_cases = list(all_cases)
            seen_ids.clear()

        retriever = LayeredRetriever()
        layered_results = retriever.retrieve(
            unseen_cases,
            assessment,
            canvas_diagnosis,
            scenario_recommendation,
        )

        pushed_cases: list[PushedCase] = []
        case_ids_to_record: list[str] = []
        for lr in layered_results[:2]:
            pushed_cases.append(PushedCase(
                case_id=lr.case_id,
                title=lr.title,
                industry=lr.industry,
                summary=lr.summary,
                fit_score=int(lr.final_score),
                source_summary=lr.source_summary,
                reference_points=lr.reference_points,
                data_foundation=lr.data_foundation,
                cautions=lr.cautions,
            ))
            case_ids_to_record.append(lr.case_id)

        record = PushRecord(
            assessment_id=assessment.id,
            cycle=next_cycle,
            case_ids_json=json.dumps(case_ids_to_record, ensure_ascii=False),
            note=_build_cycle_note(next_cycle),
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return PushCycleResult(
            cycle=next_cycle,
            pushed_cases=pushed_cases,
            cycle_note=_build_cycle_note(next_cycle),
            pushed_at=record.pushed_at,
            previous_case_ids=sorted(seen_ids),
            total_available=len(all_cases),
        )

    def get_push_history(
        self,
        db: Session,
        assessment_id: str,
    ) -> list[PushCycleResult]:
        records = (
            db.query(PushRecord)
            .filter(PushRecord.assessment_id == assessment_id)
            .order_by(PushRecord.cycle.asc())
            .all()
        )

        results: list[PushCycleResult] = []
        for rec in records:
            try:
                case_ids = json.loads(rec.case_ids_json)
            except (json.JSONDecodeError, TypeError):
                case_ids = []

            results.append(PushCycleResult(
                cycle=rec.cycle,
                pushed_cases=[],
                cycle_note=rec.note or _build_cycle_note(rec.cycle),
                pushed_at=rec.pushed_at,
                previous_case_ids=case_ids,
                total_available=0,
            ))

        return results

    def recalibrate_plan(
        self,
        db: Session,
        assessment_id: str,
        request: RecalibratePlanRequest,
    ) -> dict:
        if request.update_task_ids:
            tasks_to_complete = (
                db.query(FollowUpTask)
                .filter(
                    FollowUpTask.assessment_id == assessment_id,
                    FollowUpTask.id.in_(request.update_task_ids),
                )
                .all()
            )
            for t in tasks_to_complete:
                t.status = "completed"
                from datetime import datetime, timezone
                t.last_reviewed_at = datetime.now(timezone.utc)
                db.add(t)

        for action in request.new_actions:
            max_sort = (
                db.query(FollowUpTask.sort_order)
                .filter(FollowUpTask.assessment_id == assessment_id)
                .order_by(FollowUpTask.sort_order.desc())
                .first()
            )
            next_sort = (max_sort[0] + 1) if max_sort else 0

            new_task = FollowUpTask(
                assessment_id=assessment_id,
                period=action.period or f"校准-第{next_sort + 1}项",
                action=action.action,
                owner_suggestion=action.owner_suggestion,
                deliverable=action.deliverable,
                status=action.status,
                blocked=False,
                sort_order=next_sort,
            )
            db.add(new_task)

        db.commit()

        return {
            "status": "ok",
            "note": request.note,
            "completed_tasks": len(request.update_task_ids),
            "new_actions": len(request.new_actions),
        }
