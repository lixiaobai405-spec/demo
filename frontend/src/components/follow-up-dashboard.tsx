"use client";

import { useState } from "react";
import type { FollowUpPlan, FollowUpTaskItem, TaskUpdateRequest } from "@/lib/types";
import { updateFollowUpTask } from "@/lib/api";

const statusLabel: Record<string, string> = {
  pending: "待启动",
  in_progress: "进行中",
  completed: "已完成",
  blocked: "已阻塞",
};

const statusColor: Record<string, string> = {
  pending: "bg-slate-500/20 text-slate-300",
  in_progress: "bg-amber-500/20 text-amber-200",
  completed: "bg-emerald-500/20 text-emerald-200",
  blocked: "bg-rose-500/20 text-rose-200",
};

export function FollowUpDashboard({
  plan,
  assessmentId,
  onRefresh,
}: {
  plan: FollowUpPlan;
  assessmentId: string;
  onRefresh: () => void;
}) {
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);
  const [noteDraft, setNoteDraft] = useState("");
  const [updating, setUpdating] = useState(false);

  async function applyUpdate(task: FollowUpTaskItem, updates: TaskUpdateRequest) {
    setUpdating(true);
    try {
      await updateFollowUpTask(assessmentId, task.task_id, updates);
      onRefresh();
    } finally {
      setUpdating(false);
    }
  }

  async function handleQuickStatus(task: FollowUpTaskItem, status: TaskUpdateRequest["status"]) {
    await applyUpdate(task, { status });
  }

  async function handleSaveNote(task: FollowUpTaskItem) {
    if (!noteDraft.trim()) {
      setEditingTaskId(null);
      return;
    }
    await applyUpdate(task, { progress_note: noteDraft, status: "in_progress" });
    setEditingTaskId(null);
    setNoteDraft("");
  }

  async function handleToggleBlock(task: FollowUpTaskItem) {
    await applyUpdate(task, { blocked: !task.blocked, status: task.blocked ? task.status : "blocked" });
  }

  if (!plan.tasks.length) {
    return (
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-sm text-slate-400">
        尚未生成跟进任务，请先生成报告。
      </div>
    );
  }

  const progress = plan.overall_progress_pct;

  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            30-Day Follow-Up
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            课后 30 天跟进
          </h2>
        </div>
        <div className="flex items-center gap-4">
          <div>
            <p className="text-[10px] uppercase text-slate-500">整体进度</p>
            <div className="mt-1 flex items-center gap-2">
              <div className="h-2 w-28 overflow-hidden rounded-full bg-white/10">
                <div
                  className="h-full rounded-full bg-emerald-400 transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <span className="text-sm font-semibold text-white">{progress}%</span>
            </div>
          </div>
          <div className="flex gap-2 text-xs">
            <span className="text-emerald-300">{plan.completed_count} 完成</span>
            <span className="text-rose-300">{plan.blocked_count} 阻塞</span>
            <span className="text-slate-400">/ {plan.total_count} 项</span>
          </div>
        </div>
      </div>

      {plan.recalibration_note && (
        <div className="mt-4 rounded-2xl border border-cyan-300/15 bg-cyan-300/5 p-3">
          <p className="text-xs font-semibold text-cyan-100">最近复盘</p>
          <p className="mt-1 text-xs leading-5 text-slate-400">{plan.recalibration_note}</p>
        </div>
      )}

      <div className="mt-4 space-y-2">
        {plan.tasks.map((task) => (
          <div
            key={task.task_id}
            className={`rounded-2xl border p-4 transition ${
              task.status === "blocked"
                ? "border-rose-300/20 bg-rose-300/5"
                : task.status === "completed"
                  ? "border-emerald-300/10 bg-emerald-300/3"
                  : "border-white/8 bg-slate-950/45"
            }`}
          >
            <div className="flex flex-wrap items-start gap-3">
              {/* Left: status + period + action */}
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={`flex-shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium ${statusColor[task.status]}`}
                  >
                    {statusLabel[task.status]}
                  </span>
                  <span className="text-[10px] text-slate-500">{task.period}</span>
                  {task.blocked && (
                    <span className="text-[10px] text-rose-400">⚠ 已标记阻塞</span>
                  )}
                </div>
                <p className="mt-1.5 text-sm font-medium text-white">{task.action}</p>
                <div className="mt-1 flex flex-wrap gap-x-4 gap-y-0.5 text-[11px] text-slate-500">
                  <span>{task.owner_suggestion}</span>
                  <span>→ {task.deliverable}</span>
                </div>
                {task.progress_note && (
                  <div className="mt-2 rounded-xl border border-white/8 bg-slate-950/60 p-2">
                    <p className="text-xs leading-5 text-slate-300">
                      {task.progress_note}
                    </p>
                  </div>
                )}
                {task.blocker_description && (
                  <div className="mt-2 rounded-xl border border-rose-300/15 bg-rose-300/5 p-2">
                    <p className="text-xs leading-5 text-rose-200">
                      阻塞原因：{task.blocker_description}
                    </p>
                  </div>
                )}
              </div>

              {/* Right: actions */}
              <div className="flex flex-shrink-0 flex-wrap items-center gap-1.5">
                {editingTaskId === task.task_id ? (
                  <div className="flex items-center gap-1">
                    <input
                      className="w-40 rounded-xl border border-white/10 bg-white/5 px-2.5 py-1.5 text-xs text-white placeholder-slate-500"
                      placeholder="进展备注..."
                      value={noteDraft}
                      onChange={(e) => setNoteDraft(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleSaveNote(task);
                        if (e.key === "Escape") setEditingTaskId(null);
                      }}
                      autoFocus
                    />
                    <button
                      onClick={() => handleSaveNote(task)}
                      disabled={updating}
                      className="rounded-xl bg-emerald-500/20 px-2.5 py-1.5 text-[10px] text-emerald-200 hover:bg-emerald-500/30"
                    >
                      保存
                    </button>
                  </div>
                ) : (
                  <>
                    <button
                      onClick={() => handleQuickStatus(task, "completed")}
                      disabled={updating || task.status === "completed"}
                      className="rounded-xl bg-emerald-500/15 px-2 py-1 text-[10px] text-emerald-200 hover:bg-emerald-500/25 disabled:opacity-40"
                    >
                      ✓ 完成
                    </button>
                    <button
                      onClick={() => handleQuickStatus(task, "in_progress")}
                      disabled={updating || task.status === "completed"}
                      className="rounded-xl bg-amber-500/15 px-2 py-1 text-[10px] text-amber-200 hover:bg-amber-500/25 disabled:opacity-40"
                    >
                      启动
                    </button>
                    <button
                      onClick={() => {
                        setEditingTaskId(task.task_id);
                        setNoteDraft(task.progress_note || "");
                      }}
                      className="rounded-xl bg-white/10 px-2 py-1 text-[10px] text-slate-300 hover:bg-white/20"
                    >
                      备注
                    </button>
                    <button
                      onClick={() => handleToggleBlock(task)}
                      disabled={updating || task.status === "completed"}
                      className={`rounded-xl px-2 py-1 text-[10px] ${
                        task.blocked
                          ? "bg-rose-500/20 text-rose-200 hover:bg-rose-500/30"
                          : "bg-white/10 text-slate-400 hover:bg-rose-500/15 hover:text-rose-200"
                      } disabled:opacity-40`}
                    >
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
