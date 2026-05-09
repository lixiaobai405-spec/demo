import { useMutation, useQueryClient } from "@tanstack/react-query";
import { generateAssessmentCanvas } from "@/lib/api";
import { assessmentKeys } from "./use-assessment";

export function useGenerateCanvas() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (assessmentId: string) =>
      generateAssessmentCanvas(assessmentId),
    onSuccess: (_data, assessmentId) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
    },
  });
}
