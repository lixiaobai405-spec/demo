"use client";

import React from "react";

import type {
  AssessmentDirectionResponse,
  DirectionSuggestion,
} from "@/lib/types";

export function DirectionExpansionPanel({
  data,
  selectedIds,
  isSelecting,
  isLLMPending,
  onToggleDirection,
  onConfirmSelection,
  onNextStep,
}: {
  data: AssessmentDirectionResponse;
  selectedIds: string[];
  isSelecting: boolean;
  isLLMPending?: boolean;
  onToggleDirection: (id: string) => void;
  onConfirmSelection: () => void;
  onNextStep?: () => void;
}) {
  const { direction_expansion, direction_selection } = data;
  const seenDirectionIds = new Set<string>();
  const normalizedElements = direction_expansion.elements.map((element) => ({
    ...element,
    suggestions: element.suggestions.filter((direction) => {
      if (seenDirectionIds.has(direction.direction_id)) {
        return false;
      }
      seenDirectionIds.add(direction.direction_id);
      return true;
    }),
  }));
  const currentDirectionIdSet = new Set(
    normalizedElements.flatMap((element) =>
      element.suggestions.map((direction) => direction.direction_id),
    ),
  );
  const visibleSelectedDirections =
    direction_selection?.selected_directions.filter((direction) =>
      currentDirectionIdSet.has(direction.direction_id),
    ) ?? [];
  const hasExistingSelection = visibleSelectedDirections.length > 0;
  const displayedSuggestionCount = currentDirectionIdSet.size;
  const visibleSelectedIds = selectedIds.filter((id) =>
    currentDirectionIdSet.has(id),
  );

  if (isLLMPending) {
    return (
      <div className="card">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="section-label">方向候选</p>
            <h2 className="section-heading">创新方向延展</h2>
          </div>
          <span className="badge badge-warning animate-pulse text-xs">
            生成中
          </span>
        </div>

        <div className="mt-6 rounded-xl border border-warm-accent/15 bg-warm-accent/5 p-6">
          <p className="text-sm font-medium text-warm-text">AI 正在生成方向候选</p>
          <p className="mt-3 text-sm leading-7 text-warm-secondary">
            方向生成完成后，页面会自动刷新并展示当前可选候选池。
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">方向候选</p>
          <h2 className="section-heading">创新方向延展</h2>
        </div>
        <span className="badge badge-accent">
          共 {displayedSuggestionCount} 个候选
        </span>
      </div>

      {hasExistingSelection ? (
        <div className="mt-6">
          <p className="text-sm font-medium text-warm-success">
            已确认 {visibleSelectedDirections.length} 个创新方向
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {visibleSelectedDirections.map((direction) => (
              <DirectionCard
                key={direction.direction_id}
                direction={direction}
                isSelected
                showToggle={false}
                onToggle={() => undefined}
              />
            ))}
          </div>

          {onNextStep ? (
            <div className="mt-6 rounded-xl border border-warm-accent/20 bg-warm-accent/5 p-5">
              <p className="text-sm font-medium text-warm-text">
                方向已确认，可立即进入下一步
              </p>
              <p className="mt-2 text-sm leading-7 text-warm-secondary">
                基于当前已选方向生成候选场景池和 Top 3 AI 推荐场景。
              </p>
              <button type="button" onClick={onNextStep} className="btn-primary mt-4">
                生成 AI 推荐场景
              </button>
            </div>
          ) : null}
        </div>
      ) : (
        <>
          <div className="mt-6 rounded-xl border border-warm-accent/15 bg-warm-accent/5 p-6">
            <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">
              选择说明
            </p>
            <p className="mt-3 text-sm leading-7 text-warm-secondary">
              请从候选池中选择 1-6 个最符合当前企业实际情况的方向。确认后，后续场景池和竞争力分析都会基于这里的选择继续生成。
            </p>
          </div>

          {displayedSuggestionCount === 0 ? (
            <p className="mt-6 text-sm text-warm-muted">
              暂无可延展方向，请先完成突破要素选择。
            </p>
          ) : (
            normalizedElements.map((element) => (
              <div key={element.element_key} className="mt-6">
                <div className="flex items-center gap-3">
                  <span className="badge badge-accent">{element.element_title}</span>
                  <span className="text-xs text-warm-muted">
                    {element.suggestions.length} 个方向
                  </span>
                </div>
                <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  {element.suggestions.map((direction) => (
                    <DirectionCard
                      key={direction.direction_id}
                      direction={direction}
                      isSelected={selectedIds.includes(direction.direction_id)}
                      showToggle
                      onToggle={() => onToggleDirection(direction.direction_id)}
                    />
                  ))}
                </div>
              </div>
            ))
          )}

          {displayedSuggestionCount > 0 ? (
            <div className="mt-6 flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={onConfirmSelection}
                disabled={
                  isSelecting ||
                  visibleSelectedIds.length < 1 ||
                  visibleSelectedIds.length > 6
                }
                className="btn-primary"
              >
                {isSelecting
                  ? "保存中..."
                  : visibleSelectedIds.length < 1
                    ? "请至少选择 1 个方向"
                    : visibleSelectedIds.length > 6
                      ? `最多选择 6 个方向（已选 ${visibleSelectedIds.length}）`
                      : `确认选择（${visibleSelectedIds.length} 个方向）`}
              </button>
            </div>
          ) : null}
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
      className={`rounded-xl border bg-warm-inset p-6 text-left transition ${
        isSelected
          ? "border-warm-accent/40 bg-warm-accent/5 ring-1 ring-warm-accent/15"
          : "border-warm-border-light hover:border-warm-border hover:shadow-card"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <p className="text-sm font-semibold text-warm-text">{direction.title}</p>
          <p className="mt-2 text-xs leading-5 text-warm-muted">
            {direction.description}
          </p>
        </div>
        {isSelected ? <span className="badge badge-success text-xs">已选</span> : null}
      </div>
      <div className="mt-3 space-y-2">
        <div>
          <p className="text-[11px] uppercase tracking-[0.12em] text-warm-muted">
            预期影响
          </p>
          <p className="mt-1 text-xs leading-5 text-warm-muted">
            {direction.expected_impact}
          </p>
        </div>
        {direction.data_needed.length > 0 ? (
          <div>
            <p className="text-[11px] uppercase tracking-[0.12em] text-warm-muted">
              所需数据
            </p>
            <div className="mt-1 flex flex-wrap gap-1">
              {direction.data_needed.slice(0, 3).map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-warm-border-light bg-warm-surface px-2 py-0.5 text-[10px] text-warm-muted"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </button>
  );
}
