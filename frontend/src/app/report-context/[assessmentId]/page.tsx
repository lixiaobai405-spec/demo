import Link from "next/link";

import { ReportContextViewer } from "@/components/report-context-viewer";

export default async function ReportContextPage({
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
              <span className="badge badge-accent">Report Context</span>
              <h1 className="font-heading text-4xl font-bold tracking-tight text-warm-text">
                报告上下文页
              </h1>
              <p className="text-base leading-7 text-warm-secondary sm:text-lg">
                这里仅聚合报告生成所需的结构化上下文，不调用 LLM，也不直接生成最终报告。
              </p>
            </div>

            <div className="rounded-xl border border-amber-200 bg-amber-50/70 px-6 py-4 text-sm text-amber-800">
              <p className="font-medium">Assessment ID</p>
              <p className="mt-2 break-all font-mono text-amber-700/90">{assessmentId}</p>
            </div>
          </div>
        </section>

        <ReportContextViewer assessmentId={assessmentId} />
      </div>
    </main>
  );
}
