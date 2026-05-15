"use client";

import { use, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAssessmentDetail, useExpandDirections } from "@/hooks";
import { useGetBMCScoring } from "@/hooks/use-bmc-scoring";
import { toast } from "@/hooks/use-toast";
import { formatMutationError } from "@/lib/api";
import { BmcScoringMatrix } from "@/components/bmc-scoring-matrix";
import { Button, buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export default function ScoringPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = use(params);
  const router = useRouter();
  const detailQuery = useAssessmentDetail(assessmentId);
  const savedScoringQuery = useGetBMCScoring(assessmentId);
  const expandDirections = useExpandDirections();

  const hasBreakthrough =
    !!detailQuery.data?.breakthrough_selection &&
    detailQuery.data.breakthrough_selection.length >= 2;

  const handleGenerateDirections = useCallback(async () => {
    try {
      await expandDirections.mutateAsync(assessmentId);
      toast({ title: "创新方向延展已生成" });
      router.push(`/assessment/${assessmentId}/directions`);
    } catch (e) {
      toast({
        title: "生成失败",
        description: formatMutationError(e, "创新方向延展"),
        variant: "destructive",
      });
    }
  }, [assessmentId, expandDirections, router]);

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
            <Button variant="outline" size="sm" onClick={() => detailQuery.refetch()}>
              重试
            </Button>
          </div>
        </div>
      </main>
    );
  }

  const detail = detailQuery.data;
  const companyName = detail.assessment.company_name;
  const canvasDiagnosis = detail.canvas_diagnosis;
  const hasSavedScoring = savedScoringQuery.data?.scoring_result ?? null;

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
              <Link href={`/assessment/${assessmentId}`} className="btn-secondary text-xs">
                ← 返回工作台
              </Link>
            </div>
            <span className="badge badge-accent">BMC 三维突破要素评分</span>
            <h1 className="font-heading text-4xl font-bold tracking-tight text-warm-text sm:text-5xl">
              {companyName} · 突破要素评分矩阵
            </h1>
            <p className="text-base leading-7 text-warm-secondary">
              通过三维评分模型评估九个商业画布模块的突破优先级：
              <strong>痛点迫切度（Pain）</strong>——该业务问题对企业经营的威胁程度与改善紧迫性；
              <strong>数据基础度（Data）</strong>——该环节的数据积累质量，决定 AI 模型能否被训练落地；
              <strong>实施可行度（Feasibility）</strong>——启动 AI 改造的组织意愿、技术门槛与资源匹配度。
              拖动滑块调整评分，查看实时优先级矩阵定位与推荐结论。
            </p>
          </div>
        </section>

        {/* Canvas check */}
        {!canvasDiagnosis ? (
          <div className="card-inset">
            <p className="section-label">画布诊断</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              尚未生成商业画布诊断。请先完成企业画像和画布诊断后再进行突破要素评分。
            </p>
            <Link href={`/assessment/${assessmentId}`} className="inline-block mt-3 btn-primary text-xs">
              返回工作台
            </Link>
          </div>
        ) : (
          <BmcScoringMatrix
            assessmentId={assessmentId}
            existingScoring={hasSavedScoring}
            canvasDiagnosis={canvasDiagnosis}
          />
        )}

        {/* Next step: 创新方向延展 */}
        <section className="card">
          <p className="section-label">下一步</p>
          <h2 className="section-heading">创新方向延展</h2>
          <p className="mt-2 text-sm leading-7 text-muted-foreground">
            {hasBreakthrough
              ? "突破要素已锁定，点击下方按钮生成创新方向延展并跳转方向分析页面。"
              : "请先在上方保存 BMC 突破要素评分（选择 2-3 个模块并点击保存），再生成创新方向延展。"}
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Button
              onClick={handleGenerateDirections}
              disabled={!hasBreakthrough || expandDirections.isPending}
              loading={expandDirections.isPending}
            >
              {expandDirections.isPending
                ? "正在生成创新方向延展..."
                : "生成创新方向延展 →"}
            </Button>
            <Link
              href={`/assessment/${assessmentId}/directions`}
              className={buttonVariants({ variant: "outline" })}
            >
              查看创新方向延展
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
