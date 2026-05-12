"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { AssessmentFormSection } from "@/components/assessment-form-section";
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
  done: boolean;
  statusLabel: string;
  link?: string;
};

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

  const detailQuery = useAssessmentDetail(assessmentId);
  const prefillQuery = useIntakeSession(
    !assessmentId && prefillSessionId ? prefillSessionId : null,
  );

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
      setProgress(
        computeProgress({
          hasAssessment: true,
          hasProfile: true,
          hasCanvas: false,
          hasScenarios: false,
        }),
      );
      toast({
        title: "企业画像已生成",
        description: `模式：${result.generation_mode}`,
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
      setProgress(
        computeProgress({
          hasAssessment: true,
          hasProfile: true,
          hasCanvas: true,
          hasScenarios: false,
        }),
      );
      toast({
        title: "商业画布已生成",
        description: `总分：${result.canvas_diagnosis.overall_score}`,
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

      store.setDirectionData(result);
      window.open(
        `/assessment/${store.assessment.id}/directions`,
        "_blank",
      );
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "创新方向延展生成"),
        variant: "destructive",
      });
    }
  }, [expandDirections, store]);

  const handleSelectDirections = useCallback(async () => {
    if (!store.assessment || store.selectedDirectionIds.length < 1) return;

    try {
      const result = await selectDirections.mutateAsync({
        assessmentId: store.assessment.id,
        payload: { selected_direction_ids: store.selectedDirectionIds },
      });

      store.setDirectionSelection(result);
      setProgress(
        computeProgress({
          hasAssessment: true,
          hasProfile: store.companyProfile !== null,
          hasCanvas: store.canvasDiagnosis !== null,
          hasBreakthrough:
            progress.has_breakthrough || store.breakthroughSelection !== null,
          hasDirections: true,
          hasCompetitiveness:
            progress.has_competitiveness || store.competitivenessData !== null,
          hasScenarios: store.scenarioRecommendation !== null,
        }),
      );
      toast({ title: "创新方向已确认" });
    } catch (error) {
      toast({
        title: "保存失败",
        description: formatMutationError(error, "创新方向保存"),
        variant: "destructive",
      });
    }
  }, [progress.has_breakthrough, progress.has_competitiveness, selectDirections, store]);

  const handleGenerateScenarios = useCallback(async () => {
    if (!store.assessment) return;

    try {
      const result = await withSlowHint(
        generateScenarios.mutateAsync(store.assessment.id),
        "正在生成 Top 3 AI 场景推荐",
        toast,
      );

      store.setAssessment(result.assessment);
      store.setScenarioRecommendation(result.scenario_recommendation);
      setProgress(
        computeProgress({
          hasAssessment: true,
          hasProfile: store.companyProfile !== null,
          hasCanvas: store.canvasDiagnosis !== null,
          hasBreakthrough:
            progress.has_breakthrough || store.breakthroughSelection !== null,
          hasDirections:
            progress.has_directions ||
            store.directionData !== null ||
            store.directionSelection !== null,
          hasCompetitiveness:
            progress.has_competitiveness || store.competitivenessData !== null,
          hasScenarios: true,
        }),
      );
      toast({ title: "场景推荐已生成" });
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "场景推荐生成"),
        variant: "destructive",
      });
    }
  }, [
    generateScenarios,
    progress.has_breakthrough,
    progress.has_competitiveness,
    progress.has_directions,
    store,
  ]);

  const handleGenerateCompetitiveness = useCallback(async () => {
    if (!store.assessment) return;

    try {
      const result = await withSlowHint(
        generateCompetitiveness.mutateAsync(store.assessment.id),
        "正在分析差异化竞争力",
        toast,
      );

      store.setCompetitivenessData(result);
      setProgress(
        computeProgress({
          hasAssessment: true,
          hasProfile: store.companyProfile !== null,
          hasCanvas: store.canvasDiagnosis !== null,
          hasBreakthrough:
            progress.has_breakthrough || store.breakthroughSelection !== null,
          hasDirections:
            progress.has_directions ||
            store.directionData !== null ||
            store.directionSelection !== null,
          hasCompetitiveness: true,
          hasScenarios: store.scenarioRecommendation !== null,
        }),
      );
      toast({ title: "差异化竞争力分析已生成" });
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "差异化竞争力分析生成"),
        variant: "destructive",
      });
    }
  }, [
    generateCompetitiveness,
    progress.has_breakthrough,
    progress.has_directions,
    store,
  ]);

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
        : generateCompetitiveness.isPending
          ? 6
          : generateScenarios.isPending
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
    hasProfile ||
    hasCanvas ||
    hasBreakthrough ||
    hasDirections ||
    hasCompetitiveness ||
    hasScenarios ||
    hasEndgame;

  const workflowModules: WorkflowModule[] = currentAssessment
    ? [
        {
          key: "profile",
          label: "企业画像",
          color: "success",
          disabled: generateProfile.isPending,
          loading: generateProfile.isPending,
          hasResult: hasProfile,
          onClick: handleGenerateProfile,
        },
        {
          key: "canvas",
          label: "商业画布 9 格",
          color: "accent",
          disabled: !hasProfile || generateCanvas.isPending,
          loading: generateCanvas.isPending,
          hasResult: hasCanvas,
          onClick: handleGenerateCanvas,
        },
        {
          key: "breakthrough",
          label: "BMC 突破要素评分",
          color: "warn",
          disabled: !hasCanvas,
          loading: false,
          hasResult: hasBreakthrough,
          onClick: handleGenerateBreakthrough,
        },
        {
          key: "directions",
          label: "创新方向延展",
          color: "accent",
          disabled: !hasCanvas || expandDirections.isPending,
          loading: expandDirections.isPending,
          hasResult: hasDirections,
          onClick: handleGenerateDirections,
        },
        {
          key: "scenarios",
          label: "Top 3 AI 场景推荐",
          color: "success",
          disabled: !hasCanvas || generateScenarios.isPending,
          loading: generateScenarios.isPending,
          hasResult: hasScenarios,
          onClick: handleGenerateScenarios,
        },
        {
          key: "competitiveness",
          label: "差异化竞争力分析",
          color: "warn",
          disabled: !hasCanvas || generateCompetitiveness.isPending,
          loading: generateCompetitiveness.isPending,
          hasResult: hasCompetitiveness,
          onClick: handleGenerateCompetitiveness,
        },
        {
          key: "endgame",
          label: "商业终局设计",
          color: "accent",
          disabled: !hasCanvas || generateEndgame.isPending,
          loading: generateEndgame.isPending,
          hasResult: hasEndgame,
          onClick: handleGenerateEndgame,
        },
      ]
    : [];

  const resultCards: ResultCardItem[] = currentAssessment
    ? [
        {
          key: "profile",
          label: "企业画像",
          done: hasProfile,
          statusLabel:
            store.profileMode === "live" ? "真实生成" : "已生成",
          link: hasProfile
            ? `/assessment/${currentAssessment.id}/profile`
            : undefined,
        },
        {
          key: "canvas",
          label: "商业画布 9 格",
          done: hasCanvas,
          statusLabel: `${store.canvasDiagnosis?.overall_score ?? "-"}分`,
          link: hasCanvas
            ? `/assessment/${currentAssessment.id}/canvas`
            : undefined,
        },
        {
          key: "breakthrough",
          label: "BMC 突破要素评分",
          done: hasBreakthrough,
          statusLabel: "已完成",
          link: hasCanvas
            ? `/assessment/${currentAssessment.id}/scoring`
            : undefined,
        },
        {
          key: "directions",
          label: "创新方向延展",
          done: hasDirections,
          statusLabel: "已生成",
          link: hasDirections
            ? `/assessment/${currentAssessment.id}/directions`
            : undefined,
        },
        {
          key: "scenarios",
          label: "Top 3 AI 场景推荐",
          done: hasScenarios,
          statusLabel: `Top ${
            store.scenarioRecommendation?.top_scenarios?.length ?? 3
          }`,
          link: hasScenarios
            ? `/assessment/${currentAssessment.id}/results`
            : undefined,
        },
        {
          key: "competitiveness",
          label: "差异化竞争力分析",
          done: hasCompetitiveness,
          statusLabel: "已生成",
          link: hasCompetitiveness
            ? `/assessment/${currentAssessment.id}/results`
            : undefined,
        },
        {
          key: "endgame",
          label: "商业终局设计",
          done: hasEndgame,
          statusLabel: "已生成",
          link: hasEndgame
            ? `/assessment/${currentAssessment.id}/endgame`
            : undefined,
        },
      ]
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

      <div
        className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]"
        id="section-assessment-form"
      >
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
          <section
            id="section-profile-results"
            className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3"
          >
            {resultCards.map((card) => (
              <ResultCard
                key={card.key}
                label={card.label}
                done={card.done}
                statusLabel={card.done ? card.statusLabel : "待生成"}
                link={card.link}
              />
            ))}
          </section>

          <section className="sm:max-w-md">
            <ResultCard
              label="结果仪表盘"
              done={hasDashboard}
              statusLabel={hasDashboard ? "可查看" : "待生成"}
              link={
                hasDashboard
                  ? `/assessment/${currentAssessment.id}/results`
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

function ResultCard({
  label,
  done,
  statusLabel,
  link,
  primary,
}: {
  label: string;
  done: boolean;
  statusLabel: string;
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
