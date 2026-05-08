import { useMutation, useQueryClient } from "@tanstack/react-query";
import { generateCompetitiveness } from "@/lib/api";
import { assessmentKeys } from "./use-assessment";

export function useGenerateCompetitiveness() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (assessmentId: string) =>
      generateCompetitiveness(assessmentId),
    onSuccess: (_data, assessmentId) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
    },
  });
}
