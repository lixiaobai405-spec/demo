import Link from "next/link";
import type { ScenarioRecommendationResult } from "@/lib/types";

export function ScenarioRecommendationsPanel({
  assessmentId, readyForReport, scenarioRecommendation,
}: {
  assessmentId: string; readyForReport: boolean; scenarioRecommendation: ScenarioRecommendationResult;
}) {
  return (
    <div className="card-inset">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">场景推荐</p>
          <h2 className="section-heading">Top 3 AI 场景推荐</h2>
        </div>
        <span className="badge badge-warning">{scenarioRecommendation.scoring_method}</span>
      </div>

      <p className="mt-3 text-sm leading-7 text-warm-secondary">
        已按规则评分评估 {scenarioRecommendation.evaluated_count} 个候选场景，以下展示 Top 3。
      </p>

      {readyForReport ? (
        <div className="mt-5 flex flex-wrap gap-3">
          <Link href={`/report-context/${assessmentId}`} className="btn-secondary">查看报告上下文</Link>
          <Link href={`/report/${assessmentId}`} className="btn-primary">进入报告生成</Link>
        </div>
      ) : null}

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        {scenarioRecommendation.top_scenarios.map((item, index) => (
          <div key={item.scenario_id} className="rounded-xl border border-warm-border-light bg-warm-surface p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">Rank {index + 1}</p>
                <h3 className="mt-2 font-heading text-xl font-semibold text-warm-text">{item.name}</h3>
                <p className="mt-2 text-sm text-warm-accent">{item.category}</p>
              </div>
              <div className="rounded-lg bg-warm-success/10 px-4 py-2 text-center">
                <p className="text-xs uppercase tracking-[0.14em] text-warm-success">Score</p>
                <p className="mt-1 text-2xl font-semibold text-warm-text">{item.score}</p>
              </div>
            </div>
            <p className="mt-4 text-sm leading-7 text-warm-secondary">{item.summary}</p>
            <Section title="推荐理由" items={item.reasons} />
            <Section title="数据需求" items={item.data_requirements} />
          </div>
        ))}
      </div>
    </div>
  );
}

function Section({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="mt-5">
      <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">{title}</p>
      <ul className="mt-3 space-y-2">
        {items.map((item, i) => (
          <li key={`${title}-${i}`} className="rounded-lg bg-warm-inset px-4 py-3 text-sm text-warm-secondary">{item}</li>
        ))}
      </ul>
    </div>
  );
}
