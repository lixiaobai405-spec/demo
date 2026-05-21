import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { Mock } from "vitest";
import { beforeEach, describe, expect, it, vi } from "vitest";

const useAssessmentDetailMock = vi.fn();

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
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/hooks/use-toast", () => ({
  toast: vi.fn(),
}));

vi.mock("@/hooks", () => ({
  useAssessmentDetail: (...args: unknown[]) => useAssessmentDetailMock(...args),
  useUpdateEndgame: () => ({ mutateAsync: vi.fn(), isPending: false }),
}));

vi.mock("@/components/endgame-panel", () => ({
  EndgamePanel: () => <div>Endgame panel ready</div>,
}));

vi.mock("@/components/sync-feedback-panel", () => ({
  SyncFeedbackPanel: () => null,
}));

import EndgamePage from "@/app/assessment/[assessmentId]/endgame/page";

function renderWithQueryClient(node: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>{node}</QueryClientProvider>,
  );
}

describe("EndgamePage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows a manual edit button and opens the editor for endgame content", () => {
    (useAssessmentDetailMock as Mock).mockReturnValue({
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
      data: {
        assessment: {
          id: "assessment-1",
          company_name: "Test Company",
          industry: "Retail",
        },
        company_profile: null,
        canvas_diagnosis: null,
        breakthrough_selection: null,
        direction_expansion: null,
        direction_selection: null,
        scenario_recommendation: null,
        competitiveness: null,
        endgame: {
          assessment_id: "assessment-1",
          result: {
            generation_mode: "rule_based",
            industry_essence: "Industry essence",
            private_domain: {
              current_state: "Current state",
              target_model: "Target model",
              key_strategies: ["Strategy A"],
              customer_retention_loop: "Loop",
              revenue_impact: "Impact",
            },
            ecosystem: {
              ecosystem_positioning: "Positioning",
              key_partners_to_engage: ["Partner A"],
              orchestration_strategy: "Strategy",
              platform_effect: "Effect",
            },
            opc: {
              operations_excellence: "Ops",
              platform_capability: "Platform",
              content_and_community: "Community",
              data_flywheel_effect: "Flywheel",
            },
            three_stage_strategy: {
              stage_1: {
                title: "Stage 1",
                focus: "Focus 1",
                strategy: "Strategy 1",
                objective: "Objective 1",
                key_actions: [],
                key_risks: [],
              },
              stage_2: {
                title: "Stage 2",
                focus: "Focus 2",
                strategy: "Strategy 2",
                objective: "Objective 2",
                key_actions: [],
                key_risks: [],
              },
              stage_3: {
                title: "Stage 3",
                focus: "Focus 3",
                strategy: "Strategy 3",
                objective: "Objective 3",
                key_actions: [],
                key_risks: [],
              },
              key_risks: [],
            },
            strategic_paths: [],
            overall_narrative: "Overall narrative",
          },
          created_at: null,
          updated_at: null,
        },
        case_recommendation: null,
        generated_report: null,
        progress: {
          has_profile: true,
          has_canvas: true,
          has_breakthrough: true,
          has_directions: true,
          has_competitiveness: true,
          has_endgame: true,
          has_scenarios: true,
          has_report: false,
          ready_for_report: false,
        },
      },
    });

    renderWithQueryClient(
      <EndgamePage
        params={{ assessmentId: "assessment-1" } as unknown as Promise<{
          assessmentId: string;
        }>}
      />,
    );

    expect(screen.getByText("Endgame panel ready")).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("button", { name: /手动编辑终局报告/ }),
    );

    expect(screen.getByRole("textbox")).toBeInTheDocument();
  });
});
