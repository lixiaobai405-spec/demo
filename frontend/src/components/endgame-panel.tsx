"use client";

import type { EndgameResponse, StrategicPath } from "@/lib/types";

const pathTypeColor = (type: string) => {
  if (type === "保守") return "border-green-200 bg-green-50/40";
  if (type === "均衡") return "border-amber-200 bg-amber-50/40";
  return "border-red-200 bg-red-50/40";
};

const recLevelColor = (level: string) => {
  if (level === "推荐") return "badge badge-success";
  if (level === "可选") return "badge badge-warning";
  return "badge badge-muted";
};

export function EndgamePanel({ data }: { data: EndgameResponse }) {
  const { result } = data;
  const { private_domain, ecosystem, opc, strategic_paths, overall_narrative } = result;

  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">商业终局</p>
          <h2 className="section-heading">商业终局设计</h2>
        </div>
        <span className="badge badge-accent">私域 + 生态 + OPC</span>
      </div>

      <div className="mt-5 rounded-xl border border-warm-accent/15 bg-warm-accent/5 p-5">
        <p className="text-xs tracking-[0.14em] text-warm-muted">总体判断</p>
        <div className="mt-3 space-y-2">
          {overall_narrative.split("\n").filter(Boolean).map((line, i) => (
            <p key={i} className="text-sm leading-6 text-warm-text">{line}</p>
          ))}
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        {/* Private Domain */}
        <div className="rounded-xl border border-warm-accent/15 bg-warm-accent/5 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-warm-accent">私域</p>
          <p className="mt-3 text-xs font-medium text-warm-text">{private_domain.target_model}</p>
          <div className="mt-3 space-y-1.5">
            {private_domain.key_strategies.map((s, i) => (
              <div key={i} className="flex items-start gap-1.5">
                <span className="mt-0.5 flex-shrink-0 text-[10px] text-warm-accent">{i + 1}.</span>
                <p className="text-xs leading-4 text-warm-muted">{s}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-lg border border-warm-border-light bg-warm-surface p-3">
            <p className="text-[10px] uppercase text-warm-muted">留存飞轮</p>
            <p className="mt-1 text-[11px] leading-4 text-warm-secondary">{private_domain.customer_retention_loop}</p>
          </div>
          <div className="mt-3 rounded-lg border border-green-200 bg-green-50/40 p-3">
            <p className="text-[10px] uppercase text-warm-success">收入影响</p>
            <p className="mt-1 text-[11px] leading-4 text-warm-secondary">{private_domain.revenue_impact}</p>
          </div>
          <p className="mt-3 text-[10px] uppercase text-warm-muted">当前状态</p>
          <p className="mt-1 text-[11px] leading-4 text-warm-muted">{private_domain.current_state}</p>
        </div>

        {/* Ecosystem */}
        <div className="rounded-xl border border-warm-warning/15 bg-warm-warning/5 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-warm-warning">生态</p>
          <p className="mt-3 text-xs font-medium text-warm-text">{ecosystem.ecosystem_positioning}</p>
          <div className="mt-3">
            <p className="text-[10px] uppercase text-warm-muted">关键合作方</p>
            <div className="mt-1.5 flex flex-wrap gap-1">
              {ecosystem.key_partners_to_engage.map((p, i) => (
                <span key={i} className="badge badge-warning text-xs">{p}</span>
              ))}
            </div>
          </div>
          <div className="mt-4 rounded-lg border border-warm-border-light bg-warm-surface p-3">
            <p className="text-[10px] uppercase text-warm-muted">协作策略</p>
            <p className="mt-1 text-[11px] leading-4 text-warm-secondary">{ecosystem.orchestration_strategy}</p>
          </div>
          <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50/40 p-3">
            <p className="text-[10px] uppercase text-warm-warning">平台效应</p>
            <p className="mt-1 text-[11px] leading-4 text-warm-secondary">{ecosystem.platform_effect}</p>
          </div>
        </div>

        {/* OPC */}
        <div className="rounded-xl border border-green-200 bg-green-50/30 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-warm-success">OPC</p>
          <div className="mt-3 space-y-3">
            <div>
              <p className="text-[10px] uppercase text-warm-muted">O 卓越运营</p>
              <p className="mt-1 text-[11px] leading-4 text-warm-secondary">{opc.operations_excellence}</p>
            </div>
            <div>
              <p className="text-[10px] uppercase text-warm-muted">P 平台能力</p>
              <p className="mt-1 text-[11px] leading-4 text-warm-secondary">{opc.platform_capability}</p>
            </div>
            <div>
              <p className="text-[10px] uppercase text-warm-muted">C 内容与社群</p>
              <p className="mt-1 text-[11px] leading-4 text-warm-secondary">{opc.content_and_community}</p>
            </div>
          </div>
          <div className="mt-4 rounded-lg border border-warm-accent/15 bg-warm-accent/5 p-3">
            <p className="text-[10px] uppercase text-warm-accent">数据飞轮</p>
            <p className="mt-1 text-[11px] leading-4 text-warm-secondary">{opc.data_flywheel_effect}</p>
          </div>
        </div>
      </div>

      <div className="mt-5">
        <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">多路径推演（{strategic_paths.length} 种策略）</p>
        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          {strategic_paths.map((path, i) => <StrategicPathCard key={i} path={path} />)}
        </div>
      </div>
    </div>
  );
}

function StrategicPathCard({ path }: { path: StrategicPath }) {
  return (
    <div className={`rounded-xl border p-5 ${pathTypeColor(path.path_type)}`}>
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-warm-text">{path.path_name}</p>
          <p className="mt-0.5 text-[11px] text-warm-muted">{path.timeline}</p>
        </div>
        <span className={recLevelColor(path.recommendation_level)}>{path.recommendation_level}</span>
      </div>
      <div className="mt-3">
        <p className="text-[10px] uppercase text-warm-muted">里程碑</p>
        <ul className="mt-1.5 space-y-1">
          {path.key_milestones.map((m, i) => <li key={i} className="text-[11px] leading-4 text-warm-muted">&bull; {m}</li>)}
        </ul>
      </div>
      <div className="mt-3">
        <p className="text-[10px] uppercase text-warm-muted">投资需求</p>
        <p className="mt-1 text-[11px] leading-4 text-warm-secondary">{path.required_investments}</p>
      </div>
      <div className="mt-3">
        <p className="text-[10px] uppercase text-warm-muted">预期成果</p>
        <p className="mt-1 text-[11px] leading-4 text-warm-text">{path.expected_outcomes}</p>
      </div>
      {path.major_risks.length > 0 && (
        <div className="mt-3">
          <p className="text-[10px] uppercase text-warm-danger">主要风险</p>
          <ul className="mt-1.5 space-y-1">
            {path.major_risks.map((r, i) => <li key={i} className="text-[10px] leading-4 text-warm-muted">⚠ {r}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
