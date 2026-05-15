import React from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { IntakeConfirmationForm } from "@/components/intake-confirmation-form";
import { IntakePrefillDisplay } from "@/components/intake-prefill-display";

const pushMock = vi.fn();
const useIntakeSessionMock = vi.fn();
const useCreateAssessmentFromIntakeMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}));

vi.mock("@/stores/intake-store", () => ({
  useIntakeStore: () => ({
    importSessionId: "session-step-2",
  }),
}));

vi.mock("@/hooks", () => ({
  useIntakeSession: (...args: unknown[]) => useIntakeSessionMock(...args),
  useCreateAssessmentFromIntake: (...args: unknown[]) =>
    useCreateAssessmentFromIntakeMock(...args),
}));

/**
 * 构造导入步骤改造测试所需的最小会话数据。
 */
function buildSessionDetail() {
  return {
    import_session_id: "session-step-2",
    status: "parsed",
    source_type: "markdown",
    source_file: null,
    assessment_prefill: {
      company_name: "测试零售企业",
      industry: "零售",
      company_size: "100-499人",
      region: "华东",
      annual_revenue_range: "",
      core_products: "社区零售门店",
      target_customers: "社区家庭用户",
      current_challenges: "",
      ai_goals: "提升复购和运营效率",
      available_data: "POS、会员系统",
      notes: "",
    },
    field_meta: {
      company_name: { source_type: "raw", status: "confirmed" },
      industry: { source_type: "raw", status: "confirmed" },
      company_size: { source_type: "raw", status: "confirmed" },
      region: { source_type: "raw", status: "confirmed" },
      annual_revenue_range: { source_type: "missing", status: "needs_user_input" },
      core_products: { source_type: "raw", status: "confirmed" },
      target_customers: { source_type: "raw", status: "confirmed" },
      current_challenges: { source_type: "missing", status: "needs_user_input" },
      ai_goals: { source_type: "raw", status: "confirmed" },
      available_data: { source_type: "raw", status: "confirmed" },
      notes: { source_type: "missing", status: "needs_user_input" },
    },
    field_candidates: {},
    unmapped_notes: ["原步骤二备注不应再展示"],
    warnings: ["年营收范围未识别，请用户补充。"],
    raw_content: "企业名称：测试零售企业",
    structured_fields: {},
    created_assessment_id: null,
    created_at: "2026-05-15T00:00:00",
    updated_at: "2026-05-15T00:00:00",
  };
}

describe("intake step restructure", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useIntakeSessionMock.mockReturnValue({
      data: buildSessionDetail(),
      isLoading: false,
      isError: false,
      error: null,
    });
    useCreateAssessmentFromIntakeMock.mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    });
  });

  it("hides the old prefill preview step entirely", () => {
    const { container } = render(<IntakePrefillDisplay />);

    expect(container.firstChild).toBeNull();
    expect(screen.queryByText("问卷预填建议")).not.toBeInTheDocument();
    expect(screen.queryByText("提示信息")).not.toBeInTheDocument();
  });

  it("renames the confirmation form to step two and highlights missing fields in red", () => {
    render(<IntakeConfirmationForm />);

    expect(screen.getByText("步骤二")).toBeInTheDocument();
    expect(screen.queryByText("步骤三")).not.toBeInTheDocument();
    expect(screen.queryByText("问卷预填建议")).not.toBeInTheDocument();

    const missingNote = screen.getAllByText("系统未识别，请手动补充")[0];
    expect(missingNote.className).toContain("text-destructive");

    const revenueInput = screen.getByLabelText(/^年营收范围/);
    expect(revenueInput.className).toContain("border-destructive");
  });
});
