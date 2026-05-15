"use client";

import React from "react";
import { useState } from "react";
import Link from "next/link";
import type { ScenarioRecommendationResult } from "@/lib/types";

/**
 * 渲染 AI 场景推荐列表，以关键字段卡片形式展示。
 */
export function ScenarioRecommendationsPanel({
  assessmentId, readyForReport, scenarioRecommendation,
}: {
  assessmentId: string; readyForReport: boolean; scenarioRecommendation: ScenarioRecommendationResult;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  return (
    <div className="card-inset">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">场景推荐</p>
          <h2 className="section-heading">Top 3 AI 场景推荐</h2>
        </div>
        <span className="badge badge-warning">{scenarioRecommendation.scoring_method}</span>
      </div>

      <p className="mt-3 text-sm leading-7 text-warm-secondary">
        已评估 {scenarioRecommendation.evaluated_count} 个候选场景，以下展示 Top 3。点击卡片展开查看详情。
      </p>

      {readyForReport ? (
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href={`/report/${assessmentId}`} className="btn-primary" target="_blank" rel="noopener noreferrer">进入报告生成</Link>
        </div>
      ) : null}

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        {scenarioRecommendation.top_scenarios.map((item, index) => {
          const isExpanded = expandedId === item.scenario_id;
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
                    <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">Rank {index + 1}</p>
                    <h3 className="mt-2 font-heading text-xl font-bold text-warm-text">{item.name}</h3>
                    <p className="mt-2 text-sm text-warm-accent">{item.category}</p>
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
