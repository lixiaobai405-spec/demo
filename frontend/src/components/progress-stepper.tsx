import type { AssessmentProgress } from "@/lib/types";

const stepLabels = [
  "企业问卷",
  "企业画像",
  "商业画布",
  "场景推荐",
  "案例匹配",
  "报告预览",
];

export function ProgressStepper({
  hasAssessment,
  progress,
}: {
  hasAssessment: boolean;
  progress: AssessmentProgress;
}) {
  const statuses = [
    hasAssessment ? "done" : "current",
    progress.has_profile ? "done" : hasAssessment ? "current" : "pending",
    progress.has_canvas
      ? "done"
      : progress.has_profile
        ? "current"
        : "pending",
    progress.has_scenarios
      ? "done"
      : progress.has_canvas
        ? "current"
        : "pending",
    progress.has_cases
      ? "done"
      : progress.ready_for_report
        ? "current"
        : "pending",
    progress.has_report
      ? "done"
      : progress.has_cases
        ? "current"
        : "pending",
  ] as const;

  return (
    <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
      {stepLabels.map((label, index) => (
        <div
          key={label}
          className={`rounded-2xl border px-4 py-4 ${
            statuses[index] === "done"
              ? "border-emerald-300/25 bg-emerald-300/10 text-emerald-50"
              : statuses[index] === "current"
                ? "border-cyan-300/25 bg-cyan-300/10 text-cyan-50"
                : "border-white/10 bg-white/5 text-slate-300"
          }`}
        >
          <p className="text-xs uppercase tracking-[0.18em] opacity-80">
            Step {index + 1}
          </p>
          <p className="mt-2 text-sm font-medium">{label}</p>
        </div>
      ))}
    </div>
  );
}
