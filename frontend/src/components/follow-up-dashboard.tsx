"use client";

import { useState } from "react";
import type { FollowUpPlan, FollowUpTaskItem, TaskUpdateRequest } from "@/lib/types";
import { updateFollowUpTask } from "@/lib/api";

const statusLabel: Record<string, string> = {
  pending: "待启动", in_progress: "进行中", completed: "已完成", blocked: "已阻塞",
};

const statusColor: Record<string, string> = {
  pending: "badge-muted",
  in_progress: "badge-warning",
  completed: "badge-success",
  blocked: "badge-danger",
};

export function FollowUpDashboard({ plan, assessmentId, onRefresh }: {
  plan: FollowUpPlan; assessmentId: string; onRefresh: () => void;
}) {
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);
  const [noteDraft, setNoteDraft] = useState("");
  const [updating, setUpdating] = useState(false);

  async function applyUpdate(task: FollowUpTaskItem, updates: TaskUpdateRequest) {
    setUpdating(true);
    try { await updateFollowUpTask(assessmentId, task.task_id, updates); onRefresh(); }
    finally { setUpdating(false); }
  }

  async function handleQuickStatus(task: FollowUpTaskItem, status: TaskUpdateRequest["status"]) {
    await applyUpdate(task, { status });
  }

  async function handleSaveNote(task: FollowUpTaskItem) {
    if (!noteDraft.trim()) { setEditingTaskId(null); return; }
    await applyUpdate(task, { progress_note: noteDraft, status: "in_progress" });
    setEditingTaskId(null); setNoteDraft("");
  }

  async function handleToggleBlock(task: FollowUpTaskItem) {
    await applyUpdate(task, { blocked: !task.blocked, status: task.blocked ? task.status : "blocked" });
  }

  if (!plan.tasks.length) {
    return <div className="card text-sm text-warm-muted">尚未生成跟进任务，请先生成报告。</div>;
  }

  const progress = plan.overall_progress_pct;

  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">课后跟进</p>
          <h2 className="section-heading">课后 30 天跟进</h2>
        </div>
        <div className="flex items-center gap-4">
          <div>
            <p className="text-[10px] uppercase text-warm-muted">整体进度</p>
            <div className="mt-1 flex items-center gap-2">
              <div className="h-2 w-28 overflow-hidden rounded-full bg-warm-border-light">
                <div className="h-full rounded-full bg-warm-success transition-all" style={{ width: `${progress}%` }} />
              </div>
              <span className="text-sm font-semibold text-warm-text">{progress}%</span>
            </div>
          </div>
          <div className="flex gap-2 text-xs">
            <span className="text-warm-success">{plan.completed_count} 完成</span>
            <span className="text-warm-danger">{plan.blocked_count} 阻塞</span>
            <span className="text-warm-muted">/ {plan.total_count} 项</span>
          </div>
        </div>
      </div>

      {plan.recalibration_note && (
        <div className="mt-4 rounded-xl border border-warm-accent/15 bg-warm-accent/5 p-3">
          <p className="text-xs font-semibold text-warm-accent">最近复盘</p>
          <p className="mt-1 text-xs leading-5 text-warm-secondary">{plan.recalibration_note}</p>
        </div>
      )}

      <div className="mt-4 space-y-2">
        {plan.tasks.map((task) => (
          <div key={task.task_id}
            className={`rounded-xl border p-4 transition ${
              task.status === "blocked" ? "border-red-200 bg-red-50/40" :
              task.status === "completed" ? "border-green-200 bg-green-50/30" :
              "border-warm-border-light bg-warm-inset"
            }`}
          >
            <div className="flex flex-wrap items-start gap-3">
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`badge text-[10px] ${statusColor[task.status]}`}>{statusLabel[task.status]}</span>
                  <span className="text-[10px] text-warm-muted">{task.period}</span>
                  {task.blocked && <span className="text-[10px] text-warm-danger">⚠ 已标记阻塞</span>}
                </div>
                <p className="mt-1.5 text-sm font-medium text-warm-text">{task.action}</p>
                <div className="mt-1 flex flex-wrap gap-x-4 gap-y-0.5 text-[11px] text-warm-muted">
                  <span>{task.owner_suggestion}</span><span>→ {task.deliverable}</span>
                </div>
                {task.progress_note && (
                  <div className="mt-2 rounded-xl border border-warm-border-light bg-warm-surface p-2">
                    <p className="text-xs leading-5 text-warm-secondary">{task.progress_note}</p>
                  </div>
                )}
                {task.blocker_description && (
                  <div className="mt-2 rounded-xl border border-red-200 bg-red-50/40 p-2">
                    <p className="text-xs leading-5 text-warm-danger">阻塞原因：{task.blocker_description}</p>
                  </div>
                )}
              </div>

              <div className="flex flex-shrink-0 flex-wrap items-center gap-1.5">
                {editingTaskId === task.task_id ? (
                  <div className="flex items-center gap-1">
                    <input className="w-40 input-field text-xs py-1.5" placeholder="进展备注..." value={noteDraft}
                      onChange={(e) => setNoteDraft(e.target.value)}
                      onKeyDown={(e) => { if (e.key === "Enter") handleSaveNote(task); if (e.key === "Escape") setEditingTaskId(null); }} autoFocus />
                    <button onClick={() => handleSaveNote(task)} disabled={updating} className="rounded-xl bg-warm-success/15 px-2.5 py-1.5 text-[10px] text-warm-success hover:bg-warm-success/25">保存</button>
                  </div>
                ) : (
                  <>
                    <button onClick={() => handleQuickStatus(task, "completed")} disabled={updating || task.status === "completed"} className="rounded-xl bg-green-100 px-2 py-1 text-[10px] text-warm-success hover:bg-green-200 disabled:opacity-40">✓ 完成</button>
                    <button onClick={() => handleQuickStatus(task, "in_progress")} disabled={updating || task.status === "completed"} className="rounded-xl bg-amber-100 px-2 py-1 text-[10px] text-warm-warning hover:bg-amber-200 disabled:opacity-40">启动</button>
                    <button onClick={() => { setEditingTaskId(task.task_id); setNoteDraft(task.progress_note || ""); }} className="rounded-xl border border-warm-border px-2 py-1 text-[10px] text-warm-muted hover:bg-warm-surface">备注</button>
                    <button onClick={() => handleToggleBlock(task)} disabled={updating || task.status === "completed"}
                      className={`rounded-xl px-2 py-1 text-[10px] ${task.blocked ? "bg-red-100 text-warm-danger hover:bg-red-200" : "border border-warm-border text-warm-muted hover:bg-red-50 hover:text-warm-danger"} disabled:opacity-40`}>
                      {task.blocked ? "解除阻塞" : "标记阻塞"}
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
