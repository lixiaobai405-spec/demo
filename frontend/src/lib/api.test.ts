import { afterEach, describe, expect, it, vi } from "vitest";

import { deleteAssessment, resolveApiBaseUrl } from "@/lib/api";

describe("api request helper", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("trims accidental whitespace and trailing slash from the api base url", () => {
    expect(resolveApiBaseUrl(" http://localhost:8000/ ")).toBe(
      "http://localhost:8000",
    );
    expect(resolveApiBaseUrl(undefined)).toBe("http://localhost:8000");
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
