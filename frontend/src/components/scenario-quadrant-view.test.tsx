import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ScenarioQuadrantView } from "@/components/scenario-quadrant-view";

const updateScenarioPoolMock = vi.fn();
const toastMock = vi.fn();

vi.mock("@/hooks/use-toast", () => ({
  toast: (...args: unknown[]) => toastMock(...args),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    updateScenarioPool: (...args: unknown[]) => updateScenarioPoolMock(...args),
  };
});

function buildScenario(
  scenarioId: string,
  name: string,
  x: number,
  y: number,
) {
  return {
    scenario_id: scenarioId,
    name,
    category: "零售运营",
    summary: `${name} 摘要`,
    canvas_elements: "客户关系、关键资源",
    expected_effects: `${name} 预期效果`,
    core_data_requirements: `${name} 数据要求`,
    priority_structuredness_x: x,
    priority_complexity_y: y,
    priority_qs: x * y,
    priority_lps: x * 0.6 + (6 - y) * 0.4,
    priority_lps_display: +(((x * 0.6 + (6 - y) * 0.4) * 2).toFixed(1)),
    priority_quadrant: "自动化主战场",
    priority_tier: 1,
    priority_recommendation: `${name} 推荐说明`,
    recommendation_level: "立即启动",
    industry_coefficient: 1,
  };
}

function renderView(recommendation: Record<string, unknown>) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ScenarioQuadrantView
        assessmentId="assessment-1"
        scenarioRecommendation={recommendation as never}
      />
    </QueryClientProvider>,
  );
}

describe("ScenarioQuadrantView", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows score controls immediately by auto-selecting the first active scenario", () => {
    const s1 = buildScenario("s1", "场景 1", 5, 1);
    const s2 = buildScenario("s2", "场景 2", 4, 1);
    const s3 = buildScenario("s3", "场景 3", 4, 2);

    renderView({
      scoring_method: "four_quadrant_v1",
      evaluated_count: 3,
      top_scenarios: [s1, s2, s3],
      all_scores: [s1, s2, s3],
      active_count: 3,
      excluded_scores: [],
      created_at: null,
      updated_at: null,
    });

    expect(screen.getByText("当前场景：场景 1")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "结构化程度 X 减少" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "实施复杂度 Y 增加" }),
    ).toBeInTheDocument();
  });

  it("renders the revised two-step scene pool and Top3 copy without removed summary controls", () => {
    const s1 = {
      ...buildScenario("s1", "回款风险预警", 5, 1),
      value_text: "优先稳住现金回收质量",
      benefits: [{ text: "预计可降低逾期跟进遗漏", canvas: "收入来源 R$" }],
      resources: [{ type: "data", label: "数据基础", text: "回款记录" }],
    };
    const s2 = buildScenario("s2", "销售线索优先级排序", 4, 1);
    const s3 = buildScenario("s3", "门店销量预测", 4, 2);

    renderView({
      scoring_method: "four_quadrant_v1",
      evaluated_count: 3,
      top_scenarios: [s1, s2, s3],
      all_scores: [s1, s2, s3],
      active_count: 3,
      excluded_scores: [],
      created_at: null,
      updated_at: null,
    });

    expect(screen.getByText("步骤1/2：场景池校准")).toBeInTheDocument();
    expect(
      screen.getByText(/系统根据所选创新方向评估 3 个候选场景/),
    ).toBeInTheDocument();
    expect(screen.getByText("步骤2/2：Top3 AI 应用场景推荐")).toBeInTheDocument();
    expect(
      screen.getByText(/基于您所选的创新方向与场景池校准结果，筛选出以下 3 个最具战略价值与落地可行性的场景/),
    ).toBeInTheDocument();

    expect(screen.queryByText("评估场景总数")).not.toBeInTheDocument();
    expect(screen.queryByText("覆盖画布要素")).not.toBeInTheDocument();
    expect(screen.queryByText("推荐逻辑")).not.toBeInTheDocument();
    expect(screen.queryByText("分析依据")).not.toBeInTheDocument();

    fireEvent.click(screen.getByText("场景一 · 回款风险预警"));

    expect(screen.queryByText(/该场景推荐依据/)).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /调整此场景/ })).not.toBeInTheDocument();
  });

  it("uses distinct 15-character scenario descriptions instead of generic positioning text", () => {
    const commonPrefix = "围绕“智能运营”，结合“客户关系”，在";
    const s1 = {
      ...buildScenario("s1", "回款风险预警", 5, 1),
      positioning: "围绕“智能运营”，结合“客户关系”",
      summary: `${commonPrefix}财务经营环节布局“回款风险预警”，提前识别回款异常。`,
    };
    const s2 = {
      ...buildScenario("s2", "销售线索优先级排序", 4, 1),
      positioning: "在销售增长环节，针对客户细分",
      summary: `${commonPrefix}销售增长环节布局“销售线索优先级排序”，识别高价值销售线索。`,
    };
    const s3 = {
      ...buildScenario("s3", "门店销量预测", 4, 2),
      positioning: "在零售运营环节，围绕客户细分",
      summary: `${commonPrefix}零售运营环节布局“门店销量预测”，辅助门店补货计划。`,
    };

    renderView({
      scoring_method: "four_quadrant_v1",
      evaluated_count: 3,
      top_scenarios: [s1, s2, s3],
      all_scores: [s1, s2, s3],
      active_count: 3,
      excluded_scores: [],
      created_at: null,
      updated_at: null,
    });

    expect(screen.getByText("提前识别回款异常")).toBeInTheDocument();
    expect(screen.getByText("识别高价值销售线索")).toBeInTheDocument();
    expect(screen.getByText("辅助门店补货计划")).toBeInTheDocument();
    expect(screen.queryByText(/围绕“智能运营”/)).not.toBeInTheDocument();
  });

  it("removes a scenario from the active pool optimistically before the server returns", async () => {
    const s1 = buildScenario("s1", "场景 1", 5, 1);
    const s2 = buildScenario("s2", "场景 2", 4, 1);
    const s3 = buildScenario("s3", "场景 3", 4, 2);
    const s4 = buildScenario("s4", "场景 4", 3, 2);
    const s5 = buildScenario("s5", "场景 5", 2, 3);

    let resolvePoolUpdate: (value: unknown) => void = () => {};
    updateScenarioPoolMock.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolvePoolUpdate = resolve as (value: unknown) => void;
        }),
    );

    renderView({
      scoring_method: "four_quadrant_v1",
      evaluated_count: 5,
      top_scenarios: [s1, s2, s3],
      all_scores: [s1, s2, s3, s4],
      active_count: 4,
      excluded_scores: [s5],
      created_at: null,
      updated_at: null,
    });

    fireEvent.click(screen.getAllByRole("button", { name: "移出" })[3]);

    expect(await screen.findByText("有效 3 / 总 5")).toBeInTheDocument();

    resolvePoolUpdate({
      assessment: { id: "assessment-1" },
      scenario_recommendation: {
        scoring_method: "four_quadrant_v1",
        evaluated_count: 5,
        top_scenarios: [s1, s2, s3],
        all_scores: [s1, s2, s3],
        active_count: 3,
        excluded_scores: [s4, s5],
        created_at: null,
        updated_at: null,
      },
    });

    await waitFor(() => {
      expect(updateScenarioPoolMock).toHaveBeenCalledWith("assessment-1", {
        active_scenario_ids: ["s1", "s2", "s3"],
      });
    });
  });

  it("adds an excluded scenario back into the active pool", async () => {
    const s1 = buildScenario("s1", "场景 1", 5, 1);
    const s2 = buildScenario("s2", "场景 2", 4, 1);
    const s3 = buildScenario("s3", "场景 3", 4, 2);
    const s4 = buildScenario("s4", "场景 4", 3, 2);
    const s5 = buildScenario("s5", "场景 5", 2, 3);

    updateScenarioPoolMock.mockResolvedValueOnce({
      assessment: { id: "assessment-1" },
      scenario_recommendation: {
        scoring_method: "four_quadrant_v1",
        evaluated_count: 5,
        top_scenarios: [s1, s2, s3],
        all_scores: [s1, s2, s3, s4],
        active_count: 4,
        excluded_scores: [s5],
        created_at: null,
        updated_at: null,
      },
    });

    renderView({
      scoring_method: "four_quadrant_v1",
      evaluated_count: 5,
      top_scenarios: [s1, s2, s3],
      all_scores: [s1, s2, s3],
      active_count: 3,
      excluded_scores: [s4, s5],
      created_at: null,
      updated_at: null,
    });

    fireEvent.click(screen.getAllByRole("button", { name: "加回" })[0]);

    await waitFor(() => {
      expect(updateScenarioPoolMock).toHaveBeenCalledWith("assessment-1", {
        active_scenario_ids: ["s1", "s2", "s3", "s4"],
      });
    });

    expect(await screen.findByText("有效 4 / 总 5")).toBeInTheDocument();
    expect(screen.getAllByText("场景 4").length).toBeGreaterThan(0);
  });
});
