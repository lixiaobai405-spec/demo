import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import { HealthStatusCard } from "@/components/health-status-card";
import { LLMConfigCard } from "@/components/llm-config-card";

const milestoneItems = [
  "创建企业问卷",
  "生成企业画像",
  "生成商业画布 9 格诊断",
  "生成 Top 3 AI 场景推荐",
  "生成 Markdown / HTML 报告",
  "下载 Word / Markdown / 打印版",
];

export default function Home() {
  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 stagger">
        {/* Hero */}
        <section className="page-header">
          <div className="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl space-y-6">
              <span className="badge badge-accent">
                Stage 4 / Report Layout + Export
              </span>
              <h1 className="font-heading text-4xl font-bold tracking-tight text-warm-text sm:text-5xl">
                美太 AI 商业创新智能体 Demo
              </h1>
              <p className="text-base leading-7 text-warm-secondary sm:text-lg">
                当前 Demo 已打通企业问卷、企业画像、商业画布诊断、AI 场景推荐、报告生成和基础导出链路，
                可作为后续 RAG 与案例检索增强的稳定底座。
              </p>
            </div>

            <div className="flex flex-col gap-3 lg:items-end">
              <div className="flex flex-wrap gap-3 lg:justify-end">
                <Link href="/intake" className={buttonVariants({ variant: "outline" })}>
                  导入课前材料
                </Link>
                <Link href="/assessment" className={buttonVariants()}>
                  开始企业问卷
                </Link>
              </div>
              <p className="text-sm text-warm-muted">
                当前已支持快速填写与导入预填两种入口
              </p>
            </div>
          </div>

          {/* 点线面方法 */}
          <div className="mt-8 grid gap-3 border-t border-warm-border-light pt-6 md:grid-cols-3">
            <div className="rounded-2xl border border-warm-border-light bg-warm-surface/70 p-4">
              <span className="badge badge-accent">点</span>
              <h3 className="mt-3 font-heading text-lg font-semibold text-warm-text">AI 场景切入</h3>
              <p className="mt-2 text-sm leading-6 text-warm-secondary">从企业问卷、画像和商业画布中识别最值得启动的 AI 场景。</p>
            </div>
            <div className="rounded-2xl border border-warm-border-light bg-warm-surface/70 p-4">
              <span className="badge badge-accent">线</span>
              <h3 className="mt-3 font-heading text-lg font-semibold text-warm-text">业务链路串联</h3>
              <p className="mt-2 text-sm leading-6 text-warm-secondary">将场景、案例、报告和后续行动串成一条可执行的转型路径。</p>
            </div>
            <div className="rounded-2xl border border-warm-border-light bg-warm-surface/70 p-4">
              <span className="badge badge-accent">面</span>
              <h3 className="mt-3 font-heading text-lg font-semibold text-warm-text">能力底座沉淀</h3>
              <p className="mt-2 text-sm leading-6 text-warm-secondary">为后续 RAG、案例检索、讲师工作台和复盘运营提供统一基础。</p>
            </div>
          </div>
        </section>

        {/* Health + Scope */}
        <section className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <HealthStatusCard />

          <div className="card-inset">
            <p className="section-label">当前范围</p>
            <h2 className="section-heading">当前 Demo 已打通的链路</h2>
            <ul className="mt-6 space-y-2.5">
              {milestoneItems.map((item, index) => (
                <li
                  key={item}
                  className="flex items-center gap-3 rounded-xl border border-warm-border-light bg-warm-surface px-4 py-3 text-sm text-warm-text"
                >
                  <span className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-warm-success/10 text-xs font-semibold text-warm-success">
                    {index + 1}
                  </span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* LLM Config */}
        <section>
          <LLMConfigCard />
        </section>
      </div>
    </main>
  );
}
