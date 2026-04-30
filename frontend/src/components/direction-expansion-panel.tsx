"use client";

import type {
  AssessmentDirectionResponse,
  DirectionSuggestion,
} from "@/lib/types";

export function DirectionExpansionPanel({
  data,
  selectedIds,
  isSelecting,
  onToggleDirection,
  onConfirmSelection,
}: {
  data: AssessmentDirectionResponse;
  selectedIds: string[];
  isSelecting: boolean;
  onToggleDirection: (id: string) => void;
  onConfirmSelection: () => void;
}) {
  const { direction_expansion, direction_selection } = data;
  const hasExistingSelection =
    direction_selection !== null &&
    direction_selection.selected_directions.length > 0;

  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Direction Expansion
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            创新方向延展
          </h2>
        </div>
        <span className="inline-flex rounded-full bg-sky-300/15 px-3 py-1 text-sm font-medium text-sky-100">
          共 {direction_expansion.total_suggestions} 个方向
        </span>
      </div>

      {hasExistingSelection ? (
        <div className="mt-6">
          <p className="text-sm font-medium text-emerald-100">
            已选择 {direction_selection.selected_directions.length} 个创新方向
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {direction_selection.selected_directions.map((dir) => (
              <DirectionCard
                key={dir.direction_id}
                direction={dir}
                isSelected
                showToggle={false}
                onToggle={() => {}}
              />
            ))}
          </div>
          <p className="mt-4 text-sm text-slate-400">
            若需重新选择，请重新提交突破要素以清空当前选择。
          </p>
        </div>
      ) : (
        <>
          <div className="mt-6 rounded-3xl border border-sky-300/20 bg-sky-300/5 p-5">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
              延展说明
            </p>
            <p className="mt-3 text-sm leading-7 text-slate-200">
              基于您选定的突破要素，系统为每个要素生成了{" "}
              {direction_expansion.total_suggestions} 个具体创新方向。请勾选
              1-6 个最符合企业当前实际情况的方向，这些方向将影响后续的场景推荐和报告生成。
            </p>
          </div>

          {direction_expansion.elements.length === 0 ? (
            <p className="mt-6 text-sm text-slate-400">
              暂无可延展方向，请先完成突破要素选择。
            </p>
          ) : (
            direction_expansion.elements.map((element) => (
              <div key={element.element_key} className="mt-6">
                <div className="flex items-center gap-3">
                  <span className="rounded-full border border-sky-300/30 bg-sky-300/10 px-3 py-1 text-sm font-medium text-sky-100">
                    {element.element_title}
                  </span>
                  <span className="text-xs text-slate-400">
                    {element.suggestions.length} 个方向
                  </span>
                </div>
                <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  {element.suggestions.map((dir) => (
                    <DirectionCard
                      key={dir.direction_id}
                      direction={dir}
                      isSelected={selectedIds.includes(dir.direction_id)}
                      showToggle
                      onToggle={() => onToggleDirection(dir.direction_id)}
                    />
                  ))}
                </div>
              </div>
            ))
          )}

          {direction_expansion.elements.length > 0 && (
            <div className="mt-6 flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={onConfirmSelection}
                disabled={
                  isSelecting || selectedIds.length < 1 || selectedIds.length > 6
                }
                className="inline-flex items-center justify-center rounded-full bg-sky-300 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-sky-200 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSelecting
                  ? "保存中..."
                  : selectedIds.length < 1
                    ? "请至少选择 1 个方向"
                    : selectedIds.length > 6
                      ? `最多选择 6 个方向（已选 ${selectedIds.length}）`
                      : `确认选择（${selectedIds.length} 个方向）`}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function DirectionCard({
  direction,
  isSelected,
  showToggle,
  onToggle,
}: {
  direction: DirectionSuggestion;
  isSelected: boolean;
  showToggle: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      disabled={!showToggle}
      className={`rounded-3xl border bg-slate-950/60 p-5 text-left transition ${
        isSelected
          ? "border-sky-300/40 bg-sky-300/10 ring-1 ring-sky-300/20"
          : "border-white/8 hover:border-white/15"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <p className="text-sm font-semibold text-white">{direction.title}</p>
          <p className="mt-2 text-xs leading-5 text-slate-400">
            {direction.description}
          </p>
        </div>
        {isSelected && (
          <span className="inline-flex flex-shrink-0 rounded-full border border-emerald-300/30 bg-emerald-300/10 px-2 py-0.5 text-[10px] text-emerald-100">
            已选
          </span>
        )}
      </div>

      <div className="mt-3 space-y-2">
        <div>
          <p className="text-[11px] uppercase tracking-[0.15em] text-slate-500">
            预期影响
          </p>
          <p className="mt-1 text-xs leading-5 text-slate-400">
            {direction.expected_impact}
          </p>
        </div>
        {direction.data_needed.length > 0 && (
          <div>
            <p className="text-[11px] uppercase tracking-[0.15em] text-slate-500">
              所需数据
            </p>
            <div className="mt-1 flex flex-wrap gap-1">
              {direction.data_needed.slice(0, 3).map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-[10px] text-slate-400"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </button>
  );
}
