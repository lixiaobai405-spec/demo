import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { DirectionExpansionPanel } from "@/components/direction-expansion-panel";

describe("DirectionExpansionPanel", () => {
  /**
   * AI 增强进行中时，只允许看到等待态，不能提前看到规则版方向卡片或确认按钮。
   */
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

    expect(screen.getByText("AI 正在增强中，请稍候")).toBeInTheDocument();
    expect(screen.queryByText("AI 驱动动态定价")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /确认选择/ }),
    ).not.toBeInTheDocument();
  });

  /**
   * 确认底部确认按钮只统计当前增强后结果里仍可见的方向，避免把旧勾选残留算进去。
   */
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
});
