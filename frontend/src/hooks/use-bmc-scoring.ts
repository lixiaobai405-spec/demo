import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  calculateBMCScoring,
  saveBMCScoring,
  getBMCScoring,
  autoDeriveBMCScoring,
} from "@/lib/api";
import type { ModuleScoreInput, BmcScoringSaveRequest } from "@/lib/types";
import { assessmentKeys } from "./use-assessment";

export const bmcScoringKeys = {
  all: (id: string) => ["assessment", id, "bmc-scoring"] as const,
};

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
      queryClient.invalidateQueries({ queryKey: bmcScoringKeys.all(assessmentId) });
      queryClient.invalidateQueries({ queryKey: assessmentKeys.detail(assessmentId) });
    },
  });
}

export function useGetBMCScoring(
  assessmentId: string | undefined,
  enabled = true,
) {
  return useQuery({
    queryKey: bmcScoringKeys.all(assessmentId!),
    queryFn: () => getBMCScoring(assessmentId!),
    enabled: Boolean(assessmentId) && enabled,
    staleTime: 5 * 60 * 1000,
  });
}

export function useAutoDeriveBMCScoring() {
  return useMutation({
    mutationFn: (assessmentId: string) => autoDeriveBMCScoring(assessmentId),
  });
}
