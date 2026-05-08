"use client";

import { useCallback, useEffect, useState } from "react";
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
import { AssessmentFormSection } from "@/components/assessment-form-section";
import { AssessmentSkeleton } from "@/components/assessment-skeleton";
import { WorkflowSidebar } from "@/components/workflow-sidebar";
import { ProfileResultsSection } from "@/components/profile-results-section";
import { ProgressStepper } from "@/components/progress-stepper";
import { BusinessCanvasGrid } from "@/components/business-canvas-grid";
import { BreakthroughSelectionPanel } from "@/components/breakthrough-selection-panel";
import { DirectionExpansionPanel } from "@/components/direction-expansion-panel";
import { CompetitivenessPanel } from "@/components/competitiveness-panel";
import { EndgamePanel } from "@/components/endgame-panel";
import { ScenarioRecommendationsPanel } from "@/components/scenario-recommendations-panel";
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
      const result = await generateProfile.mutateAsync(store.assessment.id);
      store.setAssessment(result.assessment);
      store.setCompanyProfile(result.profile);
      store.setProfileMode(result.generation_mode);
      store.resetDownstream("profile");
      setProgress(computeProgress({ hasAssessment: true, hasProfile: true, hasCanvas: false, hasScenarios: false }));
      toast({ title: "企业画像已生成", description: `模式：${result.generation_mode}` });
    } catch (_e) { /* error handled by QueryClient mutation defaults */ }
  }, [store.assessment, generateProfile, store]);

  const handleGenerateCanvas = useCallback(async () => {
    if (!store.assessment) return;
    try {
      const result = await generateCanvas.mutateAsync(store.assessment.id);
      store.setAssessment(result.assessment);
      store.setCanvasDiagnosis(result.canvas_diagnosis);
      store.resetDownstream("canvas");
      setProgress(computeProgress({ hasAssessment: true, hasProfile: true, hasCanvas: true, hasScenarios: false }));
      toast({ title: "商业画布已生成", description: `总体评分：${result.canvas_diagnosis.overall_score}` });
    } catch (_e) { }
  }, [store.assessment, generateCanvas, store]);

  const handleGenerateBreakthrough = useCallback(async () => {
    if (!store.assessment) return;
    try {
      const result = await recommendBreakthrough.mutateAsync(store.assessment.id);
      store.setBreakthroughData(result);
      if (result.breakthrough_selection && result.breakthrough_selection.selected_elements.length >= 2) {
        store.setBreakthroughSelection(result.breakthrough_selection);
        store.setSelectedBreakthroughKeys(result.breakthrough_selection.selected_elements.map((e) => e.key));
      } else {
        store.setBreakthroughSelection(null);
        store.setSelectedBreakthroughKeys(result.breakthrough_recommendation.recommended_keys);
      }
      toast({ title: "突破要素推荐已生成" });
    } catch (_e) { }
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
    } catch (_e) { }
  }, [store, selectBreakthrough]);

  const handleGenerateDirections = useCallback(async () => {
    if (!store.assessment) return;
    try {
      const result = await expandDirections.mutateAsync(store.assessment.id);
      store.setDirectionData(result);
      if (result.direction_selection && result.direction_selection.selected_directions.length > 0) {
        store.setDirectionSelection(result.direction_selection);
        store.setSelectedDirectionIds(result.direction_selection.selected_directions.map((d) => d.direction_id));
      } else {
        store.setDirectionSelection(null);
        store.setSelectedDirectionIds([]);
      }
      toast({ title: "创新方向延展已生成" });
    } catch (_e) { }
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
    } catch (_e) { }
  }, [store, selectDirections]);

  const handleGenerateScenarios = useCallback(async () => {
    if (!store.assessment) return;
    try {
      const result = await generateScenarios.mutateAsync(store.assessment.id);
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
    } catch (_e) { }
  }, [store.assessment, generateScenarios, store]);

  const handleGenerateCompetitiveness = useCallback(async () => {
    if (!store.assessment) return;
    try {
      const result = await generateCompetitiveness.mutateAsync(store.assessment.id);
      store.setCompetitivenessData(result);
      toast({ title: "竞争力分析已生成" });
    } catch (_e) { }
  }, [store.assessment, generateCompetitiveness, store]);

  const handleGenerateEndgame = useCallback(async () => {
    if (!store.assessment) return;
    try {
      const result = await generateEndgame.mutateAsync(store.assessment.id);
      store.setEndgameData(result);
      toast({ title: "商业终局分析已生成" });
    } catch (_e) { }
  }, [store.assessment, generateEndgame, store]);

  // --- Loading / Error states ---
  if (detailQuery.isLoading) return <AssessmentSkeleton />;
  if (detailQuery.isError) {
    return (
      <div className="rounded-xl msg-error p-6 text-sm">
        {detailQuery.error instanceof Error ? detailQuery.error.message : "Assessment 加载失败。"}
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
      <ProgressStepper hasAssessment={currentAssessment !== null} progress={progress} />

      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
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

      {/* Results panels */}
      {store.companyProfile && (
        <ProfileResultsSection
          companyProfile={store.companyProfile}
          profileMode={store.profileMode}
        />
      )}

      {store.canvasDiagnosis && (
        <BusinessCanvasGrid canvasDiagnosis={store.canvasDiagnosis} />
      )}

      {!store.canvasDiagnosis && (
        <div className="card-inset">
          <p className="section-label">商业画布 9 格诊断</p>
          <p className="mt-4 text-sm leading-7 text-muted-foreground">
            尚未生成商业画布。企业画像完成后可开始生成；若历史结果已存在，刷新页面会自动回看。
          </p>
        </div>
      )}

      {store.breakthroughData && (
        <BreakthroughSelectionPanel
          data={store.breakthroughData}
          selectedKeys={store.selectedBreakthroughKeys}
          isSelecting={selectBreakthrough.isPending}
          onToggleElement={store.toggleBreakthroughKey}
          onConfirmSelection={handleSelectBreakthrough}
        />
      )}

      {store.directionData && store.directionSelection && store.directionSelection.selected_directions.length > 0 && (
        <DirectionExpansionPanel
          data={store.directionData}
          selectedIds={store.selectedDirectionIds}
          isSelecting={selectDirections.isPending}
          onToggleDirection={store.toggleDirectionId}
          onConfirmSelection={handleSelectDirections}
        />
      )}

      {store.competitivenessData && (
        <CompetitivenessPanel data={store.competitivenessData} />
      )}

      {store.endgameData && <EndgamePanel data={store.endgameData} />}

      {store.scenarioRecommendation && store.assessment ? (
        <ScenarioRecommendationsPanel
          assessmentId={store.assessment.id}
          readyForReport={progress.ready_for_report}
          scenarioRecommendation={store.scenarioRecommendation}
        />
      ) : (
        <div className="card-inset">
          <p className="section-label">Top 3 AI 场景推荐</p>
          <p className="mt-4 text-sm leading-7 text-muted-foreground">
            尚未生成场景推荐。商业画布完成后可开始生成；若历史结果已存在，刷新页面会自动回看。
          </p>
        </div>
      )}
    </section>
  );
}
