"use client";

import { use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAssessmentDetail, useEndgame } from "@/hooks";
import { Button, buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { EndgamePanel } from "@/components/endgame-panel";

export default function EndgamePage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = use(params);
  const router = useRouter();
  const detailQuery = useAssessmentDetail(assessmentId);
  const endgameQuery = useEndgame(assessmentId);

  const isLoading = detailQuery.isLoading || endgameQuery.isLoading;

  // Loading
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

  // Error — detail query failed
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
  const endgameData = endgameQuery.data;

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
            <span className="badge badge-accent">私域 + 生态 + OPC</span>
            <h1 className="font-heading text-4xl font-bold tracking-tight text-warm-text sm:text-5xl">
              {companyName} 商业终局设计
            </h1>
            {industry ? (
              <p className="text-base leading-7 text-warm-secondary">
                {industry}
              </p>
            ) : null}
          </div>
        </section>

        {/* Endgame Content */}
        {endgameData ? (
          <EndgamePanel data={endgameData} />
        ) : (
          <div className="card-inset">
            <p className="section-label">商业终局设计</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              尚未生成商业终局设计。请先在画布诊断、创新方向和竞争力分析之后生成终局。
            </p>
            <Link
              href={`/assessment/${assessmentId}`}
              className="inline-block mt-3 btn-primary text-xs"
            >
              返回工作台
            </Link>
          </div>
        )}

        {/* Next step */}
        <section className="card">
          <p className="section-label">下一步</p>
          <h2 className="section-heading">结果仪表盘</h2>
          <p className="mt-2 text-sm leading-7 text-muted-foreground">
            在结果仪表盘中查看所有评估产出的全景视图，包括企业画像、画布诊断、
            场景推荐、竞争力分析和商业终局设计，并生成完整报告。
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Button
              onClick={() =>
                router.push(`/assessment/${assessmentId}/results`)
              }
            >
              查看结果仪表盘 →
            </Button>
            <Link
              href={`/assessment/${assessmentId}/canvas`}
              className={buttonVariants({ variant: "outline" })}
            >
              商业画布 9 格
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
