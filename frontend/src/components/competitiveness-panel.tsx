"use client";

import type { CompetitivenessResponse } from "@/lib/types";

const barrierColor = (level: string): string => {
  if (level === "高") return "text-emerald-200 bg-emerald-300/15 border-emerald-300/25";
  if (level === "中") return "text-amber-200 bg-amber-300/15 border-amber-300/25";
  return "text-slate-300 bg-white/5 border-white/10";
};

export function CompetitivenessPanel({
  data,
}: {
  data: CompetitivenessResponse;
}) {
  const { result } = data;
  const { vp_reconstruction, connections, advantages, delivery_strategy, overall_narrative } =
    result;

  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Competitiveness Analysis
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            差异化竞争力分析
          </h2>
        </div>
        <span className="inline-flex rounded-full bg-amber-300/15 px-3 py-1 text-sm font-medium text-amber-100">
          规则分析
        </span>
      </div>

      {/* Overall Narrative */}
      <div className="mt-6 rounded-3xl border border-amber-300/20 bg-amber-300/5 p-5">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
          总体判断
        </p>
        <p className="mt-3 text-sm leading-7 text-slate-200">{overall_narrative}</p>
      </div>

      {/* VP Reconstruction */}
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-3xl border border-white/8 bg-slate-950/55 p-5">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
            当前价值主张
          </p>
          <p className="mt-3 text-sm leading-7 text-slate-300">
            {vp_reconstruction.current_vp}
          </p>
        </div>
        <div className="rounded-3xl border border-amber-300/20 bg-amber-300/5 p-5">
          <p className="text-xs uppercase tracking-[0.18em] text-amber-200">
            增强型价值主张
          </p>
          <p className="mt-3 text-sm leading-7 text-slate-200">
            {vp_reconstruction.enhanced_vp}
          </p>
        </div>
      </div>

      {/* Value Shift */}
      <div className="mt-4 rounded-3xl border border-white/8 bg-slate-950/55 p-5">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
          客户价值转移路径
        </p>
        <p className="mt-3 text-sm leading-7 text-slate-200">
          {vp_reconstruction.customer_value_shift}
        </p>
        {vp_reconstruction.differentiation_points.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {vp_reconstruction.differentiation_points.map((point) => (
              <span
                key={point}
                className="inline-flex rounded-full border border-amber-300/20 bg-amber-300/10 px-3 py-1.5 text-xs text-amber-100"
              >
                {point}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Point-to-Line Connections */}
      <div className="mt-6">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
          Point → Line 串联
        </p>
        <p className="mt-2 text-sm leading-7 text-slate-300">
          以下展示如何将选定的创新方向（点）串联为系统性竞争力线路：
        </p>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          {connections.map((conn) => (
            <div
              key={conn.line_name}
              className="rounded-3xl border border-white/8 bg-slate-950/55 p-5"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-white">
                  {conn.line_name}
                </span>
                <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] text-slate-400">
                  {conn.point_titles.length} 个方向
                </span>
              </div>
              <p className="mt-3 text-sm leading-7 text-slate-300">
                {conn.strategic_narrative}
              </p>
              <p className="mt-2 text-xs text-amber-200">
                竞争影响：{conn.competitive_impact}
              </p>
              {conn.point_titles.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {conn.point_titles.map((title) => (
                    <span
                      key={title}
                      className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[11px] text-slate-300"
                    >
                      {title}
                    </span>
                  ))}
                </div>
              )}
              {conn.key_metrics.length > 0 && (
                <div className="mt-3">
                  <p className="text-[11px] uppercase tracking-[0.15em] text-slate-500">
                    核心指标
                  </p>
                  <div className="mt-1.5 flex flex-wrap gap-1">
                    {conn.key_metrics.map((metric) => (
                      <span
                        key={metric}
                        className="rounded-full bg-emerald-300/10 px-2 py-0.5 text-[10px] text-emerald-200"
                      >
                        {metric}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Core Advantages */}
      <div className="mt-6">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
          核心优势
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {advantages.map((adv) => (
            <div
              key={adv.advantage_name}
              className="rounded-3xl border border-white/8 bg-slate-950/55 p-5"
            >
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm font-semibold text-white">
                  {adv.advantage_name}
                </p>
                <span
                  className={`inline-flex flex-shrink-0 rounded-full border px-2 py-0.5 text-[10px] ${barrierColor(adv.barrier_level)}`}
                >
                  壁垒{adv.barrier_level}
                </span>
              </div>
              <p className="mt-3 text-xs leading-5 text-slate-400">
                {adv.description}
              </p>
              {adv.source_elements.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {adv.source_elements.map((el) => (
                    <span
                      key={el}
                      className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] text-slate-400"
                    >
                      {el}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Delivery Strategy */}
      <div className="mt-6 rounded-3xl border border-white/8 bg-slate-950/55 p-5">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
          三阶段推进策略
        </p>
        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <PhaseCard
            title="Phase 1 — 快速验证"
            content={delivery_strategy.phase_1_quick_win}
          />
          <PhaseCard
            title="Phase 2 — 规模扩展"
            content={delivery_strategy.phase_2_scale}
          />
          <PhaseCard
            title="Phase 3 — 壁垒构建"
            content={delivery_strategy.phase_3_moat}
          />
        </div>
        {delivery_strategy.key_risks.length > 0 && (
          <div className="mt-4">
            <p className="text-xs uppercase tracking-[0.18em] text-rose-200">
              关键风险
            </p>
            <ul className="mt-2 space-y-1.5">
              {delivery_strategy.key_risks.map((risk) => (
                <li
                  key={risk}
                  className="flex items-start gap-2 text-xs leading-5 text-slate-400"
                >
                  <span className="mt-0.5 flex-shrink-0 text-rose-300">⚠</span>
                  {risk}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

function PhaseCard({
  title,
  content,
}: {
  title: string;
  content: string;
}) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <p className="text-xs font-semibold text-amber-100">{title}</p>
      <p className="mt-2 text-xs leading-5 text-slate-400">{content}</p>
    </div>
  );
}
