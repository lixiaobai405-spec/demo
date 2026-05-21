"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { apiBaseUrl } from "@/lib/api";
import type {
  ScenarioRecommendationItem,
  ScenarioRecommendationResult,
} from "@/lib/types";
import { assessmentKeys } from "@/hooks/use-assessment";

const QUADRANT_THRESHOLD = 3.5;
const WEIGHT_X = 0.6;
const WEIGHT_Y_INV = 0.4;
const Y_INVERSION_BASE = 6;
const LPS_DISPLAY_MULTIPLIER = 2;
const IMMEDIATE_START_THRESHOLD = 8.0;
const PLAN_ADVANCE_THRESHOLD = 5.0;

type QuadrantLabel =
  | "AI优先区"
  | "自动化主战场"
  | "人机协作区"
  | "人工保留区";

type EditableScenario = ScenarioRecommendationItem & {
  _x: number;
  _y: number;
  _qs: number;
  _lps: number;
  _lpsDisplay: number;
  _quadrant: QuadrantLabel;
  _tier: number;
  _level: string;
  _kappa: number;
};

const QUADRANT_META: Record<
  QuadrantLabel,
  {
    badgeClass: string;
    bubbleColor: string;
    areaClass: string;
    areaLabelClass: string;
    borderClass: string;
  }
> = {
  自动化主战场: {
    badgeClass: "badge-success",
    bubbleColor: "#10b981",
    areaClass: "bg-emerald-50/50",
    areaLabelClass: "text-emerald-400/70",
    borderClass: "border-emerald-300",
  },
  AI优先区: {
    badgeClass: "badge-warning",
    bubbleColor: "#f59e0b",
    areaClass: "bg-amber-50/50",
    areaLabelClass: "text-amber-400/70",
    borderClass: "border-amber-300",
  },
  人机协作区: {
    badgeClass: "badge-info",
    bubbleColor: "#0ea5e9",
    areaClass: "bg-sky-50/50",
    areaLabelClass: "text-sky-400/70",
    borderClass: "border-sky-300",
  },
  人工保留区: {
    badgeClass: "badge-muted",
    bubbleColor: "#94a3b8",
    areaClass: "bg-slate-50/70",
    areaLabelClass: "text-slate-400/70",
    borderClass: "border-slate-300",
  },
};

const X_DESCRIPTIONS: Record<number, string> = {
  1: "完全非结构化，暂不适合直接上 AI。",
  2: "低度结构化，需要先补规则和字段。",
  3: "中度结构化，可在局部场景试点。",
  4: "高度结构化，大部分流程已标准化。",
  5: "完全结构化，可优先作为规模化 AI 场景。",
};

const Y_DESCRIPTIONS: Record<number, string> = {
  1: "复杂度很低，适合快速落地。",
  2: "复杂度较低，规则可较快梳理清楚。",
  3: "复杂度中等，需要跨岗位协同。",
  4: "复杂度较高，涉及多变量判断。",
  5: "复杂度很高，落地阻力和改造成本都高。",
};

const RANK_MEDALS = ["🥇", "🥈", "🥉"];

function calcQuadrant(x: number, y: number): QuadrantLabel {
  if (x >= QUADRANT_THRESHOLD && y >= QUADRANT_THRESHOLD) {
    return "AI优先区";
  }
  if (x >= QUADRANT_THRESHOLD && y < QUADRANT_THRESHOLD) {
    return "自动化主战场";
  }
  if (x < QUADRANT_THRESHOLD && y >= QUADRANT_THRESHOLD) {
    return "人机协作区";
  }
  return "人工保留区";
}

function calcTier(quadrant: QuadrantLabel): number {
  if (quadrant === "自动化主战场") return 1;
  if (quadrant === "AI优先区") return 2;
  if (quadrant === "人机协作区") return 3;
  return 4;
}

function calcLevel(lpsDisplay: number): string {
  if (lpsDisplay >= IMMEDIATE_START_THRESHOLD) return "立即启动";
  if (lpsDisplay >= PLAN_ADVANCE_THRESHOLD) return "规划推进";
  return "持续观察";
}

function recompute(x: number, y: number, kappa = 1) {
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
  const kappa = item.industry_coefficient ?? 1;
  const { qs, lps, lpsDisplay, quadrant, tier, level } = recompute(x, y, kappa);

  return {
    ...item,
    _x: x,
    _y: y,
    _qs: qs,
    _lps: lps,
    _lpsDisplay: lpsDisplay,
    _quadrant: quadrant,
    _tier: tier,
    _level: item.recommendation_level || level,
    _kappa: kappa,
  };
}

function buildDisplayScenarios(
  recommendation: ScenarioRecommendationResult,
): EditableScenario[] {
  const all = recommendation.all_scores ?? recommendation.top_scenarios;
  const topIds = new Set(recommendation.top_scenarios.map((item) => item.scenario_id));
  const byId = new Map(all.map((item) => [item.scenario_id, item]));
  const topItems = recommendation.top_scenarios
    .map((item) => byId.get(item.scenario_id) ?? item)
    .filter(Boolean) as ScenarioRecommendationItem[];
  const restItems = all.filter((item) => !topIds.has(item.scenario_id));

  return [...topItems, ...restItems].map(toEditable);
}

function bubblePos(x: number, y: number) {
  return {
    left: `${((x - 1) / 4) * 88 + 6}%`,
    top: `${100 - (((y - 1) / 4) * 88 + 6)}%`,
  };
}

function clampScore(value: number) {
  return Math.max(1, Math.min(5, Number(value.toFixed(1))));
}

function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") {
    return {};
  }

  const token = window.localStorage.getItem("auth_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function ScenarioQuadrantView({
  scenarioRecommendation,
  assessmentId,
}: {
  scenarioRecommendation: ScenarioRecommendationResult;
  assessmentId: string;
}) {
  const queryClient = useQueryClient();
  const [recommendation, setRecommendation] =
    useState<ScenarioRecommendationResult>(scenarioRecommendation);
  const [scenarios, setScenarios] = useState<EditableScenario[]>(
    buildDisplayScenarios(scenarioRecommendation),
  );
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [expandedIds, setExpandedIds] = useState<string[]>([]);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  useEffect(() => {
    setRecommendation(scenarioRecommendation);
    setScenarios(buildDisplayScenarios(scenarioRecommendation));
  }, [scenarioRecommendation]);

  const selected = useMemo(
    () => scenarios.find((item) => item.scenario_id === selectedId) ?? null,
    [scenarios, selectedId],
  );

  const top3Ids = useMemo(
    () => new Set(recommendation.top_scenarios.map((item) => item.scenario_id)),
    [recommendation.top_scenarios],
  );

  const top3Cards = useMemo(() => {
    return recommendation.top_scenarios
      .map((item) => scenarios.find((scenario) => scenario.scenario_id === item.scenario_id))
      .filter(Boolean) as EditableScenario[];
  }, [recommendation.top_scenarios, scenarios]);

  const handleScoreChange = useCallback(
    (axis: "x" | "y", value: number) => {
      if (!selectedId) return;
      const nextValue = clampScore(value);
      setHasUnsavedChanges(true);
      setSaveStatus("idle");
      setScenarios((current) =>
        current.map((item) => {
          if (item.scenario_id !== selectedId) {
            return item;
          }

          const nextX = axis === "x" ? nextValue : item._x;
          const nextY = axis === "y" ? nextValue : item._y;
          const { qs, lps, lpsDisplay, quadrant, tier, level } = recompute(
            nextX,
            nextY,
            item._kappa,
          );

          return {
            ...item,
            _x: nextX,
            _y: nextY,
            _qs: qs,
            _lps: lps,
            _lpsDisplay: lpsDisplay,
            _quadrant: quadrant,
            _tier: tier,
            _level: level,
            priority_structuredness_x: nextX,
            priority_complexity_y: nextY,
            priority_qs: qs,
            priority_lps: lps,
            priority_lps_display: lpsDisplay,
            priority_quadrant: quadrant,
            priority_tier: tier,
            recommendation_level: level,
          };
        }),
      );
    },
    [selectedId],
  );

  const adjustScore = useCallback(
    (axis: "x" | "y", delta: number) => {
      if (!selected) return;
      const currentValue = axis === "x" ? selected._x : selected._y;
      handleScoreChange(axis, currentValue + delta);
    },
    [handleScoreChange, selected],
  );

  const handleSaveCalibration = useCallback(async () => {
    setSaveStatus("saving");
    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true",
        ...getAuthHeaders(),
      };
      const response = await fetch(
        `${apiBaseUrl}/api/assessments/${assessmentId}/scenarios/calibrations`,
        {
          method: "POST",
          headers,
          body: JSON.stringify({
            calibrations: scenarios.map((item) => ({
              scenario_id: item.scenario_id,
              priority_structuredness_x: item._x,
              priority_complexity_y: item._y,
            })),
          }),
        },
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const payload = (await response.json()) as {
        scenario_recommendation: ScenarioRecommendationResult;
      };
      setRecommendation(payload.scenario_recommendation);
      setScenarios(buildDisplayScenarios(payload.scenario_recommendation));
      setHasUnsavedChanges(false);
      setSaveStatus("saved");
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: assessmentKeys.detail(assessmentId) }),
        queryClient.invalidateQueries({ queryKey: assessmentKeys.scenarios(assessmentId) }),
        queryClient.invalidateQueries({ queryKey: assessmentKeys.competitiveness(assessmentId) }),
        queryClient.invalidateQueries({ queryKey: assessmentKeys.endgame(assessmentId) }),
      ]);
    } catch {
      setSaveStatus("error");
    }
  }, [assessmentId, queryClient, scenarios]);

  const toggleExpanded = useCallback((scenarioId: string) => {
    setExpandedIds((current) =>
      current.includes(scenarioId)
        ? current.filter((item) => item !== scenarioId)
        : [...current, scenarioId],
    );
  }, []);

  return (
    <div className="space-y-10">
      <div>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="section-label">场景候选池</p>
            <h2 className="section-heading">Top 3 AI 推荐场景</h2>
          </div>
          <span className="badge badge-warning">四象限评分</span>
        </div>
        <p className="mt-3 text-sm leading-7 text-warm-secondary">
          当前共评估 {recommendation.evaluated_count} 个候选场景。你可以在左侧校准 X/Y 评分，系统会即时重算场景象限、优先级和 Top 3 排名。
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[380px_minmax(0,1fr)]">
        <div className="space-y-4">
          <section className="rounded-2xl border border-warm-border-light bg-warm-surface p-5">
            <h3 className="font-heading text-base font-bold text-warm-text">
              候选池校准
            </h3>
            {selected ? (
              <p className="mt-1 text-sm text-warm-accent">
                当前场景：{selected.name}
              </p>
            ) : (
              <p className="mt-1 text-sm text-warm-muted">
                请先从下方候选池选择一个场景。
              </p>
            )}

            <div className="my-4 border-t border-warm-border-light" />

            {selected ? (
              <>
                <div className="grid gap-4 sm:grid-cols-2">
                  <ScoreEditor
                    label="结构化程度 X"
                    value={selected._x}
                    helper="越高越适合做成稳定 AI 能力"
                    description={X_DESCRIPTIONS[Math.round(selected._x)] ?? ""}
                    onDecrease={() => adjustScore("x", -0.1)}
                    onIncrease={() => adjustScore("x", 0.1)}
                    onChange={(value) => handleScoreChange("x", value)}
                  />
                  <ScoreEditor
                    label="实施复杂度 Y"
                    value={selected._y}
                    helper="越高代表落地阻力和复杂度越大"
                    description={Y_DESCRIPTIONS[Math.round(selected._y)] ?? ""}
                    onDecrease={() => adjustScore("y", -0.1)}
                    onIncrease={() => adjustScore("y", 0.1)}
                    onChange={(value) => handleScoreChange("y", value)}
                  />
                </div>

                <div className="mt-4 rounded-xl bg-warm-inset px-4 py-3 text-sm">
                  <p className="mb-2 text-xs font-medium text-warm-muted">实时预览</p>
                  <div className="space-y-1.5">
                    <PreviewRow label="QS 象限得分" value={String(selected._qs)} />
                    <PreviewRow
                      label="LPS 综合优先级"
                      value={`${selected._lpsDisplay} / 10`}
                    />
                    <PreviewRow label="所属象限" value={selected._quadrant} />
                    <PreviewRow label="推荐级别" value={selected._level} />
                  </div>
                </div>

                <div className="mt-3 flex items-center gap-3">
                  <button
                    type="button"
                    onClick={handleSaveCalibration}
                    disabled={saveStatus === "saving" || !hasUnsavedChanges}
                    className={`rounded-full px-4 py-1.5 text-xs font-medium transition ${
                      saveStatus === "saving"
                        ? "cursor-wait bg-warm-inset text-warm-muted"
                        : saveStatus === "saved"
                          ? "border border-emerald-200 bg-emerald-50 text-emerald-700"
                          : hasUnsavedChanges
                            ? "bg-amber-500 text-white hover:bg-amber-600"
                            : "cursor-not-allowed bg-warm-inset text-warm-muted"
                    }`}
                  >
                    {saveStatus === "saving"
                      ? "保存中..."
                      : saveStatus === "saved"
                        ? "已保存"
                        : saveStatus === "error"
                          ? "保存失败，请重试"
                          : "保存校准"}
                  </button>
                  <span className="text-[11px] text-warm-muted">
                    {hasUnsavedChanges
                      ? "保存后，后续竞争力与终局结果会自动失效。"
                      : "当前显示的是已保存的校准结果。"}
                  </span>
                </div>
              </>
            ) : (
              <p className="py-4 text-center text-sm text-warm-muted">
                选择候选场景后，可在这里通过 +/- 或滑块调整评分。
              </p>
            )}
          </section>

          <section className="rounded-2xl border border-warm-border-light bg-warm-surface p-5">
            <div className="flex items-center justify-between">
              <h3 className="font-heading text-base font-bold text-warm-text">
                候选场景池
              </h3>
              <span className="rounded-full bg-warm-inset px-2.5 py-0.5 text-xs text-warm-muted">
                {scenarios.length} 个场景
              </span>
            </div>
            <div className="my-4 border-t border-warm-border-light" />

            <div className="max-h-[440px] space-y-2 overflow-y-auto pr-2">
              {scenarios.map((item) => {
                const isSelected = selectedId === item.scenario_id;
                const meta = QUADRANT_META[item._quadrant];
                return (
                  <button
                    key={item.scenario_id}
                    type="button"
                    onClick={() =>
                      setSelectedId((current) =>
                        current === item.scenario_id ? null : item.scenario_id,
                      )
                    }
                    className={`w-full rounded-xl border px-4 py-3 text-left transition ${
                      isSelected
                        ? `${meta.borderClass} bg-white shadow-sm`
                        : "border-warm-border-light bg-white hover:border-warm-accent/30"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-semibold text-warm-text">
                          {item.name}
                        </p>
                        <p className="mt-1 line-clamp-2 text-xs leading-5 text-warm-muted">
                          {item.summary}
                        </p>
                      </div>
                      <span className={`badge shrink-0 text-[0.6rem] ${meta.badgeClass}`}>
                        {item._quadrant}
                      </span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-3 text-xs text-warm-muted">
                      <span>X: {item._x}</span>
                      <span>Y: {item._y}</span>
                      <span className="font-medium text-warm-text">
                        {item._lpsDisplay} 分
                      </span>
                      <span>{item._level}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </section>
        </div>

        <div className="min-w-0">
          <div className="card-inset">
            <div className="mb-4 rounded-xl border border-warm-border-light bg-white px-4 py-4 text-xs text-warm-muted">
              <p className="font-medium text-warm-text">评分解释</p>
              <div className="mt-2 grid gap-2 md:grid-cols-2">
                <p>X 轴：结构化程度，越高表示越适合沉淀为标准 AI 能力。</p>
                <p>Y 轴：实施复杂度，越低越适合优先启动。</p>
                <p>QS = X × Y，用于体现象限位置。</p>
                <p>
                  LPS = [X × 0.6 + (6 - Y) × 0.4] × 行业系数 × 2，用于推荐排序。
                </p>
              </div>
            </div>

            <div className="mb-4 flex flex-wrap gap-3 text-xs text-warm-muted">
              <span>● 金色外圈表示当前 Top 3</span>
              <span>点击气泡或左侧候选场景可查看并校准</span>
            </div>

            <div className="relative w-full" style={{ paddingBottom: "min(100%, 560px)" }}>
              <div className="absolute inset-0 overflow-hidden rounded-xl border border-warm-border-light bg-warm-inset">
                <div className="absolute inset-0 flex">
                  <div className="flex flex-1 flex-col">
                    <div className="flex flex-1">
                      <div className={`flex flex-1 items-center justify-center ${QUADRANT_META["人机协作区"].areaClass}`}>
                        <span className={`text-[0.65rem] font-medium ${QUADRANT_META["人机协作区"].areaLabelClass}`}>
                          人机协作区
                        </span>
                      </div>
                      <div className={`flex flex-1 items-center justify-center ${QUADRANT_META["AI优先区"].areaClass}`}>
                        <span className={`text-[0.65rem] font-medium ${QUADRANT_META["AI优先区"].areaLabelClass}`}>
                          AI优先区
                        </span>
                      </div>
                    </div>
                    <div className="flex flex-1">
                      <div className={`flex flex-1 items-center justify-center ${QUADRANT_META["人工保留区"].areaClass}`}>
                        <span className={`text-[0.65rem] font-medium ${QUADRANT_META["人工保留区"].areaLabelClass}`}>
                          人工保留区
                        </span>
                      </div>
                      <div className={`flex flex-1 items-center justify-center ${QUADRANT_META["自动化主战场"].areaClass}`}>
                        <span className={`text-[0.65rem] font-medium ${QUADRANT_META["自动化主战场"].areaLabelClass}`}>
                          自动化主战场
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div
                  className="absolute bg-warm-border-light/70"
                  style={{ left: "50%", top: 0, bottom: 0, width: 1 }}
                />
                <div
                  className="absolute bg-warm-border-light/70"
                  style={{ top: "50%", left: 0, right: 0, height: 1 }}
                />

                <div className="absolute bottom-1 left-1/2 -translate-x-1/2 text-[0.65rem] text-warm-muted">
                  结构化程度 →
                </div>
                <div
                  className="absolute left-1 top-1/2 -translate-y-1/2 text-[0.65rem] text-warm-muted"
                  style={{ writingMode: "vertical-rl" }}
                >
                  实施复杂度 →
                </div>

                {scenarios.map((item) => {
                  const position = bubblePos(item._x, item._y);
                  const meta = QUADRANT_META[item._quadrant];
                  const isTop3 = top3Ids.has(item.scenario_id);
                  const isSelected = item.scenario_id === selectedId;
                  return (
                    <button
                      key={item.scenario_id}
                      type="button"
                      title={`${item.name}\nX:${item._x} Y:${item._y} LPS:${item._lpsDisplay}`}
                      onClick={() =>
                        setSelectedId((current) =>
                          current === item.scenario_id ? null : item.scenario_id,
                        )
                      }
                      className="absolute -translate-x-1/2 -translate-y-1/2 rounded-full text-[0.6rem] font-bold text-white transition"
                      style={{
                        left: position.left,
                        top: position.top,
                        width: isTop3 ? "2.45rem" : "2.1rem",
                        height: isTop3 ? "2.45rem" : "2.1rem",
                        backgroundColor: meta.bubbleColor,
                        boxShadow: isSelected
                          ? "0 0 0 3px rgba(255,255,255,0.9), 0 0 0 5px rgba(245,158,11,0.5)"
                          : isTop3
                            ? "0 0 0 2px rgba(245,158,11,0.7)"
                            : "0 4px 12px rgba(45,34,24,0.15)",
                        zIndex: isSelected ? 12 : isTop3 ? 10 : 5,
                      }}
                    >
                      {item.name.slice(0, 1)}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <p className="section-label">最终推荐</p>
        <h2 className="section-heading mb-4">Top 3 推荐场景</h2>
        <div className="grid gap-4 xl:grid-cols-3">
          {top3Cards.map((item, index) => {
            const meta = QUADRANT_META[item._quadrant];
            const isExpanded = expandedIds.includes(item.scenario_id);
            return (
              <article
                key={item.scenario_id}
                className={`rounded-xl border-2 bg-warm-surface transition ${
                  isExpanded ? `${meta.borderClass} shadow-md` : "border-warm-border-light"
                }`}
              >
                <button
                  type="button"
                  onClick={() => toggleExpanded(item.scenario_id)}
                  className="w-full p-6 text-left"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="text-lg">{RANK_MEDALS[index] ?? "⭐"}</p>
                      <h3 className="mt-1 font-heading text-xl font-bold text-warm-text">
                        {item.name}
                      </h3>
                      <div className="mt-2 flex flex-wrap items-center gap-2">
                        <p className="text-sm text-warm-accent">{item.category}</p>
                        <span className={`badge text-[0.65rem] ${meta.badgeClass}`}>
                          {item._quadrant}
                        </span>
                        <span className="badge badge-warning text-[0.65rem]">
                          {item._level}
                        </span>
                      </div>
                    </div>
                    <div className="shrink-0 text-right">
                      <p className="text-2xl font-bold text-warm-text">
                        {item._lpsDisplay}
                      </p>
                      <p className="text-[0.65rem] text-warm-muted">/ 10 分</p>
                    </div>
                  </div>
                  <p className="mt-4 text-sm leading-7 text-warm-secondary">
                    {item.summary}
                  </p>
                  <div className="mt-3 text-xs text-warm-accent">
                    {isExpanded ? "收起详情" : "展开详情"}
                  </div>
                </button>

                {isExpanded ? (
                  <div className="border-t border-warm-border-light px-6 pb-6">
                    <div className="mt-4 space-y-3">
                      {item.canvas_elements ? (
                        <DetailCard title="对应突破与画布切入点" content={item.canvas_elements} />
                      ) : null}
                      {item.expected_effects ? (
                        <DetailCard title="预期效果" content={item.expected_effects} />
                      ) : null}
                      {item.core_data_requirements ? (
                        <DetailCard title="核心数据要求" content={item.core_data_requirements} />
                      ) : null}
                      <div className="rounded-xl bg-warm-inset px-4 py-3">
                        <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">
                          四象限评分
                        </p>
                        <div className="mt-2 grid grid-cols-2 gap-2 text-sm text-warm-secondary">
                          <div>
                            <span className="text-warm-muted">结构化程度 X：</span>
                            <span className="font-semibold text-warm-text">{item._x}</span>
                          </div>
                          <div>
                            <span className="text-warm-muted">实施复杂度 Y：</span>
                            <span className="font-semibold text-warm-text">{item._y}</span>
                          </div>
                          <div>
                            <span className="text-warm-muted">QS：</span>
                            <span className="font-semibold text-warm-text">{item._qs}</span>
                          </div>
                          <div>
                            <span className="text-warm-muted">LPS：</span>
                            <span className="font-semibold text-warm-text">
                              {item._lpsDisplay} / 10
                            </span>
                          </div>
                        </div>
                      </div>
                      {item.priority_recommendation ? (
                        <DetailCard title="推荐说明" content={item.priority_recommendation} />
                      ) : null}
                    </div>
                  </div>
                ) : null}
              </article>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function PreviewRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-warm-muted">{label}</span>
      <span className="font-semibold text-warm-text">{value}</span>
    </div>
  );
}

function ScoreEditor({
  label,
  value,
  helper,
  description,
  onDecrease,
  onIncrease,
  onChange,
}: {
  label: string;
  value: number;
  helper: string;
  description: string;
  onDecrease: () => void;
  onIncrease: () => void;
  onChange: (value: number) => void;
}) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm">
        <span className="font-medium text-warm-secondary">{label}</span>
        <span className="font-bold text-warm-text">{value}</span>
      </div>
      <p className="mb-2 text-[0.7rem] text-warm-muted">{helper}</p>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onDecrease}
          className="flex h-8 w-8 items-center justify-center rounded-full border border-warm-border-light bg-white text-sm text-warm-text transition hover:border-warm-accent"
        >
          -
        </button>
        <input
          type="range"
          min="1"
          max="5"
          step="0.1"
          value={value}
          onChange={(event) => onChange(parseFloat(event.target.value))}
          className="w-full accent-amber-600"
        />
        <button
          type="button"
          onClick={onIncrease}
          className="flex h-8 w-8 items-center justify-center rounded-full border border-warm-border-light bg-white text-sm text-warm-text transition hover:border-warm-accent"
        >
          +
        </button>
      </div>
      <div className="mt-1 flex justify-between text-[0.65rem] text-warm-muted">
        <span>1</span>
        <span>5</span>
      </div>
      <p className="mt-2 text-[0.7rem] leading-relaxed text-warm-muted">
        {description}
      </p>
    </div>
  );
}

function DetailCard({ title, content }: { title: string; content: string }) {
  return (
    <div className="rounded-xl bg-warm-inset px-4 py-3">
      <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">
        {title}
      </p>
      <p className="mt-1 text-sm leading-7 text-warm-secondary">{content}</p>
    </div>
  );
}
