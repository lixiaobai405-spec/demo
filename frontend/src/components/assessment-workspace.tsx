"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAssessmentStore } from "@/stores/assessment-store";
import {
  useAssessmentDetail,
  useIntakeSession,
  useGenerateProfile,
  useGenerateCanvas,
  useRecommendBreakthrough,
  useSelectBreakthrough,
  useExpandDirections,
  useSelectDirections,
  useGenerateScenarios,
  useGenerateCompetitiveness,
  useGenerateEndgame,
} from "@/hooks";
import { toast } from "@/hooks/use-toast";
import { formatMutationError } from "@/lib/api";
import { AssessmentFormSection } from "@/components/assessment-form-section";
import { AssessmentSkeleton } from "@/components/assessment-skeleton";
import { WorkflowSidebar } from "@/components/workflow-sidebar";
import { ProgressStepper } from "@/components/progress-stepper";
import { BreakthroughSelectionPanel } from "@/components/breakthrough-selection-panel";
import { DirectionExpansionPanel } from "@/components/direction-expansion-panel";
import {
  initialForm,
  initialProgress,
  mapAssessmentToForm,
  mergePrefillIntoForm,
  countPrefillFields,
  computeProgress,
  applyAssessmentDetailToStore,
} from "@/lib/assessment-utils";
import type { AssessmentCreateRequest, AssessmentProgress } from "@/lib/types";

const SLOW_HINT_DELAY_MS = 5000;

function withSlowHint<T>(
  promise: Promise<T>,
  title: string,
  showToast: (msg: { title: string; description: string }) => void,
): Promise<T> {
  const timer = setTimeout(() => {
    showToast({
      title: "请耐心等待",
      description: `${title}，正在进行 AI 分析...`,
    });
  }, SLOW_HINT_DELAY_MS);
  return promise.finally(() => clearTimeout(timer));
}

export function AssessmentWorkspace({
  assessmentId,
  prefillSessionId,
}: {
  assessmentId?: string;
  prefillSessionId?: string;
}) {
  const router = useRouter();
  const store = useAssessmentStore();

  // --- Form state (local — needed for prefill merge + RHF integration point) ---
  const [form, setForm] = useState<AssessmentCreateRequest>(initialForm);
  const [prefillSummary, setPrefillSummary] = useState<{
    importSessionId: string;
    mappedCount: number;
  } | null>(null);
  const [prefillError, setPrefillError] = useState<string | null>(null);
  const [appliedPrefillSessionId, setAppliedPrefillSessionId] = useState<string | null>(null);
  const [progress, setProgress] = useState<AssessmentProgress>(initialProgress);

  // --- React Query: server state ---
  const detailQuery = useAssessmentDetail(assessmentId);
  const prefillQuery = useIntakeSession(!assessmentId && prefillSessionId ? prefillSessionId : null);

  // --- Mutations ---
  const generateProfile = useGenerateProfile();
  const generateCanvas = useGenerateCanvas();
  const recommendBreakthrough = useRecommendBreakthrough();
  const selectBreakthrough = useSelectBreakthrough();
  const expandDirections = useExpandDirections();
  const selectDirections = useSelectDirections();
  const generateScenarios = useGenerateScenarios();
  const generateCompetitiveness = useGenerateCompetitiveness();
  const generateEndgame = useGenerateEndgame();

  // --- Sync detail query data to store ---
  useEffect(() => {
    if (detailQuery.data) {
      applyAssessmentDetailToStore(detailQuery.data, store);
      setForm(mapAssessmentToForm(detailQuery.data.assessment));
      setProgress(detailQuery.data.progress);
    }
  }, [detailQuery.data]); // eslint-disable-line react-hooks/exhaustive-deps

  // --- Sync prefill data to form ---
  useEffect(() => {
    if (!assessmentId && prefillQuery.data && appliedPrefillSessionId !== prefillQuery.data.import_session_id) {
      setForm((current) => mergePrefillIntoForm(current, prefillQuery.data.assessment_prefill));
      setPrefillSummary({
        importSessionId: prefillQuery.data.import_session_id,
        mappedCount: countPrefillFields(prefillQuery.data.assessment_prefill),
      });
      setAppliedPrefillSessionId(prefillQuery.data.import_session_id);
    }
  }, [prefillQuery.data, assessmentId, appliedPrefillSessionId]);

  // --- Form helpers ---
  const updateField = useCallback((key: keyof AssessmentCreateRequest, value: string) => {
    setForm((current) => ({ ...current, [key]: value }));
  }, []);

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

  // --- Generation handlers ---
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
      setProgress(computeProgress({ hasAssessment: true, hasProfile: true, hasCanvas: false, hasScenarios: false }));
      toast({ title: "企业画像已生成", description: `模式：${result.generation_mode}` });
    } catch (e) {
      toast({ title: "生成失败", description: formatMutationError(e, "企业画像生成"), variant: "destructive" });
    }
  }, [store.assessment, generateProfile, store]);

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
      setProgress(computeProgress({ hasAssessment: true, hasProfile: true, hasCanvas: true, hasScenarios: false }));
      toast({ title: "商业画布已生成", description: `总体评分：${result.canvas_diagnosis.overall_score}` });
    } catch (e) {
      toast({ title: "生成失败", description: formatMutationError(e, "商业画布生成"), variant: "destructive" });
    }
  }, [store.assessment, generateCanvas, store]);

  const handleGenerateBreakthrough = useCallback(async () => {
    if (!store.assessment) return;
    try {
      const result = await withSlowHint(
        recommendBreakthrough.mutateAsync(store.assessment.id),
        "正在生成突破要素推荐",
        toast,
      );
      store.setBreakthroughData(result);
      if (result.breakthrough_selection && result.breakthrough_selection.selected_elements.length >= 2) {
        store.setBreakthroughSelection(result.breakthrough_selection);
        store.setSelectedBreakthroughKeys(result.breakthrough_selection.selected_elements.map((e) => e.key));
      } else {
        store.setBreakthroughSelection(null);
        store.setSelectedBreakthroughKeys(result.breakthrough_recommendation.recommended_keys);
      }
      toast({ title: "突破要素推荐已生成" });
    } catch (e) {
      toast({ title: "生成失败", description: formatMutationError(e, "突破要素推荐生成"), variant: "destructive" });
    }
  }, [store.assessment, recommendBreakthrough, store]);

  const handleSelectBreakthrough = useCallback(async () => {
    if (!store.assessment || store.selectedBreakthroughKeys.length < 2) return;
    try {
      const result = await selectBreakthrough.mutateAsync({
        assessmentId: store.assessment.id,
        payload: { selected_keys: store.selectedBreakthroughKeys, selection_mode: "system_recommended" },
      });
      store.setBreakthroughSelection(result);
      setProgress(computeProgress({
        hasAssessment: true,
        hasProfile: store.companyProfile !== null,
        hasCanvas: store.canvasDiagnosis !== null,
        hasBreakthrough: true,
        hasScenarios: store.scenarioRecommendation !== null,
      }));
      toast({ title: "突破要素已保存" });

      // Fire directions(+chain competitiveness+endgame) || scenarios in parallel
      Promise.allSettled([
        (async () => {
          try {
            const dResult = await withSlowHint(
              expandDirections.mutateAsync(store.assessment!.id),
              "正在延展创新方向",
              toast,
            );
            store.setDirectionData(dResult);
            if (dResult.direction_selection && dResult.direction_selection.selected_directions.length > 0) {
              store.setDirectionSelection(dResult.direction_selection);
              store.setSelectedDirectionIds(dResult.direction_selection.selected_directions.map((d) => d.direction_id));
            }
            toast({ title: "创新方向延展已生成" });

            // Chain: competitiveness after directions complete (needs selected_directions)
            try {
              const cResult = await withSlowHint(
                generateCompetitiveness.mutateAsync(store.assessment!.id),
                "正在分析差异化竞争力",
                toast,
              );
              store.setCompetitivenessData(cResult);
              toast({ title: "竞争力分析已生成" });

              // Chain: endgame after competitiveness (takes optional competitiveness result)
              try {
                const eResult = await withSlowHint(
                  generateEndgame.mutateAsync(store.assessment!.id),
                  "正在设计商业终局",
                  toast,
                );
                store.setEndgameData(eResult);
                toast({ title: "商业终局分析已生成" });
              } catch (e) {
                toast({ title: "生成失败", description: formatMutationError(e, "商业终局分析生成"), variant: "destructive" });
              }
            } catch (e) {
              toast({ title: "生成失败", description: formatMutationError(e, "竞争力分析生成"), variant: "destructive" });
            }
          } catch (e) {
            toast({ title: "生成失败", description: formatMutationError(e, "创新方向延展生成"), variant: "destructive" });
          }
        })(),
        (async () => {
          try {
            const sResult = await withSlowHint(
              generateScenarios.mutateAsync(store.assessment!.id),
              "正在匹配 AI 场景推荐",
              toast,
            );
            store.setAssessment(sResult.assessment);
            store.setScenarioRecommendation(sResult.scenario_recommendation);
            setProgress((prev) => computeProgress({
              hasAssessment: true,
              hasProfile: store.companyProfile !== null,
              hasCanvas: store.canvasDiagnosis !== null,
              hasBreakthrough: true,
              hasScenarios: true,
            }));
            toast({ title: "场景推荐已生成" });
          } catch (e) {
            toast({ title: "生成失败", description: formatMutationError(e, "场景推荐生成"), variant: "destructive" });
          }
        })(),
      ]);
    } catch (e) {
      toast({ title: "保存失败", description: formatMutationError(e, "突破要素保存"), variant: "destructive" });
    }
  }, [store, selectBreakthrough, expandDirections, generateScenarios]);

  const handleGenerateDirections = useCallback(async () => {
    if (!store.assessment) return;
    try {
      const result = await withSlowHint(
        expandDirections.mutateAsync(store.assessment.id),
        "正在延展创新方向",
        toast,
      );
      store.setDirectionData(result);
      if (result.direction_selection && result.direction_selection.selected_directions.length > 0) {
        store.setDirectionSelection(result.direction_selection);
        store.setSelectedDirectionIds(result.direction_selection.selected_directions.map((d) => d.direction_id));
      } else {
        store.setDirectionSelection(null);
        store.setSelectedDirectionIds([]);
      }
      toast({ title: "创新方向延展已生成" });
    } catch (e) {
      toast({ title: "生成失败", description: formatMutationError(e, "创新方向延展生成"), variant: "destructive" });
    }
  }, [store.assessment, expandDirections, store]);

  const handleSelectDirections = useCallback(async () => {
    if (!store.assessment || store.selectedDirectionIds.length < 1) return;
    try {
      const result = await selectDirections.mutateAsync({
        assessmentId: store.assessment.id,
        payload: { selected_direction_ids: store.selectedDirectionIds },
      });
      store.setDirectionSelection(result);
      toast({ title: "方向选择已保存" });
    } catch (e) {
      toast({ title: "保存失败", description: formatMutationError(e, "方向选择保存"), variant: "destructive" });
    }
  }, [store, selectDirections]);

  const handleGenerateScenarios = useCallback(async () => {
    if (!store.assessment) return;
    try {
      const result = await withSlowHint(
        generateScenarios.mutateAsync(store.assessment.id),
        "正在匹配 AI 场景推荐",
        toast,
      );
      store.setAssessment(result.assessment);
      store.setScenarioRecommendation(result.scenario_recommendation);
      setProgress(computeProgress({
        hasAssessment: true,
        hasProfile: store.companyProfile !== null,
        hasCanvas: store.canvasDiagnosis !== null,
        hasBreakthrough: store.breakthroughSelection !== null,
        hasScenarios: true,
      }));
      toast({ title: "场景推荐已生成" });
    } catch (e) {
      toast({ title: "生成失败", description: formatMutationError(e, "场景推荐生成"), variant: "destructive" });
    }
  }, [store.assessment, generateScenarios, store]);

  const handleGenerateCompetitiveness = useCallback(async () => {
    if (!store.assessment) return;
    try {
      const result = await withSlowHint(
        generateCompetitiveness.mutateAsync(store.assessment.id),
        "正在分析差异化竞争力",
        toast,
      );
      store.setCompetitivenessData(result);
      toast({ title: "竞争力分析已生成" });
    } catch (e) {
      toast({ title: "生成失败", description: formatMutationError(e, "竞争力分析生成"), variant: "destructive" });
    }
  }, [store.assessment, generateCompetitiveness, store]);

  const handleGenerateEndgame = useCallback(async () => {
    if (!store.assessment) return;
    try {
      const result = await withSlowHint(
        generateEndgame.mutateAsync(store.assessment.id),
        "正在设计商业终局",
        toast,
      );
      store.setEndgameData(result);
      toast({ title: "商业终局分析已生成" });
    } catch (e) {
      toast({ title: "生成失败", description: formatMutationError(e, "商业终局分析生成"), variant: "destructive" });
    }
  }, [store.assessment, generateEndgame, store]);

  // --- Which step is currently generating? (for stepper pulse) ---
  const activeGenStep: number | null =
    generateProfile.isPending ? 2 :
    generateCanvas.isPending ? 3 :
    recommendBreakthrough.isPending || selectBreakthrough.isPending ? 4 :
    expandDirections.isPending || selectDirections.isPending ? 5 :
    generateCompetitiveness.isPending ? 6 :
    generateScenarios.isPending ? 7 :
    null;

  // --- Loading / Error states ---
  if (detailQuery.isLoading) return <AssessmentSkeleton />;
  if (detailQuery.isError) {
    return (
      <div className="rounded-xl msg-error p-6 text-sm space-y-4">
        <p>{detailQuery.error instanceof Error ? detailQuery.error.message : "Assessment 加载失败。"}</p>
        <button type="button" onClick={() => detailQuery.refetch()} className="btn-secondary text-xs">
          重试加载
        </button>
      </div>
    );
  }

  const currentAssessment = store.assessment || null;
  const hasProfile = store.companyProfile !== null;
  const hasCanvas = store.canvasDiagnosis !== null;
  const hasBreakthrough = store.breakthroughSelection !== null && store.breakthroughSelection.selected_elements.length >= 2;
  const hasScenarios = store.scenarioRecommendation !== null;

  return (
    <section className="flex flex-col gap-6">
      <ProgressStepper hasAssessment={currentAssessment !== null} progress={progress} activeStep={activeGenStep} />

      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]" id="section-assessment-form">
        <AssessmentFormSection
          assessmentId={assessmentId}
          prefillSummary={prefillSummary}
          prefillError={prefillError}
          form={form}
          onFormChange={updateField}
          assessment={currentAssessment}
          onReset={handleResetForm}
        />

        <WorkflowSidebar
          assessment={currentAssessment}
          progress={progress}
          hasProfile={hasProfile}
          hasCanvas={hasCanvas}
          hasBreakthrough={hasBreakthrough}
          hasScenarios={hasScenarios}
          companyProfile={store.companyProfile}
          profileMode={store.profileMode}
          canvasDiagnosis={store.canvasDiagnosis}
          breakthroughSelection={store.breakthroughSelection}
          scenarioRecommendation={store.scenarioRecommendation}
          onGenerateProfile={handleGenerateProfile}
          onGenerateCanvas={handleGenerateCanvas}
          onGenerateBreakthrough={handleGenerateBreakthrough}
          onGenerateDirections={handleGenerateDirections}
          onGenerateScenarios={handleGenerateScenarios}
          onGenerateCompetitiveness={handleGenerateCompetitiveness}
          onGenerateEndgame={handleGenerateEndgame}
          isPendingProfile={generateProfile.isPending}
          isPendingCanvas={generateCanvas.isPending}
          isPendingBreakthrough={recommendBreakthrough.isPending}
          isPendingDirections={expandDirections.isPending}
          isPendingScenarios={generateScenarios.isPending}
          isPendingCompetitiveness={generateCompetitiveness.isPending}
          isPendingEndgame={generateEndgame.isPending}
        />
      </div>

      {/* ── Result cards: compact status + links to full pages ── */}
      {currentAssessment && (
        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <ResultCard
            label="企业画像"
            done={hasProfile}
            mode={store.profileMode}
            link={
              hasProfile
                ? `/assessment/${currentAssessment.id}/profile`
                : undefined
            }
          />
          <ResultCard
            label="商业画布 9 格"
            done={hasCanvas}
            score={store.canvasDiagnosis?.overall_score}
            link={
              hasCanvas
                ? `/assessment/${currentAssessment.id}/canvas`
                : undefined
            }
          />
          <ResultCard
            label="AI 场景推荐"
            done={hasScenarios}
            count={store.scenarioRecommendation?.top_scenarios?.length}
            link={
              hasScenarios
                ? `/assessment/${currentAssessment.id}/results`
                : undefined
            }
          />
          <ResultCard
            label="差异化竞争力"
            done={!!store.competitivenessData}
            link={
              store.competitivenessData
                ? `/assessment/${currentAssessment.id}/results`
                : undefined
            }
          />
          <ResultCard
            label="商业终局"
            done={!!store.endgameData}
            link={
              store.endgameData
                ? `/assessment/${currentAssessment.id}/results`
                : undefined
            }
          />
          <ResultCard
            label="结果仪表盘"
            done={hasProfile || hasCanvas || hasScenarios}
            link={
              hasProfile || hasCanvas || hasScenarios
                ? `/assessment/${currentAssessment.id}/results`
                : undefined
            }
            primary
          />
        </section>
      )}

      {/* ── Interactive panels: stay inline (need user selection) ── */}
      <section id="section-breakthrough">
        {store.breakthroughData && (
        <BreakthroughSelectionPanel
          data={store.breakthroughData}
          selectedKeys={store.selectedBreakthroughKeys}
          isSelecting={selectBreakthrough.isPending}
          onToggleElement={store.toggleBreakthroughKey}
          onConfirmSelection={handleSelectBreakthrough}
        />
      )}
      </section>

      {store.directionData && store.directionSelection && store.directionSelection.selected_directions.length > 0 && (
        <DirectionExpansionPanel
          data={store.directionData}
          selectedIds={store.selectedDirectionIds}
          isSelecting={selectDirections.isPending}
          onToggleDirection={store.toggleDirectionId}
          onConfirmSelection={handleSelectDirections}
        />
      )}
    </section>
  );
}

/** Compact result status card — links to dedicated result page in new tab. */
function ResultCard({
  label,
  done,
  score,
  count,
  mode,
  link,
  primary,
}: {
  label: string;
  done: boolean;
  score?: number;
  count?: number;
  mode?: string | null;
  link?: string;
  primary?: boolean;
}) {
  const content = (
    <div
      className={`rounded-xl border px-4 py-4 transition ${
        primary
          ? "border-warm-accent/30 bg-warm-accent/5 ring-1 ring-warm-accent/10"
          : done
            ? "border-warm-border-light bg-warm-surface"
            : "border-dashed border-warm-border bg-secondary/50"
      } ${link ? "hover:shadow-md hover:-translate-y-px cursor-pointer" : ""}`}
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
              : "badge-muted"
          }`}
        >
          {done
            ? mode === "live"
              ? "真实生成"
              : score != null
                ? `${score}分`
                : count != null
                  ? `Top ${count}`
                  : "已完成"
            : "待生成"}
        </span>
      </div>
    </div>
  );

  if (link) {
    return (
      <Link href={link} target="_blank" rel="noopener noreferrer">
        {content}
      </Link>
    );
  }
  return content;
}
