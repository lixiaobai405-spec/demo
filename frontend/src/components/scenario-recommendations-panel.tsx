"use client";

import React, { useCallback, useState } from "react";
import { useRouter } from "next/navigation";

import type {
  ScenarioRecommendationItem,
  ScenarioRecommendationResult,
} from "@/lib/types";
import { useGenerateCompetitiveness } from "@/hooks/use-competitiveness";
import { toast } from "@/hooks/use-toast";
import { formatMutationError } from "@/lib/api";
import { Button } from "@/components/ui/button";

const RANK_LABELS = ["No.1", "No.2", "No.3"];

const QUADRANT_BADGE: Record<string, string> = {
  自动化主战场: "badge-success",
  AI优先区: "badge-warning",
  人机协作区: "badge-info",
  人工保留区: "badge-muted",
};

function getRecommendationLevel(item: ScenarioRecommendationItem): string | null {
  if (item.recommendation_level) {
    return item.recommendation_level;
  }

  if (item.priority_lps_display == null) return null;
  if (item.priority_lps_display >= 8.0) return "立即启动";
  if (item.priority_lps_display >= 5.0) return "规划推进";
  return "持续观察";
}

function getLevelBadge(level: string): string {
  if (level === "立即启动") return "badge-success";
  if (level === "规划推进") return "badge-warning";
  return "badge-muted";
}

export function ScenarioRecommendationsPanel({
  assessmentId,
  readyForReport,
  scenarioRecommendation,
  hideNextAction,
}: {
  assessmentId: string;
  readyForReport: boolean;
  scenarioRecommendation: ScenarioRecommendationResult;
  hideNextAction?: boolean;
}) {
  const [expandedIds, setExpandedIds] = useState<string[]>([]);
  const router = useRouter();
  const generateCompetitiveness = useGenerateCompetitiveness();

  const handleGenerateCompetitiveness = useCallback(async () => {
    try {
      await generateCompetitiveness.mutateAsync(assessmentId);
      toast({ title: "差异化竞争力报告已生成" });
      router.push(`/assessment/${assessmentId}/competitiveness`);
    } catch (error) {
      toast({
        title: "生成失败",
        description: formatMutationError(error, "差异化竞争力分析"),
        variant: "destructive",
      });
    }
  }, [assessmentId, generateCompetitiveness, router]);

  const toggleExpanded = useCallback((scenarioId: string) => {
    setExpandedIds((current) =>
      current.includes(scenarioId)
        ? current.filter((item) => item !== scenarioId)
        : [...current, scenarioId],
    );
  }, []);

  return (
    <div className="card-inset">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">场景推荐</p>
          <h2 className="section-heading">Top 3 AI 推荐场景</h2>
        </div>
        <span className="badge badge-warning">
          {scenarioRecommendation.scoring_method === "four_quadrant_v1"
            ? "四象限评分"
            : "规则评分"}
        </span>
      </div>

      <p className="mt-3 text-sm leading-7 text-warm-secondary">
        当前共评估 {scenarioRecommendation.evaluated_count} 个候选场景。下方展示最终 Top 3 推荐结果，可同时展开查看详情。
      </p>

      {!hideNextAction && readyForReport ? (
        <div className="mt-6 flex flex-wrap gap-3">
          <Button
            onClick={handleGenerateCompetitiveness}
            disabled={generateCompetitiveness.isPending}
            loading={generateCompetitiveness.isPending}
          >
            {generateCompetitiveness.isPending
              ? "生成中..."
              : "生成差异化竞争力"}
          </Button>
        </div>
      ) : null}

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        {scenarioRecommendation.top_scenarios.map((item, index) => {
          const isExpanded = expandedIds.includes(item.scenario_id);
          const level = getRecommendationLevel(item);
          return (
            <article
              key={item.scenario_id}
              className={`rounded-xl border bg-warm-surface transition ${
                isExpanded
                  ? "border-warm-accent/40 ring-1 ring-warm-accent/15"
                  : "border-warm-border-light"
              }`}
            >
              <button
                type="button"
                onClick={() => toggleExpanded(item.scenario_id)}
                className="w-full p-6 text-left"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">
                      {RANK_LABELS[index] ?? `Rank ${index + 1}`}
                    </p>
                    <h3 className="mt-2 font-heading text-xl font-bold text-warm-text">
                      {item.name}
                    </h3>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <p className="text-sm text-warm-accent">{item.category}</p>
                      {item.priority_quadrant ? (
                        <span
                          className={`badge text-[0.65rem] ${
                            QUADRANT_BADGE[item.priority_quadrant] ?? "badge-muted"
                          }`}
                        >
                          {item.priority_quadrant}
                        </span>
                      ) : null}
                      {level ? (
                        <span className={`badge text-[0.65rem] ${getLevelBadge(level)}`}>
                          {level}
                        </span>
                      ) : null}
                    </div>
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
                      <DetailCard title="对应切入点" content={item.canvas_elements} />
                    ) : null}
                    {item.expected_effects ? (
                      <DetailCard title="预期效果" content={item.expected_effects} />
                    ) : null}
                    {item.core_data_requirements ? (
                      <DetailCard title="核心数据要求" content={item.core_data_requirements} />
                    ) : null}
                    {item.priority_lps_display != null ? (
                      <div className="rounded-xl bg-warm-inset px-4 py-3">
                        <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">
                          四象限评分
                        </p>
                        <div className="mt-2 grid grid-cols-2 gap-2 text-sm text-warm-secondary">
                          <div>结构化程度 X：<span className="font-semibold text-warm-text">{item.priority_structuredness_x}</span></div>
                          <div>实施复杂度 Y：<span className="font-semibold text-warm-text">{item.priority_complexity_y}</span></div>
                          <div>QS：<span className="font-semibold text-warm-text">{item.priority_qs}</span></div>
                          <div>LPS：<span className="font-semibold text-warm-text">{item.priority_lps_display} / 10</span></div>
                        </div>
                      </div>
                    ) : null}
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
