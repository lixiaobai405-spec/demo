"use client";

import type { AssessmentDirectionResponse, DirectionSuggestion } from "@/lib/types";

export function DirectionExpansionPanel({
  data, selectedIds, isSelecting, onToggleDirection, onConfirmSelection,
}: {
  data: AssessmentDirectionResponse;
  selectedIds: string[];
  isSelecting: boolean;
  onToggleDirection: (id: string) => void;
  onConfirmSelection: () => void;
}) {
  const { direction_expansion, direction_selection } = data;
  const hasExistingSelection = direction_selection !== null && direction_selection.selected_directions.length > 0;

  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">延展结果</p>
          <h2 className="section-heading">创新方向延展</h2>
        </div>
        <span className="badge badge-accent">共 {direction_expansion.total_suggestions} 个方向</span>
      </div>

      {hasExistingSelection ? (
        <div className="mt-6">
          <p className="text-sm font-medium text-warm-success">已选择 {direction_selection.selected_directions.length} 个创新方向</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {direction_selection.selected_directions.map((dir) => (
              <DirectionCard key={dir.direction_id} direction={dir} isSelected showToggle={false} onToggle={() => {}} />
            ))}
          </div>
          <p className="mt-4 text-sm text-warm-muted">若需重新选择，请重新提交突破要素以清空当前选择。</p>
        </div>
      ) : (
        <>
          <div className="mt-6 rounded-xl border border-warm-accent/15 bg-warm-accent/5 p-5">
            <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">延展说明</p>
            <p className="mt-3 text-sm leading-7 text-warm-secondary">
              基于您选定的突破要素，系统为每个要素生成了 {direction_expansion.total_suggestions} 个具体创新方向。请勾选 1-6 个最符合企业当前实际情况的方向。
            </p>
          </div>

          {direction_expansion.elements.length === 0 ? (
            <p className="mt-6 text-sm text-warm-muted">暂无可延展方向，请先完成突破要素选择。</p>
          ) : (
            direction_expansion.elements.map((element) => (
              <div key={element.element_key} className="mt-6">
                <div className="flex items-center gap-3">
                  <span className="badge badge-accent">{element.element_title}</span>
                  <span className="text-xs text-warm-muted">{element.suggestions.length} 个方向</span>
                </div>
                <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  {element.suggestions.map((dir) => (
                    <DirectionCard key={dir.direction_id} direction={dir} isSelected={selectedIds.includes(dir.direction_id)} showToggle onToggle={() => onToggleDirection(dir.direction_id)} />
                  ))}
                </div>
              </div>
            ))
          )}

          {direction_expansion.elements.length > 0 && (
            <div className="mt-6 flex flex-wrap items-center gap-3">
              <button type="button" onClick={onConfirmSelection} disabled={isSelecting || selectedIds.length < 1 || selectedIds.length > 6} className="btn-primary">
                {isSelecting ? "保存中..." : selectedIds.length < 1 ? "请至少选择 1 个方向" : selectedIds.length > 6 ? `最多选择 6 个方向（已选 ${selectedIds.length}）` : `确认选择（${selectedIds.length} 个方向）`}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function DirectionCard({ direction, isSelected, showToggle, onToggle }: {
  direction: DirectionSuggestion; isSelected: boolean; showToggle: boolean; onToggle: () => void;
}) {
  return (
    <button type="button" onClick={onToggle} disabled={!showToggle}
      className={`rounded-xl border bg-warm-inset p-5 text-left transition ${
        isSelected ? "border-warm-accent/40 bg-warm-accent/5 ring-1 ring-warm-accent/15" : "border-warm-border-light hover:border-warm-border hover:shadow-card"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <p className="text-sm font-semibold text-warm-text">{direction.title}</p>
          <p className="mt-2 text-xs leading-5 text-warm-muted">{direction.description}</p>
        </div>
        {isSelected && <span className="badge badge-success text-xs">已选</span>}
      </div>
      <div className="mt-3 space-y-2">
        <div>
          <p className="text-[11px] uppercase tracking-[0.12em] text-warm-muted">预期影响</p>
          <p className="mt-1 text-xs leading-5 text-warm-muted">{direction.expected_impact}</p>
        </div>
        {direction.data_needed.length > 0 && (
          <div>
            <p className="text-[11px] uppercase tracking-[0.12em] text-warm-muted">所需数据</p>
            <div className="mt-1 flex flex-wrap gap-1">
              {direction.data_needed.slice(0, 3).map((item) => (
                <span key={item} className="rounded-full border border-warm-border-light bg-warm-surface px-2 py-0.5 text-[10px] text-warm-muted">{item}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </button>
  );
}
