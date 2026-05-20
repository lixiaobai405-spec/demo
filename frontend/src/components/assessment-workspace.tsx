"use client";

import React from "react";
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { AssessmentFormSection } from "@/components/assessment-form-section";
import { IntakeImportSection } from "@/components/intake-import-section";
import { AssessmentSkeleton } from "@/components/assessment-skeleton";
import { ProgressStepper } from "@/components/progress-stepper";
import {
  WorkflowSidebar,
  type WorkflowModule,
} from "@/components/workflow-sidebar";
import {
  applyAssessmentDetailToStore,
  computeProgress,
  countPrefillFields,
  initialForm,
  initialProgress,
  mapAssessmentToForm,
  mergePrefillIntoForm,
} from "@/lib/assessment-utils";
import {
  buildAssessmentWorkflowState,
  type WorkflowDisplayState,
} from "@/lib/assessment-workflow-state";
import {
  getCompetitivenessResultPath,
  getResultsDashboardPath,
  getScenarioResultPath,
} from "@/lib/assessment-result-routes";
import { formatMutationError } from "@/lib/api";
import type { AssessmentCreateRequest, AssessmentProgress } from "@/lib/types";
import {
  useAssessmentDetail,
  useExpandDirections,
  useGenerateCanvas,
  useGenerateCompetitiveness,
  useGenerateEndgame,
  useGenerateProfile,
  useGenerateScenarios,
  useIntakeSession,
  useSelectDirections,
} from "@/hooks";
import { toast } from "@/hooks/use-toast";
import { useAssessmentStore } from "@/stores/assessment-store";

const SLOW_HINT_DELAY_MS = 5000;

function withSlowHint<T>(
  promise: Promise<T>,
  title: string,
  showToast: (msg: { title: string; description: string }) => void,
): Promise<T> {
  const timer = setTimeout(() => {
    showToast({
      title: "请稍候",
      description: `${title}，正在进行 AI 分析...`,
    });
  }, SLOW_HINT_DELAY_MS);

  return promise.finally(() => clearTimeout(timer));
}

type ResultCardItem = {
  key: string;
  label: string;
  state: WorkflowDisplayState;
  done: boolean;
  statusLabel: string;
  link?: string;
};

/**
 * 承载评估工作台主流程、状态卡和结果入口。
 */
export function AssessmentWorkspace({
  assessmentId,
  prefillSessionId,
}: {
  assessmentId?: string;
  prefillSessionId?: string;
}) {
  const router = useRouter();
  const store = useAssessmentStore();

  const [form, setForm] = useState<AssessmentCreateRequest>(initialForm);
  const [prefillSummary, setPrefillSummary] = useState<{
    importSessionId: string;
    mappedCount: number;
  } | null>(null);
  const [prefillError, setPrefillError] = useState<string | null>(null);
  const [appliedPrefillSessionId, setAppliedPrefillSessionId] = useState<
    string | null
  >(null);
  const [progress, setProgress] = useState<AssessmentProgress>(initialProgress);
  const [showImport, setShowImport] = useState(false);
  const [localPrefillSessionId, setLocalPrefillSessionId] = useState<
    string | null
  >(null);

  const effectivePrefillSessionId =
    !assessmentId
      ? (localPrefillSessionId ?? prefillSessionId ?? null)
      : null;

  const detailQuery = useAssessmentDetail(assessmentId);
  const prefillQuery = useIntakeSession(effectivePrefillSessionId);

  const generateProfile = useGenerateProfile();
  const generateCanvas = useGenerateCanvas();
  const expandDirections = useExpandDirections();
  const selectDirections = useSelectDirections();
  const generateScenarios = useGenerateScenarios();
  const generateCompetitiveness = useGenerateCompetitiveness();
  const generateEndgame = useGenerateEndgame();

  useEffect(() => {
    if (!detailQuery.data) return;

    applyAssessmentDetailToStore(detailQuery.data, store);
    setForm(mapAssessmentToForm(detailQuery.data.assessment));
    setProgress(detailQuery.data.progress);
    // store actions are stable Zustand references — including the store object
    // itself in deps would cause an infinite loop because useAssessmentStore()
    // returns a new merged object on every state change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [detailQuery.data]);

  useEffect(() => {
    if (
      assessmentId ||
      !prefillQuery.data ||
      appliedPrefillSessionId === prefillQuery.data.import_session_id
    ) {
      return;
    }

    setForm((current) =>
      mergePrefillIntoForm(current, prefillQuery.data.assessment_prefill),
    );
    setPrefillSummary({
      importSessionId: prefillQuery.data.import_session_id,
      mappedCount: countPrefillFields(prefillQuery.data.assessment_prefill),
    });
    setAppliedPrefillSessionId(prefillQuery.data.import_session_id);
  }, [appliedPrefillSessionId, assessmentId, prefillQuery.data]);

  const updateField = useCallback(
    (key: keyof AssessmentCreateRequest, value: string) => {
      setForm((current) => ({ ...current, [key]: value }));
    },
    [],
  );

  const handleResetForm = useCallback(() => {
    if (assessmentId) {
      router.push("/assessment");
      return;
    }

    setForm(initialForm);
    store.resetAll();
    setProgress(initialProgress);
    setPrefillSummary(null);
    setPrefillError(null);
  }, [assessmentId, router, store]);

  const handleGenerateProfile = useCallback(async () => {
    if (!store.assessment) return;

    try {
      const result = await withSlowHint(
        generateProfile.mutateAsync(store.assessment.id),
        "正在生成企业画像",
        toast,
      );

      store.setAssessment(result.assessment);
      store.setCompanyProfile(result.profile);
      store.setProfileMode(result.generation_mode);
      store.resetDownstream("profile");
      setProgress((prev) =>
        computeProgress({
          hasAssessment: true,
          hasProfile: true,
          hasCanvas: false,
          hasBreakthrough: false,
          hasDirections: false,
          hasCompetitiveness: false,
          hasScenarios: false,
          hasReport: false,
        }),
      );
      toast({
        title: "企业画像已生成",
        description: `模式：${result.generation_mode}`,
      });
      new BroadcastChannel("ai-chat-context").postMessage({
        type: "context-updated",
        assessmentId: store.assessment!.id,
      });
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "企业画像生成"),
        variant: "destructive",
      });
    }
  }, [generateProfile, store]);

  const handleGenerateCanvas = useCallback(async () => {
    if (!store.assessment) return;

    try {
      const result = await withSlowHint(
        generateCanvas.mutateAsync(store.assessment.id),
        "正在生成商业画布 9 格诊断",
        toast,
      );

      store.setAssessment(result.assessment);
      store.setCanvasDiagnosis(result.canvas_diagnosis);
      store.resetDownstream("canvas");
      setProgress((prev) =>
        computeProgress({
          hasAssessment: true,
          hasProfile: true,
          hasCanvas: true,
          hasBreakthrough: false,
          hasDirections: false,
          hasCompetitiveness: false,
          hasScenarios: false,
          hasReport: false,
        }),
      );
      toast({
        title: "商业画布已生成",
        description: "可查看薄弱模块与建议优先动作。",
      });
      new BroadcastChannel("ai-chat-context").postMessage({
        type: "context-updated",
        assessmentId: store.assessment!.id,
      });
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "商业画布生成"),
        variant: "destructive",
      });
    }
  }, [generateCanvas, store]);

  const handleGenerateBreakthrough = useCallback(async () => {
    if (!store.assessment) return;
    router.push(`/assessment/${store.assessment.id}/scoring`);
  }, [router, store.assessment]);

  const handleGenerateDirections = useCallback(async () => {
    if (!store.assessment) return;

    try {
      const result = await withSlowHint(
        expandDirections.mutateAsync(store.assessment.id),
        "正在延展创新方向",
        toast,
      );

      store.resetDownstream("directions");
      store.setDirectionData(result);
      setProgress((prev) =>
        computeProgress({
          hasAssessment: true,
          hasProfile: progress.has_profile,
          hasCanvas: progress.has_canvas,
          hasBreakthrough: progress.has_breakthrough,
          hasDirections: true,
          hasCompetitiveness: false,
          hasScenarios: false,
          hasReport: false,
        }),
      );
      toast({ title: "创新方向延展已生成" });
      new BroadcastChannel("ai-chat-context").postMessage({
        type: "context-updated",
        assessmentId: store.assessment!.id,
      });
      router.push(`/assessment/${store.assessment.id}/directions`);
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "创新方向延展生成"),
        variant: "destructive",
      });
    }
  }, [expandDirections, router, store]);

  const handleSelectDirections = useCallback(async () => {
    if (!store.assessment || store.selectedDirectionIds.length < 1) return;

    try {
      const result = await selectDirections.mutateAsync({
        assessmentId: store.assessment.id,
        payload: { selected_direction_ids: store.selectedDirectionIds },
      });

      store.setDirectionSelection(result);
      setProgress((prev) =>
        computeProgress({
          hasAssessment: true,
          hasProfile: progress.has_profile,
          hasCanvas: progress.has_canvas,
          hasBreakthrough: progress.has_breakthrough,
          hasDirections: true,
          hasCompetitiveness: false,
          hasScenarios: false,
          hasReport: false,
        }),
      );
      toast({ title: "创新方向已确认" });
      new BroadcastChannel("ai-chat-context").postMessage({
        type: "context-updated",
        assessmentId: store.assessment!.id,
      });
    } catch (error) {
      toast({
        title: "保存失败",
        description: formatMutationError(error, "创新方向保存"),
        variant: "destructive",
      });
    }
  }, [selectDirections, store]);

  const handleGenerateScenarios = useCallback(async () => {
    if (!store.assessment) return;

    try {
      const result = await withSlowHint(
        generateScenarios.mutateAsync(store.assessment.id),
        "正在生成 Top 3 AI 场景推荐",
        toast,
      );

      store.resetDownstream("scenarios");
      store.setAssessment(result.assessment);
      store.setScenarioRecommendation(result.scenario_recommendation);
      setProgress((prev) =>
        computeProgress({
          hasAssessment: true,
          hasProfile: progress.has_profile,
          hasCanvas: progress.has_canvas,
          hasBreakthrough: progress.has_breakthrough,
          hasDirections: progress.has_directions,
          hasCompetitiveness: false,
          hasScenarios: true,
          hasReport: false,
        }),
      );
      toast({ title: "场景推荐已生成" });
      new BroadcastChannel("ai-chat-context").postMessage({
        type: "context-updated",
        assessmentId: store.assessment!.id,
      });
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "场景推荐生成"),
        variant: "destructive",
      });
    }
  }, [generateScenarios, store]);

  const handleGenerateCompetitiveness = useCallback(async () => {
    if (!store.assessment) return;

    try {
      const result = await withSlowHint(
        generateCompetitiveness.mutateAsync(store.assessment.id),
        "正在分析差异化竞争力",
        toast,
      );

      store.resetDownstream("competitiveness");
      store.setCompetitivenessData(result);
      setProgress((prev) =>
        computeProgress({
          hasAssessment: true,
          hasProfile: progress.has_profile,
          hasCanvas: progress.has_canvas,
          hasBreakthrough: progress.has_breakthrough,
          hasDirections: progress.has_directions,
          hasCompetitiveness: true,
          hasScenarios: progress.has_scenarios,
          hasReport: false,
        }),
      );
      toast({ title: "差异化竞争力分析已生成" });
      new BroadcastChannel("ai-chat-context").postMessage({
        type: "context-updated",
        assessmentId: store.assessment!.id,
      });
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "差异化竞争力分析生成"),
        variant: "destructive",
      });
    }
  }, [generateCompetitiveness, store]);

  const handleGenerateEndgame = useCallback(async () => {
    if (!store.assessment) return;

    try {
      const result = await withSlowHint(
        generateEndgame.mutateAsync(store.assessment.id),
        "正在设计商业终局",
        toast,
      );

      store.setEndgameData(result);
      toast({ title: "商业终局设计已生成" });
      new BroadcastChannel("ai-chat-context").postMessage({
        type: "context-updated",
        assessmentId: store.assessment!.id,
      });
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "商业终局设计生成"),
        variant: "destructive",
      });
    }
  }, [generateEndgame, store]);

  const activeGenStep: number | null = generateProfile.isPending
    ? 2
    : generateCanvas.isPending
      ? 3
      : expandDirections.isPending || selectDirections.isPending
        ? 5
        : generateScenarios.isPending
          ? 6
          : generateCompetitiveness.isPending
            ? 7
            : null;

  if (detailQuery.isLoading) return <AssessmentSkeleton />;

  if (detailQuery.isError) {
    return (
      <div className="space-y-4 rounded-xl msg-error p-6 text-sm">
        <p>
          {detailQuery.error instanceof Error
            ? detailQuery.error.message
            : "Assessment 加载失败。"}
        </p>
        <button
          type="button"
          onClick={() => detailQuery.refetch()}
          className="btn-secondary text-xs"
        >
          重试加载
        </button>
      </div>
    );
  }

  const currentAssessment = store.assessment ?? null;
  const hasProfile = store.companyProfile !== null;
  const hasCanvas = store.canvasDiagnosis !== null;
  const hasBreakthrough =
    progress.has_breakthrough ||
    (store.breakthroughSelection !== null &&
      store.breakthroughSelection.selected_elements.length >= 2);
  const hasDirections =
    progress.has_directions ||
    store.directionData !== null ||
    store.directionSelection !== null;
  const hasCompetitiveness =
    progress.has_competitiveness || store.competitivenessData !== null;
  const hasScenarios = store.scenarioRecommendation !== null;
  const hasEndgame = store.endgameData !== null;
  const hasDashboard =
    progress.has_profile ||
    progress.has_canvas ||
    progress.has_breakthrough ||
    progress.has_directions ||
    progress.has_competitiveness ||
    progress.has_scenarios ||
    hasEndgame;

  const workflowState = buildAssessmentWorkflowState({
    assessmentId: currentAssessment?.id,
    hasAssessment: currentAssessment !== null,
    hasProfile,
    hasCanvas,
    hasBreakthroughSelection:
      store.breakthroughSelection !== null &&
      store.breakthroughSelection.selected_elements.length >= 2,
    hasDirectionDraft: store.directionData !== null,
    hasDirectionSelection: store.directionSelection !== null,
    hasScenarios,
    scenarioCount: store.scenarioRecommendation?.top_scenarios?.length ?? 0,
    hasCompetitiveness,
    hasEndgame,
    progress,
    profileMode: store.profileMode,
  });

  const workflowModules: WorkflowModule[] = currentAssessment
    ? workflowState.actionModules.map((module) => ({
        ...module,
        color:
          module.key === "profile" || module.key === "scenarios"
            ? "success"
            : module.key === "breakthrough" || module.key === "competitiveness"
              ? "warn"
              : "accent",
        disabled:
          module.disabled ||
          (module.key === "profile" && generateProfile.isPending) ||
          (module.key === "canvas" && generateCanvas.isPending) ||
          (module.key === "directions" && expandDirections.isPending) ||
          (module.key === "scenarios" && generateScenarios.isPending) ||
          (module.key === "competitiveness" &&
            generateCompetitiveness.isPending) ||
          (module.key === "endgame" && generateEndgame.isPending),
        loading:
          (module.key === "profile" && generateProfile.isPending) ||
          (module.key === "canvas" && generateCanvas.isPending) ||
          (module.key === "directions" && expandDirections.isPending) ||
          (module.key === "scenarios" && generateScenarios.isPending) ||
          (module.key === "competitiveness" &&
            generateCompetitiveness.isPending) ||
          (module.key === "endgame" && generateEndgame.isPending),
        onClick:
          module.key === "profile"
            ? handleGenerateProfile
            : module.key === "canvas"
              ? handleGenerateCanvas
              : module.key === "breakthrough"
                ? handleGenerateBreakthrough
                : module.key === "directions"
                  ? handleGenerateDirections
                  : module.key === "scenarios"
                    ? handleGenerateScenarios
                    : module.key === "competitiveness"
                      ? handleGenerateCompetitiveness
                      : handleGenerateEndgame,
      }))
    : [];

  const resultCards: ResultCardItem[] = currentAssessment
    ? workflowState.resultCards.map((card) => ({
        ...card,
        link: (() => {
          if (!card.isNavigable) return undefined;
          if (card.key === "profile") return `/assessment/${currentAssessment.id}/profile`;
          if (card.key === "canvas") return `/assessment/${currentAssessment.id}/canvas`;
          if (card.key === "breakthrough") return `/assessment/${currentAssessment.id}/scoring`;
          if (card.key === "directions") return `/assessment/${currentAssessment.id}/directions`;
          if (card.key === "scenarios") return getScenarioResultPath(currentAssessment.id);
          if (card.key === "competitiveness") {
            return getCompetitivenessResultPath(currentAssessment.id);
          }
          return `/assessment/${currentAssessment.id}/endgame`;
        })(),
      }))
    : [];

  return (
    <section className="flex flex-col gap-6">
      <div className="sticky top-0 z-10 -mx-6 bg-background/95 px-6 pb-4 backdrop-blur-sm">
        <ProgressStepper
          hasAssessment={currentAssessment !== null}
          progress={progress}
          activeStep={activeGenStep}
        />
      </div>

      {!assessmentId && !currentAssessment ? (
        <div className="card">
          <button
            type="button"
            onClick={() => setShowImport(!showImport)}
            className="flex w-full items-center justify-between text-left"
          >
            <div>
              <p className="section-label">可选步骤</p>
              <h2 className="section-heading">课前材料导入（可选）</h2>
            </div>
            <span className="text-sm text-muted-foreground">
              {showImport ? "收起 ▲" : "展开 ▼"}
            </span>
          </button>
          {showImport ? (
            <div className="mt-4">
              <IntakeImportSection onImported={setLocalPrefillSessionId} />
            </div>
          ) : null}
        </div>
      ) : null}

      <div
        className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]"
        id="section-assessment-form"
      >
        <AssessmentFormSection
          assessmentId={assessmentId}
          prefillSummary={prefillSummary}
          prefillError={prefillError}
          prefillFieldMeta={prefillQuery.data?.field_meta ?? null}
          form={form}
          onFormChange={updateField}
          assessment={currentAssessment}
          onReset={handleResetForm}
        />

        <WorkflowSidebar
          assessment={currentAssessment}
          progress={progress}
          companyProfile={store.companyProfile}
          profileMode={store.profileMode}
          canvasDiagnosis={store.canvasDiagnosis}
          breakthroughSelection={store.breakthroughSelection}
          scenarioRecommendation={store.scenarioRecommendation}
          modules={workflowModules}
        />
      </div>

      {currentAssessment ? (
        <>
          <div className="border-t border-warm-border-light pt-6">
            <p className="section-label">下一步</p>
            <h2 className="section-heading">继续生成分析结果</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              问卷已创建，你可以通过下方卡片进入各模块，或使用右侧工作流按钮逐步生成。
            </p>
          </div>

          <section
            id="section-profile-results"
            className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3"
          >
            {resultCards.map((card) => (
              <ResultCard
                key={card.key}
                label={card.label}
                state={card.state}
                done={card.done}
                statusLabel={card.statusLabel}
                link={card.link}
              />
            ))}
          </section>

          <section className="sm:max-w-md">
            <ResultCard
              label="结果仪表盘"
              state={hasDashboard ? "done" : "locked"}
              done={hasDashboard}
              statusLabel={hasDashboard ? "可查看" : "待生成"}
              link={
                hasDashboard
                  ? getResultsDashboardPath(currentAssessment.id)
                  : undefined
              }
              primary
            />
          </section>
        </>
      ) : null}

    </section>
  );
}

/**
 * 渲染工作台中的单个结果卡片。
 */
function ResultCard({
  label,
  state,
  done,
  statusLabel,
  link,
  primary,
}: {
  label: string;
  state: WorkflowDisplayState;
  done: boolean;
  statusLabel: string;
  link?: string;
  primary?: boolean;
}) {
  const isBright = state !== "locked";
  const content = (
    <div
      className={`rounded-xl border px-4 py-4 transition ${
        primary
          ? "border-warm-accent/30 bg-warm-accent/5 ring-1 ring-warm-accent/10"
          : isBright
            ? "border-warm-border-light bg-warm-surface"
            : "border-dashed border-warm-border bg-secondary/50"
      } ${link ? "cursor-pointer hover:-translate-y-px hover:shadow-md" : ""}`}
    >
      <div className="flex items-center justify-between gap-2">
        <p
          className={`text-sm font-medium ${
            done ? "text-warm-text" : "text-muted-foreground"
          }`}
        >
          {label}
        </p>
        <span
          className={`badge text-[10px] ${
            done
              ? primary
                ? "badge-accent"
                : "badge-success"
              : state === "pending-review" || state === "available"
                ? "badge-warning"
                : "badge-muted"
          }`}
        >
          {statusLabel}
        </span>
      </div>
    </div>
  );

  if (!link) return content;

  return (
    <Link href={link} target="_blank" rel="noopener noreferrer">
      {content}
    </Link>
  );
}
