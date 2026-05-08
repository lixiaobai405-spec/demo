import { useMutation, useQueryClient } from "@tanstack/react-query";
import { generateScenarioRecommendations } from "@/lib/api";
import { assessmentKeys } from "./use-assessment";

export function useGenerateScenarios() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (assessmentId: string) =>
      generateScenarioRecommendations(assessmentId),
    onSuccess: (_data, assessmentId) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
    },
  });
}
