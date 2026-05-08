import { useMutation, useQueryClient } from "@tanstack/react-query";
import { generateAssessmentProfile } from "@/lib/api";
import { assessmentKeys } from "./use-assessment";

export function useGenerateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (assessmentId: string) =>
      generateAssessmentProfile(assessmentId),
    onSuccess: (_data, assessmentId) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
    },
  });
}
