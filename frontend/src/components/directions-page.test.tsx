import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";

const useAssessmentDetailMock = vi.fn();
const useGenerateScenariosMock = vi.fn();
const getDirectionsMock = vi.fn();
const selectDirectionsMock = vi.fn();
const toastMock = vi.fn();
const routerPushMock = vi.fn();

vi.mock("react", async () => {
  const actual = await vi.importActual<typeof import("react")>("react");
  return {
    ...actual,
    use: <T,>(value: T) => value,
  };
});

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: routerPushMock }),
}));

vi.mock("@/hooks", () => ({
  useAssessmentDetail: (...args: unknown[]) => useAssessmentDetailMock(...args),
  useGenerateScenarios: (...args: unknown[]) => useGenerateScenariosMock(...args),
}));

vi.mock("@/hooks/use-toast", () => ({
  toast: (...args: unknown[]) => toastMock(...args),
}));

vi.mock("@/components/sync-feedback-panel", () => ({
  SyncFeedbackPanel: () => null,
}));

vi.mock("@/components/direction-expansion-panel", () => ({
  DirectionExpansionPanel: ({
    onConfirmSelection,
  }: {
    onConfirmSelection: () => void;
  }) => (
    <button type="button" onClick={onConfirmSelection}>
      Confirm directions
    </button>
  ),
}));

const storeState = {
  assessment: null,
  selectedDirectionIds: ["direction-1"],
  toggleDirectionId: vi.fn(),
  setAssessment: vi.fn(),
  setCompanyProfile: vi.fn(),
  setProfileMode: vi.fn(),
  setCanvasDiagnosis: vi.fn(),
  setBreakthroughSelection: vi.fn(),
  setSelectedBreakthroughKeys: vi.fn(),
  setScenarioRecommendation: vi.fn(),
  setDirectionData: vi.fn(),
  setDirectionSelection: vi.fn(),
  setSelectedDirectionIds: vi.fn(),
  setCompetitivenessData: vi.fn(),
  setEndgameData: vi.fn(),
};

vi.mock("@/stores/assessment-store", () => ({
  useAssessmentStore: () => storeState,
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    getDirections: (...args: unknown[]) => getDirectionsMock(...args),
    selectDirections: (...args: unknown[]) => selectDirectionsMock(...args),
  };
});

import DirectionsPage from "@/app/assessment/[assessmentId]/directions/page";

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <DirectionsPage
        params={{ assessmentId: "assessment-1" } as unknown as Promise<{
          assessmentId: string;
        }>}
      />
    </QueryClientProvider>,
  );
}

describe("DirectionsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    useGenerateScenariosMock.mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    });

    useAssessmentDetailMock.mockReturnValue({
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
      data: {
        assessment: {
          id: "assessment-1",
          company_name: "测试企业",
          industry: "零售",
          profile_generation_mode: null,
        },
        company_profile: null,
        canvas_diagnosis: {
          overall_summary: "ok",
          weakest_blocks: [],
          strongest_blocks: [],
          overall_score: 80,
          blocks: [],
        },
        breakthrough_selection: ["revenue_streams", "key_resources"],
        direction_expansion: null,
        direction_selection: null,
        scenario_recommendation: null,
        competitiveness: null,
        endgame: null,
        case_recommendation: null,
        generated_report: null,
        progress: {
          has_profile: true,
          has_canvas: true,
          has_breakthrough: true,
          has_directions: false,
          has_competitiveness: false,
          has_endgame: false,
          has_scenarios: false,
          has_report: false,
          ready_for_report: false,
        },
      },
    });

    getDirectionsMock.mockResolvedValue({
      assessment_id: "assessment-1",
      direction_expansion: {
        generation_mode: "llm",
        llm_status: "completed",
        total_suggestions: 1,
        elements: [
          {
            element_key: "revenue_streams",
            element_title: "价值主张",
            suggestions: [
              {
                direction_id: "direction-1",
                element_key: "revenue_streams",
                title: "方向 1",
                description: "描述",
                expected_impact: "影响",
                data_needed: ["数据"],
                related_scenario_categories: ["零售"],
              },
            ],
          },
        ],
      },
      direction_selection: null,
    });

    selectDirectionsMock.mockResolvedValue({
      assessment_id: "assessment-1",
      generation_mode: "rule_based",
      created_at: null,
      updated_at: null,
      selected_directions: [
        {
          direction_id: "direction-1",
          element_key: "revenue_streams",
          title: "方向 1",
          description: "描述",
          expected_impact: "影响",
          data_needed: ["数据"],
          related_scenario_categories: ["零售"],
        },
      ],
    });
  });

  it("confirms directions from the page flow even before the workspace store is hydrated", async () => {
    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: "Confirm directions" }));

    await waitFor(() => {
      expect(selectDirectionsMock).toHaveBeenCalledWith("assessment-1", {
        selected_direction_ids: ["direction-1"],
      });
    });
    expect(storeState.setAssessment).toHaveBeenCalledWith(
      expect.objectContaining({ id: "assessment-1" }),
    );
  });
});
