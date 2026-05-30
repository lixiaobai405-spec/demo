import React from "react";

import type { CanvasDiagnosisResult } from "@/lib/types";

export function BusinessCanvasGrid({
  canvasDiagnosis,
}: {
  canvasDiagnosis: CanvasDiagnosisResult;
}) {
  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">画布诊断</p>
          <h2 className="section-heading">商业画布 9 格诊断</h2>
        </div>
        <span className="badge badge-success">
          {canvasDiagnosis.generation_mode === "mock" ? "模拟生成" : "真实生成"}
        </span>
      </div>

      <div className="mt-6 space-y-4">
        <section className="rounded-xl border border-warm-border-light bg-warm-inset p-6">
          <p className="text-xs font-medium uppercase tracking-[0.14em] text-warm-muted">
            总体摘要
          </p>
          <p className="mt-3 text-sm leading-7 text-warm-text">
            {canvasDiagnosis.canvas.overall_summary}
          </p>
        </section>

        <section className="rounded-xl border border-warm-border-light bg-warm-inset p-6">
          <p className="text-xs font-medium uppercase tracking-[0.14em] text-warm-muted">
            诊断概览
          </p>
          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            <ListSection
              title="当前薄弱模块"
              items={canvasDiagnosis.weakest_blocks}
              emptyLabel="暂无薄弱模块"
            />
            <ListSection
              title="建议优先动作"
              items={canvasDiagnosis.recommended_focus}
              emptyLabel="暂无建议动作"
              formatItem={formatRecommendedFocus}
            />
          </div>
        </section>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {canvasDiagnosis.canvas.blocks.map((block) => (
          <article
            key={block.key}
            className="rounded-xl border border-warm-border-light bg-warm-inset p-6"
          >
            <p className="text-xs font-medium uppercase tracking-[0.14em] text-warm-accent">
              {block.title}
            </p>
            <div className="mt-4 space-y-4 text-sm leading-7 text-warm-text">
              <CanvasDetail label="当前状态" content={block.current_state} />
              <CanvasDetail
                label="诊断判断"
                content={formatCompleteShortSentence(block.diagnosis, 100)}
              />
              <CanvasDetail
                label="AI 机会"
                content={formatCompleteShortSentence(block.ai_opportunity, 80)}
              />
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

function CanvasDetail({
  label,
  content,
}: {
  label: string;
  content: string;
}) {
  return (
    <div>
      <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">{label}</p>
      <p className="mt-2 text-sm leading-7 text-warm-secondary">{content}</p>
    </div>
  );
}

function ListSection({
  title,
  items,
  emptyLabel,
  formatItem = (item) => item,
}: {
  title: string;
  items: string[];
  emptyLabel: string;
  formatItem?: (item: string) => string;
}) {
  const visibleItems = items.filter((item) => item.trim().length > 0);

  return (
    <div className="rounded-xl bg-warm-surface px-4 py-4">
      <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">{title}</p>
      {visibleItems.length > 0 ? (
        <ul className="mt-3 space-y-2">
          {visibleItems.map((item, index) => (
            <li
              key={`${title}-${index}`}
              className="rounded-xl border border-warm-border-light bg-white px-4 py-3 text-sm text-warm-text"
            >
              {formatItem(item)}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-warm-muted">{emptyLabel}</p>
      )}
    </div>
  );
}

function formatRecommendedFocus(item: string): string {
  const withoutTail = item.split("——")[0]?.trim() ?? item.trim();
  const match = withoutTail.match(/^([^（(:：]+)(?:（[^）]*）)?[：:]\s*(.+)$/);

  if (!match) {
    return truncateText(withoutTail, 100);
  }

  const element = match[1].trim();
  const sentence = truncateText(match[2].trim(), 100);
  return `${element}：${sentence}`;
}

function truncateText(value: string, maxLength: number): string {
  return value.length > maxLength ? value.slice(0, maxLength) : value;
}

function formatCompleteShortSentence(value: string, maxLength: number): string {
  const cleaned = value.replace(/\s+/g, " ").trim();
  const sentence = firstCompleteSentence(cleaned, maxLength);

  if (sentence) {
    return sentence;
  }

  if (cleaned.length <= maxLength) {
    return ensureSentencePunctuation(cleaned);
  }

  return ensureSentencePunctuation(
    cleaned.slice(0, maxLength).replace(/[，；、：:,. ]+$/, ""),
  );
}

function firstCompleteSentence(value: string, maxLength: number): string {
  const match = value.match(/[。！？!?]/);
  if (!match || match.index === undefined) {
    return "";
  }

  const sentence = value.slice(0, match.index + match[0].length).trim();
  return sentence.length <= maxLength ? sentence : "";
}

function ensureSentencePunctuation(value: string): string {
  if (!value || /[。！？!?]$/.test(value)) {
    return value;
  }

  return `${value}。`;
}
