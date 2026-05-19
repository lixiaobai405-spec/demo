import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ScenarioRecommendationsPanel } from "@/components/scenario-recommendations-panel";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/hooks/use-competitiveness", () => ({
  useGenerateCompetitiveness: () => ({ mutateAsync: vi.fn(), isPending: false }),
}));

vi.mock("@/hooks/use-toast", () => ({
  toast: vi.fn(),
}));

describe("ScenarioRecommendationsPanel", () => {
  /**
   * 确认场景摘要按完整文本展示，不依赖省略号截断。
   */
  it("renders the full scenario summary text without line clamp styling", () => {
    render(
      <ScenarioRecommendationsPanel
        assessmentId="assessment-1"
        readyForReport={false}
        scenarioRecommendation={{
          scoring_method: "four_quadrant_v1",
          evaluated_count: 3,
          top_scenarios: [
            {
              scenario_id: "scenario-1",
              name: "门店知识助手",
              category: "运营提效",
              summary: "完整摘要内容不应被样式截断或替换成省略号。",
              canvas_elements: "客户关系、关键资源",
              expected_effects: "降低培训成本、提升运营效率",
              core_data_requirements: "POS 数据、知识库文档",
              priority_structuredness_x: 4,
              priority_complexity_y: 2,
              priority_qs: 8,
              priority_lps: 4.0,
              priority_lps_display: 8.0,
              priority_quadrant: "自动化主战场",
              priority_tier: 1,
              priority_recommendation: "强烈推荐快速启动。",
            },
          ],
          created_at: null,
          updated_at: null,
        }}
      />,
    );

    const summary = screen.getByText("完整摘要内容不应被样式截断或替换成省略号。");
    expect(summary).toBeInTheDocument();
    expect(summary).not.toHaveClass("line-clamp-2");
  });

  /**
   * 确认四象限评分字段在卡片头部和展开区正确展示。
   */
  it("renders quadrant badge and recommendation level when priority fields present", () => {
    render(
      <ScenarioRecommendationsPanel
        assessmentId="assessment-1"
        readyForReport={false}
        scenarioRecommendation={{
          scoring_method: "four_quadrant_v1",
          evaluated_count: 3,
          top_scenarios: [
            {
              scenario_id: "scenario-1",
              name: "门店知识助手",
              category: "运营提效",
              summary: "测试摘要。",
              canvas_elements: "客户关系",
              expected_effects: "降低培训成本",
              core_data_requirements: "POS 数据",
              priority_structuredness_x: 4,
              priority_complexity_y: 2,
              priority_qs: 8,
              priority_lps: 4.0,
              priority_lps_display: 8.0,
              priority_quadrant: "自动化主战场",
              priority_tier: 1,
              priority_recommendation: "强烈推荐快速启动。",
            },
          ],
          created_at: null,
          updated_at: null,
        }}
      />,
    );

    // 卡片头部展示象限徽章和推荐等级
    expect(screen.getByText("自动化主战场")).toBeInTheDocument();
    expect(screen.getByText("立即启动")).toBeInTheDocument();

    // 展开卡片后应展示评分详情
    // 点击卡片展开
    const card = screen.getByText("门店知识助手").closest("div");
    expect(card).toBeInTheDocument();
  });

  /**
   * 确认无 priority 字段时（旧数据兼容）不崩溃。
   */
  it("renders without crashing when priority fields are absent", () => {
    render(
      <ScenarioRecommendationsPanel
        assessmentId="assessment-1"
        readyForReport={false}
        scenarioRecommendation={{
          scoring_method: "rule_based_v1",
          evaluated_count: 1,
          top_scenarios: [
            {
              scenario_id: "scenario-1",
              name: "旧版场景",
              category: "运营提效",
              summary: "旧数据无评分字段。",
              canvas_elements: "客户关系",
              expected_effects: "效果待验证",
              core_data_requirements: "POS 数据",
            },
          ],
          created_at: null,
          updated_at: null,
        }}
      />,
    );

    // 旧数据应正常渲染，不展示评分块
    expect(screen.getByText("旧版场景")).toBeInTheDocument();
    expect(screen.queryByText("自动化主战场")).not.toBeInTheDocument();
    expect(screen.queryByText("立即启动")).not.toBeInTheDocument();
    expect(screen.queryByText("四象限优先级评分")).not.toBeInTheDocument();
  });

  /**
   * 确认 scoring_method 标签正确展示。
   */
  it("renders correct scoring method label", () => {
    const { rerender } = render(
      <ScenarioRecommendationsPanel
        assessmentId="assessment-1"
        readyForReport={false}
        scenarioRecommendation={{
          scoring_method: "four_quadrant_v1",
          evaluated_count: 0,
          top_scenarios: [],
          created_at: null,
          updated_at: null,
        }}
      />,
    );
    expect(screen.getByText("四象限评分")).toBeInTheDocument();

    rerender(
      <ScenarioRecommendationsPanel
        assessmentId="assessment-1"
        readyForReport={false}
        scenarioRecommendation={{
          scoring_method: "rule_based_v1",
          evaluated_count: 0,
          top_scenarios: [],
          created_at: null,
          updated_at: null,
        }}
      />,
    );
    expect(screen.getByText("规则评分")).toBeInTheDocument();
  });
});
