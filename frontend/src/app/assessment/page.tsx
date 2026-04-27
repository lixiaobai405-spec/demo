import Link from "next/link";

import { AssessmentWorkbench } from "@/components/assessment-workbench";

export default function AssessmentPage() {
  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8">
        <section className="rounded-[32px] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-slate-950/30 backdrop-blur">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-4xl space-y-4">
              <Link
                href="/"
                className="inline-flex w-fit items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 transition hover:bg-white/10"
              >
                返回首页
              </Link>
              <span className="inline-flex w-fit rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-sm text-cyan-100">
                企业问卷 / 企业画像 / 商业画布 / AI 场景 / 案例 / 报告
              </span>
              <h1 className="text-4xl font-semibold tracking-tight text-white">
                企业问卷工作台
              </h1>
              <p className="text-base leading-7 text-slate-300 sm:text-lg">
                先收集企业基础信息、经营挑战和 AI 目标，再依次生成企业画像、商业画布、
                场景推荐，并进入案例匹配和报告预览。
              </p>
            </div>

            <div className="rounded-3xl border border-amber-300/30 bg-amber-300/10 px-5 py-4 text-sm text-amber-50">
              <p className="font-medium">当前阶段范围</p>
              <p className="mt-2 text-amber-100/90">
                当前阶段已包含问卷、画像、画布、场景推荐、案例匹配和最终报告预览。
              </p>
            </div>
          </div>
        </section>

        <AssessmentWorkbench />
      </div>
    </main>
  );
}
