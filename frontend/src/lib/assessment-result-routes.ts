/**
 * 生成 AI 场景推荐结果页路由。
 */
export function getScenarioResultPath(assessmentId: string): string {
  return `/assessment/${assessmentId}/scenarios`;
}

/**
 * 生成差异化竞争力结果页路由。
 */
export function getCompetitivenessResultPath(assessmentId: string): string {
  return `/assessment/${assessmentId}/competitiveness`;
}

/**
 * 生成结果仪表盘路由。
 */
export function getResultsDashboardPath(assessmentId: string): string {
  return `/assessment/${assessmentId}/results`;
}
