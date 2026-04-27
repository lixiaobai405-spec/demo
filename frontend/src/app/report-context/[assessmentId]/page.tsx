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
                Report Context
              </span>
              <h1 className="text-4xl font-semibold tracking-tight text-white">
                报告上下文页
              </h1>
              <p className="text-base leading-7 text-slate-300 sm:text-lg">
                这里仅聚合报告生成所需的结构化上下文，不调用 LLM，也不直接生成最终报告。
              </p>
            </div>

            <div className="rounded-3xl border border-amber-300/30 bg-amber-300/10 px-5 py-4 text-sm text-amber-50">
              <p className="font-medium">Assessment ID</p>
              <p className="mt-2 break-all text-amber-100/90">{assessmentId}</p>
            </div>
          </div>
        </section>

        <ReportContextViewer assessmentId={assessmentId} />
      </div>
    </main>
  );
}
