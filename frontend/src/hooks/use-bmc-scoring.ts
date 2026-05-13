import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  autoDeriveBMCScoring,
  calculateBMCScoring,
  getBMCScoring,
  saveBMCScoring,
} from "@/lib/api";
import type { BmcScoringSaveRequest, ModuleScoreInput } from "@/lib/types";
import { assessmentKeys } from "./use-assessment";

/** BMC 评分相关的 React Query 缓存键。 */
export const bmcScoringKeys = {
  all: ["bmc-scoring"] as const,
  detail: (assessmentId: string) => [...assessmentKeys.detail(assessmentId), "bmc-scoring"] as const,
};

/** 查询指定评估的 BMC 评分结果。 */
export function useGetBMCScoring(assessmentId: string | undefined) {
  return useQuery({
    queryKey: bmcScoringKeys.detail(assessmentId!),
    queryFn: () => getBMCScoring(assessmentId!),
    enabled: Boolean(assessmentId),
    staleTime: 5 * 60 * 1000,
  });
}

/** 调用后端计算 BMC 三维评分结果。 */
export function useCalculateBMCScoring() {
  return useMutation({
    mutationFn: ({
      assessmentId,
      modules,
    }: {
      assessmentId: string;
      modules: ModuleScoreInput[];
    }) => calculateBMCScoring(assessmentId, { modules }),
  });
}

/** 保存 BMC 评分选择结果，并刷新详情与评分缓存。 */
export function useSaveBMCScoring() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      assessmentId,
      payload,
    }: {
      assessmentId: string;
      payload: BmcScoringSaveRequest;
    }) => saveBMCScoring(assessmentId, payload),
    onSuccess: (_data, { assessmentId }) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.detail(assessmentId),
      });
      queryClient.invalidateQueries({
        queryKey: bmcScoringKeys.detail(assessmentId),
      });
    },
  });
}

/** 基于商业画布数据自动推导 BMC 模块分值。 */
export function useAutoDeriveBMCScoring() {
  return useMutation({
    mutationFn: (assessmentId: string) => autoDeriveBMCScoring(assessmentId),
  });
}
