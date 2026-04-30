"use client";

import type { EndgameResponse, StrategicPath } from "@/lib/types";

const pathTypeColor = (type: string) => {
  if (type === "保守") return "text-emerald-200 border-emerald-300/20 bg-emerald-300/5";
  if (type === "均衡") return "text-amber-200 border-amber-300/20 bg-amber-300/5";
  return "text-rose-200 border-rose-300/20 bg-rose-300/5";
};

const recLevelColor = (level: string) => {
  if (level === "推荐") return "bg-emerald-300/20 text-emerald-100 border-emerald-300/30";
  if (level === "可选") return "bg-amber-300/20 text-amber-100 border-amber-300/30";
  return "bg-slate-300/10 text-slate-300 border-white/10";
};

export function EndgamePanel({
  data,
}: {
  data: EndgameResponse;
}) {
  const { result } = data;
  const { private_domain, ecosystem, opc, strategic_paths, overall_narrative } = result;

  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Business Endgame Design
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            商业终局设计
          </h2>
        </div>
        <span className="inline-flex rounded-full bg-violet-300/15 px-3 py-1 text-sm font-medium text-violet-100">
          私域 + 生态 + OPC
        </span>
      </div>

      {/* Overall Narrative */}
      <div className="mt-5 rounded-3xl border border-violet-300/15 bg-violet-300/5 p-5">
        <p className="text-xs tracking-[0.18em] text-slate-400">总体判断</p>
        <div className="mt-3 space-y-2">
          {overall_narrative.split("\n").filter(Boolean).map((line, i) => (
            <p key={i} className="text-sm leading-6 text-slate-200">
              {line}
            </p>
          ))}
        </div>
      </div>

      {/* Three Pillars */}
      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        {/* Private Domain */}
        <div className="rounded-3xl border border-cyan-300/15 bg-cyan-300/5 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-100">
            私域
          </p>
          <p className="mt-3 text-xs font-medium text-white">
            {private_domain.target_model}
          </p>
          <div className="mt-3 space-y-1.5">
            {private_domain.key_strategies.map((s, i) => (
              <div key={i} className="flex items-start gap-1.5">
                <span className="mt-0.5 flex-shrink-0 text-[10px] text-cyan-300">
                  {i + 1}.
                </span>
                <p className="text-xs leading-4 text-slate-400">{s}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-2xl border border-white/8 bg-slate-950/50 p-3">
            <p className="text-[10px] uppercase text-slate-500">留存飞轮</p>
            <p className="mt-1 text-[11px] leading-4 text-slate-300">
              {private_domain.customer_retention_loop}
            </p>
          </div>
          <div className="mt-3 rounded-2xl border border-emerald-300/15 bg-emerald-300/5 p-3">
            <p className="text-[10px] uppercase text-emerald-200">收入影响</p>
            <p className="mt-1 text-[11px] leading-4 text-slate-300">
              {private_domain.revenue_impact}
            </p>
          </div>
          <p className="mt-3 text-[10px] uppercase text-slate-500">当前状态</p>
          <p className="mt-1 text-[11px] leading-4 text-slate-400">
            {private_domain.current_state}
          </p>
        </div>

        {/* Ecosystem */}
        <div className="rounded-3xl border border-amber-300/15 bg-amber-300/5 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-100">
            生态
          </p>
          <p className="mt-3 text-xs font-medium text-white">
            {ecosystem.ecosystem_positioning}
          </p>
          <div className="mt-3">
            <p className="text-[10px] uppercase text-slate-500">关键合作方</p>
            <div className="mt-1.5 flex flex-wrap gap-1">
              {ecosystem.key_partners_to_engage.map((p, i) => (
                <span
                  key={i}
                  className="rounded-full border border-amber-300/20 bg-amber-300/10 px-2 py-0.5 text-[10px] text-amber-100"
                >
                  {p}
                </span>
              ))}
            </div>
          </div>
          <div className="mt-4 rounded-2xl border border-white/8 bg-slate-950/50 p-3">
            <p className="text-[10px] uppercase text-slate-500">协作策略</p>
            <p className="mt-1 text-[11px] leading-4 text-slate-300">
              {ecosystem.orchestration_strategy}
            </p>
          </div>
          <div className="mt-3 rounded-2xl border border-amber-300/15 bg-amber-300/5 p-3">
            <p className="text-[10px] uppercase text-amber-200">平台效应</p>
            <p className="mt-1 text-[11px] leading-4 text-slate-300">
              {ecosystem.platform_effect}
            </p>
          </div>
        </div>

        {/* OPC */}
        <div className="rounded-3xl border border-emerald-300/15 bg-emerald-300/5 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-100">
            OPC
          </p>
          <div className="mt-3 space-y-3">
            <div>
              <p className="text-[10px] uppercase text-slate-500">O 卓越运营</p>
              <p className="mt-1 text-[11px] leading-4 text-slate-300">
                {opc.operations_excellence}
              </p>
            </div>
            <div>
              <p className="text-[10px] uppercase text-slate-500">P 平台能力</p>
              <p className="mt-1 text-[11px] leading-4 text-slate-300">
                {opc.platform_capability}
              </p>
            </div>
            <div>
              <p className="text-[10px] uppercase text-slate-500">C 内容与社群</p>
              <p className="mt-1 text-[11px] leading-4 text-slate-300">
                {opc.content_and_community}
              </p>
            </div>
          </div>
          <div className="mt-4 rounded-2xl border border-violet-300/15 bg-violet-300/5 p-3">
            <p className="text-[10px] uppercase text-violet-200">数据飞轮</p>
            <p className="mt-1 text-[11px] leading-4 text-slate-300">
              {opc.data_flywheel_effect}
            </p>
          </div>
        </div>
      </div>

      {/* Strategic Paths */}
      <div className="mt-5">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
          多路径推演（{strategic_paths.length} 种策略）
        </p>
        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          {strategic_paths.map((path, i) => (
            <StrategicPathCard key={i} path={path} />
          ))}
        </div>
      </div>
    </div>
  );
}

function StrategicPathCard({ path }: { path: StrategicPath }) {
  return (
    <div
      className={`rounded-3xl border p-5 ${pathTypeColor(path.path_type)}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-white">{path.path_name}</p>
          <p className="mt-0.5 text-[11px] text-slate-400">{path.timeline}</p>
        </div>
        <span
          className={`inline-flex flex-shrink-0 rounded-full border px-2 py-0.5 text-[10px] ${recLevelColor(path.recommendation_level)}`}
        >
          {path.recommendation_level}
        </span>
      </div>

      <div className="mt-3">
        <p className="text-[10px] uppercase text-slate-500">里程碑</p>
        <ul className="mt-1.5 space-y-1">
          {path.key_milestones.map((m, i) => (
            <li key={i} className="text-[11px] leading-4 text-slate-400">
              &bull; {m}
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-3">
        <p className="text-[10px] uppercase text-slate-500">投资需求</p>
        <p className="mt-1 text-[11px] leading-4 text-slate-300">
          {path.required_investments}
        </p>
      </div>

      <div className="mt-3">
        <p className="text-[10px] uppercase text-slate-500">预期成果</p>
        <p className="mt-1 text-[11px] leading-4 text-slate-200">
          {path.expected_outcomes}
        </p>
      </div>

      {path.major_risks.length > 0 && (
        <div className="mt-3">
          <p className="text-[10px] uppercase text-rose-200">主要风险</p>
          <ul className="mt-1.5 space-y-1">
            {path.major_risks.map((r, i) => (
              <li key={i} className="text-[10px] leading-4 text-slate-500">
                ⚠ {r}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
