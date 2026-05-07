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
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 stagger">
        <section className="page-header">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-4xl space-y-4">
              <Link href="/assessment" className="btn-secondary text-xs">
                ← 返回 Assessment 列表入口
              </Link>
              <span className="badge badge-success">HTML Report Preview</span>
              <h1 className="font-heading text-4xl font-semibold tracking-tight text-warm-text">
                富文本报告预览页
              </h1>
              <p className="text-base leading-7 text-warm-secondary sm:text-lg">
                这里展示已经保存到数据库的 HTML 报告内容，并提供 Markdown、Word 和打印版导出能力。
              </p>
            </div>

            <div className="rounded-xl border border-amber-200 bg-amber-50/70 px-5 py-4 text-sm text-amber-800">
              <p className="font-medium">Report ID</p>
              <p className="mt-2 break-all font-mono text-amber-700/90">{reportId}</p>
            </div>
          </div>
        </section>

        <ReportDocumentViewer reportId={reportId} />
      </div>
    </main>
  );
}
