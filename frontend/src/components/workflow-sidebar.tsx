"use client";

import { Button } from "@/components/ui/button";
import type { AssessmentProgress, AssessmentResponse } from "@/lib/types";

export type WorkflowModule = {
  key: string;
  label: string;
  color: "accent" | "success" | "warn";
  disabled: boolean;
  loading: boolean;
  hasResult: boolean;
  onClick: () => void;
};

/** 工作流侧边栏，统一展示当前阶段状态与可执行操作。 */
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
  const hasProfile = progress.has_profile || Boolean(companyProfile);
  const hasCanvas = progress.has_canvas || Boolean(canvasDiagnosis);
  const hasBreakthrough =
    progress.has_breakthrough ||
    Boolean(
      breakthroughSelection &&
        breakthroughSelection.selected_elements.length > 0,
    );
  const hasScenarios =
    progress.has_scenarios || Boolean(scenarioRecommendation);

  return (
    <div className="flex flex-col gap-6">
      <div className="card-inset">
        <p className="section-label">工作流</p>
        <h2 className="section-heading">当前状态</h2>
        <div className="mt-6 space-y-3">
          <StepItem
            title="企业问卷"
            status={assessment ? "done" : "current"}
            description={assessment ? `问卷已创建：${assessment.id}` : "先录入企业信息并创建问卷。"}
          />
          <StepItem
            title="企业画像"
            status={progress.has_profile ? "done" : assessment ? "current" : "pending"}
            description={companyProfile ? `画像已存在，模式：${profileMode ?? "mock"}` : "尚未生成企业画像。"}
          />
          <StepItem
            title="商业画布诊断"
            status={progress.has_canvas ? "done" : hasProfile ? "current" : "pending"}
            description={canvasDiagnosis ? `已生成 9 格诊断，总体分：${canvasDiagnosis.overall_score}` : "尚未生成商业画布。"}
          />
          <StepItem
            title="突破要素选择"
            status={progress.has_breakthrough ? "done" : hasCanvas ? "current" : "pending"}
            description={breakthroughSelection ? `已选择 ${breakthroughSelection.selected_elements.length} 个要素` : "尚未选择突破要素。"}
          />
          <StepItem
            title="场景推荐"
            status={progress.has_scenarios ? "done" : hasBreakthrough ? "current" : "pending"}
            description={scenarioRecommendation ? `已生成 Top 3，评分方法：${scenarioRecommendation.scoring_method}` : "尚未生成 AI 场景推荐。"}
          />
          <StepItem
            title="报告草稿"
            status={progress.ready_for_report ? "current" : "pending"}
            description={progress.ready_for_report ? "上下文已齐备，可以进入报告草稿页。" : "需补齐画像、画布、突破要素和场景推荐后才可进入。"}
          />
          {modules
            .filter((module) =>
              ["directions", "competitiveness", "endgame"].includes(module.key),
            )
            .map((module) => (
              <StepItem
                key={module.key}
                title={module.label}
                status={module.loading ? "current" : module.hasResult ? "done" : module.disabled ? "pending" : "current"}
                description={getModuleDescription(module, {
                  canvasDiagnosis,
                  breakthroughSelection,
                  scenarioRecommendation,
                })}
              />
            ))}
        </div>
      </div>

      <div className="card">
        <p className="section-label">操作</p>
        <h2 className="section-heading">生成与回看</h2>
        <div className="mt-6 grid gap-3">
          {modules.length > 0 ? (
            modules.map((module) => (
              <ActionBtn
                key={module.key}
                onClick={module.onClick}
                disabled={!assessment || module.disabled}
                loading={module.loading}
                hasResult={module.hasResult}
                label={module.label}
                color={module.color}
              />
            ))
          ) : (
            <div className="rounded-xl border border-dashed border-warm-border bg-secondary/40 px-4 py-4 text-sm text-muted-foreground">
              请先创建企业问卷，随后这里会显示可执行的工作流操作。
            </div>
          )}
        </div>
        <p className="mt-4 text-sm leading-7 text-muted-foreground">
          刷新页面后会自动从后端恢复当前 Assessment 状态。重新生成上游模块时，下游结果会被自动失效并需要重新生成。
        </p>
      </div>
    </div>
  );
}

/** 根据模块阶段生成简短描述，帮助用户判断下一步操作。 */
function getModuleDescription(
  module: WorkflowModule,
  data: {
    canvasDiagnosis: { overall_score?: number } | null;
    breakthroughSelection: { selected_elements: unknown[] } | null;
    scenarioRecommendation: { scoring_method?: string } | null;
  },
) {
  switch (module.key) {
    case "directions":
      return module.hasResult
        ? "创新方向已生成，可进入方向选择页继续确认。"
        : module.disabled
          ? "需先完成商业画布诊断后才能继续。"
          : "可基于当前画布结果生成创新方向。";
    case "competitiveness":
      return module.hasResult
        ? "差异化竞争力分析结果已生成。"
        : module.disabled
          ? "需先完成商业画布诊断后才能继续。"
          : "可基于当前画布结果分析竞争力。";
    case "endgame":
      return module.hasResult
        ? "商业终局设计结果已生成。"
        : module.disabled
          ? "需先完成商业画布诊断后才能继续。"
          : "可基于当前画布结果设计商业终局。";
    case "canvas":
      return data.canvasDiagnosis
        ? `已生成 9 格诊断，总体分：${data.canvasDiagnosis.overall_score ?? "-"}`
        : "尚未生成商业画布。";
    case "breakthrough":
      return data.breakthroughSelection
        ? `已选择 ${data.breakthroughSelection.selected_elements.length} 个要素`
        : "尚未选择突破要素。";
    case "scenarios":
      return data.scenarioRecommendation
        ? `已生成场景推荐，评分方式：${data.scenarioRecommendation.scoring_method ?? "系统评分"}`
        : "尚未生成 AI 场景推荐。";
    default:
      return module.hasResult ? "该阶段已完成。" : "该阶段尚未完成。";
  }
}

/** 展示单个工作流步骤的状态与说明。 */
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
      <p className="font-medium text-sm">{title}</p>
      <p className="mt-1.5 text-sm leading-6 opacity-85">{description}</p>
    </div>
  );
}

/** 展示单个操作按钮，并根据状态给出文案。 */
function ActionBtn({
  onClick,
  disabled,
  loading,
  hasResult,
  label,
  color,
}: {
  onClick: () => void;
  disabled: boolean;
  loading: boolean;
  hasResult: boolean;
  label: string;
  color: "accent" | "success" | "warn";
}) {
  const variant = color === "success" ? "success" : color === "warn" ? "default" : "default";
  const verb = loading ? "生成中..." : hasResult ? `重新生成${label}` : `开始生成${label}`;

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
      {loading ? `${label}生成中...` : hasResult ? `重新生成${label}` : `生成${label}`}
    </Button>
  );
}
