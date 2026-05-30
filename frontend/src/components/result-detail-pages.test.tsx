import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { Mock } from "vitest";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ScenariosPageContent } from "@/components/scenarios-page-content";
import { CompetitivenessPageContent } from "@/components/competitiveness-page-content";

const useAssessmentDetailMock = vi.fn();
const useCompetitivenessMock = vi.fn();
const updateCompetitivenessMock = vi.fn();

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

vi.mock("@/hooks/use-endgame", () => ({
  useGenerateEndgame: () => ({ mutateAsync: vi.fn(), isPending: false }),
}));

vi.mock("@/hooks/use-competitiveness", () => ({
  useCompetitiveness: (...args: unknown[]) => useCompetitivenessMock(...args),
  useGenerateCompetitiveness: () => ({ mutateAsync: vi.fn(), isPending: false }),
}));

vi.mock("@/hooks", () => ({
  useAssessmentDetail: (...args: unknown[]) => useAssessmentDetailMock(...args),
  useCompetitiveness: (...args: unknown[]) => useCompetitivenessMock(...args),
  useGenerateCompetitiveness: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useGenerateEndgame: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useUpdateCompetitiveness: () => ({ mutateAsync: updateCompetitivenessMock, isPending: false }),
  useUpdateEndgame: () => ({ mutateAsync: vi.fn(), isPending: false }),
}));

function buildCompetitiveness() {
  return {
    assessment_id: "assessment-1",
    result: {
      generation_mode: "rule_based",
      vp_reconstruction: {
        current_vp: "Current value proposition",
        enhanced_vp: "Enhanced AI-led proposition",
        differentiation_points: ["Customer operations depth"],
        customer_value_shift: "Shift from efficiency to sustained growth",
      },
      connections: [
        {
          line_name: "Customer growth line",
          point_ids: ["direction-1"],
          point_titles: ["Customer lifecycle operations"],
          strategic_narrative: "Connect customer touchpoints into a repeatable system.",
          competitive_impact: "Increase retention and repurchase rate.",
          key_metrics: ["Retention"],
          linkage_logic: "Use AI to connect customer data and response flows.",
          competitive_moat: "Data-driven operating moat",
        },
      ],
      advantages: [
        {
          advantage_name: "Customer operations moat",
          source_elements: ["customer_relationships"],
          description: "Forms a stronger closed-loop operating system.",
          barrier_level: "高",
        },
      ],
      delivery_strategy: {
        phase_1_quick_win: "Pilot one scenario first",
        phase_2_scale: "Scale after validation",
        phase_3_moat: "沉淀为长期能力",
        key_risks: ["Cross-team coordination"],
      },
      overall_narrative: "Competitive direction is clear.",
    },
    created_at: null,
    updated_at: null,
  };
}

function buildDetail() {
  return {
    assessment: {
      id: "assessment-1",
      company_name: "Test Company",
      industry: "Retail",
      company_size: "100-499",
      region: "East China",
      annual_revenue_range: "50M-100M",
      core_products: "Membership services",
      target_customers: "Members",
      current_challenges: "Repurchase fluctuation",
      ai_goals: "Improve operating efficiency",
      available_data: "POS and member systems",
      notes: null,
      created_at: null,
      updated_at: null,
      profile_generated_at: null,
      profile_generation_mode: null,
    },
    company_profile: null,
    canvas_diagnosis: null,
    breakthrough_selection: null,
    direction_expansion: null,
    direction_selection: null,
    scenario_recommendation: {
      scoring_method: "rule_based_v1",
      evaluated_count: 3,
      top_scenarios: [
        {
          scenario_id: "scenario-1",
          name: "Store knowledge copilot",
          category: "Operations",
          summary: "Help frontline staff answer store questions quickly.",
          canvas_elements: "Key activities",
          expected_effects: "Reduce training cost",
          core_data_requirements: "POS data",
        },
      ],
      created_at: null,
      updated_at: null,
    },
    competitiveness: buildCompetitiveness(),
    endgame: null,
    case_recommendation: null,
    generated_report: null,
    progress: {
      has_profile: true,
      has_canvas: true,
      has_breakthrough: true,
      has_directions: true,
      has_competitiveness: true,
      has_endgame: false,
      has_scenarios: true,
      has_report: false,
      ready_for_report: false,
    },
  };
}

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

describe("result detail page content", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the scenarios page with client-fetched detail data", () => {
    (useAssessmentDetailMock as Mock).mockReturnValue({
      isLoading: false,
      isError: false,
      data: buildDetail(),
      error: null,
      refetch: vi.fn(),
    });

    renderWithQueryClient(
      <ScenariosPageContent assessmentId="assessment-1" />,
    );

    expect(
      screen.getByRole("heading", { name: "Test Company AI 推荐场景" }),
    ).toBeInTheDocument();
    expect(screen.getAllByText("Store knowledge copilot").length).toBeGreaterThanOrEqual(1);
  });

  it("renders the competitiveness page and allows opening manual edit mode", async () => {
    const refetchMock = vi.fn();
    (useAssessmentDetailMock as Mock).mockReturnValue({
      isLoading: false,
      isError: false,
      data: buildDetail(),
      error: null,
      refetch: refetchMock,
    });
    updateCompetitivenessMock.mockResolvedValue(buildCompetitiveness());

    renderWithQueryClient(
      <CompetitivenessPageContent assessmentId="assessment-1" />,
    );

    expect(
      screen.getByRole("heading", { name: "Test Company 差异化竞争力分析" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Competitive direction is clear.")).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("button", { name: /手动编辑竞争力报告/ }),
    );

    expect(screen.getByLabelText("当前 VP")).toBeInTheDocument();
    expect(screen.getByLabelText("强化 VP")).toBeInTheDocument();
    expect(screen.getByLabelText("差异化定位")).toBeInTheDocument();
    expect(screen.queryByText(/vp_reconstruction/)).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("当前 VP"), {
      target: { value: "Updated current VP" },
    });
    fireEvent.click(screen.getByRole("button", { name: "保存修改并清除下游" }));

    await waitFor(() => {
      expect(updateCompetitivenessMock).toHaveBeenCalledWith({
        assessmentId: "assessment-1",
        payload: expect.objectContaining({
          vp_reconstruction: expect.objectContaining({
            current_vp: "Updated current VP",
          }),
        }),
      });
    });
  });
});
