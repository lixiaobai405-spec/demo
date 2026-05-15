import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AssessmentFormSection } from "@/components/assessment-form-section";
import { initialForm } from "@/lib/assessment-utils";
import type { AssessmentCreateRequest, IntakeFieldMeta } from "@/lib/types";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

vi.mock("@/hooks", () => ({
  useCreateAssessment: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

vi.mock("@/hooks/use-toast", () => ({
  toast: vi.fn(),
}));

/**
 * 渲染正式问卷表单，验证导入缺失字段提示样式。
 */
function renderForm(
  prefillFieldMeta?: Partial<Record<keyof AssessmentCreateRequest, IntakeFieldMeta>>,
  formOverrides?: Partial<AssessmentCreateRequest>,
) {
  return render(
    <AssessmentFormSection
      form={{
        ...initialForm,
        company_name: "测试连锁零售企业",
        industry: "零售",
        company_size: "100-499人",
        region: "华东",
        annual_revenue_range: "5000万-1亿",
        available_data: "ERP、CRM、客服系统",
        core_products: "门店数字化管理服务",
        target_customers: "连锁零售总部",
        current_challenges: "跨门店数据分散",
        ai_goals: "提升选品和运营效率",
        notes: "已有年度预算规划",
        ...formOverrides,
      }}
      prefillSummary={{ importSessionId: "session-prefill", mappedCount: 3 }}
      prefillFieldMeta={prefillFieldMeta ?? null}
      onFormChange={vi.fn()}
      assessment={null}
      onReset={vi.fn()}
    />,
  );
}

describe("AssessmentFormSection", () => {
  it("highlights imported missing fields in red", () => {
    renderForm(
      {
        current_challenges: { source_type: "missing", status: "needs_user_input" },
        annual_revenue_range: { source_type: "missing", status: "needs_user_input" },
      },
      {
        current_challenges: "",
        annual_revenue_range: "",
      },
    );

    const missingHints = screen.getAllByText("系统未识别，请手动补充");
    expect(missingHints).toHaveLength(2);
    expect(missingHints[0].className).toContain("text-destructive");

    const currentChallenges = screen.getByLabelText(/^当前经营\/管理挑战/);
    expect(currentChallenges.className).toContain("border-destructive");

    const revenueRange = screen.getByLabelText(/^年营收范围/);
    expect(revenueRange.className).toContain("border-destructive");
  });

  it("highlights empty required selects and keeps optional notes neutral", () => {
    renderForm(
      {
        company_size: { source_type: "raw", status: "confirmed" },
        notes: { source_type: "missing", status: "needs_user_input" },
      },
      {
        company_size: "",
        notes: "",
      },
    );

    const companySize = screen.getByLabelText(/^企业规模/);
    expect(companySize.className).toContain("border-destructive");

    const hints = screen.getAllByText("系统未识别，请手动补充");
    expect(hints).toHaveLength(2);
    expect(hints[0].className).toContain("text-destructive");
    expect(hints[1].className).not.toContain("text-destructive");

    const notes = screen.getByLabelText(/^补充说明/);
    expect(notes.className).toBe("input-field");
  });
});
