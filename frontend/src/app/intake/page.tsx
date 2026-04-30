import Link from "next/link";

import { IntakeWorkbench } from "@/components/intake-workbench";

export default function IntakePage() {
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
                课前输入 / 导入预填 / 人工确认
              </span>
              <h1 className="text-4xl font-semibold tracking-tight text-white">
                课前材料导入工作台
              </h1>
              <p className="text-base leading-7 text-slate-300 sm:text-lg">
                通过文本或 Markdown 导入企业课前材料，先生成问卷预填建议，再进入后续确认与正式创建流程。
              </p>
            </div>

            <div className="rounded-3xl border border-amber-300/30 bg-amber-300/10 px-5 py-4 text-sm text-amber-50">
              <p className="font-medium">当前阶段范围</p>
              <p className="mt-2 text-amber-100/90">
                当前页面用于验证导入回显闭环，后续会继续补充字段编辑与“确认创建问卷”交互。
              </p>
            </div>
          </div>
        </section>

        <IntakeWorkbench />
      </div>
    </main>
  );
}
