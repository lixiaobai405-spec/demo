import Link from "next/link";

import { ReportDocumentViewer } from "@/components/report-document-viewer";

export default async function ReportDocumentPage({
  params,
}: {
  params: Promise<{ reportId: string }>;
}) {
  const { reportId } = await params;

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8">
        <section className="rounded-[32px] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-slate-950/30 backdrop-blur">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-4xl space-y-4">
              <Link
                href="/assessment"
                className="inline-flex w-fit items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 transition hover:bg-white/10"
              >
                返回 Assessment 列表入口
              </Link>
              <span className="inline-flex w-fit rounded-full border border-emerald-300/30 bg-emerald-300/10 px-3 py-1 text-sm text-emerald-100">
                HTML Report Preview
              </span>
              <h1 className="text-4xl font-semibold tracking-tight text-white">
                富文本报告预览页
              </h1>
              <p className="text-base leading-7 text-slate-300 sm:text-lg">
                这里展示已经保存到数据库的 HTML 报告内容，并提供 Markdown、Word 和打印版导出能力。
              </p>
            </div>

            <div className="rounded-3xl border border-amber-300/30 bg-amber-300/10 px-5 py-4 text-sm text-amber-50">
              <p className="font-medium">Report ID</p>
              <p className="mt-2 break-all text-amber-100/90">{reportId}</p>
            </div>
          </div>
        </section>

        <ReportDocumentViewer reportId={reportId} />
      </div>
    </main>
  );
}
