import React from "react";
import { render, screen } from "@testing-library/react";
import type { Mock } from "vitest";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ScenariosPageContent } from "@/components/scenarios-page-content";
import { CompetitivenessPageContent } from "@/components/competitiveness-page-content";

const useAssessmentDetailMock = vi.fn();
const useCompetitivenessMock = vi.fn();

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
}));

/**
 * 构造结果页测试所需的最小评估详情数据。
 */
function buildDetail() {
  return {
    assessment: {
      id: "assessment-1",
      company_name: "测试企业",
      industry: "零售",
      company_size: "100-499人",
      region: "华东",
      annual_revenue_range: "5000万-1亿元",
      core_products: "会员服务",
      target_customers: "会员用户",
      current_challenges: "复购波动",
      ai_goals: "提升运营效率",
      available_data: "POS、会员系统",
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
          name: "门店知识助手",
          category: "运营提效",
          summary: "帮助门店快速调用标准知识。",
          score: 92,
          reasons: ["降低培训成本"],
          data_requirements: ["POS 数据"],
        },
      ],
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
      has_scenarios: true,
      has_report: false,
      ready_for_report: true,
    },
  };
}

/**
 * 构造竞争力分析页测试所需的最小数据。
 */
function buildCompetitiveness() {
  return {
    assessment_id: "assessment-1",
    result: {
      generation_mode: "rule_based",
      vp_reconstruction: {
        current_vp: "帮助门店提升经营效率",
        enhanced_vp: "通过客户经营和知识复用形成差异化竞争力",
        differentiation_points: ["客户经营深化"],
        customer_value_shift: "从单点提效升级为持续经营。",
      },
      connections: [
        {
          line_name: "客户关系深化线",
          point_ids: ["direction-1"],
          point_titles: ["客户分层经营"],
          strategic_narrative: "围绕客户关系深化形成系统性能力。",
          competitive_impact: "提高复购与留存",
          key_metrics: ["复购率"],
        },
      ],
      advantages: [
        {
          advantage_name: "客户经营优势",
          source_elements: ["客户关系"],
          description: "形成更强的客户经营闭环。",
          barrier_level: "高",
        },
      ],
      delivery_strategy: {
        phase_1_quick_win: "先试点",
        phase_2_scale: "再扩展",
        phase_3_moat: "最后沉淀壁垒",
        key_risks: ["跨团队协同不足"],
      },
      overall_narrative: "竞争力方向清晰。",
    },
    created_at: null,
    updated_at: null,
  };
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

    render(<ScenariosPageContent assessmentId="assessment-1" />);

    expect(screen.getByText("测试企业 AI 场景推荐")).toBeInTheDocument();
    expect(screen.getAllByText("门店知识助手").length).toBeGreaterThanOrEqual(1);
  });

  it("renders the competitiveness page with client-fetched queries", () => {
    (useAssessmentDetailMock as Mock).mockReturnValue({
      isLoading: false,
      isError: false,
      data: buildDetail(),
      error: null,
      refetch: vi.fn(),
    });
    (useCompetitivenessMock as Mock).mockReturnValue({
      isLoading: false,
      isError: false,
      data: buildCompetitiveness(),
      error: null,
      refetch: vi.fn(),
    });

    render(<CompetitivenessPageContent assessmentId="assessment-1" />);

    expect(screen.getByText("测试企业 差异化竞争力分析")).toBeInTheDocument();
    expect(screen.getByText("竞争力方向清晰。")).toBeInTheDocument();
  });
});
