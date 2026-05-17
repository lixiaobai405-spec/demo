"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { useAssessmentDetail, useGenerateScenarios } from "@/hooks";
import { getDirections, expandDirections, formatMutationError } from "@/lib/api";
import { Button, buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { DirectionExpansionPanel } from "@/components/direction-expansion-panel";
import { useAssessmentStore } from "@/stores/assessment-store";
import { toast } from "@/hooks/use-toast";
import type { AssessmentDirectionResponse } from "@/lib/types";

/**
 * 提取当前方向页正在展示的方向 ID，确保选择和计数只基于当前这一版结果。
 */
function extractCurrentDirectionIds(
  directionData: AssessmentDirectionResponse | undefined,
): string[] {
  if (!directionData) {
    return [];
  }

  return directionData.direction_expansion.elements.flatMap((element) =>
    element.suggestions.map((direction) => direction.direction_id),
  );
}

export default function DirectionsPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = use(params);
  const router = useRouter();
  const detailQuery = useAssessmentDetail(assessmentId);
  const store = useAssessmentStore();

  const directionsQuery = useQuery({
    queryKey: ["assessment", assessmentId, "directions"],
    queryFn: ({ signal }) => getDirections(assessmentId, { signal }),
    enabled: Boolean(assessmentId),
    refetchInterval: (query) => {
      if (query.state.data?.direction_expansion.llm_status === "pending")
        return 3000;
      return false;
    },
    staleTime: 0,
    retry: false,
  });

  const directionData = directionsQuery.data;
  const isLLMPending =
    directionData?.direction_expansion.llm_status === "pending";
  const currentDirectionIds = extractCurrentDirectionIds(directionData);
  const currentDirectionIdSet = new Set(currentDirectionIds);
  const currentSelectedDirectionIds = store.selectedDirectionIds.filter((id) =>
    currentDirectionIdSet.has(id),
  );

  // Sync polled data back to store for cross-tab consistency
  useEffect(() => {
    if (!directionData) return;
    const status = directionData.direction_expansion.llm_status;
    if (status !== "pending") {
      store.setDirectionData(directionData);
      store.setDirectionSelection(directionData.direction_selection);
      store.setSelectedDirectionIds(
        directionData.direction_selection?.selected_directions.map(
          (direction) => direction.direction_id,
        ) ?? [],
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [directionData]);

  // Trigger generation if no directions exist
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSelecting, setIsSelecting] = useState(false);
  const hasConfirmedSelection =
    store.directionSelection !== null &&
    store.directionSelection.selected_directions.length > 0;

  const handleGenerate = useCallback(async () => {
    setIsGenerating(true);
    try {
      const result = await expandDirections(assessmentId);
      store.setDirectionData(result);
      directionsQuery.refetch();
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "创新方向延展生成"),
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  }, [assessmentId, store, directionsQuery]);

  // Loading
  if (detailQuery.isLoading) {
    return (
      <main className="min-h-screen px-6 py-10">
        <div className="mx-auto max-w-7xl space-y-6">
          <Skeleton className="h-24 w-full rounded-xl" />
          <Skeleton className="h-96 w-full rounded-xl" />
        </div>
      </main>
    );
  }

  // Error
  if (detailQuery.isError || !detailQuery.data) {
    return (
      <main className="min-h-screen px-6 py-10">
        <div className="mx-auto max-w-7xl">
          <div className="rounded-xl msg-error p-6 text-sm space-y-4">
            <p className="font-medium">加载失败</p>
            <p>
              {detailQuery.error instanceof Error
                ? detailQuery.error.message
                : "无法加载评估数据。"}
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => detailQuery.refetch()}
            >
              重试
            </Button>
          </div>
        </div>
      </main>
    );
  }

  const detail = detailQuery.data;
  const companyName = detail.assessment.company_name;
  const industry = detail.assessment.industry;
  const hasCanvas = detail.canvas_diagnosis !== null;

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8">
        {/* Header */}
        <section className="page-header">
          <div className="flex flex-col gap-4">
            <div className="flex flex-wrap items-center gap-2">
              <Link href="/" className="btn-secondary text-xs">
                ← 返回首页
              </Link>
              <Link
                href={`/assessment/${assessmentId}`}
                className="btn-secondary text-xs"
              >
                ← 返回工作台
              </Link>
              <Link
                href={`/assessment/${assessmentId}/results`}
                className="btn-secondary text-xs"
              >
                结果仪表盘 →
              </Link>
            </div>
            <span className="badge badge-accent">创新方向延展</span>
            <h1 className="font-heading text-4xl font-bold tracking-tight text-warm-text sm:text-5xl">
              {companyName} 创新方向延展
            </h1>
            {industry ? (
              <p className="text-base leading-7 text-warm-secondary">
                {industry}
              </p>
            ) : null}
          </div>
        </section>

        {/* Directions Content */}
        {!hasCanvas ? (
          <div className="card-inset">
            <p className="section-label">前提条件</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              创新方向延展需要先生成商业画布 9 格诊断。请先在画布诊断页面完成。
            </p>
            <Link
              href={`/assessment/${assessmentId}/canvas`}
              className="inline-block mt-3 btn-primary text-xs"
            >
              前往画布诊断 →
            </Link>
          </div>
        ) : directionData ? (
          <DirectionExpansionPanel
            data={directionData}
            selectedIds={currentSelectedDirectionIds}
            isSelecting={isSelecting}
            isLLMPending={isLLMPending}
            onToggleDirection={store.toggleDirectionId}
            onConfirmSelection={async () => {
              if (!store.assessment || currentSelectedDirectionIds.length < 1) return;
              setIsSelecting(true);
              try {
                const { selectDirections: selectDirs } = await import("@/lib/api");
                const result = await selectDirs(
                  store.assessment.id,
                  { selected_direction_ids: currentSelectedDirectionIds },
                );
                store.setDirectionSelection(result);
                store.setSelectedDirectionIds(
                  result.selected_directions.map((direction) => direction.direction_id),
                );
                await directionsQuery.refetch();
                toast({ title: "创新方向已确认" });
              } catch (error) {
                toast({
                  title: "保存失败",
                  description: formatMutationError(error, "创新方向保存"),
                  variant: "destructive",
                });
              } finally {
                setIsSelecting(false);
              }
            }}
          />
        ) : directionsQuery.isLoading ? (
          <div className="mx-auto max-w-7xl">
            <Skeleton className="h-96 w-full rounded-xl" />
          </div>
        ) : (
          <div className="card-inset">
            <p className="section-label">创新方向延展</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              尚未生成创新方向延展。请在完成画布诊断和突破要素评分后生成。
            </p>
            <Button
              onClick={handleGenerate}
              disabled={isGenerating}
              loading={isGenerating}
              className="mt-4"
            >
              生成创新方向
            </Button>
            <Link
              href={`/assessment/${assessmentId}`}
              className="inline-block mt-3 btn-secondary text-xs"
            >
              返回工作台
            </Link>
          </div>
        )}

        {/* Next step — only show when directions are confirmed */}
        {directionData && hasConfirmedSelection && (
          <DirectionsNextStep assessmentId={assessmentId} />
        )}
      </div>
    </main>
  );
}

function DirectionsNextStep({ assessmentId }: { assessmentId: string }) {
  const router = useRouter();
  const generateScenarios = useGenerateScenarios();

  const handleGenerateScenarios = useCallback(async () => {
    try {
      await generateScenarios.mutateAsync(assessmentId);
      toast({ title: "AI 场景推荐已生成" });
      router.push(`/assessment/${assessmentId}/scenarios`);
    } catch (e) {
      toast({
        title: "生成失败",
        description: formatMutationError(e, "AI 场景推荐生成"),
        variant: "destructive",
      });
    }
  }, [assessmentId, generateScenarios, router]);

  return (
    <section className="card">
      <p className="section-label">下一步</p>
      <h2 className="section-heading">Top 3 AI 场景推荐</h2>
      <p className="mt-2 text-sm leading-7 text-muted-foreground">
        基于创新方向延展结果，系统自动推荐 Top 3 AI 应用场景，
        评估落地可行性和业务价值。
      </p>
      <div className="mt-4 flex flex-wrap gap-3">
        <Button
          onClick={handleGenerateScenarios}
          disabled={generateScenarios.isPending}
          loading={generateScenarios.isPending}
        >
          {generateScenarios.isPending ? "正在生成..." : "生成 Top 3 AI 场景推荐 →"}
        </Button>
        <Link
          href={`/assessment/${assessmentId}/results`}
          className={buttonVariants({ variant: "outline" })}
        >
          查看结果仪表盘
        </Link>
      </div>
    </section>
  );
}
