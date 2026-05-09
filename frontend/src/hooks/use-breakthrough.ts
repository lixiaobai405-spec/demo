import { useMutation, useQueryClient } from "@tanstack/react-query";
import { recommendBreakthrough, selectBreakthrough } from "@/lib/api";
import type { BreakthroughSelectionRequest } from "@/lib/types";
import { assessmentKeys } from "./use-assessment";

export function useRecommendBreakthrough() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (assessmentId: string) => recommendBreakthrough(assessmentId),
    onSuccess: (_data, assessmentId) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
    },
  });
}

export function useSelectBreakthrough() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      assessmentId,
      payload,
    }: {
      assessmentId: string;
      payload: BreakthroughSelectionRequest;
    }) => selectBreakthrough(assessmentId, payload),
    onSuccess: (_data, { assessmentId }) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
    },
  });
}
