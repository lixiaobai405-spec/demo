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
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8">
        <section className="rounded-[32px] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-slate-950/30 backdrop-blur">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-4xl space-y-4">
              <Link
                href={`/assessment/${assessmentId}`}
                className="inline-flex w-fit items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 transition hover:bg-white/10"
              >
                返回 Assessment
              </Link>
              <span className="inline-flex w-fit rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-sm text-cyan-100">
                Report Generation
              </span>
              <h1 className="text-4xl font-semibold tracking-tight text-white">
                报告生成与导出
              </h1>
              <p className="text-base leading-7 text-slate-300 sm:text-lg">
                当前页面只负责检查报告前置条件、触发模板化报告生成，并跳转到正式的富文本报告预览页。
              </p>
            </div>

            <div className="rounded-3xl border border-amber-300/30 bg-amber-300/10 px-5 py-4 text-sm text-amber-50">
              <p className="font-medium">Assessment ID</p>
              <p className="mt-2 break-all text-amber-100/90">{assessmentId}</p>
            </div>
          </div>
        </section>

        <ReportPreviewViewer assessmentId={assessmentId} />
      </div>
    </main>
  );
}
