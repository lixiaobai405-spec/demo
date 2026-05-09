"use client";

import { useState } from "react";
import type { PushCycleResult } from "@/lib/types";
import { triggerCasePush, recalibratePlan } from "@/lib/api";

export function PushPanel({ assessmentId, onPlanRefresh }: { assessmentId: string; onPlanRefresh: () => void }) {
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
    try { const result = await triggerCasePush(assessmentId); setPushResult(result); }
    catch (error) { setPushError(error instanceof Error ? error.message : "案例推送失败"); }
    finally { setIsPushing(false); }
  }

  async function handleRecalibrate() {
    if (!recalNote.trim()) return;
    setIsRecalibrating(true);
    try {
      await recalibratePlan(assessmentId, { note: recalNote, new_actions: [], update_task_ids: Array.from(selectedCompleteIds) });
      setRecalDone(`已完成 ${selectedCompleteIds.size} 项任务，记录复盘心得。`);
      setRecalNote(""); setSelectedCompleteIds(new Set()); onPlanRefresh();
    } catch { setRecalDone("提交失败，请稍后重试。"); }
    finally { setIsRecalibrating(false); }
  }

  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">双周推送</p>
          <h2 className="section-heading">双周案例推送与方案校准</h2>
        </div>
        <button type="button" onClick={handlePush} disabled={isPushing} className="btn-primary text-sm">
          {isPushing ? "推送中..." : "推送本期案例"}
        </button>
      </div>

      {pushError && <div className="mt-3 text-sm text-warm-danger">{pushError}</div>}

      {pushResult && (
        <div className="mt-6 rounded-xl border border-warm-accent/15 bg-warm-accent/5 p-6">
          <div className="flex items-center gap-3">
            <span className="badge badge-accent">第 {pushResult.cycle} 轮 · 双周推送</span>
            <span className="text-xs text-warm-muted">库中共 {pushResult.total_available} 个案例，已推送 {pushResult.previous_case_ids.length} 个</span>
          </div>
          <p className="mt-3 text-xs leading-5 text-warm-secondary">{pushResult.cycle_note}</p>
          {pushResult.pushed_cases.length > 0 && (
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {pushResult.pushed_cases.map((c) => (
                <div key={c.case_id} className="rounded-xl border border-warm-border-light bg-warm-inset p-4">
                  <p className="text-sm font-medium text-warm-text truncate">{c.title}</p>
                  <p className="mt-0.5 text-xs text-warm-muted">{c.industry} · 匹配度 {c.fit_score}%</p>
                  <p className="mt-2 text-xs leading-5 text-warm-muted">{c.summary}</p>
                  {c.source_summary && <p className="mt-2 text-xs text-warm-accent">来源：{c.source_summary}</p>}
                  {c.reference_points.length > 0 && (
                    <div className="mt-2">
                      <p className="text-[10px] uppercase text-warm-muted">参考做法</p>
                      <ul className="mt-1 space-y-0.5">
                        {c.reference_points.slice(0, 2).map((r, i) => <li key={i} className="text-[10px] leading-4 text-warm-muted">&bull; {r}</li>)}
                      </ul>
                    </div>
                  )}
                  {c.cautions.length > 0 && (
                    <div className="mt-2">
                      <p className="text-[10px] uppercase text-warm-danger">注意事项</p>
                      <ul className="mt-1 space-y-0.5">
                        {c.cautions.slice(0, 2).map((w, i) => <li key={i} className="text-[10px] leading-4 text-warm-danger/80">⚠ {w}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="mt-6 rounded-xl border border-warm-border-light bg-warm-inset p-6">
        <p className="text-xs font-semibold text-warm-text">方案再校准</p>
        <p className="mt-1 text-xs leading-5 text-warm-muted">根据新的案例学习调整跟进计划：选择已完成的任务、记录复盘心得。</p>
        <textarea className="input-field mt-3" rows={3} placeholder="输入本次复盘心得（如：从XX案例中发现，我们的试点范围应该扩大...）" value={recalNote} onChange={(e) => setRecalNote(e.target.value)} />
        <div className="mt-3 flex items-center gap-3">
          <button type="button" onClick={handleRecalibrate} disabled={!recalNote.trim() || isRecalibrating} className="btn-primary text-sm">
            {isRecalibrating ? "提交中..." : "提交复盘校准"}
          </button>
          {recalDone && <span className="text-xs text-warm-success">{recalDone}</span>}
        </div>
      </div>
    </div>
  );
}
