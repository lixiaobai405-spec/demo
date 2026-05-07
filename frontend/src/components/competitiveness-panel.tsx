"use client";

import type { CompetitivenessResponse } from "@/lib/types";

const barrierColor = (level: string): string => {
  if (level === "高") return "badge badge-success";
  if (level === "中") return "badge badge-warning";
  return "badge badge-muted";
};

export function CompetitivenessPanel({ data }: { data: CompetitivenessResponse }) {
  const { result } = data;
  const { vp_reconstruction, connections, advantages, delivery_strategy, overall_narrative } = result;

  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">竞争力分析</p>
          <h2 className="section-heading">差异化竞争力分析</h2>
        </div>
        <span className="badge badge-warning">规则分析</span>
      </div>

      <div className="mt-6 rounded-xl border border-warm-warning/15 bg-warm-warning/5 p-5">
        <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">总体判断</p>
        <p className="mt-3 text-sm leading-7 text-warm-text">{overall_narrative}</p>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-warm-border-light bg-warm-inset p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">当前价值主张</p>
          <p className="mt-3 text-sm leading-7 text-warm-secondary">{vp_reconstruction.current_vp}</p>
        </div>
        <div className="rounded-xl border border-warm-warning/15 bg-warm-warning/5 p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-warm-warning">增强型价值主张</p>
          <p className="mt-3 text-sm leading-7 text-warm-text">{vp_reconstruction.enhanced_vp}</p>
        </div>
      </div>

      <div className="mt-4 rounded-xl border border-warm-border-light bg-warm-inset p-5">
        <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">客户价值转移路径</p>
        <p className="mt-3 text-sm leading-7 text-warm-text">{vp_reconstruction.customer_value_shift}</p>
        {vp_reconstruction.differentiation_points.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {vp_reconstruction.differentiation_points.map((point) => (
              <span key={point} className="badge badge-warning">{point}</span>
            ))}
          </div>
        )}
      </div>

      <div className="mt-6">
        <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">Point → Line 串联</p>
        <p className="mt-2 text-sm leading-7 text-warm-secondary">以下展示如何将选定的创新方向（点）串联为系统性竞争力线路：</p>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          {connections.map((conn) => (
            <div key={conn.line_name} className="rounded-xl border border-warm-border-light bg-warm-inset p-5">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-warm-text">{conn.line_name}</span>
                <span className="badge badge-muted text-xs">{conn.point_titles.length} 个方向</span>
              </div>
              <p className="mt-3 text-sm leading-7 text-warm-secondary">{conn.strategic_narrative}</p>
              <p className="mt-2 text-xs text-warm-accent">竞争影响：{conn.competitive_impact}</p>
              {conn.point_titles.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {conn.point_titles.map((title) => <span key={title} className="badge badge-muted text-xs">{title}</span>)}
                </div>
              )}
              {conn.key_metrics.length > 0 && (
                <div className="mt-3">
                  <p className="text-[11px] uppercase tracking-[0.12em] text-warm-muted">核心指标</p>
                  <div className="mt-1.5 flex flex-wrap gap-1">
                    {conn.key_metrics.map((m) => <span key={m} className="rounded-full bg-warm-success/10 px-2 py-0.5 text-[10px] text-warm-success">{m}</span>)}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6">
        <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">核心优势</p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {advantages.map((adv) => (
            <div key={adv.advantage_name} className="rounded-xl border border-warm-border-light bg-warm-inset p-5">
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm font-semibold text-warm-text">{adv.advantage_name}</p>
                <span className={barrierColor(adv.barrier_level)}>壁垒{adv.barrier_level}</span>
              </div>
              <p className="mt-3 text-xs leading-5 text-warm-muted">{adv.description}</p>
              {adv.source_elements.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {adv.source_elements.map((el) => <span key={el} className="badge badge-muted text-xs">{el}</span>)}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-warm-border-light bg-warm-inset p-5">
        <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">三阶段推进策略</p>
        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <PhaseCard title="Phase 1 — 快速验证" content={delivery_strategy.phase_1_quick_win} />
          <PhaseCard title="Phase 2 — 规模扩展" content={delivery_strategy.phase_2_scale} />
          <PhaseCard title="Phase 3 — 壁垒构建" content={delivery_strategy.phase_3_moat} />
        </div>
        {delivery_strategy.key_risks.length > 0 && (
          <div className="mt-4">
            <p className="text-xs uppercase tracking-[0.14em] text-warm-danger">关键风险</p>
            <ul className="mt-2 space-y-1.5">
              {delivery_strategy.key_risks.map((risk) => (
                <li key={risk} className="flex items-start gap-2 text-xs leading-5 text-warm-muted">
                  <span className="mt-0.5 flex-shrink-0 text-warm-danger">⚠</span>{risk}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

function PhaseCard({ title, content }: { title: string; content: string }) {
  return (
    <div className="rounded-lg border border-warm-border-light bg-warm-surface p-4">
      <p className="text-xs font-semibold text-warm-accent">{title}</p>
      <p className="mt-2 text-xs leading-5 text-warm-muted">{content}</p>
    </div>
  );
}
