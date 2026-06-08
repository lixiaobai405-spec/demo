import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { PaymentUnlockPanel } from "@/components/payment-unlock-panel";
import { getPaymentOrder } from "@/lib/api";
import type {
  AssessmentEntitlementResponse,
  PaymentOrderResponse,
} from "@/lib/types";

const createOrderMutate = vi.fn();
const completeMockPaymentMutate = vi.fn();

vi.mock("@/hooks/use-payments", () => ({
  useCreatePaymentOrder: () => ({
    mutateAsync: createOrderMutate,
    isPending: false,
  }),
  useCompleteMockPayment: () => ({
    mutateAsync: completeMockPaymentMutate,
    isPending: false,
  }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    getPaymentOrder: vi.fn(),
  };
});

function renderWithQueryClient(node: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>{node}</QueryClientProvider>,
  );
}

function buildOrder(overrides: Partial<PaymentOrderResponse> = {}) {
  return {
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
    ...overrides,
  } satisfies PaymentOrderResponse;
}

function buildEntitlement(
  overrides: Partial<AssessmentEntitlementResponse> = {},
) {
  return {
    assessment_id: "assessment-1",
    is_unlocked: false,
    can_continue: false,
    locked_after_stage: "canvas",
    unlock_type: null,
    unlocked_at: null,
    latest_order: null,
    ...overrides,
  } satisfies AssessmentEntitlementResponse;
}

describe("PaymentUnlockPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("creates a mock scan order and unlocks after mock completion", async () => {
    const pendingOrder = buildOrder();
    const paidOrder = buildOrder({
      status: "paid",
      paid_at: "2026-06-08T09:35:00Z",
    });
    createOrderMutate.mockResolvedValue(pendingOrder);
    completeMockPaymentMutate.mockResolvedValue({
      status: "paid",
      order_no: pendingOrder.order_no,
      assessment_id: pendingOrder.assessment_id,
      is_unlocked: true,
    });
    vi.mocked(getPaymentOrder).mockResolvedValue(paidOrder);
    const onUnlocked = vi.fn();

    const user = userEvent.setup();
    renderWithQueryClient(
      <PaymentUnlockPanel
        assessmentId="assessment-1"
        entitlement={buildEntitlement()}
        onUnlocked={onUnlocked}
      />,
    );

    await user.click(screen.getByRole("button", { name: "创建扫码订单" }));

    expect(createOrderMutate).toHaveBeenCalledWith("wechat");
    expect(await screen.findByText(pendingOrder.qr_code_url!)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "模拟支付成功" }));

    await waitFor(() => {
      expect(completeMockPaymentMutate).toHaveBeenCalledWith(pendingOrder);
      expect(onUnlocked).toHaveBeenCalled();
    });
  });
});
