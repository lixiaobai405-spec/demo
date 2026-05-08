"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { AssessmentWorkspace } from "@/components/assessment-workspace";
import { InstructorDashboard } from "@/components/instructor-dashboard";

function AssessmentPageContent() {
  const [tab, setTab] = useState<"student" | "instructor">("student");
  const searchParams = useSearchParams();
  const prefillSessionId = searchParams.get("import_session_id")?.trim() || undefined;

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
                企业问卷 / 企业画像 / 商业画布 / AI 场景 / 案例 / 报告
              </span>
              <h1 className="font-heading text-4xl font-semibold tracking-tight text-warm-text">
                {tab === "student" ? "企业问卷工作台" : "讲师工作台"}
              </h1>
              <p className="text-base leading-7 text-warm-secondary sm:text-lg">
                {tab === "student"
                  ? "先收集企业基础信息、经营挑战和 AI 目标，再依次生成企业画像、商业画布、场景推荐，并进入案例匹配和报告预览。"
                  : "查看所有学员推进状态，按班级分组筛选，批量提交讲师点评，导出学员成果汇总。"}
              </p>
              {tab === "student" && (
                <p className="text-sm text-warm-muted">
                  如果你已经有课前材料，可先进入
                  <Link
                    href="/intake"
                    className="ml-1 font-medium text-warm-accent underline underline-offset-4"
                  >
                    导入预填模式
                  </Link>
                  ，再回到问卷确认。
                </p>
              )}
            </div>

            <div className="flex items-center gap-1 rounded-full border border-warm-border bg-warm-inset p-1">
              <button
                type="button"
                onClick={() => setTab("student")}
                className={`rounded-full px-5 py-2 text-sm font-medium transition ${
                  tab === "student"
                    ? "bg-warm-accent text-white shadow-sm"
                    : "text-warm-muted hover:text-warm-text"
                }`}
              >
                学员视角
              </button>
              <button
                type="button"
                onClick={() => setTab("instructor")}
                className={`rounded-full px-5 py-2 text-sm font-medium transition ${
                  tab === "instructor"
                    ? "bg-warm-accent text-white shadow-sm"
                    : "text-warm-muted hover:text-warm-text"
                }`}
              >
                讲师视角
              </button>
            </div>
          </div>
        </section>

        {tab === "student" ? (
          <AssessmentWorkspace prefillSessionId={prefillSessionId} />
        ) : (
          <InstructorDashboard />
        )}
      </div>
    </main>
  );
}

function AssessmentPageFallback() {
  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 stagger">
        <section className="page-header">
          <div className="max-w-4xl space-y-4">
            <Link href="/" className="btn-secondary text-xs">
              ← 返回首页
            </Link>
            <span className="badge badge-accent">
              企业问卷 / 企业画像 / 商业画布 / AI 场景 / 案例 / 报告
            </span>
            <h1 className="font-heading text-4xl font-semibold tracking-tight text-warm-text">
              企业问卷工作台
            </h1>
            <p className="text-base leading-7 text-warm-secondary sm:text-lg">
              正在加载问卷工作台与课前材料预填信息...
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}

export default function AssessmentPage() {
  return (
    <Suspense fallback={<AssessmentPageFallback />}>
      <AssessmentPageContent />
    </Suspense>
  );
}
