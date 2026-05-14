import { describe, expect, it } from "vitest";

import { buildAssessmentWorkflowState } from "@/lib/assessment-workflow-state";
import { initialProgress } from "@/lib/assessment-utils";

/**
 * 构造工作流状态测试所需的基础入参。
 */
function buildInput() {
  return {
    assessmentId: "assessment-1",
    hasAssessment: true,
    hasProfile: false,
    hasCanvas: false,
    hasBreakthroughSelection: false,
    hasDirectionDraft: false,
    hasDirectionSelection: false,
    hasScenarios: false,
    scenarioCount: 0,
    hasCompetitiveness: false,
    hasEndgame: false,
    progress: initialProgress,
    profileMode: null as "mock" | "live" | null,
  };
}

describe("buildAssessmentWorkflowState", () => {
  it("keeps breakthrough aligned with the chain and uses pending confirmation wording", () => {
    const state = buildAssessmentWorkflowState({
      ...buildInput(),
      hasProfile: true,
      hasCanvas: true,
      progress: {
        ...initialProgress,
        has_profile: true,
        has_canvas: true,
      },
    });

    const breakthroughAction = state.actionModules.find(
      (module) => module.key === "breakthrough",
    );
    const breakthroughCard = state.resultCards.find(
      (card) => card.key === "breakthrough",
    );

    expect(breakthroughAction?.disabled).toBe(false);
    expect(breakthroughAction?.state).toBe("available");
    expect(breakthroughCard?.state).toBe("available");
    expect(breakthroughCard?.statusLabel).toBe("待确认");
  });

  it("shows directions as pending review when draft data exists but confirmation is unfinished", () => {
    const state = buildAssessmentWorkflowState({
      ...buildInput(),
      hasProfile: true,
      hasCanvas: true,
      hasBreakthroughSelection: true,
      hasDirectionDraft: true,
      progress: {
        ...initialProgress,
        has_profile: true,
        has_canvas: true,
        has_breakthrough: true,
      },
    });

    const directionsCard = state.resultCards.find(
      (card) => card.key === "directions",
    );

    expect(directionsCard?.state).toBe("pending-review");
    expect(directionsCard?.statusLabel).toBe("待确认");
  });

  it("keeps downstream modules locked when upstream completion is missing", () => {
    const state = buildAssessmentWorkflowState({
      ...buildInput(),
      hasProfile: true,
      hasCanvas: true,
      hasScenarios: true,
      hasCompetitiveness: true,
      scenarioCount: 3,
      progress: {
        ...initialProgress,
        has_profile: true,
        has_canvas: true,
        has_scenarios: true,
        has_competitiveness: true,
      },
    });

    const breakthroughCard = state.resultCards.find(
      (card) => card.key === "breakthrough",
    );
    const scenariosCard = state.resultCards.find(
      (card) => card.key === "scenarios",
    );
    const competitivenessCard = state.resultCards.find(
      (card) => card.key === "competitiveness",
    );

    expect(breakthroughCard?.statusLabel).toBe("待确认");
    expect(scenariosCard?.state).toBe("locked");
    expect(scenariosCard?.statusLabel).toBe("待生成");
    expect(competitivenessCard?.state).toBe("locked");
    expect(competitivenessCard?.statusLabel).toBe("待生成");
  });

  it("uses confirmed wording for completed breakthrough instead of locked wording", () => {
    const state = buildAssessmentWorkflowState({
      ...buildInput(),
      hasProfile: true,
      hasCanvas: true,
      hasBreakthroughSelection: true,
      progress: {
        ...initialProgress,
        has_profile: true,
        has_canvas: true,
        has_breakthrough: true,
      },
    });

    const breakthroughCard = state.resultCards.find(
      (card) => card.key === "breakthrough",
    );

    expect(breakthroughCard?.state).toBe("done");
    expect(breakthroughCard?.statusLabel).toBe("已确认");
  });
});
