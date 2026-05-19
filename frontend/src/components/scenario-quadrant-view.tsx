"use client";

import React, { useCallback, useMemo, useState } from "react";
import type { ScenarioRecommendationItem, ScenarioRecommendationResult } from "@/lib/types";

// ── PRD 算法常量 ──────────────────────────────────────
const QUADRANT_THRESHOLD = 3.5;
const WEIGHT_X = 0.6;
const WEIGHT_Y_INV = 0.4;
const Y_INVERSION_BASE = 6;
const LPS_DISPLAY_MULTIPLIER = 2;
const IMMEDIATE_START_THRESHOLD = 8.0;
const PLAN_ADVANCE_THRESHOLD = 5.0;

type QuadrantLabel = "AI优先区" | "自动化主战场" | "人机协作区" | "人类保留区";

interface EditableScenario extends ScenarioRecommendationItem {
  _x: number;
  _y: number;
  _qs: number;
  _lps: number;
  _lpsDisplay: number;
  _quadrant: QuadrantLabel;
  _tier: number;
  _level: string;
  _kappa: number;
}

// ── 纯函数：前端重算 ──────────────────────────────────

function calcQuadrant(x: number, y: number): QuadrantLabel {
  if (x >= QUADRANT_THRESHOLD && y >= QUADRANT_THRESHOLD) return "AI优先区";
  if (x >= QUADRANT_THRESHOLD && y < QUADRANT_THRESHOLD) return "自动化主战场";
  if (x < QUADRANT_THRESHOLD && y >= QUADRANT_THRESHOLD) return "人机协作区";
  return "人类保留区";
}

function calcTier(quadrant: QuadrantLabel): number {
  const map: Record<QuadrantLabel, number> = { "自动化主战场": 1, "AI优先区": 2, "人机协作区": 3, "人类保留区": 4 };
  return map[quadrant];
}

function calcLevel(lpsDisplay: number): string {
  if (lpsDisplay >= IMMEDIATE_START_THRESHOLD) return "立即启动";
  if (lpsDisplay >= PLAN_ADVANCE_THRESHOLD) return "规划推进";
  return "观察";
}

function recompute(x: number, y: number, kappa: number = 1.0) {
  const qs = +(x * y).toFixed(1);
  const lps = +(x * WEIGHT_X + (Y_INVERSION_BASE - y) * WEIGHT_Y_INV).toFixed(4);
  const lpsDisplay = +(lps * kappa * LPS_DISPLAY_MULTIPLIER).toFixed(1);
  const quadrant = calcQuadrant(x, y);
  const tier = calcTier(quadrant);
  const level = calcLevel(lpsDisplay);
  return { qs, lps, lpsDisplay, quadrant, tier, level };
}

function toEditable(item: ScenarioRecommendationItem): EditableScenario {
  const x = item.priority_structuredness_x ?? 3;
  const y = item.priority_complexity_y ?? 3;
  const kappa = item.industry_coefficient ?? 1.0;
  const { qs, lps, lpsDisplay, quadrant, tier, level } = recompute(x, y, kappa);
  return { ...item, _x: x, _y: y, _qs: qs, _lps: lps, _lpsDisplay: lpsDisplay, _quadrant: quadrant, _tier: tier, _level: level, _kappa: kappa };
}

function bubblePos(x: number, y: number) {
  return {
    left: `${(((x - 1) / 4) * 88 + 6)}%`,
    top: `${(100 - (((y - 1) / 4) * 88 + 6))}%`,
  };
}

// ── 滑块描述文案 ──────────────────────────────────────

const X_DESCRIPTIONS: Record<number, string> = {
  1: "完全非结构化，依赖直觉",
  2: "低度结构化，规则难描述",
  3: "中度结构化，部分规则可编码",
  4: "高度结构化，大部分已标准化",
  5: "完全结构化，全程数字化+SOP",
};

const Y_DESCRIPTIONS: Record<number, string> = {
  1: "极低复杂，极易落地",
  2: "低复杂，规则线性可执行",
  3: "中等复杂，需一定专业知识",
  4: "高复杂，多变量跨域判断",
  5: "极高复杂，阻力最大",
};

function xDesc(x: number): string {
  const r = Math.round(x);
  return X_DESCRIPTIONS[r] ?? "";
}

function yDesc(y: number): string {
  const r = Math.round(y);
  return Y_DESCRIPTIONS[r] ?? "";
}

// ── 视觉常量 ──────────────────────────────────────────

const QUADRANT_COLORS: Record<QuadrantLabel, { bg: string; text: string; ring: string; bar: string }> = {
  "自动化主战场": { bg: "bg-emerald-50", text: "text-emerald-700", ring: "ring-emerald-400", bar: "bg-emerald-400" },
  "AI优先区": { bg: "bg-amber-50", text: "text-amber-700", ring: "ring-amber-400", bar: "bg-amber-400" },
  "人机协作区": { bg: "bg-sky-50", text: "text-sky-700", ring: "ring-sky-400", bar: "bg-sky-400" },
  "人类保留区": { bg: "bg-rose-50", text: "text-rose-700", ring: "ring-rose-400", bar: "bg-rose-400" },
};

const QUADRANT_BADGE_CLASS: Record<QuadrantLabel, string> = {
  "自动化主战场": "badge-success",
  "AI优先区": "badge-warning",
  "人机协作区": "badge-info",
  "人类保留区": "badge-muted",
};

const RANK_MEDAL = ["🥇", "🥈", "🥉"];

// ── 组件 ──────────────────────────────────────────────

export function ScenarioQuadrantView({
  scenarioRecommendation,
  assessmentId,
}: {
  scenarioRecommendation: ScenarioRecommendationResult;
  assessmentId: string;
}) {
  const rawCandidates = scenarioRecommendation.all_scores ?? scenarioRecommendation.top_scenarios;
  const isFullPool = scenarioRecommendation.all_scores != null && scenarioRecommendation.all_scores.length > 0;

  const [scenarios, setScenarios] = useState<EditableScenario[]>(() =>
    rawCandidates.map(toEditable),
  );
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const selected = useMemo(
    () => scenarios.find((s) => s.scenario_id === selectedId) ?? null,
    [scenarios, selectedId],
  );

  // 按梯队+LPS_display排序得到Top3
  const ranked = useMemo(() => {
    const sorted = [...scenarios].sort((a, b) => {
      if (a._tier !== b._tier) return a._tier - b._tier;
      return b._lpsDisplay - a._lpsDisplay;
    });
    return sorted.slice(0, 3).map((s, i) => ({ ...s, rank: i }));
  }, [scenarios]);

  const handleSlider = useCallback(
    (axis: "x" | "y", value: number) => {
      if (!selectedId) return;
      setHasUnsavedChanges(true);
      setSaveStatus("idle");
      setScenarios((prev) =>
        prev.map((s) => {
          if (s.scenario_id !== selectedId) return s;
          const x = axis === "x" ? value : s._x;
          const y = axis === "y" ? value : s._y;
          const { qs, lps, lpsDisplay, quadrant, tier, level } = recompute(x, y, s._kappa);
          return {
            ...s,
            _x: x,
            _y: y,
            _qs: qs,
            _lps: lps,
            _lpsDisplay: lpsDisplay,
            _quadrant: quadrant,
            _tier: tier,
            _level: level,
            priority_structuredness_x: x,
            priority_complexity_y: y,
            priority_qs: qs,
            priority_lps: lps,
            priority_lps_display: lpsDisplay,
            priority_quadrant: quadrant,
            priority_tier: tier,
          };
        }),
      );
    },
    [selectedId],
  );

  const handleSaveCalibration = useCallback(async () => {
    setSaveStatus("saving");
    try {
      const body = {
        calibrations: scenarios.map((s) => ({
          scenario_id: s.scenario_id,
          priority_structuredness_x: s._x,
          priority_complexity_y: s._y,
        })),
      };
      const res = await fetch(`/api/assessments/${assessmentId}/scenarios/calibrations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(await res.text());
      setHasUnsavedChanges(false);
      setSaveStatus("saved");
    } catch {
      setSaveStatus("error");
    }
  }, [assessmentId, scenarios]);

  return (
    <div className="space-y-10">
      {/* ═══ 顶部摘要 ═══ */}
      <div>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="section-label">场景评分矩阵</p>
            <h2 className="section-heading">Top 3 AI 场景推荐</h2>
          </div>
          <span className="badge badge-warning">四象限评分</span>
        </div>
        <p className="mt-3 text-sm leading-7 text-warm-secondary">
          已评估 {scenarioRecommendation.evaluated_count} 个候选场景
          {isFullPool
            ? "，候选场景来自已选择的创新方向，系统按结构化程度和实施复杂度自动评分。"
            : "，当前展示 Top 3 推荐场景分布。"}
          点击候选场景可手动校准 X/Y 评分，点击气泡查看详情。
        </p>
      </div>

      {/* ═══ 上半部分：候选池 + 矩阵 ═══ */}
      <div className="flex flex-col gap-6 lg:flex-row">
        {/* ── 左侧：校准评分 + 候选场景池 ── */}
        <div className="flex-shrink-0 lg:w-[380px] space-y-4">
          {/* 校准评分框 */}
          <div className="rounded-2xl border border-warm-border-light bg-warm-surface p-5">
            <h3 className="font-heading text-base font-bold text-warm-text">校准候选场景</h3>
            {selected ? (
              <p className="mt-0.5 text-sm text-warm-accent">当前校准：{selected.name}</p>
            ) : (
              <p className="mt-0.5 text-sm text-warm-muted">请先在下方候选场景池中选择一个场景</p>
            )}
            <div className="my-4 border-t border-warm-border-light" />

            {selected ? (
              <>
                {/* 两列滑块 */}
                <div className="grid gap-4 sm:grid-cols-2">
                  {/* X 滑块 */}
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-warm-secondary font-medium">结构化程度 X</span>
                      <span className="font-bold text-warm-text">{selected._x}</span>
                    </div>
                    <p className="text-[0.65rem] text-warm-muted mb-1">高 = AI 易落地</p>
                    <input
                      type="range"
                      min="1"
                      max="5"
                      step="0.1"
                      value={selected._x}
                      onChange={(e) => handleSlider("x", parseFloat(e.target.value))}
                      className="w-full accent-amber-600"
                    />
                    <div className="flex justify-between text-[0.65rem] text-warm-muted mt-0.5">
                      <span>1</span>
                      <span>5</span>
                    </div>
                    <p className="mt-1 text-[0.65rem] leading-relaxed text-warm-muted">{xDesc(selected._x)}</p>
                  </div>

                  {/* Y 滑块 */}
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-warm-secondary font-medium">实施复杂度 Y</span>
                      <span className="font-bold text-warm-text">{selected._y}</span>
                    </div>
                    <p className="text-[0.65rem] text-warm-muted mb-1">高 = 落地阻力大（取反计分）</p>
                    <input
                      type="range"
                      min="1"
                      max="5"
                      step="0.1"
                      value={selected._y}
                      onChange={(e) => handleSlider("y", parseFloat(e.target.value))}
                      className="w-full accent-amber-600"
                    />
                    <div className="flex justify-between text-[0.65rem] text-warm-muted mt-0.5">
                      <span>1</span>
                      <span>5</span>
                    </div>
                    <p className="mt-1 text-[0.65rem] leading-relaxed text-warm-muted">{yDesc(selected._y)}</p>
                  </div>
                </div>

                {/* 实时预览 */}
                <div className="mt-4 rounded-xl bg-warm-inset px-4 py-3 space-y-1.5 text-sm">
                  <p className="text-xs font-medium text-warm-muted mb-2">实时预览</p>
                  <div className="flex justify-between">
                    <span className="text-warm-muted">QS 象限分</span>
                    <span className="font-semibold text-warm-text">{selected._qs}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-warm-muted">LPS 综合优先级</span>
                    <span className="font-semibold text-warm-text">{selected._lpsDisplay} / 10</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-warm-muted">象限</span>
                    <span className={`badge text-[0.65rem] ${QUADRANT_BADGE_CLASS[selected._quadrant]}`}>
                      {selected._quadrant}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-warm-muted">推荐等级</span>
                    <span className="font-semibold text-warm-text">{selected._level}</span>
                  </div>
                </div>

                {/* 保存校准按钮 */}
                <div className="mt-3 flex items-center gap-3">
                  <button
                    type="button"
                    onClick={handleSaveCalibration}
                    disabled={saveStatus === "saving" || !hasUnsavedChanges}
                    className={`rounded-full px-4 py-1.5 text-xs font-medium transition ${
                      saveStatus === "saving"
                        ? "bg-warm-inset text-warm-muted cursor-wait"
                        : saveStatus === "saved"
                          ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          : hasUnsavedChanges
                            ? "bg-amber-500 text-white hover:bg-amber-600"
                            : "bg-warm-inset text-warm-muted cursor-not-allowed"
                    }`}
                  >
                    {saveStatus === "saving"
                      ? "保存中..."
                      : saveStatus === "saved"
                        ? "已保存"
                        : saveStatus === "error"
                          ? "保存失败，点击重试"
                          : "保存校准"}
                  </button>
                  {!hasUnsavedChanges && (
                    <span className="text-[0.65rem] text-warm-muted">
                      {saveStatus === "saved" ? "已应用到推荐结果" : "当前页校准"}
                    </span>
                  )}
                  {hasUnsavedChanges && (
                    <span className="text-[0.65rem] text-amber-600">当前页校准，刷新将丢失</span>
                  )}
                </div>
              </>
            ) : (
              <p className="text-sm text-warm-muted py-4 text-center">
                选择一个候选场景后，可在此处校准其 X/Y 评分
              </p>
            )}
          </div>

          {/* 候选场景池 */}
          <div className="rounded-2xl border border-warm-border-light bg-warm-surface p-5">
            <div className="flex items-center justify-between">
              <h3 className="font-heading text-base font-bold text-warm-text">候选场景池</h3>
              <span className="text-xs text-warm-muted bg-warm-inset rounded-full px-2.5 py-0.5">
                {scenarios.length} 个场景
              </span>
            </div>
            {!isFullPool && (
              <p className="mt-1 text-xs text-warm-muted">当前为降级展示（仅 Top 3）</p>
            )}
            <div className="my-4 border-t border-warm-border-light" />

            <div className="space-y-2 max-h-[420px] overflow-y-auto pr-2">
              {scenarios.map((s) => {
                const isSel = selectedId === s.scenario_id;
                const colors = QUADRANT_COLORS[s._quadrant];
                return (
                  <button
                    key={s.scenario_id}
                    type="button"
                    onClick={() => setSelectedId(isSel ? null : s.scenario_id)}
                    className={`w-full text-left rounded-xl border bg-white flex items-stretch overflow-hidden transition text-sm ${
                      isSel
                        ? `border-2 border-${colors.ring.replace("ring-", "")} ring-1 ${colors.ring}/20`
                        : "border-warm-border-light hover:border-warm-accent/30 hover:bg-amber-50/30"
                    }`}
                  >
                    {/* 左侧象限色条 */}
                    <div className={`w-1.5 flex-shrink-0 ${colors.bar}`} />

                    <div className="flex-1 px-3 py-2.5 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-semibold text-warm-text truncate">{s.name}</span>
                        <span className={`badge text-[0.6rem] shrink-0 ${QUADRANT_BADGE_CLASS[s._quadrant]}`}>
                          {s._quadrant}
                        </span>
                      </div>
                      <div className="mt-1.5 flex items-center gap-3 text-xs text-warm-muted">
                        <span>X: {s._x}</span>
                        <span>Y: {s._y}</span>
                        <span className="font-medium text-warm-text">{s._lpsDisplay} 分</span>
                        <span>{s._level}</span>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* ── 右侧：四象限矩阵 ── */}
        <div className="flex-1 min-w-0">
          <div className="card-inset">
            {/* 图例 */}
            <div className="flex flex-wrap gap-3 mb-4 text-xs text-warm-muted">
              <span>X 轴 → 结构化程度</span>
              <span>Y 轴 → 实施复杂度</span>
              <span>● 金环 = Top3</span>
            </div>

            {/* 矩阵容器 */}
            <div className="relative w-full" style={{ paddingBottom: "min(100%, 560px)" }}>
              <div className="absolute inset-0 rounded-xl border border-warm-border-light bg-warm-inset overflow-hidden">
                {/* 象限背景：左上=人机协作区 右上=AI优先区 左下=人类保留区 右下=自动化主战场 */}
                <div className="absolute inset-0 flex">
                  <div className="flex-1 flex flex-col">
                    <div className="flex-1 flex">
                      <div className="flex-1 bg-sky-50/40 flex items-center justify-center">
                        <span className="text-[0.6rem] text-sky-400/60 font-medium">人机协作区</span>
                      </div>
                      <div className="flex-1 bg-amber-50/40 flex items-center justify-center">
                        <span className="text-[0.6rem] text-amber-400/60 font-medium">AI优先区</span>
                      </div>
                    </div>
                    <div className="flex-1 flex">
                      <div className="flex-1 bg-rose-50/40 flex items-center justify-center">
                        <span className="text-[0.6rem] text-rose-400/60 font-medium">人类保留区</span>
                      </div>
                      <div className="flex-1 bg-emerald-50/40 flex items-center justify-center">
                        <span className="text-[0.6rem] text-emerald-400/60 font-medium">自动化主战场</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 分界线 */}
                <div
                  className="absolute bg-warm-border-light/60"
                  style={{ left: "50%", top: 0, bottom: 0, width: 1 }}
                />
                <div
                  className="absolute bg-warm-border-light/60"
                  style={{ top: "50%", left: 0, right: 0, height: 1 }}
                />

                {/* 轴标签 */}
                <div className="absolute bottom-1 left-1/2 -translate-x-1/2 text-[0.6rem] text-warm-muted">
                  结构化程度 →
                </div>
                <div
                  className="absolute left-1 top-1/2 -translate-y-1/2 text-[0.6rem] text-warm-muted"
                  style={{ writingMode: "vertical-rl" }}
                >
                  复杂程度 →
                </div>

                {/* 气泡 */}
                {scenarios.map((s) => {
                  const pos = bubblePos(s._x, s._y);
                  const isTop3 = ranked.some((r) => r.scenario_id === s.scenario_id);
                  const isSel = s.scenario_id === selectedId;
                  const colors = QUADRANT_COLORS[s._quadrant];
                  return (
                    <div
                      key={s.scenario_id}
                      title={`${s.name}\nX:${s._x} Y:${s._y} QS:${s._qs} LPS:${s._lpsDisplay}\n${s._quadrant} · ${s._level}`}
                      onClick={() =>
                        setSelectedId(isSel ? null : s.scenario_id)
                      }
                      className={`absolute -translate-x-1/2 -translate-y-1/2 rounded-full flex items-center justify-center cursor-pointer transition text-[0.6rem] font-bold text-center leading-tight
                        ${isTop3 ? "ring-2 ring-amber-400 ring-offset-1" : ""}
                        ${isSel ? `ring-2 ${colors.ring} ring-offset-1 scale-110` : ""}
                      `}
                      style={{
                        left: pos.left,
                        top: pos.top,
                        width: isTop3 ? "2.4rem" : "2rem",
                        height: isTop3 ? "2.4rem" : "2rem",
                        backgroundColor: isTop3
                          ? "#f59e0b"
                          : isSel
                            ? colors.ring.replace("ring-", "#")
                            : "#d1d5db",
                        color: isTop3 ? "#fff" : isSel ? "#fff" : "#374151",
                        zIndex: isTop3 ? 10 : isSel ? 9 : 5,
                      }}
                    >
                      {s.name.charAt(0)}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ═══ 下半部分：Top 3 推荐卡片 ═══ */}
      <div>
        <p className="section-label">最终推荐</p>
        <h2 className="section-heading mb-4">Top 3 推荐场景</h2>
        <div className="grid gap-4 xl:grid-cols-3">
          {ranked.map((item, index) => {
            const isExpanded = expandedId === item.scenario_id;
            const colors = QUADRANT_COLORS[item._quadrant];
            const rankBorder =
              index === 0
                ? "border-amber-400"
                : index === 1
                  ? "border-slate-300"
                  : "border-orange-300";
            return (
              <div
                key={item.scenario_id}
                className={`rounded-xl border-2 bg-warm-surface transition cursor-pointer hover:shadow-md ${
                  isExpanded
                    ? `${colors.ring.replace("ring-", "border-")} ring-1 ${colors.ring.replace("ring-", "ring-")}/20`
                    : `${rankBorder}`
                }`}
                onClick={() => setExpandedId(isExpanded ? null : item.scenario_id)}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="text-lg">{RANK_MEDAL[index]}</p>
                      <h3 className="mt-1 font-heading text-xl font-bold text-warm-text">
                        {item.name}
                      </h3>
                      <div className="mt-2 flex flex-wrap items-center gap-2">
                        <p className="text-sm text-warm-accent">{item.category}</p>
                        <span className={`badge text-[0.65rem] ${QUADRANT_BADGE_CLASS[item._quadrant]}`}>
                          {item._quadrant}
                        </span>
                        <span className="badge badge-warning text-[0.65rem]">{item._level}</span>
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="text-2xl font-bold text-warm-text">{item._lpsDisplay}</p>
                      <p className="text-[0.65rem] text-warm-muted">/ 10 分</p>
                    </div>
                  </div>
                  <p className="mt-4 text-sm leading-7 text-warm-secondary">{item.summary}</p>
                  <div className="mt-3 flex items-center gap-1 text-xs text-warm-accent">
                    <span>{isExpanded ? "收起" : "展开详情"}</span>
                  </div>
                </div>

                {isExpanded && (
                  <div className="border-t border-warm-border-light px-6 pb-6 animate-in fade-in">
                    <div className="mt-4 space-y-3">
                      {item.canvas_elements ? (
                        <div className="rounded-xl bg-warm-inset px-4 py-3">
                          <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">对应画布要素</p>
                          <p className="mt-1 text-sm text-warm-secondary">{item.canvas_elements}</p>
                        </div>
                      ) : null}
                      {item.expected_effects ? (
                        <div className="rounded-xl bg-warm-inset px-4 py-3">
                          <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">预期价值量化</p>
                          <p className="mt-1 text-sm text-warm-secondary">{item.expected_effects}</p>
                        </div>
                      ) : null}
                      {item.core_data_requirements ? (
                        <div className="rounded-xl bg-warm-inset px-4 py-3">
                          <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">所需核心数据</p>
                          <p className="mt-1 text-sm text-warm-secondary">{item.core_data_requirements}</p>
                        </div>
                      ) : null}
                      <div className="rounded-xl bg-warm-inset px-4 py-3">
                        <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">四象限评分</p>
                        <div className="mt-2 grid grid-cols-2 gap-2 text-sm text-warm-secondary">
                          <div><span className="text-warm-muted">结构化程度 X：</span><span className="font-semibold text-warm-text">{item._x}</span><span className="text-warm-muted"> / 5</span></div>
                          <div><span className="text-warm-muted">实施复杂度 Y：</span><span className="font-semibold text-warm-text">{item._y}</span><span className="text-warm-muted"> / 5</span></div>
                          <div><span className="text-warm-muted">QS 象限分：</span><span className="font-semibold text-warm-text">{item._qs}</span></div>
                          <div><span className="text-warm-muted">综合优先级：</span><span className="font-semibold text-warm-text">{item._lpsDisplay}</span><span className="text-warm-muted"> / 10</span></div>
                        </div>
                      </div>
                      {item.priority_recommendation ? (
                        <div className="rounded-xl bg-warm-inset px-4 py-3">
                          <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">推荐话术</p>
                          <p className="mt-1 text-sm leading-7 text-warm-secondary">{item.priority_recommendation}</p>
                        </div>
                      ) : null}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
