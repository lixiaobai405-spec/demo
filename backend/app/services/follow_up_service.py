"""D1: Follow-up service — 课后30天跟进任务管理"""
import json

from sqlalchemy.orm import Session

from app.models.follow_up import FollowUpTask
from app.schemas.follow_up import (
    DEFAULT_FOLLOW_UP_TASKS,
    FollowUpPlan,
    FollowUpTaskItem,
    TaskUpdateRequest,
)


class FollowUpService:
    TASK_STATUSES = ("pending", "in_progress", "completed", "blocked")

    def get_or_create_plan(self, db: Session, assessment_id: str) -> FollowUpPlan:
        existing = (
            db.query(FollowUpTask)
            .filter(FollowUpTask.assessment_id == assessment_id)
            .order_by(FollowUpTask.sort_order)
            .all()
        )

        if not existing:
            self._seed_default_tasks(db, assessment_id)
            existing = (
                db.query(FollowUpTask)
                .filter(FollowUpTask.assessment_id == assessment_id)
                .order_by(FollowUpTask.sort_order)
                .all()
            )

        tasks = [self._to_item(t) for t in existing]
        return self._build_plan(assessment_id, tasks)

    def update_task(
        self,
        db: Session,
        task_id: str,
        request: TaskUpdateRequest,
    ) -> FollowUpTaskItem | None:
        task = db.get(FollowUpTask, task_id)
        if task is None:
            return None

        changed = False
        if request.status is not None and request.status in self.TASK_STATUSES:
            task.status = request.status
            changed = True
        if request.progress_note is not None:
            task.progress_note = request.progress_note
            changed = True
        if request.blocked is not None:
            task.blocked = request.blocked
            if request.blocked and task.status != "blocked":
                task.status = "blocked"
            changed = True
        if request.blocker_description is not None:
            task.blocker_description = request.blocker_description
            changed = True

        if changed:
            from datetime import datetime, timezone
            task.last_reviewed_at = datetime.now(timezone.utc)
            db.add(task)
            db.commit()
            db.refresh(task)

        return self._to_item(task)

    def recalibrate(
        self,
        db: Session,
        assessment_id: str,
        note: str,
        updated_tasks: list[dict],
    ) -> FollowUpPlan:
        for ut in updated_tasks:
            task_id = ut.get("task_id")
            if not task_id:
                continue
            task = db.get(FollowUpTask, task_id)
            if task is None:
                continue
            if "action" in ut:
                task.action = ut["action"]
            if "owner_suggestion" in ut:
                task.owner_suggestion = ut["owner_suggestion"]
            if "deliverable" in ut:
                task.deliverable = ut["deliverable"]
            if "status" in ut and ut["status"] in self.TASK_STATUSES:
                task.status = ut["status"]
            if "blocked" in ut:
                task.blocked = ut["blocked"]
            if "blocker_description" in ut:
                task.blocker_description = ut["blocker_description"]
            db.add(task)

        db.commit()

        plan = self.get_or_create_plan(db, assessment_id)
        plan.recalibration_note = note
        return plan

    def _seed_default_tasks(self, db: Session, assessment_id: str) -> None:
        for i, task_data in enumerate(DEFAULT_FOLLOW_UP_TASKS):
            task = FollowUpTask(
                assessment_id=assessment_id,
                period=task_data["period"],
                action=task_data["action"],
                owner_suggestion=task_data["owner_suggestion"],
                deliverable=task_data["deliverable"],
                status="pending",
                blocked=False,
                sort_order=i,
            )
            db.add(task)
        db.commit()

    @staticmethod
    def _to_item(task: FollowUpTask) -> FollowUpTaskItem:
        return FollowUpTaskItem(
            task_id=task.id,
            period=task.period,
            action=task.action,
            owner_suggestion=task.owner_suggestion,
            deliverable=task.deliverable,
            status=task.status,
            progress_note=task.progress_note,
            blocked=task.blocked,
            blocker_description=task.blocker_description,
            sort_order=task.sort_order or 0,
            last_reviewed_at=task.last_reviewed_at,
        )

    @staticmethod
    def _build_plan(assessment_id: str, tasks: list[FollowUpTaskItem]) -> FollowUpPlan:
        completed = sum(1 for t in tasks if t.status == "completed")
        blocked = sum(1 for t in tasks if t.status == "blocked")
        total = max(len(tasks), 1)
        pct = int(completed / total * 100)

        return FollowUpPlan(
            assessment_id=assessment_id,
            tasks=tasks,
            overall_progress_pct=pct,
            completed_count=completed,
            blocked_count=blocked,
            total_count=len(tasks),
            next_review_date=None,
            recalibration_note=None,
        )
