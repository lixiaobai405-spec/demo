import { describe, expect, it } from "vitest";

import {
  getCompetitivenessResultPath,
  getResultsDashboardPath,
  getScenarioResultPath,
} from "@/lib/assessment-result-routes";

describe("assessment result routing helpers", () => {
  /**
   * 确认场景推荐结果页使用独立路由。
   */
  it("builds the dedicated scenario result route", () => {
    expect(getScenarioResultPath("assessment-1")).toBe("/assessment/assessment-1/scenarios");
  });

  /**
   * 确认差异化竞争力结果页使用独立路由。
   */
  it("builds the dedicated competitiveness result route", () => {
    expect(getCompetitivenessResultPath("assessment-1")).toBe(
      "/assessment/assessment-1/competitiveness",
    );
  });

  /**
   * 确认结果仪表盘仍保留独立汇总页路由。
   */
  it("keeps the dashboard route separate from module pages", () => {
    expect(getResultsDashboardPath("assessment-1")).toBe("/assessment/assessment-1/results");
  });
});
