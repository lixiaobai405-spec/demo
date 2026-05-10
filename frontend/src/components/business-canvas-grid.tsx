import type { CanvasDiagnosisResult } from "@/lib/types";

export function BusinessCanvasGrid({ canvasDiagnosis }: { canvasDiagnosis: CanvasDiagnosisResult }) {
  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">画布诊断</p>
          <h2 className="section-heading">商业画布 9 格诊断</h2>
        </div>
        <span className="badge badge-success">
          {canvasDiagnosis.generation_mode === "mock" ? "模拟" : "真实"}
        </span>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-xl border border-warm-border-light bg-warm-inset p-6">
          <p className="text-xs font-medium uppercase tracking-[0.14em] text-warm-muted">总体摘要</p>
          <p className="mt-3 text-sm leading-7 text-warm-text">{canvasDiagnosis.canvas.overall_summary}</p>
        </div>
        <div className="rounded-xl border border-warm-border-light bg-warm-inset p-6">
          <p className="text-xs font-medium uppercase tracking-[0.14em] text-warm-muted">诊断概览</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <Metric label="Overall Score" value={`${canvasDiagnosis.overall_score}`} />
            <Metric label="Weakest Blocks" value={`${canvasDiagnosis.weakest_blocks.length}`} />
            <Metric label="Focus Areas" value={`${canvasDiagnosis.recommended_focus.length}`} />
          </div>
          <ListSection title="薄弱模块" items={canvasDiagnosis.weakest_blocks} className="mt-4" />
          <ListSection title="建议优先动作" items={canvasDiagnosis.recommended_focus} className="mt-4" />
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {canvasDiagnosis.canvas.blocks.map((block) => (
          <div key={block.key} className="rounded-xl border border-warm-border-light bg-warm-inset p-6">
            <p className="text-xs font-medium uppercase tracking-[0.14em] text-warm-accent">{block.title}</p>
            <div className="mt-4 space-y-4 text-sm leading-7 text-warm-text">
              <CanvasDetail label="当前状态" content={block.current_state} />
              <CanvasDetail label="诊断" content={block.diagnosis} />
              <CanvasDetail label="AI 机会" content={block.ai_opportunity} />
              <CanvasDetail label="待补充" content={block.missing_information} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CanvasDetail({ label, content }: { label: string; content: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">{label}</p>
      <p className="mt-2 text-sm leading-7 text-warm-secondary">{content}</p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-warm-surface px-4 py-3">
      <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">{label}</p>
      <p className="mt-2 text-xl font-semibold text-warm-text">{value}</p>
    </div>
  );
}

function ListSection({ title, items, className }: { title: string; items: string[]; className?: string }) {
  return (
    <div className={className}>
      <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">{title}</p>
      <ul className="mt-3 space-y-2">
        {items.map((item, i) => (
          <li key={`${title}-${i}`} className="rounded-xl bg-warm-surface px-4 py-3 text-sm text-warm-text">{item}</li>
        ))}
      </ul>
    </div>
  );
}
