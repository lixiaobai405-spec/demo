"use client";

import { useState } from "react";
import Link from "next/link";

import { AssessmentWorkbench } from "@/components/assessment-workbench";
import { InstructorDashboard } from "@/components/instructor-dashboard";

export default function AssessmentPage() {
  const [tab, setTab] = useState<"student" | "instructor">("student");

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
                {tab === "student" ? "企业问卷工作台" : "讲师工作台"}
              </h1>
              <p className="text-base leading-7 text-slate-300 sm:text-lg">
                {tab === "student"
                  ? "先收集企业基础信息、经营挑战和 AI 目标，再依次生成企业画像、商业画布、场景推荐，并进入案例匹配和报告预览。"
                  : "查看所有学员推进状态，按班级分组筛选，批量提交讲师点评，导出学员成果汇总。"}
              </p>
              {tab === "student" && (
                <p className="text-sm text-slate-400">
                  如果你已经有课前材料，可先进入
                  <Link href="/intake" className="ml-1 text-cyan-200 underline-offset-4 hover:underline">
                    导入预填模式
                  </Link>
                  ，再回到问卷确认。
                </p>
              )}
            </div>

            <div className="flex items-center gap-1 rounded-full border border-white/10 bg-slate-950/50 p-1">
              <button
                type="button"
                onClick={() => setTab("student")}
                className={`rounded-full px-5 py-2 text-sm font-medium transition ${
                  tab === "student"
                    ? "bg-cyan-400/20 text-cyan-100"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                学员视角
              </button>
              <button
                type="button"
                onClick={() => setTab("instructor")}
                className={`rounded-full px-5 py-2 text-sm font-medium transition ${
                  tab === "instructor"
                    ? "bg-indigo-400/20 text-indigo-100"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                讲师视角
              </button>
            </div>
          </div>
        </section>

        {tab === "student" ? <AssessmentWorkbench /> : <InstructorDashboard />}
      </div>
    </main>
  );
}
