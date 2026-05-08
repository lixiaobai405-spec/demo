"use client";

import { Button } from "@/components/ui/button";
import type { AssessmentProgress, AssessmentResponse } from "@/lib/types";

export function WorkflowSidebar({
  assessment,
  progress,
  hasProfile,
  hasCanvas,
  hasBreakthrough,
  hasScenarios,
  companyProfile,
  profileMode,
  canvasDiagnosis,
  breakthroughSelection,
  scenarioRecommendation,
  onGenerateProfile,
  onGenerateCanvas,
  onGenerateBreakthrough,
  onGenerateDirections,
  onGenerateScenarios,
  onGenerateCompetitiveness,
  onGenerateEndgame,
  isPendingProfile,
  isPendingCanvas,
  isPendingBreakthrough,
  isPendingDirections,
  isPendingScenarios,
  isPendingCompetitiveness,
  isPendingEndgame,
}: {
  assessment: AssessmentResponse | null;
  progress: AssessmentProgress;
  hasProfile: boolean;
  hasCanvas: boolean;
  hasBreakthrough: boolean;
  hasScenarios: boolean;
  companyProfile: unknown;
  profileMode: string | null;
  canvasDiagnosis: { overall_score?: number } | null;
  breakthroughSelection: { selected_elements: unknown[] } | null;
  scenarioRecommendation: { scoring_method?: string } | null;
  onGenerateProfile: () => void;
  onGenerateCanvas: () => void;
  onGenerateBreakthrough: () => void;
  onGenerateDirections: () => void;
  onGenerateScenarios: () => void;
  onGenerateCompetitiveness: () => void;
  onGenerateEndgame: () => void;
  isPendingProfile: boolean;
  isPendingCanvas: boolean;
  isPendingBreakthrough: boolean;
  isPendingDirections: boolean;
  isPendingScenarios: boolean;
  isPendingCompetitiveness: boolean;
  isPendingEndgame: boolean;
}) {
  return (
    <div className="flex flex-col gap-6">
      {/* Status */}
      <div className="card-inset">
        <p className="section-label">工作流</p>
        <h2 className="section-heading">当前状态</h2>
        <div className="mt-5 space-y-3">
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
        </div>
      </div>

      {/* Actions */}
      <div className="card">
        <p className="section-label">操作</p>
        <h2 className="section-heading">生成与回看</h2>
        <div className="mt-5 grid gap-3">
          <ActionBtn
            onClick={onGenerateProfile}
            disabled={!assessment || isPendingProfile}
            loading={isPendingProfile}
            hasResult={!!companyProfile}
            label="企业画像"
            color="success"
          />
          <ActionBtn
            onClick={onGenerateCanvas}
            disabled={!assessment || !hasProfile || isPendingCanvas}
            loading={isPendingCanvas}
            hasResult={!!canvasDiagnosis}
            label="商业画布"
            color="accent"
          />
          <ActionBtn
            onClick={onGenerateBreakthrough}
            disabled={!assessment || !hasCanvas || isPendingBreakthrough}
            loading={isPendingBreakthrough}
            hasResult={!!breakthroughSelection}
            label="突破要素推荐"
            color="warn"
          />
          <ActionBtn
            onClick={onGenerateDirections}
            disabled={!assessment || !hasCanvas || isPendingDirections}
            loading={isPendingDirections}
            hasResult={false}
            label="创新方向延展"
            color="accent"
          />
          <ActionBtn
            onClick={onGenerateScenarios}
            disabled={!assessment || !hasCanvas || isPendingScenarios}
            loading={isPendingScenarios}
            hasResult={!!scenarioRecommendation}
            label="Top 3 场景推荐"
            color="success"
          />
        </div>
        <div className="mt-3 grid gap-3">
          <ActionBtn
            onClick={onGenerateCompetitiveness}
            disabled={!assessment || !hasCanvas || isPendingCompetitiveness}
            loading={isPendingCompetitiveness}
            hasResult={false}
            label="差异化竞争力分析"
            color="warn"
          />
          <ActionBtn
            onClick={onGenerateEndgame}
            disabled={!assessment || !hasCanvas || isPendingEndgame}
            loading={isPendingEndgame}
            hasResult={false}
            label="商业终局设计"
            color="accent"
          />
        </div>
        <p className="mt-4 text-sm leading-7 text-muted-foreground">
          刷新页面后会自动从后端恢复当前 Assessment 状态。重新生成上游模块时，下游结果会被自动失效并需要重新生成。
        </p>
      </div>
    </div>
  );
}

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
