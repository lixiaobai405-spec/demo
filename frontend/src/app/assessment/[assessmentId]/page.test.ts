import { describe, expect, it } from "vitest";

import { formatShortAssessmentId } from "@/lib/assessment-display";

describe("AssessmentDetailPage", () => {
  it("formats the assessment id as an 8-character display id", () => {
    expect(formatShortAssessmentId("59b65b1c-242b-45e9-9e08-72348e491813")).toBe(
      "59b65b1c",
    );
  });
});
