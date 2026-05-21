"use client";

import React, { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import {
  useAssessmentDetail,
  useGenerateScenarios,
} from "@/hooks";
import { applyAssessmentDetailToStore } from "@/lib/assessment-utils";
import { expandDirections, formatMutationError, getDirections } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { DirectionExpansionPanel } from "@/components/direction-expansion-panel";
import { SyncFeedbackPanel } from "@/components/sync-feedback-panel";
import { useAssessmentStore } from "@/stores/assessment-store";
import { toast } from "@/hooks/use-toast";
import type { AssessmentDirectionResponse } from "@/lib/types";

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
  const generateScenarios = useGenerateScenarios();

  const directionsQuery = useQuery({
    queryKey: ["assessment", assessmentId, "directions"],
    queryFn: ({ signal }) => getDirections(assessmentId, { signal }),
    enabled: Boolean(assessmentId),
    refetchInterval: (query) => {
      if (query.state.data?.direction_expansion.llm_status === "pending") {
        return 3000;
      }
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
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSelecting, setIsSelecting] = useState(false);

  useEffect(() => {
    if (!detailQuery.data) return;

    applyAssessmentDetailToStore(detailQuery.data, store);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [detailQuery.data]);

  useEffect(() => {
    if (!directionData) return;
    if (directionData.direction_expansion.llm_status !== "pending") {
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

  const handleGenerate = useCallback(async () => {
    setIsGenerating(true);
    try {
      store.setDirectionSelection(null);
      store.setSelectedDirectionIds([]);
      const result = await expandDirections(assessmentId);
      store.setDirectionData(result);
      store.setDirectionSelection(result.direction_selection);
      store.setSelectedDirectionIds(
        result.direction_selection?.selected_directions.map(
          (direction) => direction.direction_id,
        ) ?? [],
      );
      await directionsQuery.refetch();
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "创新方向候选生成"),
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  }, [assessmentId, directionsQuery, store]);

  const handleGenerateScenarios = useCallback(async () => {
    try {
      await generateScenarios.mutateAsync(assessmentId);
      toast({ title: "AI 推荐场景已生成" });
      router.push(`/assessment/${assessmentId}/scenarios`);
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "AI 推荐场景生成"),
        variant: "destructive",
      });
    }
  }, [assessmentId, generateScenarios, router]);

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

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <main className="min-h-screen px-6 py-10">
        <div className="mx-auto max-w-7xl">
          <div className="space-y-4 rounded-xl p-6 text-sm msg-error">
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
        <section className="page-header">
          <div className="flex flex-col gap-4">
            <div className="flex flex-wrap items-center gap-2">
              <Link href="/" className="btn-secondary text-xs">
                返回首页
              </Link>
              <Link
                href={`/assessment/${assessmentId}`}
                className="btn-secondary text-xs"
              >
                返回主流程工作台
              </Link>
            </div>
            <span className="badge badge-accent">创新方向候选</span>
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

        {!hasCanvas ? (
          <div className="card-inset">
            <p className="section-label">前置条件</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              创新方向延展需要先完成商业画布 9 格诊断和突破要素评分。
            </p>
            <Link
              href={`/assessment/${assessmentId}/canvas`}
              className="mt-3 inline-block btn-primary text-xs"
            >
              前往商业画布
            </Link>
          </div>
        ) : directionData ? (
          <DirectionExpansionPanel
            data={directionData}
            selectedIds={currentSelectedDirectionIds}
            isSelecting={isSelecting}
            isLLMPending={isLLMPending}
            isNextStepPending={generateScenarios.isPending}
            onToggleDirection={store.toggleDirectionId}
            onConfirmSelection={async () => {
              if (currentSelectedDirectionIds.length < 1) return;
              setIsSelecting(true);
              try {
                const { selectDirections } = await import("@/lib/api");
                const result = await selectDirections(assessmentId, {
                  selected_direction_ids: currentSelectedDirectionIds,
                });
                store.setDirectionSelection(result);
                store.setSelectedDirectionIds(
                  result.selected_directions.map(
                    (direction) => direction.direction_id,
                  ),
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
            onNextStep={handleGenerateScenarios}
          />
        ) : directionsQuery.isLoading ? (
          <div className="mx-auto max-w-7xl">
            <Skeleton className="h-96 w-full rounded-xl" />
          </div>
        ) : (
          <div className="card-inset">
            <p className="section-label">创新方向候选</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              尚未生成创新方向候选。请在完成突破要素评分后生成。
            </p>
            <Button
              onClick={handleGenerate}
              disabled={isGenerating}
              loading={isGenerating}
              className="mt-4"
            >
              生成创新方向候选
            </Button>
          </div>
        )}
      </div>

      <SyncFeedbackPanel assessmentId={assessmentId} />
    </main>
  );
}
