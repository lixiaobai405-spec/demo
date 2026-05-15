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
          scoring_method: "rule_based_v1",
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
});
