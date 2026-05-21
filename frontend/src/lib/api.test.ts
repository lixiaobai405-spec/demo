import { afterEach, describe, expect, it, vi } from "vitest";

import { deleteAssessment } from "@/lib/api";

describe("api request helper", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("treats 204 responses as successful empty payloads", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(null, { status: 204 }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(deleteAssessment("assessment-1")).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
