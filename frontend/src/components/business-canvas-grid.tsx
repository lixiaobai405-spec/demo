import type { CanvasDiagnosisResult } from "@/lib/types";

export function BusinessCanvasGrid({
  canvasDiagnosis,
}: {
  canvasDiagnosis: CanvasDiagnosisResult;
}) {
  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Business Model Canvas
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            商业画布 9 格诊断
          </h2>
        </div>

        <span className="inline-flex rounded-full bg-emerald-300/15 px-3 py-1 text-sm font-medium text-emerald-100">
          {canvasDiagnosis.generation_mode === "mock" ? "Mock" : "Live"}
        </span>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-3xl border border-white/8 bg-slate-950/55 p-5">
          <p className="text-sm uppercase tracking-[0.18em] text-slate-400">
            Overall Summary
          </p>
          <p className="mt-3 text-sm leading-7 text-slate-200">
            {canvasDiagnosis.canvas.overall_summary}
          </p>
        </div>

        <div className="rounded-3xl border border-white/8 bg-slate-950/55 p-5">
          <p className="text-sm uppercase tracking-[0.18em] text-slate-400">
            Diagnosis Meta
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <Metric label="Overall Score" value={`${canvasDiagnosis.overall_score}`} />
            <Metric
              label="Weakest Blocks"
              value={`${canvasDiagnosis.weakest_blocks.length}`}
            />
            <Metric
              label="Focus Areas"
              value={`${canvasDiagnosis.recommended_focus.length}`}
            />
          </div>
          <ListSection
            title="薄弱模块"
            items={canvasDiagnosis.weakest_blocks}
            className="mt-4"
          />
          <ListSection
            title="建议优先动作"
            items={canvasDiagnosis.recommended_focus}
            className="mt-4"
          />
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {canvasDiagnosis.canvas.blocks.map((block) => (
          <div
            key={block.key}
            className="rounded-3xl border border-white/8 bg-slate-950/55 p-5"
          >
            <p className="text-sm uppercase tracking-[0.18em] text-cyan-100">
              {block.title}
            </p>
            <div className="mt-4 space-y-4 text-sm leading-7 text-slate-200">
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

function CanvasDetail({
  label,
  content,
}: {
  label: string;
  content: string;
}) {
  return (
    <div>
      <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
        {label}
      </p>
      <p className="mt-2 text-sm leading-7 text-slate-200">{content}</p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-white/5 px-4 py-3">
      <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
        {label}
      </p>
      <p className="mt-2 text-xl font-semibold text-white">{value}</p>
    </div>
  );
}

function ListSection({
  title,
  items,
  className,
}: {
  title: string;
  items: string[];
  className?: string;
}) {
  return (
    <div className={className}>
      <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
        {title}
      </p>
      <ul className="mt-3 space-y-2 text-sm leading-7 text-slate-200">
        {items.map((item, index) => (
          <li
            key={`${title}-${index}`}
            className="rounded-2xl bg-white/5 px-4 py-3"
          >
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
