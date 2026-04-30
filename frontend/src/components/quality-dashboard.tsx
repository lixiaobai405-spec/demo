"use client";

import type { OverallQualityReport, QualityFlag } from "@/lib/types";

const confidenceColor = (level: string) => {
  if (level === "高") return "text-emerald-100 bg-emerald-300/15";
  if (level === "中") return "text-amber-100 bg-amber-300/15";
  return "text-rose-100 bg-rose-300/15";
};

const flagIcon = (level: string) => {
  if (level === "error") return "🔴";
  if (level === "warn") return "🟡";
  return "🔵";
};

export function QualityDashboard({
  data,
}: {
  data: OverallQualityReport;
}) {
  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Quality Dashboard
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            报告质量仪表盘
          </h2>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-right">
            <p className="text-[10px] uppercase tracking-[0.18em] text-slate-400">
              整体评分
            </p>
            <p className="text-2xl font-bold text-white">{data.overall_score}</p>
          </span>
          <span
            className={`inline-flex rounded-full px-3 py-1.5 text-sm font-medium ${confidenceColor(data.overall_confidence)}`}
          >
            {data.overall_confidence}
          </span>
        </div>
      </div>

      <p className="mt-4 text-sm leading-7 text-slate-300">{data.summary}</p>

      {data.critical_flags.length > 0 && (
        <div className="mt-4 rounded-2xl border border-rose-300/20 bg-rose-300/5 p-4">
          <p className="text-xs font-semibold text-rose-100">
            关键问题（{data.critical_flags.length}）
          </p>
          <ul className="mt-2 space-y-1.5">
            {data.critical_flags.map((flag, i) => (
              <FlagItem key={i} flag={flag} />
            ))}
          </ul>
        </div>
      )}

      <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {data.sections.map((section) => (
          <div
            key={section.section_key}
            className="rounded-2xl border border-white/8 bg-slate-950/45 p-3"
          >
            <div className="flex items-center justify-between gap-2">
              <p className="text-xs font-medium text-white truncate">
                {section.section_title}
              </p>
              <span
                className={`flex-shrink-0 rounded-full px-1.5 py-0.5 text-[10px] font-medium ${confidenceColor(section.confidence)}`}
              >
                {section.confidence}
              </span>
            </div>
            <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
              <span className="rounded-full bg-white/10 px-1.5 py-0.5 text-[9px] text-slate-400">
                {section.source}
              </span>
              {!section.has_actionable_content && (
                <span className="rounded-full border border-amber-300/20 bg-amber-300/10 px-1.5 py-0.5 text-[9px] text-amber-200">
                  待补充
                </span>
              )}
            </div>
            {section.flags.length > 0 && (
              <div className="mt-2 space-y-1">
                {section.flags.slice(0, 2).map((flag, i) => (
                  <FlagItem key={i} flag={flag} mini />
                ))}
                {section.flags.length > 2 && (
                  <p className="text-[9px] text-slate-500">
                    +{section.flags.length - 2} 个问题
                  </p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {data.improvement_suggestions.length > 0 && (
        <div className="mt-4 rounded-2xl border border-cyan-300/15 bg-cyan-300/5 p-4">
          <p className="text-xs font-semibold text-cyan-100">改进建议</p>
          <ul className="mt-2 space-y-1">
            {data.improvement_suggestions.map((s, i) => (
              <li key={i} className="text-xs leading-5 text-slate-400">
                &bull; {s}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function FlagItem({ flag, mini }: { flag: QualityFlag; mini?: boolean }) {
  return (
    <div className="flex items-start gap-1.5">
      <span className="mt-0.5 flex-shrink-0 text-[10px]">{flagIcon(flag.level)}</span>
      <p className={mini ? "text-[9px] leading-4 text-slate-400" : "text-xs leading-5 text-slate-300"}>
        {flag.message}
      </p>
    </div>
  );
}
