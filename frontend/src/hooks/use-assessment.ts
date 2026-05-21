import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, createAssessment, getAssessmentDetail } from "@/lib/api";
import type { AssessmentCreateRequest } from "@/lib/types";

export const assessmentKeys = {
  all: ["assessment"] as const,
  detail: (id: string) => ["assessment", id] as const,
  profile: (id: string) => ["assessment", id, "profile"] as const,
  canvas: (id: string) => ["assessment", id, "canvas"] as const,
  breakthrough: (id: string) => ["assessment", id, "breakthrough"] as const,
  directions: (id: string) => ["assessment", id, "directions"] as const,
  scenarios: (id: string) => ["assessment", id, "scenarios"] as const,
  competitiveness: (id: string) =>
    ["assessment", id, "competitiveness"] as const,
  endgame: (id: string) => ["assessment", id, "endgame"] as const,
  followUp: (id: string) => ["assessment", id, "followUp"] as const,
};

export function useAssessmentDetail(assessmentId: string | undefined) {
  return useQuery({
    queryKey: assessmentKeys.detail(assessmentId!),
    queryFn: () => getAssessmentDetail(assessmentId!),
    enabled: Boolean(assessmentId),
    staleTime: 0, // always refetch on mount so workbench shows latest state
    retry: (failureCount, error) =>
      !(
        error instanceof ApiError &&
        (error.status === 403 || error.status === 404)
      ) && failureCount < 2,
  });
}

export function useCreateAssessment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AssessmentCreateRequest) =>
      createAssessment({ ...payload, notes: (payload.notes ?? "").trim() || null }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: assessmentKeys.all });
    },
  });
}
