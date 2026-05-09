import { useMutation, useQueryClient } from "@tanstack/react-query";
import { expandDirections, selectDirections } from "@/lib/api";
import type { DirectionSelectionRequest } from "@/lib/types";
import { assessmentKeys } from "./use-assessment";

export function useExpandDirections() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (assessmentId: string) => expandDirections(assessmentId),
    onSuccess: (_data, assessmentId) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
    },
  });
}

export function useSelectDirections() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      assessmentId,
      payload,
    }: {
      assessmentId: string;
      payload: DirectionSelectionRequest;
    }) => selectDirections(assessmentId, payload),
    onSuccess: (_data, { assessmentId }) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
    },
  });
}
