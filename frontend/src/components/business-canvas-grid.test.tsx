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
    weakest_blocks: ["Key Activities", "Value Propositions", "Customer Segments"],
    recommended_focus: [
      "客户细分（CS）：客户画像粗粒度：仅凭人口属性（如宝妈）无法精确指导营销；高价值客户识别缺失；未区分复购频次、客单价等，无法聚焦资源；细分维度单一，未结合购物偏好、家庭结构等深层属性。—— 建议优先完善该模块数据基础并启动 AI 试点。",
      "Key Activities: 核心流程如会员运营与到家配送缺乏标准化SOP，客服响应慢反映知识沉淀与复用不足。",
    ],
    created_at: null,
    updated_at: null,
    canvas: {
      overall_summary: "这是完整摘要，不应被省略。",
      blocks: [
        {
          key: "value_propositions",
          title: "Value Propositions",
          current_state: "完整现状",
          diagnosis:
            "价值主张差异化不足，尚未形成清晰的客户价值表达。第二句不应展示。",
          ai_opportunity:
            "优先用客户反馈和消费数据提炼高价值卖点。第二个 AI 机会不应展示。",
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
    expect(screen.getAllByText("关键活动").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("价值主张").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("客户细分").length).toBeGreaterThanOrEqual(1);
    expect(screen.queryByText("Key Activities")).not.toBeInTheDocument();
    expect(screen.queryByText("Value Propositions")).not.toBeInTheDocument();
    expect(screen.queryByText("Customer Segments")).not.toBeInTheDocument();
    expect(
      screen.getByText(
        "客户细分：客户画像粗粒度：仅凭人口属性（如宝妈）无法精确指导营销；高价值客户识别缺失；未区分复购频次、客单价等，无法聚焦资源；细分维度单一，未结合购物偏好、家庭结构等深层属性。",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "关键活动：核心流程如会员运营与到家配送缺乏标准化SOP，客服响应慢反映知识沉淀与复用不足。",
      ),
    ).toBeInTheDocument();
    expect(screen.queryByText(/（CS）/)).not.toBeInTheDocument();
    expect(screen.queryByText(/——/)).not.toBeInTheDocument();
    expect(screen.queryByText(/建议优先完善/)).not.toBeInTheDocument();
    expect(
      screen.getByText("价值主张差异化不足，尚未形成清晰的客户价值表达。"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("优先用客户反馈和消费数据提炼高价值卖点。"),
    ).toBeInTheDocument();
    expect(screen.queryByText(/第二句不应展示/)).not.toBeInTheDocument();
    expect(screen.queryByText(/第二个 AI 机会不应展示/)).not.toBeInTheDocument();
  });
});
