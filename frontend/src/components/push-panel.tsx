"use client";

import { useState } from "react";
import type { PushCycleResult, FollowUpPlan } from "@/lib/types";
import { triggerCasePush, recalibratePlan } from "@/lib/api";

export function PushPanel({
  assessmentId,
  onPlanRefresh,
}: {
  assessmentId: string;
  onPlanRefresh: () => void;
}) {
  const [pushResult, setPushResult] = useState<PushCycleResult | null>(null);
  const [isPushing, setIsPushing] = useState(false);
  const [pushError, setPushError] = useState<string | null>(null);

  const [recalNote, setRecalNote] = useState("");
  const [isRecalibrating, setIsRecalibrating] = useState(false);
  const [recalDone, setRecalDone] = useState<string | null>(null);
  const [selectedCompleteIds, setSelectedCompleteIds] = useState<Set<string>>(new Set());

  async function handlePush() {
    setPushError(null);
    setIsPushing(true);
    try {
      const result = await triggerCasePush(assessmentId);
      setPushResult(result);
    } catch (error) {
      setPushError(error instanceof Error ? error.message : "案例推送失败");
    } finally {
      setIsPushing(false);
    }
  }

  async function handleRecalibrate() {
    if (!recalNote.trim()) return;
    setIsRecalibrating(true);
    try {
      await recalibratePlan(assessmentId, {
        note: recalNote,
        new_actions: [],
        update_task_ids: Array.from(selectedCompleteIds),
      });
      setRecalDone(`已完成 ${selectedCompleteIds.size} 项任务，记录复盘心得。`);
      setRecalNote("");
      setSelectedCompleteIds(new Set());
      onPlanRefresh();
    } catch {
      setRecalDone("提交失败，请稍后重试。");
    } finally {
      setIsRecalibrating(false);
    }
  }

  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Bi-Weekly Push &amp; Recalibrate
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            双周案例推送与方案校准
          </h2>
        </div>
        <button
          type="button"
          onClick={handlePush}
          disabled={isPushing}
          className="inline-flex items-center rounded-full bg-indigo-300 px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-indigo-200 disabled:opacity-50"
        >
          {isPushing ? "推送中..." : "推送本期案例"}
        </button>
      </div>

      {pushError && (
        <div className="mt-3 text-sm text-rose-300">{pushError}</div>
      )}

      {pushResult && (
        <div className="mt-5 rounded-3xl border border-indigo-300/15 bg-indigo-300/5 p-5">
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-indigo-300/15 px-2.5 py-1 text-xs font-medium text-indigo-100">
              第 {pushResult.cycle} 轮 · 双周推送
            </span>
            <span className="text-xs text-slate-400">
              库中共 {pushResult.total_available} 个案例，已推送 {pushResult.previous_case_ids.length} 个
            </span>
          </div>
          <p className="mt-3 text-xs leading-5 text-slate-300">
            {pushResult.cycle_note}
          </p>

          {pushResult.pushed_cases.length > 0 && (
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {pushResult.pushed_cases.map((c) => (
                <div
                  key={c.case_id}
                  className="rounded-2xl border border-white/8 bg-slate-950/50 p-4"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-white truncate">
                        {c.title}
                      </p>
                      <p className="mt-0.5 text-[10px] text-slate-500">
                        {c.industry} · 匹配度 {c.fit_score}%
                      </p>
                    </div>
                  </div>
                  <p className="mt-2 text-xs leading-5 text-slate-400">
                    {c.summary}
                  </p>
                  {c.source_summary && (
                    <p className="mt-2 text-[10px] leading-4 text-indigo-200/70">
                      来源：{c.source_summary}
                    </p>
                  )}
                  {c.reference_points.length > 0 && (
                    <div className="mt-2">
                      <p className="text-[10px] uppercase text-slate-500">参考做法</p>
                      <ul className="mt-1 space-y-0.5">
                        {c.reference_points.slice(0, 2).map((r, i) => (
                          <li key={i} className="text-[10px] leading-4 text-slate-400">
                            &bull; {r}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {c.cautions.length > 0 && (
                    <div className="mt-2">
                      <p className="text-[10px] uppercase text-rose-300">注意事项</p>
                      <ul className="mt-1 space-y-0.5">
                        {c.cautions.slice(0, 2).map((w, i) => (
                          <li key={i} className="text-[10px] leading-4 text-rose-300/70">
                            ⚠ {w}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Recalibration section */}
      <div className="mt-6 rounded-3xl border border-white/8 bg-slate-950/45 p-5">
        <p className="text-xs font-semibold text-white">方案再校准</p>
        <p className="mt-1 text-xs leading-5 text-slate-400">
          根据新的案例学习调整跟进计划：选择已完成的任务、记录复盘心得。
        </p>

        <textarea
          className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-white placeholder-slate-500 resize-none"
          rows={3}
          placeholder="输入本次复盘心得（如：从XX案例中发现，我们的试点范围应该扩大...）"
          value={recalNote}
          onChange={(e) => setRecalNote(e.target.value)}
        />

        <div className="mt-3 flex items-center gap-3">
          <button
            type="button"
            onClick={handleRecalibrate}
            disabled={!recalNote.trim() || isRecalibrating}
            className="inline-flex items-center rounded-full bg-cyan-300 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:opacity-50"
          >
            {isRecalibrating ? "提交中..." : "提交复盘校准"}
          </button>
          {recalDone && (
            <span className="text-xs text-emerald-300">{recalDone}</span>
          )}
        </div>
      </div>
    </div>
  );
}
