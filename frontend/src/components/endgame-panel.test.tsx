import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CompetitivenessPanel } from "@/components/competitiveness-panel";
import { EndgamePanel } from "@/components/endgame-panel";

describe("EndgamePanel", () => {
  /**
   * 确认商业终局页承接三阶段推进策略展示。
   */
  it("renders the three-stage strategy in the endgame panel", () => {
    render(
      <EndgamePanel
        data={{
          assessment_id: "assessment-1",
          result: {
            generation_mode: "rule_based",
            private_domain: {
              current_state: "私域基础薄弱",
              target_model: "建立统一客户经营私域",
              key_strategies: ["统一客户视图"],
              customer_retention_loop: "触点数据化 -> 分层运营 -> 价值留存",
              revenue_impact: "提升留存和复购",
            },
            ecosystem: {
              ecosystem_positioning: "连接品牌与消费者",
              key_partners_to_engage: ["品牌供应商"],
              orchestration_strategy: "围绕数据平台做协同",
              platform_effect: "更多伙伴带来更强协同",
            },
            opc: {
              operations_excellence: "建立统一运营机制",
              platform_capability: "沉淀平台能力",
              content_and_community: "建设内容与社群",
              data_flywheel_effect: "数据沉淀形成正循环",
            },
            three_stage_strategy: {
              stage_1: {
                title: "阶段 1",
                focus: "快速验证",
                objective: "先在单一门店验证客户分层与触达闭环。",
              },
              stage_2: {
                title: "阶段 2",
                focus: "规模扩展",
                objective: "复制到区域门店并统一运营方法。",
              },
              stage_3: {
                title: "阶段 3",
                focus: "壁垒构建",
                objective: "沉淀为长期平台能力和组织标准。",
              },
              key_risks: ["跨团队协同不足"],
            },
            strategic_paths: [
              {
                path_name: "稳健试点路径",
                path_type: "保守",
                execution_rhythm: "以试点验证为先，成熟后再复制扩展",
                key_milestones: ["完成试点准备"],
                capability_requirements: "优先复用现有团队与客户经营机制",
                expected_outcomes: "形成可复制样板",
                major_risks: ["推进节奏不一致"],
                recommendation_level: "推荐",
              },
            ],
            overall_narrative: "终局方向清晰。",
          },
          created_at: null,
          updated_at: null,
        }}
      />,
    );

    expect(screen.getByText("三阶段推进策略")).toBeInTheDocument();
    expect(screen.getByText("阶段 1")).toBeInTheDocument();
    expect(screen.getByText("快速验证")).toBeInTheDocument();
    expect(screen.getByText("先在单一门店验证客户分层与触达闭环。")).toBeInTheDocument();
    expect(screen.getByText("跨团队协同不足")).toBeInTheDocument();
    expect(screen.getByText("推进节奏")).toBeInTheDocument();
    expect(screen.getByText("能力前提")).toBeInTheDocument();
    expect(screen.queryByText("投资需求")).not.toBeInTheDocument();
  });

  /**
   * 确认竞争力页移除三阶段推进策略展示，避免与商业终局重复承载。
   */
  it("does not render the three-stage strategy block in the competitiveness panel", () => {
    render(
      <CompetitivenessPanel
        data={{
          assessment_id: "assessment-1",
          result: {
            generation_mode: "rule_based",
            vp_reconstruction: {
              current_vp: "帮助门店提升经营效率",
              enhanced_vp: "通过客户经营形成差异化竞争力",
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
              phase_2_scale: "再复制",
              phase_3_moat: "后沉淀",
              key_risks: ["跨团队协同不足"],
            },
            overall_narrative: "竞争力已具备向终局迁移的基础。",
          },
          created_at: null,
          updated_at: null,
        }}
      />,
    );

    expect(screen.queryByText("三阶段推进策略")).not.toBeInTheDocument();
    expect(screen.queryByText("Phase 1 — 快速验证")).not.toBeInTheDocument();
  });
});
