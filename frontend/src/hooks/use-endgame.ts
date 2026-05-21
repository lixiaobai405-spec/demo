import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { generateEndgame, getEndgame, updateEndgame } from "@/lib/api";
import type { UpdateEndgamePayload } from "@/lib/types";
import { assessmentKeys } from "./use-assessment";

export function useEndgame(assessmentId: string | undefined) {
  return useQuery({
    queryKey: assessmentKeys.endgame(assessmentId!),
    queryFn: () => getEndgame(assessmentId!),
    enabled: Boolean(assessmentId),
    staleTime: 5 * 60 * 1000,
  });
}

export function useGenerateEndgame() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (assessmentId: string) => generateEndgame(assessmentId),
    onSuccess: (_data, assessmentId) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.endgame(assessmentId),
      });
    },
  });
}

export function useUpdateEndgame() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      assessmentId,
      payload,
    }: {
      assessmentId: string;
      payload: UpdateEndgamePayload;
    }) => updateEndgame(assessmentId, payload),
    onSuccess: (_data, { assessmentId }) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.endgame(assessmentId),
      });
    },
  });
}
