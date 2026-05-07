import React from "react";

import type { AssessmentProgress } from "@/lib/types";

const stepLabels = [
  "企业问卷", "企业画像", "商业画布", "突破要素",
  "方向延展", "竞争力", "场景推荐", "案例匹配", "报告预览",
];

export function ProgressStepper({
  hasAssessment,
  progress,
}: {
  hasAssessment: boolean;
  progress: AssessmentProgress;
}) {
  const statuses: Array<"done" | "current" | "pending"> = [
    hasAssessment ? "done" : "current",
    progress.has_profile ? "done" : hasAssessment ? "current" : "pending",
    progress.has_canvas ? "done" : progress.has_profile ? "current" : "pending",
    progress.has_breakthrough ? "done" : progress.has_canvas ? "current" : "pending",
    progress.has_directions ? "done" : progress.has_breakthrough ? "current" : "pending",
    progress.has_competitiveness ? "done" : progress.has_directions ? "current" : "pending",
    progress.has_scenarios ? "done" : progress.has_competitiveness ? "current" : "pending",
    progress.has_cases ? "done" : progress.ready_for_report ? "current" : "pending",
    progress.has_report ? "done" : progress.has_cases ? "current" : "pending",
  ];

  return (
    <div className="grid gap-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-9">
      {stepLabels.map((label, index) => {
        const step = index + 1;
        const status = statuses[index];
        const colorCls =
          status === "current"
            ? `step-current-${step}`
            : status === "done"
              ? `step-done-${step}`
              : "step-pending";

        return (
          <div key={label} className={`rounded-xl border px-4 py-4 ${colorCls}`}>
            <p className="text-xs uppercase tracking-[0.16em] opacity-70">
              Step {step}
            </p>
            <p className="mt-2 text-sm font-medium">{label}</p>
          </div>
        );
      })}
    </div>
  );
}
