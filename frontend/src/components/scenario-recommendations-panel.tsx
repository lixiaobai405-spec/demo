"use client";

import React from "react";
import { useCallback, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { ScenarioRecommendationItem, ScenarioRecommendationResult } from "@/lib/types";
import { useGenerateCompetitiveness } from "@/hooks/use-competitiveness";
import { toast } from "@/hooks/use-toast";
import { formatMutationError } from "@/lib/api";
import { Button } from "@/components/ui/button";

const RANK_LABELS = ["No.1", "No.2", "No.3"];

const QUADRANT_BADGE: Record<string, string> = {
  "自动化主战场": "badge-success",
  "AI优先区": "badge-warning",
  "人机协作区": "badge-info",
  "人类保留区": "badge-muted",
};

function getRecommendationLevel(lpsDisplay: number | null | undefined): string | null {
  if (lpsDisplay == null) return null;
  if (lpsDisplay >= 8.0) return "立即启动";
  if (lpsDisplay >= 5.0) return "规划推进";
  return "观察";
}

function getLevelBadge(level: string): string {
  if (level === "立即启动") return "badge-success";
  if (level === "规划推进") return "badge-warning";
  return "badge-muted";
}

function hasPriorityFields(item: ScenarioRecommendationItem): boolean {
  return item.priority_lps_display != null;
}

/**
 * 渲染 AI 场景推荐列表，以关键字段卡片形式展示。
 * 当 scoring_method 为 four_quadrant_v1 时展示四象限评分字段。
 */
export function ScenarioRecommendationsPanel({
  assessmentId, readyForReport, scenarioRecommendation, hideNextAction,
}: {
  assessmentId: string; readyForReport: boolean; scenarioRecommendation: ScenarioRecommendationResult;
  hideNextAction?: boolean;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const router = useRouter();
  const generateCompetitiveness = useGenerateCompetitiveness();

  const handleGenerateCompetitiveness = useCallback(async () => {
    try {
      await generateCompetitiveness.mutateAsync(assessmentId);
      toast({ title: "差异化竞争力分析已生成" });
      router.push(`/assessment/${assessmentId}/competitiveness`);
    } catch (e) {
      toast({
        title: "生成失败",
        description: formatMutationError(e, "差异化竞争力分析"),
        variant: "destructive",
      });
    }
  }, [assessmentId, generateCompetitiveness, router]);

  const scoringLabel =
    scenarioRecommendation.scoring_method === "four_quadrant_v1"
      ? "四象限评分"
      : "规则评分";

  return (
    <div className="card-inset">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">场景推荐</p>
          <h2 className="section-heading">Top 3 AI 场景推荐</h2>
        </div>
        <span className="badge badge-warning">{scoringLabel}</span>
      </div>

      <p className="mt-3 text-sm leading-7 text-warm-secondary">
        已评估 {scenarioRecommendation.evaluated_count} 个候选场景，以下展示 Top 3。点击卡片展开查看详情。
      </p>

      {!hideNextAction && readyForReport ? (
        <div className="mt-6 flex flex-wrap gap-3">
          <Button
            onClick={handleGenerateCompetitiveness}
            disabled={generateCompetitiveness.isPending}
            loading={generateCompetitiveness.isPending}
          >
            {generateCompetitiveness.isPending ? "正在生成..." : "生成差异化竞争力 →"}
          </Button>
        </div>
      ) : null}

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        {scenarioRecommendation.top_scenarios.map((item, index) => {
          const isExpanded = expandedId === item.scenario_id;
          const recLevel = getRecommendationLevel(item.priority_lps_display);
          const showPriority = hasPriorityFields(item);

          return (
            <div
              key={item.scenario_id}
              className={`rounded-xl border bg-warm-surface transition cursor-pointer hover:shadow-md ${
                isExpanded ? "border-warm-accent/40 ring-1 ring-warm-accent/15" : "border-warm-border-light"
              }`}
              onClick={() => setExpandedId(isExpanded ? null : item.scenario_id)}
            >
              {/* Always visible header */}
              <div className="p-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">{RANK_LABELS[index] ?? `Rank ${index + 1}`}</p>
                    <h3 className="mt-2 font-heading text-xl font-bold text-warm-text">{item.name}</h3>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <p className="text-sm text-warm-accent">{item.category}</p>
                      {showPriority && item.priority_quadrant && (
                        <span className={`badge text-[0.65rem] ${QUADRANT_BADGE[item.priority_quadrant] ?? "badge-muted"}`}>
                          {item.priority_quadrant}
                        </span>
                      )}
                      {recLevel && (
                        <span className={`badge text-[0.65rem] ${getLevelBadge(recLevel)}`}>
                          {recLevel}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <p className="mt-4 text-sm leading-7 text-warm-secondary">{item.summary}</p>
                <div className="mt-3 flex items-center gap-1 text-xs text-warm-accent">
                  <span>{isExpanded ? "收起" : "展开查看关键字段"}</span>
                </div>
              </div>

              {/* Expandable detail */}
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
                        <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">预期效果</p>
                        <p className="mt-1 text-sm text-warm-secondary">{item.expected_effects}</p>
                      </div>
                    ) : null}
                    {item.core_data_requirements ? (
                      <div className="rounded-xl bg-warm-inset px-4 py-3">
                        <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">所需核心数据</p>
                        <p className="mt-1 text-sm text-warm-secondary">{item.core_data_requirements}</p>
                      </div>
                    ) : null}

                    {/* 四象限评分详情 */}
                    {showPriority && (
                      <div className="rounded-xl bg-warm-inset px-4 py-3">
                        <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">四象限优先级评分</p>
                        <div className="mt-2 grid grid-cols-2 gap-2 text-sm text-warm-secondary">
                          <div>
                            <span className="text-warm-muted">结构化程度 X：</span>
                            <span className="font-semibold text-warm-text">{item.priority_structuredness_x}</span>
                            <span className="text-warm-muted"> / 5</span>
                          </div>
                          <div>
                            <span className="text-warm-muted">实施复杂度 Y：</span>
                            <span className="font-semibold text-warm-text">{item.priority_complexity_y}</span>
                            <span className="text-warm-muted"> / 5</span>
                          </div>
                          <div>
                            <span className="text-warm-muted">QS 象限分：</span>
                            <span className="font-semibold text-warm-text">{item.priority_qs}</span>
                          </div>
                          <div>
                            <span className="text-warm-muted">综合优先级：</span>
                            <span className="font-semibold text-warm-text">{item.priority_lps_display}</span>
                            <span className="text-warm-muted"> / 10</span>
                          </div>
                        </div>
                      </div>
                    )}

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
  );
}
