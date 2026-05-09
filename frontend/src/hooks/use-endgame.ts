import { useMutation, useQueryClient } from "@tanstack/react-query";
import { generateEndgame } from "@/lib/api";
import { assessmentKeys } from "./use-assessment";

export function useGenerateEndgame() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (assessmentId: string) => generateEndgame(assessmentId),
    onSuccess: (_data, assessmentId) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
    },
  });
}
