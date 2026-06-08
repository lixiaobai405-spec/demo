import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  completeMockPaymentOrder,
  createPaymentOrder,
} from "@/lib/api";
import type { PaymentOrderResponse, PaymentProvider } from "@/lib/types";

import { assessmentKeys } from "./use-assessment";

export function useCreatePaymentOrder(assessmentId: string) {
  return useMutation({
    mutationFn: (provider: PaymentProvider) =>
      createPaymentOrder(assessmentId, { provider }),
  });
}

export function useCompleteMockPayment(assessmentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (order: PaymentOrderResponse) => completeMockPaymentOrder(order),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
    },
  });
}
