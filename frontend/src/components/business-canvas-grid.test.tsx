import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { BusinessCanvasGrid } from "@/components/business-canvas-grid";
import type { CanvasDiagnosisResult } from "@/lib/types";

/**
 * 构造用于界面展示测试的商业画布结果。
 */
function buildCanvasDiagnosis(): CanvasDiagnosisResult {
  return {
    generation_mode: "mock",
    overall_score: 81,
    weakest_blocks: ["客户关系"],
    recommended_focus: ["优化客户分层"],
    created_at: null,
    updated_at: null,
    canvas: {
      overall_summary: "这是完整摘要，不应被省略。",
      blocks: [
        {
          key: "value_propositions",
          title: "价值主张",
          current_state: "完整现状",
          diagnosis: "完整诊断",
          ai_opportunity: "完整机会",
          missing_information: "这里不应展示",
        },
      ],
    },
  };
}

describe("BusinessCanvasGrid", () => {
  /**
   * 确认商业画布结果中不再显示总分和待补充标签。
   */
  it("does not render overall score or missing information labels", () => {
    render(<BusinessCanvasGrid canvasDiagnosis={buildCanvasDiagnosis()} />);

    expect(screen.queryByText(/overall score/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/待补充/i)).not.toBeInTheDocument();
    expect(screen.getByText("客户关系")).toBeInTheDocument();
    expect(screen.getByText("优化客户分层")).toBeInTheDocument();
  });
});
