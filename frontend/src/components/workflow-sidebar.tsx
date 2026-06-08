"use client";

import React from "react";

import { Button } from "@/components/ui/button";
import type { AssessmentWorkflowKey, WorkflowDisplayState } from "@/lib/assessment-workflow-state";
import type { AssessmentProgress, AssessmentResponse } from "@/lib/types";

export type WorkflowModule = {
  key: AssessmentWorkflowKey;
  label: string;
  color: "accent" | "success" | "warn";
  state: WorkflowDisplayState;
  disabled: boolean;
  loading: boolean;
  hasResult: boolean;
  onClick: () => void;
  paymentLocked?: boolean;
};

/**
 * 渲染工作流状态与主要操作按钮，统一隐藏总分文案。
 */
export function WorkflowSidebar({
  assessment,
  progress,
  companyProfile,
  profileMode,
  canvasDiagnosis,
  breakthroughSelection,
  scenarioRecommendation,
  modules,
}: {
  assessment: AssessmentResponse | null;
  progress: AssessmentProgress;
  companyProfile: unknown;
  profileMode: string | null;
  canvasDiagnosis: { overall_score?: number } | null;
  breakthroughSelection: { selected_elements: unknown[] } | null;
  scenarioRecommendation: { scoring_method?: string } | null;
  modules: WorkflowModule[];
}) {
  return (
    <div className="flex flex-col gap-6">
      <div className="card-inset">
        <p className="section-label">工作流</p>
        <h2 className="section-heading">当前状态</h2>
        <div className="mt-6 space-y-3">
          <StepItem
            title="企业问卷"
            status={assessment ? "done" : "current"}
            description={
              assessment
                ? `问卷已创建：${assessment.id}`
                : "先录入企业信息并创建问卷。"
            }
          />
          <StepItem
            title="企业画像"
            status={progress.has_profile ? "done" : assessment ? "current" : "pending"}
            description={
              companyProfile
                ? `画像已生成，模式：${profileMode ?? "mock"}`
                : "尚未生成企业画像。"
            }
          />
          <StepItem
            title="商业画布 9 格"
            status={progress.has_canvas ? "done" : progress.has_profile ? "current" : "pending"}
            description={
              canvasDiagnosis
                ? "已生成画布诊断，可查看薄弱模块与建议优先动作"
                : "尚未生成商业画布。"
            }
          />
          <StepItem
            title="BMC 突破要素评分"
            status={progress.has_breakthrough ? "done" : progress.has_canvas ? "current" : "pending"}
            description={
              breakthroughSelection
                ? `已确认 ${breakthroughSelection.selected_elements.length} 个突破要素`
                : "进入评分矩阵后完成突破要素确认。"
            }
          />
          <StepItem
            title="Top 3 AI 场景推荐"
            status={progress.has_scenarios ? "done" : progress.has_directions ? "current" : "pending"}
            description={
              scenarioRecommendation
                ? `已生成 Top 3，评分方式：${scenarioRecommendation.scoring_method ?? "rule"}`
                : "尚未生成场景推荐。"
            }
          />
          <StepItem
            title="报告准备"
            status={progress.ready_for_report ? "current" : "pending"}
            description={
              progress.ready_for_report
                ? "上下文已齐备，可以进入报告生成。"
                : "需补齐画像、画布、方向、场景、竞争力和终局后进入。"
            }
          />
        </div>
      </div>

      <div className="card">
        <p className="section-label">操作</p>
        <h2 className="section-heading">逐步生成</h2>
        <div className="mt-6 grid gap-3">
          {modules.map((module) => {
            const { key, ...actionProps } = module;
            return <ActionBtn key={key} {...actionProps} />;
          })}
        </div>
        <p className="mt-4 text-sm leading-7 text-muted-foreground">
          刷新页面后会自动从后端恢复当前 Assessment 状态。重新生成上游模块时，
          下游结果会自动失效并需要重新生成。
        </p>
      </div>
    </div>
  );
}

/**
 * 渲染工作流中的单个状态步骤。
 */
function StepItem({
  title,
  description,
  status,
}: {
  title: string;
  description: string;
  status: "pending" | "current" | "done";
}) {
  const cls =
    status === "done"
      ? "step-done"
      : status === "current"
        ? "step-current"
        : "step-pending";

  return (
    <div className={`rounded-xl border px-4 py-3 ${cls}`}>
      <p className="text-sm font-medium">{title}</p>
      <p className="mt-1.5 text-sm leading-6 opacity-85">{description}</p>
    </div>
  );
}

/**
 * 渲染工作流操作按钮。
 */
export function ActionBtn({
  onClick,
  disabled,
  loading,
  hasResult,
  label,
  color,
  state,
  paymentLocked = false,
}: WorkflowModule) {
  const variant =
    paymentLocked
      ? "outline"
      : color === "success"
        ? "success"
        : color === "warn"
          ? "default"
          : "default";
  const actionLabel =
    paymentLocked
      ? `解锁${label}`
      : state === "pending-review"
      ? `继续确认${label}`
      : loading
        ? `${label}生成中...`
        : hasResult
          ? `重新生成${label}`
          : `生成${label}`;

  return (
    <Button
      type="button"
      onClick={onClick}
      disabled={disabled}
      variant={variant}
      loading={loading}
      size="sm"
      className="w-full justify-start"
    >
      {actionLabel}
    </Button>
  );
}
