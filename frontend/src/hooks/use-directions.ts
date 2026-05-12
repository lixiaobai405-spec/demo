import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { expandDirections, getDirections, selectDirections } from "@/lib/api";
import type { DirectionSelectionRequest } from "@/lib/types";
import { assessmentKeys } from "./use-assessment";

export function useDirectionPolling(
  assessmentId: string | null,
  shouldPoll: boolean,
) {
  return useQuery({
    queryKey: assessmentKeys.directions(assessmentId!),
    queryFn: ({ signal }) => getDirections(assessmentId!, { signal }),
    enabled: Boolean(assessmentId) && shouldPoll,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.direction_expansion.llm_status === "pending") return 3000;
      return false;
    },
    staleTime: 0,
    gcTime: 0,
    retry: false,
  });
}

export function useExpandDirections() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (assessmentId: string) => expandDirections(assessmentId),
    onSuccess: (_data, assessmentId) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.directions(assessmentId),
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
