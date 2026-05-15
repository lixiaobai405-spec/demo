import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { generateCompetitiveness, getCompetitiveness } from "@/lib/api";
import { assessmentKeys } from "./use-assessment";

/**
 * 在客户端查询差异化竞争力分析结果。
 */
export function useCompetitiveness(assessmentId: string | undefined) {
  return useQuery({
    queryKey: assessmentKeys.competitiveness(assessmentId!),
    queryFn: () => getCompetitiveness(assessmentId!),
    enabled: Boolean(assessmentId),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * 触发差异化竞争力分析生成，并刷新相关缓存。
 */
export function useGenerateCompetitiveness() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (assessmentId: string) =>
      generateCompetitiveness(assessmentId),
    onSuccess: (_data, assessmentId) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.competitiveness(assessmentId),
      });
    },
  });
}
