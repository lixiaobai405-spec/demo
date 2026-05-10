import Link from "next/link";

import { ReportPreviewViewer } from "@/components/report-preview-viewer";

export default async function ReportGenerationPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = await params;

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 stagger">
        <section className="page-header">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-4xl space-y-4">
              <div className="flex flex-wrap gap-2">
                <Link href="/" className="btn-secondary text-xs">
                  ← 返回首页
                </Link>
                <Link href={`/assessment/${assessmentId}`} className="btn-secondary text-xs">
                  ← 返回 Assessment
                </Link>
              </div>
              <span className="badge badge-accent">Report Generation</span>
              <h1 className="font-heading text-4xl font-bold tracking-tight text-warm-text">
                报告生成与导出
              </h1>
              <p className="text-base leading-7 text-warm-secondary sm:text-lg">
                当前页面只负责检查报告前置条件、触发模板化报告生成，并跳转到正式的富文本报告预览页。
              </p>
            </div>

            <div className="rounded-xl border border-amber-200 bg-amber-50/70 px-6 py-4 text-sm text-amber-800">
              <p className="font-medium">Assessment ID</p>
              <p className="mt-2 break-all font-mono text-amber-700/90">{assessmentId}</p>
            </div>
          </div>
        </section>

        <ReportPreviewViewer assessmentId={assessmentId} />
      </div>
    </main>
  );
}
