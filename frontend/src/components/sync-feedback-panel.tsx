"use client";

import { useState } from "react";
import { useAssessmentDetail } from "@/hooks";

type StepStatus = {
  label: string;
  key: string;
  exists: boolean;
  detail: string;
};

export function SyncFeedbackPanel({ assessmentId }: { assessmentId: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const detailQuery = useAssessmentDetail(assessmentId);
  const data = detailQuery.data;

  if (!data) return null;

  const { progress } = data;

  const steps: StepStatus[] = [
    {
      label: "企业画像",
      key: "profile",
      exists: progress.has_profile,
      detail: progress.has_profile ? "已生成" : "未生成",
    },
    {
      label: "商业画布",
      key: "canvas",
      exists: progress.has_canvas,
      detail: data.canvas_diagnosis
        ? `${data.canvas_diagnosis.canvas.blocks.length} 个模块, 评分 ${data.canvas_diagnosis.overall_score}`
        : "未生成",
    },
    {
      label: "突破要素",
      key: "breakthrough",
      exists: progress.has_breakthrough,
      detail: data.breakthrough_selection?.length
        ? `已选 ${data.breakthrough_selection.length} 个`
        : "未选择",
    },
    {
      label: "创新方向",
      key: "directions",
      exists: progress.has_directions,
      detail: data.direction_selection?.selected_directions?.length
        ? `已选 ${data.direction_selection.selected_directions.length} 个`
        : "未选择",
    },
    {
      label: "AI 场景",
      key: "scenarios",
      exists: progress.has_scenarios,
      detail: data.scenario_recommendation
        ? `Top ${data.scenario_recommendation.top_scenarios.length}`
        : "未生成",
    },
    {
      label: "差异化竞争力",
      key: "competitiveness",
      exists: progress.has_competitiveness,
      detail: progress.has_competitiveness ? "已生成" : "未生成",
    },
    {
      label: "商业终局",
      key: "endgame",
      exists: progress.ready_for_report && data.scenario_recommendation !== null,
      detail: progress.ready_for_report ? "已具备" : "未满足条件",
    },
  ];

  const readyCount = steps.filter((s) => s.exists).length;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {!isOpen ? (
        <button
          onClick={() => setIsOpen(true)}
          className="rounded-full bg-warm-accent text-white px-4 py-2 text-xs font-semibold shadow-lg hover:bg-warm-accent/90 transition"
        >
          🔍 {readyCount}/{steps.length}
        </button>
      ) : (
        <div className="w-80 rounded-xl border border-warm-border-light bg-warm-surface shadow-2xl">
          <div className="flex items-center justify-between p-4 border-b border-warm-border-light">
            <p className="text-sm font-semibold text-warm-text">
              同步状态 ({readyCount}/{steps.length})
            </p>
            <button
              onClick={() => setIsOpen(false)}
              className="text-xs text-muted-foreground hover:text-warm-text"
            >
              关闭
            </button>
          </div>
          <div className="p-4 space-y-2 max-h-96 overflow-y-auto">
            {steps.map((step) => (
              <div
                key={step.key}
                className={`flex items-center justify-between rounded-lg p-2 text-xs ${
                  step.exists
                    ? "bg-warm-success/10 border border-green-200"
                    : "bg-muted border border-warm-border-light"
                }`}
              >
                <div>
                  <p className={`font-medium ${step.exists ? "text-warm-success" : "text-muted-foreground"}`}>
                    {step.exists ? "✓" : "○"} {step.label}
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-0.5">{step.detail}</p>
                </div>
              </div>
            ))}
            <button
              onClick={() => detailQuery.refetch()}
              className="w-full mt-3 rounded-lg border border-warm-accent/30 bg-warm-accent/5 py-1.5 text-xs text-warm-accent hover:bg-warm-accent/10 transition"
            >
              刷新同步状态
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
