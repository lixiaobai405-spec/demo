"use client";

import React from "react";
import Link from "next/link";

import { useAssessmentDetail, useCompetitiveness } from "@/hooks";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CompetitivenessPanel } from "@/components/competitiveness-panel";

/**
 * 在客户端加载差异化竞争力详情，避免服务端请求拿不到本地登录态。
 */
export function CompetitivenessPageContent({
  assessmentId,
}: {
  assessmentId: string;
}) {
  const detailQuery = useAssessmentDetail(assessmentId);
  const competitivenessQuery = useCompetitiveness(assessmentId);
  const isLoading = detailQuery.isLoading || competitivenessQuery.isLoading;

  if (isLoading) {
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

  if (competitivenessQuery.isError) {
    return (
      <main className="min-h-screen px-6 py-10">
        <div className="mx-auto max-w-7xl">
          <div className="space-y-4 rounded-xl msg-error p-6 text-sm">
            <p className="font-medium">加载失败</p>
            <p>
              {competitivenessQuery.error instanceof Error
                ? competitivenessQuery.error.message
                : "无法加载差异化竞争力分析。"}
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => competitivenessQuery.refetch()}
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
  const competitiveness = competitivenessQuery.data;

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
            <span className="badge badge-warning">差异化竞争力</span>
            <h1 className="font-heading text-4xl font-bold tracking-tight text-warm-text sm:text-5xl">
              {companyName} 差异化竞争力分析
            </h1>
            {industry ? (
              <p className="text-base leading-7 text-warm-secondary">
                {industry}
              </p>
            ) : null}
          </div>
        </section>

        {competitiveness ? (
          <CompetitivenessPanel data={competitiveness} />
        ) : (
          <div className="card-inset">
            <p className="section-label">差异化竞争力</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              尚未生成差异化竞争力分析。请先完成前置步骤后再查看。
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
