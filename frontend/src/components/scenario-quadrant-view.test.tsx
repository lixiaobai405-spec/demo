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

  it("removes a scenario from the active pool optimistically before the server returns", async () => {
    const s1 = buildScenario("s1", "场景 1", 5, 1);
    const s2 = buildScenario("s2", "场景 2", 4, 1);
    const s3 = buildScenario("s3", "场景 3", 4, 2);
    const s4 = buildScenario("s4", "场景 4", 3, 2);
    const s5 = buildScenario("s5", "场景 5", 2, 3);

    let resolvePoolUpdate: ((value: unknown) => void) | null = null;
    updateScenarioPoolMock.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolvePoolUpdate = resolve;
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

    resolvePoolUpdate?.({
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
