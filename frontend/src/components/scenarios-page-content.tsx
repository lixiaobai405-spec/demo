"use client";

import React, { useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAssessmentDetail } from "@/hooks";
import { useGenerateCompetitiveness } from "@/hooks/use-competitiveness";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ScenarioRecommendationsPanel } from "@/components/scenario-recommendations-panel";
import { toast } from "@/hooks/use-toast";
import { formatMutationError } from "@/lib/api";

/**
 * 在客户端加载 AI 场景推荐详情，避免服务端请求拿不到本地登录态。
 */
export function ScenariosPageContent({
  assessmentId,
}: {
  assessmentId: string;
}) {
  const detailQuery = useAssessmentDetail(assessmentId);

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
          <div className="space-y-4 rounded-xl msg-error p-6 text-sm">
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

  const router = useRouter();
  const generateCompetitiveness = useGenerateCompetitiveness();

  const handleGenerateCompetitiveness = useCallback(async () => {
    try {
      await generateCompetitiveness.mutateAsync(assessmentId);
      toast({ title: "差异化竞争力分析已生成" });
      router.push(`/assessment/${assessmentId}/competitiveness`);
    } catch (e) {
      toast({
        title: "生成失败",
        description: formatMutationError(e, "差异化竞争力分析"),
        variant: "destructive",
      });
    }
  }, [assessmentId, generateCompetitiveness, router]);

  const detail = detailQuery.data;
  const companyName = detail.assessment.company_name;
  const industry = detail.assessment.industry;
  const scenarios = detail.scenario_recommendation;

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8">
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
            <span className="badge badge-warning">AI 场景推荐</span>
            <h1 className="font-heading text-4xl font-bold tracking-tight text-warm-text sm:text-5xl">
              {companyName} AI 场景推荐
            </h1>
            {industry ? (
              <p className="text-base leading-7 text-warm-secondary">
                {industry}
              </p>
            ) : null}
          </div>
        </section>

        {scenarios ? (
          <>
            <ScenarioRecommendationsPanel
              assessmentId={assessmentId}
              readyForReport={detail.progress.ready_for_report}
              scenarioRecommendation={scenarios}
              hideNextAction
            />
            {/* Next step */}
            {detail.progress.ready_for_report && (
              <section className="card mt-8">
                <p className="section-label">下一步</p>
                <h2 className="section-heading">差异化竞争力分析</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  基于 Top 3 AI 场景推荐结果，分析企业的差异化竞争力，
                  包括 Point-to-Line 串联和核心优势。
                </p>
                <div className="mt-4 flex flex-wrap gap-3">
                  <Button
                    onClick={handleGenerateCompetitiveness}
                    disabled={generateCompetitiveness.isPending}
                    loading={generateCompetitiveness.isPending}
                  >
                    {generateCompetitiveness.isPending ? "正在生成..." : "生成差异化竞争力 →"}
                  </Button>
                  <Link
                    href={`/assessment/${assessmentId}/results`}
                    className="btn-secondary text-xs"
                  >
                    查看结果仪表盘
                  </Link>
                </div>
              </section>
            )}
          </>
        ) : (
          <div className="card-inset">
            <p className="section-label">AI 场景推荐</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              尚未生成 AI 场景推荐。请先完成前置步骤后再查看。
            </p>
            <Link
              href={`/assessment/${assessmentId}`}
              className="mt-3 inline-block btn-primary text-xs"
            >
              返回工作台
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}
