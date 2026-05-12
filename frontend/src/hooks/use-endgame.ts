import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { generateEndgame, getEndgame } from "@/lib/api";
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
