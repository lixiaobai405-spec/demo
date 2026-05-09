"use client";

import type { AssessmentBreakthroughResponse, BreakthroughElement } from "@/lib/types";

const scoreColor = (score: number): string => {
  if (score <= 30) return "text-warm-danger bg-red-50";
  if (score <= 55) return "text-warm-warning bg-amber-50";
  if (score <= 70) return "text-warm-accent bg-amber-50/60";
  return "text-warm-success bg-green-50";
};

const sourceLabel = (score: number): string => {
  if (score <= 30) return "优先突破";
  if (score <= 55) return "建议突破";
  if (score <= 70) return "可考虑";
  return "持续优化";
};

export function BreakthroughSelectionPanel({
  data, selectedKeys, isSelecting, onToggleElement, onConfirmSelection,
}: {
  data: AssessmentBreakthroughResponse;
  selectedKeys: string[];
  isSelecting: boolean;
  onToggleElement: (key: string) => void;
  onConfirmSelection: () => void;
}) {
  const { breakthrough_recommendation, breakthrough_selection } = data;
  const { elements, recommended_keys, overall_suggestion, generation_mode } = breakthrough_recommendation;
  const sortedElements = [...elements].sort((a, b) => a.score - b.score);
  const hasExistingSelection = breakthrough_selection !== null && breakthrough_selection.selected_elements.length >= 2;

  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">突破分析</p>
          <h2 className="section-heading">突破要素选择</h2>
        </div>
        <span className="badge badge-accent">
          {generation_mode === "rule_based" ? "规则评分" : "Mock"}
        </span>
      </div>

      {hasExistingSelection && breakthrough_selection.selected_elements.length >= 2 ? (
        <div className="mt-6">
          <p className="text-sm font-medium text-warm-success">
            已选择 {breakthrough_selection.selected_elements.length} 个突破要素
          </p>
          <p className="mt-1 text-xs text-warm-muted">
            选择模式：{breakthrough_selection.selection_mode === "system_recommended" ? "系统推荐" : "人工选择"}
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {breakthrough_selection.selected_elements.map((el) => (
              <ElementCard key={el.key} element={el} isRecommended={recommended_keys.includes(el.key)} isSelected showToggle={!hasExistingSelection} onToggle={() => onToggleElement(el.key)} />
            ))}
          </div>
          {!hasExistingSelection ? null : (
            <p className="mt-4 text-sm text-warm-muted">若需重新选择，请重新生成画布诊断以清空当前选择。</p>
          )}
        </div>
      ) : (
        <>
          <div className="mt-6 flex flex-col gap-4 lg:flex-row lg:items-start">
            <div className="flex-1 rounded-xl border border-warm-accent/15 bg-warm-accent/5 p-6">
              <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">系统建议</p>
              <p className="mt-3 text-sm leading-7 text-warm-secondary">{overall_suggestion}</p>
              {recommended_keys.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {recommended_keys.map((key) => {
                    const el = elements.find((e) => e.key === key);
                    return <span key={key} className="badge badge-accent">{el?.title ?? key}</span>;
                  })}
                </div>
              )}
            </div>
            <div className="rounded-xl border border-amber-200 bg-amber-50/70 px-6 py-4 text-sm text-amber-800 lg:max-w-[220px]">
              <p className="font-medium">选择规则</p>
              <ul className="mt-2 list-inside list-disc space-y-1">
                <li>必须选择 2-3 个要素</li>
                <li>评分越低，越需要优先突破</li>
                <li>可以采纳系统推荐，也可以手动调整</li>
              </ul>
            </div>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {sortedElements.map((el) => (
              <ElementCard key={el.key} element={el} isRecommended={recommended_keys.includes(el.key)} isSelected={selectedKeys.includes(el.key)} showToggle onToggle={() => onToggleElement(el.key)} />
            ))}
          </div>

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button type="button" onClick={onConfirmSelection} disabled={isSelecting || selectedKeys.length < 2 || selectedKeys.length > 3} className="btn-primary">
              {isSelecting ? "保存中..." : selectedKeys.length < 2 ? `请至少选择 2 个要素（已选 ${selectedKeys.length}）` : selectedKeys.length > 3 ? `最多选择 3 个要素（已选 ${selectedKeys.length}）` : `确认选择（${selectedKeys.length} 个要素）`}
            </button>
            <button type="button" onClickCapture={(e) => { e.preventDefault(); selectedKeys.forEach((k) => onToggleElement(k)); }} className="btn-secondary">
              清空选择
            </button>
          </div>
        </>
      )}
    </div>
  );
}

function ElementCard({ element, isRecommended, isSelected, showToggle, onToggle }: {
  element: BreakthroughElement; isRecommended: boolean; isSelected: boolean; showToggle: boolean; onToggle: () => void;
}) {
  return (
    <button type="button" onClick={onToggle}
      className={`rounded-xl border bg-warm-inset p-6 text-left transition ${
        isSelected ? "border-warm-accent/40 bg-warm-accent/5 ring-1 ring-warm-accent/15" : "border-warm-border-light hover:border-warm-border hover:shadow-card"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <p className="text-sm font-semibold text-warm-text">{element.title}</p>
            {isRecommended && !isSelected && <span className="badge badge-accent text-xs">推荐</span>}
            {isSelected && <span className="badge badge-success text-xs">已选</span>}
          </div>
          <p className="mt-2 text-xs leading-5 text-warm-muted">{element.reason}</p>
          <p className="mt-2 text-xs leading-5 text-warm-muted">{element.ai_opportunity}</p>
        </div>
        <div className={`flex-shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ${scoreColor(element.score)}`}>
          {element.score}
        </div>
      </div>
      <div className="mt-3">
        <span className="text-[11px] uppercase tracking-[0.12em] text-warm-muted">{sourceLabel(element.score)}</span>
      </div>
    </button>
  );
}
