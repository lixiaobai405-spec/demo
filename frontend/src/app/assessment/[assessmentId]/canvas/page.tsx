"use client";

import { use, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAssessmentDetail } from "@/hooks";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { BusinessCanvasGrid } from "@/components/business-canvas-grid";
import { CanvasEditor } from "@/components/canvas-editor";
import { SyncFeedbackPanel } from "@/components/sync-feedback-panel";
import type { CanvasDiagnosisResult } from "@/lib/types";

export default function CanvasPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = use(params);
  const router = useRouter();
  const detailQuery = useAssessmentDetail(assessmentId);
  const [isEditing, setIsEditing] = useState(false);
  const [editedCanvas, setEditedCanvas] = useState<CanvasDiagnosisResult | null>(null);

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
  const canvasDiagnosis = editedCanvas || detail.canvas_diagnosis;
  const companyName = detail.assessment.company_name;
  const industry = detail.assessment.industry;

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
          <>
            {/* Edit toggle */}
            <div className="flex items-center gap-3">
              <Button
                variant={isEditing ? "default" : "outline"}
                size="sm"
                onClick={() => setIsEditing(!isEditing)}
              >
                {isEditing ? "退出编辑" : "✏️ 手动编辑画布"}
              </Button>
              {isEditing && (
                <span className="text-xs text-warm-accent">
                  编辑模式下可直接修改每个模块的诊断内容
                </span>
              )}
            </div>

            {isEditing ? (
              <CanvasEditor
                assessmentId={assessmentId}
                canvasDiagnosis={canvasDiagnosis}
                onSaved={(updated) => {
                  setEditedCanvas(updated);
                  setIsEditing(false);
                  detailQuery.refetch();
                }}
              />
            ) : (
              <BusinessCanvasGrid canvasDiagnosis={canvasDiagnosis} />
            )}
          </>
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
          <h2 className="section-heading">BMC 突破要素评分</h2>
          <p className="mt-2 text-sm leading-7 text-muted-foreground">
            通过三维评分模型（痛点迫切度 × 数据基础度 × 实施可行度），
            科学评估九个画布模块的突破优先级，系统自动推荐 Top 3。
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Button
              onClick={() => router.push(`/assessment/${assessmentId}/scoring`)}
              disabled={!canvasDiagnosis}
            >
              进入 BMC 三维评分矩阵 →
            </Button>
          </div>
        </section>
      </div>

      {/* Sync feedback panel — always visible */}
      <SyncFeedbackPanel assessmentId={assessmentId} />
    </main>
  );
}
