import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createAssessmentFromIntake,
  getIntakeImportSession,
  importAssessmentIntake,
  importAssessmentIntakeFile,
} from "@/lib/api";
import type { IntakeCreateAssessmentRequest } from "@/lib/types";

export const intakeKeys = {
  session: (id: string) => ["intake", "session", id] as const,
};

export function useImportIntake() {
  return useMutation({
    mutationFn: (params: {
      sourceType: string;
      rawContent?: string | null;
      structuredFields?: Record<string, string>;
    }) =>
      importAssessmentIntake({
        source_type: params.sourceType as "text" | "markdown" | "form",
        raw_content: params.rawContent ?? null,
        structured_fields: params.structuredFields,
      }),
  });
}

export function useImportIntakeFile() {
  return useMutation({
    mutationFn: (file: File) => importAssessmentIntakeFile(file),
  });
}

export function useIntakeSession(sessionId: string | null) {
  return useQuery({
    queryKey: intakeKeys.session(sessionId!),
    queryFn: () => getIntakeImportSession(sessionId!),
    enabled: Boolean(sessionId),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateAssessmentFromIntake() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sessionId,
      payload,
    }: {
      sessionId: string;
      payload: IntakeCreateAssessmentRequest;
    }) => createAssessmentFromIntake(sessionId, payload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: intakeKeys.session(variables.sessionId),
      });
    },
  });
}
