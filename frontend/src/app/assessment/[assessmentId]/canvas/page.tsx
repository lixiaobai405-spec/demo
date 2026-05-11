"use client";

import { use, useCallback } from "react";
import Link from "next/link";

import { useAssessmentDetail, useRecommendBreakthrough } from "@/hooks";
import { toast } from "@/hooks/use-toast";
import { formatMutationError } from "@/lib/api";
import { Button, buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { BusinessCanvasGrid } from "@/components/business-canvas-grid";
import type { AssessmentBreakthroughResponse } from "@/lib/types";

export default function CanvasPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = use(params);
  const detailQuery = useAssessmentDetail(assessmentId);
  const recommendBreakthrough = useRecommendBreakthrough();

  const handleGenerateBreakthrough = useCallback(async () => {
    try {
      const result: AssessmentBreakthroughResponse =
        await recommendBreakthrough.mutateAsync(assessmentId);
      const keys =
        result.breakthrough_selection?.selected_elements?.map(
          (e: { key: string }) => e.key,
        ) ?? result.breakthrough_recommendation.recommended_keys;
      toast({
        title: "突破要素已生成",
        description: `推荐 ${keys.length} 个突破要素，请在下方选择 2-3 个。`,
      });
      // Force open workspace in new tab for interactive selection
      window.open(
        `/assessment/${assessmentId}`,
        "_blank",
        "noopener,noreferrer",
      );
    } catch (e) {
      toast({
        title: "生成失败",
        description: formatMutationError(e, "突破要素生成"),
        variant: "destructive",
      });
    }
  }, [assessmentId, recommendBreakthrough]);

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
  const canvasDiagnosis = detail.canvas_diagnosis;
  const companyName = detail.assessment.company_name;
  const industry = detail.assessment.industry;
  const hasBreakthrough =
    detail.breakthrough_selection && detail.breakthrough_selection.length >= 2;

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
            </div>
            <span className="badge badge-accent">商业画布 9 格诊断</span>
            <h1 className="font-heading text-4xl font-bold tracking-tight text-warm-text sm:text-5xl">
              {companyName} 商业模式画布
            </h1>
            {industry ? (
              <p className="text-base leading-7 text-warm-secondary">
                {industry}
              </p>
            ) : null}
          </div>
        </section>

        {/* Canvas */}
        {canvasDiagnosis ? (
          <BusinessCanvasGrid canvasDiagnosis={canvasDiagnosis} />
        ) : (
          <div className="card-inset">
            <p className="section-label">画布诊断</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              尚未生成商业画布诊断。请先生成企业画像，再生成画布诊断。
            </p>
            <Link href={`/assessment/${assessmentId}`} className="inline-block mt-3 btn-primary text-xs">
              返回工作台
            </Link>
          </div>
        )}

        {/* Next step */}
        <section className="card">
          <p className="section-label">下一步</p>
          <h2 className="section-heading">
            {hasBreakthrough ? "突破要素" : "选择突破要素"}
          </h2>
          <p className="mt-2 text-sm leading-7 text-muted-foreground">
            {hasBreakthrough
              ? "突破要素已选择，可进入工作台继续创新方向延展。"
              : "基于画布诊断结果，系统会推荐优先突破的薄弱要素。"}
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            {hasBreakthrough ? (
              <Link href={`/assessment/${assessmentId}`} className="btn-primary">
                进入工作台继续 →
              </Link>
            ) : (
              <Button
                onClick={handleGenerateBreakthrough}
                disabled={recommendBreakthrough.isPending || !canvasDiagnosis}
                loading={recommendBreakthrough.isPending}
              >
                {recommendBreakthrough.isPending
                  ? "生成中..."
                  : "生成突破要素推荐"}
              </Button>
            )}
            <Link
              href={`/assessment/${assessmentId}/results`}
              className={buttonVariants({ variant: "outline" })}
            >
              查看结果仪表盘
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
