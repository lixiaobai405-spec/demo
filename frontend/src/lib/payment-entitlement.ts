import type { AssessmentWorkflowKey } from "@/lib/assessment-workflow-state";
import type { AssessmentEntitlementResponse } from "@/lib/types";

const PAID_WORKFLOW_KEYS = new Set<AssessmentWorkflowKey>([
  "breakthrough",
  "directions",
  "scenarios",
  "competitiveness",
  "endgame",
]);

export function isPaidWorkflowKey(key: AssessmentWorkflowKey): boolean {
  return PAID_WORKFLOW_KEYS.has(key);
}

export function isPaymentRequired(
  entitlement: AssessmentEntitlementResponse | null | undefined,
): boolean {
  return Boolean(entitlement && !entitlement.can_continue);
}
