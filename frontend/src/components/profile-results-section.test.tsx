import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ProfileResultsSection } from "@/components/profile-results-section";

describe("ProfileResultsSection", () => {
  /**
   * 确认企业画像结果中不再显示待补充信息模块。
   */
  it("does not render missing information block", () => {
    render(
      <ProfileResultsSection
        profileMode="mock"
        companyProfile={{
          company_name: "测试企业",
          company_summary: "企业概览",
          value_proposition: "价值主张",
          customer_and_market: "客户市场",
          operations_and_resources: "运营资源",
          digital_and_ai_readiness: "AI 准备度",
          key_challenges: ["挑战 1"],
          priority_ai_directions: ["方向 1"],
          missing_information: ["这部分不应展示"],
        }}
      />,
    );

    expect(screen.queryByText("待补充信息")).not.toBeInTheDocument();
    expect(screen.getByText("挑战 1")).toBeInTheDocument();
    expect(screen.getByText("方向 1")).toBeInTheDocument();
  });
});
