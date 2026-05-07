import Link from "next/link";

import { AssessmentWorkbench } from "@/components/assessment-workbench";

export default async function AssessmentDetailPage({
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
              <Link href="/" className="btn-secondary text-xs">
                ← 返回首页
              </Link>
              <span className="badge badge-accent">
                Assessment 回看 / 状态恢复
              </span>
              <h1 className="font-heading text-4xl font-semibold tracking-tight text-warm-text">
                企业问卷工作台
              </h1>
              <p className="text-base leading-7 text-warm-secondary sm:text-lg">
                当前页面会根据 URL 中的 assessment_id 恢复企业画像、商业画布、
                场景推荐、案例匹配和报告状态，支持刷新回看与重新生成。
              </p>
            </div>

            <div className="rounded-xl border border-amber-200 bg-amber-50/70 px-5 py-4 text-sm text-amber-800">
              <p className="font-medium">当前 Assessment</p>
              <p className="mt-2 break-all font-mono text-amber-700/90">{assessmentId}</p>
            </div>
          </div>
        </section>

        <AssessmentWorkbench assessmentId={assessmentId} />
      </div>
    </main>
  );
}
