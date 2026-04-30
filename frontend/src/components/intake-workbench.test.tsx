import React from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { Mock } from "vitest";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { IntakeWorkbench } from "@/components/intake-workbench";
import {
  createAssessmentFromIntake,
  getIntakeImportSession,
  importAssessmentIntake,
  importAssessmentIntakeFile,
} from "@/lib/api";
import type { IntakeSessionDetailResponse } from "@/lib/types";

const pushMock = vi.fn();

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
  useRouter: () => ({
    push: pushMock,
  }),
}));

vi.mock("@/lib/api", () => ({
  importAssessmentIntake: vi.fn(),
  importAssessmentIntakeFile: vi.fn(),
  getIntakeImportSession: vi.fn(),
  createAssessmentFromIntake: vi.fn(),
}));

function buildSessionDetail(
  overrides: Partial<IntakeSessionDetailResponse> = {},
): IntakeSessionDetailResponse {
  return {
    import_session_id: "session-1",
    status: "parsed",
    source_type: "markdown",
    source_file: null,
    assessment_prefill: {
      company_name: "测试零售企业",
      industry: "零售",
      company_size: "100-499人",
      region: "华东",
      annual_revenue_range: "3000万-1亿",
      core_products: "社区零售门店",
      target_customers: "社区家庭用户",
      current_challenges: "门店运营效率不足",
      ai_goals: "提升复购和运营效率",
      available_data: "POS、会员系统",
      notes: null,
    },
    field_meta: {
      company_name: { source_type: "raw", status: "confirmed" },
      industry: { source_type: "raw", status: "confirmed" },
      company_size: { source_type: "raw", status: "confirmed" },
      region: { source_type: "raw", status: "confirmed" },
      annual_revenue_range: { source_type: "inferred", status: "needs_user_confirmation" },
      core_products: { source_type: "raw", status: "confirmed" },
      target_customers: { source_type: "raw", status: "confirmed" },
      current_challenges: { source_type: "inferred", status: "needs_user_confirmation" },
      ai_goals: { source_type: "raw", status: "confirmed" },
      available_data: { source_type: "raw", status: "confirmed" },
      notes: { source_type: "missing", status: "needs_user_input" },
    },
    field_candidates: {
      company_name: {
        value: "测试零售企业",
        source: "原文",
        confidence: "high",
        evidence: "企业名称：测试零售企业",
      },
    },
    unmapped_notes: [],
    warnings: [],
    raw_content: "企业名称：测试零售企业",
    structured_fields: {},
    created_assessment_id: null,
    created_at: "2026-04-29T00:00:00",
    updated_at: "2026-04-29T00:00:00",
    ...overrides,
  };
}

describe("IntakeWorkbench", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it("支持通过后端文件上传接口导入 md 文件", async () => {
    (importAssessmentIntakeFile as Mock).mockResolvedValue({
      import_session_id: "session-file-1",
    });
    (getIntakeImportSession as Mock).mockResolvedValue(
      buildSessionDetail({
        import_session_id: "session-file-1",
        source_type: "file",
        source_file: {
          name: "brief.md",
          kind: "markdown",
          size_bytes: 12,
        },
      }),
    );

    const { container } = render(<IntakeWorkbench />);
    const user = userEvent.setup();

    await user.selectOptions(screen.getByLabelText("输入类型"), "file");
    const fileInput = container.querySelector('input[type="file"]');
    expect(fileInput).not.toBeNull();

    const file = new File(["# 企业简介"], "brief.md", {
      type: "text/markdown",
    });
    fireEvent.change(fileInput as HTMLInputElement, {
      target: {
        files: [file],
      },
    });

    expect(screen.getByText("待上传文件：brief.md")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "导入并生成预填建议" }));

    await waitFor(() => {
      expect(importAssessmentIntakeFile).toHaveBeenCalledWith(file);
    });
    expect(screen.getByText(/源文件：brief\.md/)).toBeInTheDocument();
    expect(screen.getByText("来源类型：文件上传")).toBeInTheDocument();
  });

  it("会在前端拦截超大文件并显示明确错误", async () => {
    const { container } = render(<IntakeWorkbench />);
    const user = userEvent.setup();

    await user.selectOptions(screen.getByLabelText("输入类型"), "file");
    const fileInput = container.querySelector('input[type="file"]');
    expect(fileInput).not.toBeNull();

    const file = new File(["oversized"], "oversized.pdf", {
      type: "application/pdf",
    });
    Object.defineProperty(file, "size", {
      value: 10 * 1024 * 1024 + 1,
    });

    fireEvent.change(fileInput as HTMLInputElement, {
      target: {
        files: [file],
      },
    });

    expect(
      screen.getByText(/文件过大，当前文件为 10\.0 MB，请控制在 10\.0 MB 以内。/),
    ).toBeInTheDocument();
    expect(importAssessmentIntakeFile).not.toHaveBeenCalled();
  });

  it("会根据上传阶段显示进度文案", async () => {
    let resolveImport: ((value: { import_session_id: string }) => void) | undefined;
    (importAssessmentIntakeFile as Mock).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveImport = resolve;
        }),
    );
    (getIntakeImportSession as Mock).mockResolvedValue(
      buildSessionDetail({
        import_session_id: "session-file-progress",
        source_type: "file",
        source_file: {
          name: "scan.pdf",
          kind: "pdf",
          size_bytes: 1024,
        },
      }),
    );

    const { container } = render(<IntakeWorkbench />);
    const user = userEvent.setup();

    await user.selectOptions(screen.getByLabelText("输入类型"), "file");
    const fileInput = container.querySelector('input[type="file"]');
    const file = new File(["fake"], "scan.pdf", {
      type: "application/pdf",
    });

    fireEvent.change(fileInput as HTMLInputElement, {
      target: {
        files: [file],
      },
    });

    expect(screen.getByText("当前状态：文件校验完成，等待上传")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "导入并生成预填建议" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "上传中..." })).toBeInTheDocument();
    });

    resolveImport?.({ import_session_id: "session-file-progress" });

    await waitFor(() => {
      expect(screen.getByText("当前状态：解析完成")).toBeInTheDocument();
    });
  });

  it("结构化表单模式会提交已填写字段", async () => {
    (importAssessmentIntake as Mock).mockResolvedValue({
      import_session_id: "session-form-1",
    });
    (getIntakeImportSession as Mock).mockResolvedValue(
      buildSessionDetail({
        import_session_id: "session-form-1",
        source_type: "form",
        structured_fields: {
          company_name: "结构化录入企业",
          industry: "消费品",
        },
      }),
    );

    const user = userEvent.setup();
    render(<IntakeWorkbench />);

    await user.selectOptions(screen.getByLabelText("输入类型"), "form");
    await user.type(screen.getByLabelText(/^企业名称/), "结构化录入企业");
    await user.type(screen.getByLabelText(/^所属行业/), "消费品");
    await user.click(screen.getByRole("button", { name: "导入并生成预填建议" }));

    await waitFor(() => {
      expect(importAssessmentIntake).toHaveBeenCalledWith({
        source_type: "form",
        raw_content: null,
        structured_fields: {
          company_name: "结构化录入企业",
          industry: "消费品",
        },
      });
    });
  });

  it("在确认表单中显示字段级已修改标记", async () => {
    (importAssessmentIntake as Mock).mockResolvedValue({
      import_session_id: "session-1",
    });
    (getIntakeImportSession as Mock).mockResolvedValue(buildSessionDetail());

    const user = userEvent.setup();
    render(<IntakeWorkbench />);

    await user.click(screen.getByRole("button", { name: "导入并生成预填建议" }));

    await screen.findByRole("button", { name: "确认并创建问卷" });
    expect(screen.getByText("已修改 0 项")).toBeInTheDocument();

    await user.clear(screen.getByLabelText(/企业名称/));
    await user.type(screen.getByLabelText(/企业名称/), "手动修正后的企业名称");

    await waitFor(() => {
      expect(screen.getByText("已修改 1 项")).toBeInTheDocument();
    });
    expect(screen.getAllByText("已修改").length).toBeGreaterThan(0);
  });

  it("确认创建问卷时提交修改后的字段并跳转详情页", async () => {
    (importAssessmentIntake as Mock).mockResolvedValue({
      import_session_id: "session-1",
    });
    (getIntakeImportSession as Mock).mockResolvedValue(buildSessionDetail());
    (createAssessmentFromIntake as Mock).mockResolvedValue({
      import_session_id: "session-1",
      status: "confirmed",
      assessment: {
        id: "assessment-123",
        company_name: "手动修正后的企业名称",
      },
    });

    const user = userEvent.setup();
    render(<IntakeWorkbench />);

    await user.click(screen.getByRole("button", { name: "导入并生成预填建议" }));
    await screen.findByRole("button", { name: "确认并创建问卷" });

    await user.clear(screen.getByLabelText(/企业名称/));
    await user.type(screen.getByLabelText(/企业名称/), "手动修正后的企业名称");
    await user.click(screen.getByRole("button", { name: "确认并创建问卷" }));

    await waitFor(() => {
      expect(createAssessmentFromIntake).toHaveBeenCalledWith("session-1", {
        confirmed_assessment_input: expect.objectContaining({
          company_name: "手动修正后的企业名称",
          notes: null,
        }),
      });
    });
    expect(pushMock).toHaveBeenCalledWith("/assessment/assessment-123");
  });
});
