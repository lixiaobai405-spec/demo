import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { DirectionExpansionPanel } from "@/components/direction-expansion-panel";

describe("DirectionExpansionPanel", () => {
  it("shows only waiting state while llm enhancement is pending", () => {
    render(
      <DirectionExpansionPanel
        data={{
          assessment_id: "assessment-1",
          direction_expansion: {
            generation_mode: "llm",
            llm_status: "pending",
            total_suggestions: 2,
            elements: [
              {
                element_key: "revenue_streams",
                element_title: "收入来源",
                suggestions: [
                  {
                    direction_id: "rule-direction-1",
                    element_key: "revenue_streams",
                    title: "AI 驱动动态定价",
                    description: "根据用户偏好实时调价。",
                    expected_impact: "提升转化率。",
                    data_needed: ["订单数据"],
                    related_scenario_categories: ["销售增长"],
                  },
                ],
              },
            ],
          },
          direction_selection: null,
        }}
        selectedIds={["rule-direction-1"]}
        isSelecting={false}
        isLLMPending
        onToggleDirection={vi.fn()}
        onConfirmSelection={vi.fn()}
      />,
    );

    expect(screen.getByText("AI 正在生成方向候选")).toBeInTheDocument();
    expect(screen.queryByText("AI 驱动动态定价")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /确认选择/ }),
    ).not.toBeInTheDocument();
  });

  it("shows a scenario waiting state after directions are confirmed", () => {
    render(
      <DirectionExpansionPanel
        data={{
          assessment_id: "assessment-1",
          direction_expansion: {
            generation_mode: "llm",
            llm_status: "completed",
            total_suggestions: 2,
            elements: [
              {
                element_key: "revenue_streams",
                element_title: "收入来源",
                suggestions: [
                  {
                    direction_id: "direction-1",
                    element_key: "revenue_streams",
                    title: "AI 驱动动态定价",
                    description: "根据用户偏好实时调价。",
                    expected_impact: "提升转化率。",
                    data_needed: ["订单数据"],
                    related_scenario_categories: ["销售增长"],
                  },
                ],
              },
            ],
          },
          direction_selection: {
            assessment_id: "assessment-1",
            generation_mode: "rule_based",
            created_at: null,
            updated_at: null,
            selected_directions: [
              {
                direction_id: "direction-1",
                element_key: "revenue_streams",
                title: "AI 驱动动态定价",
                description: "根据用户偏好实时调价。",
                expected_impact: "提升转化率。",
                data_needed: ["订单数据"],
                related_scenario_categories: ["销售增长"],
              },
            ],
          },
        }}
        selectedIds={["direction-1"]}
        isSelecting={false}
        isNextStepPending
        onToggleDirection={vi.fn()}
        onConfirmSelection={vi.fn()}
        onNextStep={vi.fn()}
      />,
    );

    expect(screen.getByText("AI 正在生成推荐场景")).toBeInTheDocument();
    expect(screen.getByText("请稍候，系统正在同步场景结果。")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "生成 AI 推荐场景" }),
    ).not.toBeInTheDocument();
  });

  it("counts only directions that exist in the current expansion result", () => {
    render(
      <DirectionExpansionPanel
        data={{
          assessment_id: "assessment-1",
          direction_expansion: {
            generation_mode: "llm",
            llm_status: "completed",
            total_suggestions: 2,
            elements: [
              {
                element_key: "revenue_streams",
                element_title: "收入来源",
                suggestions: [
                  {
                    direction_id: "enhanced-direction-1",
                    element_key: "revenue_streams",
                    title: "AI 驱动动态定价",
                    description: "根据用户偏好实时调价。",
                    expected_impact: "提升转化率。",
                    data_needed: ["订单数据"],
                    related_scenario_categories: ["销售增长"],
                  },
                  {
                    direction_id: "enhanced-direction-2",
                    element_key: "revenue_streams",
                    title: "会员订阅计划",
                    description: "构建持续付费模式。",
                    expected_impact: "提升复购率。",
                    data_needed: ["会员数据"],
                    related_scenario_categories: ["销售增长"],
                  },
                ],
              },
            ],
          },
          direction_selection: null,
        }}
        selectedIds={["legacy-direction", "enhanced-direction-1"]}
        isSelecting={false}
        onToggleDirection={vi.fn()}
        onConfirmSelection={vi.fn()}
      />,
    );

    expect(
      screen.getByRole("button", { name: "确认选择（1 个方向）" }),
    ).toBeInTheDocument();
  });

  it("ignores stale selections and deduplicates the displayed candidate count", () => {
    render(
      <DirectionExpansionPanel
        data={{
          assessment_id: "assessment-1",
          direction_expansion: {
            generation_mode: "llm",
            llm_status: "completed",
            total_suggestions: 7,
            elements: [
              {
                element_key: "revenue_streams",
                element_title: "收入来源",
                suggestions: [
                  {
                    direction_id: "direction-1",
                    element_key: "revenue_streams",
                    title: "方向 1",
                    description: "描述 1",
                    expected_impact: "影响 1",
                    data_needed: ["数据 1"],
                    related_scenario_categories: ["销售增长"],
                  },
                  {
                    direction_id: "direction-2",
                    element_key: "revenue_streams",
                    title: "方向 2",
                    description: "描述 2",
                    expected_impact: "影响 2",
                    data_needed: ["数据 2"],
                    related_scenario_categories: ["销售增长"],
                  },
                  {
                    direction_id: "direction-3",
                    element_key: "revenue_streams",
                    title: "方向 3",
                    description: "描述 3",
                    expected_impact: "影响 3",
                    data_needed: ["数据 3"],
                    related_scenario_categories: ["销售增长"],
                  },
                ],
              },
              {
                element_key: "customer_relationships",
                element_title: "客户关系",
                suggestions: [
                  {
                    direction_id: "direction-3",
                    element_key: "customer_relationships",
                    title: "重复方向 3",
                    description: "重复描述",
                    expected_impact: "重复影响",
                    data_needed: ["重复数据"],
                    related_scenario_categories: ["客户服务"],
                  },
                  {
                    direction_id: "direction-4",
                    element_key: "customer_relationships",
                    title: "方向 4",
                    description: "描述 4",
                    expected_impact: "影响 4",
                    data_needed: ["数据 4"],
                    related_scenario_categories: ["客户服务"],
                  },
                  {
                    direction_id: "direction-5",
                    element_key: "customer_relationships",
                    title: "方向 5",
                    description: "描述 5",
                    expected_impact: "影响 5",
                    data_needed: ["数据 5"],
                    related_scenario_categories: ["客户服务"],
                  },
                  {
                    direction_id: "direction-6",
                    element_key: "customer_relationships",
                    title: "方向 6",
                    description: "描述 6",
                    expected_impact: "影响 6",
                    data_needed: ["数据 6"],
                    related_scenario_categories: ["客户服务"],
                  },
                ],
              },
            ],
          },
          direction_selection: {
            assessment_id: "assessment-1",
            generation_mode: "rule_based",
            created_at: null,
            updated_at: null,
            selected_directions: [
              {
                direction_id: "legacy-direction",
                element_key: "revenue_streams",
                title: "旧方向",
                description: "旧描述",
                expected_impact: "旧影响",
                data_needed: [],
                related_scenario_categories: [],
              },
            ],
          },
        }}
        selectedIds={["direction-1"]}
        isSelecting={false}
        onToggleDirection={vi.fn()}
        onConfirmSelection={vi.fn()}
      />,
    );

    expect(screen.getByText("共 6 个候选")).toBeInTheDocument();
    expect(screen.queryByText("已确认 1 个创新方向")).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "确认选择（1 个方向）" }),
    ).toBeInTheDocument();
  });
});
