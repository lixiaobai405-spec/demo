import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getFollowUpPlan,
  updateFollowUpTask,
  recalibrateFollowUp,
} from "@/lib/api";
import type { FollowUpTaskItem, TaskUpdateRequest } from "@/lib/types";
import { assessmentKeys } from "./use-assessment";

export function useFollowUpPlan(assessmentId: string | undefined) {
  return useQuery({
    queryKey: assessmentKeys.followUp(assessmentId!),
    queryFn: () => getFollowUpPlan(assessmentId!),
    enabled: Boolean(assessmentId),
  });
}

export function useUpdateFollowUpTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      assessmentId,
      taskId,
      payload,
    }: {
      assessmentId: string;
      taskId: string;
      payload: TaskUpdateRequest;
    }) => updateFollowUpTask(assessmentId, taskId, payload),
    onSuccess: (_data, { assessmentId }) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.followUp(assessmentId),
      });
    },
  });
}

export function useRecalibrateFollowUp() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      assessmentId,
      payload,
    }: {
      assessmentId: string;
      payload: { note: string; updated_tasks: Partial<FollowUpTaskItem>[] };
    }) => recalibrateFollowUp(assessmentId, payload),
    onSuccess: (_data, { assessmentId }) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.followUp(assessmentId),
      });
    },
  });
}
