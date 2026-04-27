import Link from "next/link";

import type { ScenarioRecommendationResult } from "@/lib/types";

export function ScenarioRecommendationsPanel({
  assessmentId,
  readyForReport,
  scenarioRecommendation,
}: {
  assessmentId: string;
  readyForReport: boolean;
  scenarioRecommendation: ScenarioRecommendationResult;
}) {
  return (
    <div className="rounded-[28px] border border-white/10 bg-slate-900/70 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Rule-Based AI Recommendations
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            Top 3 AI 场景推荐
          </h2>
        </div>

        <div className="rounded-full bg-amber-300/15 px-3 py-1 text-sm font-medium text-amber-100">
          {scenarioRecommendation.scoring_method}
        </div>
      </div>

      <p className="mt-4 text-sm leading-7 text-slate-300">
        已按规则评分评估 {scenarioRecommendation.evaluated_count} 个候选场景，以下展示 Top 3。
      </p>

      {readyForReport ? (
        <div className="mt-5 flex flex-wrap gap-3">
          <Link
            href={`/report-context/${assessmentId}`}
            className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-medium text-white transition hover:bg-white/10"
          >
            查看报告上下文
          </Link>
          <Link
            href={`/report/${assessmentId}`}
            className="inline-flex items-center justify-center rounded-full bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
          >
            进入报告生成
          </Link>
        </div>
      ) : null}

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        {scenarioRecommendation.top_scenarios.map((item, index) => (
          <div
            key={item.scenario_id}
            className="rounded-3xl border border-white/8 bg-white/5 p-5"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
                  Rank {index + 1}
                </p>
                <h3 className="mt-2 text-xl font-semibold text-white">
                  {item.name}
                </h3>
                <p className="mt-2 text-sm text-cyan-100">{item.category}</p>
              </div>

              <div className="rounded-2xl bg-emerald-300/15 px-4 py-2 text-center">
                <p className="text-xs uppercase tracking-[0.18em] text-emerald-100">
                  Score
                </p>
                <p className="mt-1 text-2xl font-semibold text-white">
                  {item.score}
                </p>
              </div>
            </div>

            <p className="mt-4 text-sm leading-7 text-slate-200">{item.summary}</p>

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
      <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
        {title}
      </p>
      <ul className="mt-3 space-y-2 text-sm leading-7 text-slate-200">
        {items.map((item, index) => (
          <li
            key={`${title}-${index}`}
            className="rounded-2xl bg-slate-950/55 px-4 py-3"
          >
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
