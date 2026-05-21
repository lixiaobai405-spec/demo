"use client";

import React from "react";

import type { CompetitivenessResponse } from "@/lib/types";

type TemplateField = {
  label: string;
  value: string;
};

type TemplateRow = {
  module: string;
  intro: string;
  fields: TemplateField[];
};

export function CompetitivenessPanel({
  data,
  companyName = "企业",
  topScenarioNames = [],
}: {
  data: CompetitivenessResponse;
  companyName?: string;
  topScenarioNames?: string[];
}) {
  const rows = buildTemplateRows(data.result, topScenarioNames);

  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">差异化竞争力</p>
          <h2 className="section-heading">内容输出结构（Output Template）</h2>
        </div>
        <span className="badge badge-accent">固定模板版式</span>
      </div>

      <div className="mt-6 space-y-3">
        <p className="text-sm font-medium text-primary">输出文档标题：</p>
        <div className="rounded-2xl border border-[rgba(212,168,83,0.18)] bg-[linear-gradient(135deg,rgba(212,168,83,0.08),rgba(246,242,235,0.92))] px-6 py-4 font-heading text-xl text-foreground shadow-sm">
          # 《{companyName}·差异化竞争力策略概要》
        </div>
      </div>

      <div className="mt-8 overflow-x-auto rounded-[22px] border border-[hsl(var(--border))] bg-[hsl(var(--card))] shadow-[0_10px_30px_rgba(61,52,40,0.06)]">
        <table className="min-w-[920px] w-full border-collapse">
          <thead>
            <tr className="bg-[linear-gradient(135deg,#4A3728,#6A513A)] text-left text-[#FFF8EE]">
              <th className="w-[240px] border border-[rgba(255,248,238,0.12)] px-5 py-4 font-heading text-lg font-semibold tracking-[0.01em]">
                字段模块
              </th>
              <th className="border border-[rgba(255,248,238,0.12)] px-5 py-4 font-heading text-lg font-semibold tracking-[0.01em]">
                输出内容说明
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.module}
                className="align-top transition-colors odd:bg-[rgba(246,242,235,0.66)] even:bg-[rgba(255,253,249,0.96)] hover:bg-[rgba(212,168,83,0.06)]"
              >
                <td className="border border-[hsl(var(--border))] bg-[rgba(241,236,226,0.72)] px-5 py-5 font-heading text-[1.05rem] font-semibold leading-8 text-foreground">
                  {row.module}
                </td>
                <td className="border border-[hsl(var(--border))] px-5 py-5">
                  <div className="space-y-3 text-[1.02rem] leading-8 text-foreground">
                    <p className="font-medium text-foreground">{row.intro}</p>
                    {row.fields.map((field) => (
                      <div key={`${row.module}-${field.label}`}>
                        <span className="font-semibold text-primary">{field.label}：</span>
                        <span className="text-foreground">{field.value}</span>
                      </div>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function buildTemplateRows(
  result: CompetitivenessResponse["result"],
  topScenarioNames: string[],
): TemplateRow[] {
  const scenarios = topScenarioNames.length > 0 ? topScenarioNames : collectPointTitles(result);

  return [
    {
      module: "① AI 点优势串联叙述",
      intro: `将选定的 Top 3 AI 场景（${joinOrFallback(scenarios)}）串联为系统性方案命名：`,
      fields: [
        { label: "系统方案名称", value: buildSystemSolutionName(result, scenarios) },
        { label: "串联逻辑描述", value: buildSolutionChainLogic(result) },
        { label: "各 AI 点如何协同增效", value: buildSynergyDescription(result) },
      ],
    },
    {
      module: "② VP 重构输出",
      intro: "基于 AI 系统方案，重构价值主张（VP）：",
      fields: [
        { label: "旧 VP", value: result.vp_reconstruction.current_vp },
        { label: "新 VP（AI 重构）", value: result.vp_reconstruction.enhanced_vp },
        { label: "VP 交付逻辑变化", value: result.vp_reconstruction.customer_value_shift },
      ],
    },
    {
      module: "③ 竞争优势差异化定位",
      intro: "与行业竞争对手的差异化优势描述：",
      fields: [
        { label: "差异化优势描述", value: buildDifferentiationOverview(result) },
        { label: "差异化定位语", value: buildDifferentiationPositioning(result) },
        { label: "AI 原生竞争者的威胁应对策略", value: buildAiNativeThreatResponse(result) },
      ],
    },
    {
      module: "④ 核心竞争力提升路径",
      intro: "3 个阶段的竞争力提升路径（短中长期）：",
      fields: [
        { label: "短期", value: result.delivery_strategy.phase_1_quick_win },
        { label: "中期", value: result.delivery_strategy.phase_2_scale },
        { label: "长期", value: result.delivery_strategy.phase_3_moat },
      ],
    },
  ];
}

function buildSystemSolutionName(
  result: CompetitivenessResponse["result"],
  topScenarioNames: string[],
): string {
  const connections = result.connections.slice(0, 2);
  if (connections.length > 0) {
    const primary = stripLineSuffix(connections[0].line_name);
    if (connections.length > 1) {
      const secondary = stripLineSuffix(connections[1].line_name);
      if (secondary && secondary !== primary) {
        return `${primary}×${secondary}智能协同系统`;
      }
    }
    return `${primary}智能协同系统`;
  }
  if (topScenarioNames.length > 0) {
    return `${topScenarioNames[0]}智能协同系统`;
  }
  return "AI 差异化竞争力协同系统";
}

function buildSolutionChainLogic(result: CompetitivenessResponse["result"]): string {
  const parts = result.connections.slice(0, 3)
    .map((conn) => {
      const logic = conn.linkage_logic || conn.strategic_narrative || conn.competitive_impact;
      return logic ? `${conn.line_name}：${logic}` : "";
    })
    .filter(Boolean);
  return parts.join("；") || result.overall_narrative;
}

function buildSynergyDescription(result: CompetitivenessResponse["result"]): string {
  const parts = result.connections.slice(0, 3)
    .map((conn) => {
      const pointTitles = joinOrFallback(conn.point_titles);
      return `${pointTitles}共同支撑${conn.line_name}，带来${conn.competitive_impact || "竞争力增益"}`;
    })
    .filter(Boolean);
  return parts.join("；") || result.overall_narrative;
}

function buildDifferentiationOverview(result: CompetitivenessResponse["result"]): string {
  return result.overall_narrative?.trim() || buildDifferentiationPositioning(result);
}

function buildDifferentiationPositioning(result: CompetitivenessResponse["result"]): string {
  const advantages = result.advantages.slice(0, 2).map((item) => item.advantage_name);
  return `围绕“${result.vp_reconstruction.enhanced_vp}”，以${joinOrFallback(advantages)}构建不可替代的客户价值定位。`;
}

function buildAiNativeThreatResponse(result: CompetitivenessResponse["result"]): string {
  const lineNames = result.connections.slice(0, 2).map((item) => item.line_name);
  return `不与 AI 原生竞争者比拼单点模型能力，而是把${joinOrFallback(lineNames)}所需的数据、流程与知识沉淀为组织标准；先通过“${result.delivery_strategy.phase_1_quick_win}”快速验证，再以“${result.delivery_strategy.phase_3_moat}”形成持续迭代与交付壁垒。`;
}

function collectPointTitles(result: CompetitivenessResponse["result"]): string[] {
  return result.connections
    .flatMap((item) => item.point_titles)
    .filter((value, index, self) => Boolean(value) && self.indexOf(value) === index)
    .slice(0, 3);
}

function joinOrFallback(values: string[]): string {
  const filtered = values.map((item) => item.trim()).filter(Boolean);
  return filtered.length > 0 ? filtered.join("、") : "当前已选 AI 方向";
}

function stripLineSuffix(value: string): string {
  return value.replace(/线$/, "").trim() || value;
}
