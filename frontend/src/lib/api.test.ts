import { afterEach, describe, expect, it, vi } from "vitest";

import {
  createPaymentOrder,
  deleteAssessment,
  getReportContext,
  resolveApiBaseUrl,
} from "@/lib/api";

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

  it("creates a payment order for the selected provider", async () => {
    const orderPayload = {
      order_id: "order-1",
      order_no: "PAY202606080001",
      assessment_id: "assessment-1",
      provider: "wechat",
      amount_cents: 9900,
      currency: "CNY",
      status: "pending",
      qr_code_url: "mockpay://wechat/PAY202606080001",
      expires_at: "2026-06-08T10:00:00Z",
      paid_at: null,
      created_at: "2026-06-08T09:30:00Z",
    };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(orderPayload), { status: 201 }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      createPaymentOrder("assessment-1", { provider: "wechat" }),
    ).resolves.toEqual(orderPayload);

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/assessments/assessment-1/payments/orders",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ provider: "wechat" }),
      }),
    );
  });

  it("surfaces structured payment required messages", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: {
              code: "PAYMENT_REQUIRED",
              message: "请先解锁当前评估。",
              assessment_id: "assessment-1",
            },
          }),
          { status: 402 },
        ),
      ),
    );

    await expect(getReportContext("assessment-1")).rejects.toMatchObject({
      status: 402,
      message: "请先解锁当前评估。",
    });
  });
});
