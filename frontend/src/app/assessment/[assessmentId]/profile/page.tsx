"use client";

import { use, useCallback } from "react";
import Link from "next/link";

import { useAssessmentDetail, useGenerateCanvas } from "@/hooks";
import { toast } from "@/hooks/use-toast";
import { formatMutationError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ProfileResultsSection } from "@/components/profile-results-section";
import { SyncFeedbackPanel } from "@/components/sync-feedback-panel";

export default function ProfilePage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = use(params);
  const detailQuery = useAssessmentDetail(assessmentId);
  const generateCanvas = useGenerateCanvas();

  const handleGenerateCanvas = useCallback(async () => {
    try {
      await generateCanvas.mutateAsync(assessmentId);
      toast({
        title: "商业画布已生成",
        description: "已为你打开下一步页面。",
      });
      window.open(
        `/assessment/${assessmentId}/canvas`,
        "_blank",
        "noopener,noreferrer",
      );
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "商业画布生成"),
        variant: "destructive",
      });
    }
  }, [assessmentId, generateCanvas]);

  if (detailQuery.isLoading) {
    return (
      <main className="min-h-screen px-6 py-10">
        <div className="mx-auto max-w-7xl space-y-6">
          <Skeleton className="h-24 w-full rounded-xl" />
          <Skeleton className="h-64 w-full rounded-xl" />
          <Skeleton className="h-64 w-full rounded-xl" />
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
  const companyProfile = detail.company_profile;
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
            <div className="flex flex-wrap items-center gap-3">
              <span className="badge badge-accent">企业画像</span>
              {companyProfile ? <Badge variant="success">已完成</Badge> : null}
            </div>
            <h1 className="font-heading text-4xl font-bold tracking-tight text-warm-text sm:text-5xl">
              {companyName} 企业画像
            </h1>
            {industry ? (
              <p className="text-base leading-7 text-warm-secondary">
                {industry}
              </p>
            ) : null}
          </div>
        </section>

        {companyProfile ? (
          <ProfileResultsSection
            companyProfile={companyProfile}
            profileMode={null}
          />
        ) : (
          <div className="card-inset">
            <p className="section-label">企业画像</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              尚未生成企业画像。请先在主流程工作台生成画像后再查看。
            </p>
            <Link
              href={`/assessment/${assessmentId}`}
              className="mt-3 inline-block btn-primary text-xs"
            >
              返回主流程工作台
            </Link>
          </div>
        )}

        <section className="card">
          <p className="section-label">下一步</p>
          <h2 className="section-heading">
            {hasCanvas ? "查看商业画布 9 格诊断" : "生成商业画布"}
          </h2>
          <p className="mt-2 text-sm leading-7 text-muted-foreground">
            {hasCanvas
              ? "商业画布已生成，可直接进入查看和人工修订。"
              : "基于企业画像生成商业模式画布 9 格诊断，作为后续突破要素评分的输入。"}
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            {hasCanvas ? (
              <Link
                href={`/assessment/${assessmentId}/canvas`}
                className="btn-primary"
              >
                查看画布诊断
              </Link>
            ) : (
              <Button
                onClick={handleGenerateCanvas}
                disabled={generateCanvas.isPending || !companyProfile}
                loading={generateCanvas.isPending}
              >
                {generateCanvas.isPending ? "生成中..." : "生成商业画布"}
              </Button>
            )}
          </div>
        </section>
      </div>

      <SyncFeedbackPanel assessmentId={assessmentId} />
    </main>
  );
}
