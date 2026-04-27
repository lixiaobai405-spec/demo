import Link from "next/link";

import { HealthStatusCard } from "@/components/health-status-card";

const milestoneItems = [
  "创建企业问卷",
  "生成企业画像",
  "生成商业画布 9 格诊断",
  "生成 Top 3 AI 场景推荐",
  "匹配匿名行业参考案例",
  "生成 Markdown / HTML 报告",
  "下载 Word / Markdown / 打印版",
];

export default function Home() {
  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8">
        <section className="rounded-[32px] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-slate-950/30 backdrop-blur">
          <div className="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl space-y-4">
              <span className="inline-flex w-fit rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-sm text-cyan-100">
                Stage 4 / Report Layout + Export
              </span>
              <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                美太 AI 商业创新智能体 Demo
              </h1>
              <p className="text-base leading-7 text-slate-300 sm:text-lg">
                当前 Demo 已打通企业问卷、企业画像、商业画布诊断、AI 场景推荐、案例匹配、报告生成和基础导出链路，
                可作为后续 RAG 与案例检索增强的稳定底座。
              </p>
            </div>

            <div className="flex flex-col gap-3 lg:items-end">
              <Link
                href="/assessment"
                className="inline-flex items-center justify-center rounded-full bg-cyan-300 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
              >
                开始企业问卷
              </Link>
              <p className="text-sm text-slate-400">
                当前已支持问卷、画像、画布、场景、案例、报告与导出
              </p>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <HealthStatusCard />

          <div className="rounded-[28px] border border-white/10 bg-slate-900/70 p-6">
            <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
              Current Scope
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-white">
              当前 Demo 已打通的链路
            </h2>
            <ul className="mt-5 space-y-3 text-sm leading-6 text-slate-300">
              {milestoneItems.map((item, index) => (
                <li
                  key={item}
                  className="flex items-center gap-3 rounded-2xl border border-white/8 bg-white/5 px-4 py-3"
                >
                  <span className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-300/15 text-xs font-semibold text-emerald-100">
                    {index + 1}
                  </span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </div>
    </main>
  );
}
