import type {
  AssessmentBreakthroughResponse,
  AssessmentCanvasResponse,
  AssessmentCaseResponse,
  AssessmentCreateRequest,
  AssessmentDetailResponse,
  AssessmentDirectionResponse,
  AssessmentProfileResponse,
  AssessmentResponse,
  AssessmentScenarioRecommendationResponse,
  BreakthroughSelectionRequest,
  BreakthroughSelectionResponse,
  CompetitivenessResponse,
  DirectionSelectionRequest,
  DirectionSelectionResponse,
  IntakeCreateAssessmentRequest,
  IntakeCreateAssessmentResponse,
  IntakeImportRequest,
  IntakeImportResponse,
  IntakeSessionDetailResponse,
  ReportContextResponse,
  ReportDocumentResponse,
  ReportEnrichmentResult,
  EndgameResponse,
  OverallQualityReport,
  FollowUpPlan,
  FollowUpTaskItem,
  TaskUpdateRequest,
  PushCycleResult,
  RecalibratePlanRequest,
  InstructorDashboardResponse,
  BatchCommentResponse,
} from "@/lib/types";

export const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(message: string, status: number, detail?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const maxRetries = 2;
  let lastError: unknown;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const isFormData = init?.body instanceof FormData;
      const response = await fetch(`${apiBaseUrl}${path}`, {
        cache: "no-store",
        ...init,
        headers: {
          ...(isFormData ? {} : { "Content-Type": "application/json" }),
          ...(init?.headers ?? {}),
        },
      });

      if (!response.ok) {
        const text = await response.text();
        let detail: unknown = text;
        let message = text || `HTTP ${response.status}`;

        try {
          const payload = JSON.parse(text) as { detail?: unknown };
          detail = payload.detail ?? payload;
          if (typeof payload.detail === "string" && payload.detail.trim()) {
            message = payload.detail;
          }
        } catch {
          // Keep raw text when response is not JSON.
        }

        if (response.status >= 500 && attempt < maxRetries) {
          lastError = new ApiError(message, response.status, detail);
          await new Promise((r) => setTimeout(r, (attempt + 1) * 800));
          continue;
        }

        throw new ApiError(message, response.status, detail);
      }

      return (await response.json()) as T;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      if (attempt < maxRetries) {
        lastError = error;
        await new Promise((r) => setTimeout(r, (attempt + 1) * 800));
        continue;
      }
      throw new ApiError(
        error instanceof TypeError ? "网络连接失败，请检查后端服务是否启动。" : String(error),
        0,
      );
    }
  }

  throw lastError;
}

export function createAssessment(
  payload: AssessmentCreateRequest,
): Promise<AssessmentResponse> {
  return request<AssessmentResponse>("/api/assessments", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function importAssessmentIntake(
  payload: IntakeImportRequest,
): Promise<IntakeImportResponse> {
  return request<IntakeImportResponse>("/api/intake/import", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function importAssessmentIntakeFile(
  file: File,
): Promise<IntakeImportResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return request<IntakeImportResponse>("/api/intake/import/file", {
    method: "POST",
    body: formData,
  });
}

export function getIntakeImportSession(
  importSessionId: string,
): Promise<IntakeSessionDetailResponse> {
  return request<IntakeSessionDetailResponse>(
    `/api/intake/import/${importSessionId}`,
  );
}

export function createAssessmentFromIntake(
  importSessionId: string,
  payload: IntakeCreateAssessmentRequest,
): Promise<IntakeCreateAssessmentResponse> {
  return request<IntakeCreateAssessmentResponse>(
    `/api/intake/import/${importSessionId}/assessment`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function getAssessmentDetail(
  assessmentId: string,
): Promise<AssessmentDetailResponse> {
  return request<AssessmentDetailResponse>(`/api/assessments/${assessmentId}`);
}

export function getReportContext(
  assessmentId: string,
): Promise<ReportContextResponse> {
  return request<ReportContextResponse>(
    `/api/assessments/${assessmentId}/report-context`,
  );
}

export function generateAssessmentProfile(
  assessmentId: string,
): Promise<AssessmentProfileResponse> {
  return request<AssessmentProfileResponse>(
    `/api/assessments/${assessmentId}/profile`,
    { method: "POST" },
  );
}

export function generateAssessmentCanvas(
  assessmentId: string,
): Promise<AssessmentCanvasResponse> {
  return request<AssessmentCanvasResponse>(
    `/api/assessments/${assessmentId}/canvas`,
    { method: "POST" },
  );
}

export function generateScenarioRecommendations(
  assessmentId: string,
): Promise<AssessmentScenarioRecommendationResponse> {
  return request<AssessmentScenarioRecommendationResponse>(
    `/api/assessments/${assessmentId}/scenarios`,
    { method: "POST" },
  );
}

export function generateCaseRecommendations(
  assessmentId: string,
): Promise<AssessmentCaseResponse> {
  return request<AssessmentCaseResponse>(
    `/api/assessments/${assessmentId}/cases`,
    { method: "POST" },
  );
}

export function generateAssessmentReport(
  assessmentId: string,
  mode: "template" | "llm" = "template",
): Promise<ReportDocumentResponse> {
  return request<ReportDocumentResponse>(
    `/api/assessments/${assessmentId}/report?mode=${mode}`,
    { method: "POST" },
  );
}

export function getReport(reportId: string): Promise<ReportDocumentResponse> {
  return request<ReportDocumentResponse>(`/api/reports/${reportId}`);
}

export function getReportMarkdownExportUrl(reportId: string): string {
  return `${apiBaseUrl}/api/reports/${reportId}/export/markdown`;
}

export function getReportDocxExportUrl(reportId: string): string {
  return `${apiBaseUrl}/api/reports/${reportId}/export/docx`;
}

export function getReportPrintUrl(reportId: string): string {
  return `${apiBaseUrl}/api/reports/${reportId}/print`;
}

export function recommendBreakthrough(
  assessmentId: string,
): Promise<AssessmentBreakthroughResponse> {
  return request<AssessmentBreakthroughResponse>(
    `/api/assessments/${assessmentId}/breakthrough/recommend`,
    { method: "POST" },
  );
}

export function selectBreakthrough(
  assessmentId: string,
  payload: BreakthroughSelectionRequest,
): Promise<BreakthroughSelectionResponse> {
  return request<BreakthroughSelectionResponse>(
    `/api/assessments/${assessmentId}/breakthrough/select`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function getBreakthrough(
  assessmentId: string,
): Promise<AssessmentBreakthroughResponse> {
  return request<AssessmentBreakthroughResponse>(
    `/api/assessments/${assessmentId}/breakthrough`,
  );
}

export function expandDirections(
  assessmentId: string,
): Promise<AssessmentDirectionResponse> {
  return request<AssessmentDirectionResponse>(
    `/api/assessments/${assessmentId}/directions/expand`,
    { method: "POST" },
  );
}

export function selectDirections(
  assessmentId: string,
  payload: DirectionSelectionRequest,
): Promise<DirectionSelectionResponse> {
  return request<DirectionSelectionResponse>(
    `/api/assessments/${assessmentId}/directions/select`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function getDirections(
  assessmentId: string,
): Promise<AssessmentDirectionResponse> {
  return request<AssessmentDirectionResponse>(
    `/api/assessments/${assessmentId}/directions`,
  );
}

export function generateCompetitiveness(
  assessmentId: string,
): Promise<CompetitivenessResponse> {
  return request<CompetitivenessResponse>(
    `/api/assessments/${assessmentId}/competitiveness/generate`,
    { method: "POST" },
  );
}

export function getCompetitiveness(
  assessmentId: string,
): Promise<CompetitivenessResponse> {
  return request<CompetitivenessResponse>(
    `/api/assessments/${assessmentId}/competitiveness`,
  );
}

export function getReportEnrichment(
  reportId: string,
): Promise<ReportEnrichmentResult> {
  return request<ReportEnrichmentResult>(
    `/api/reports/${reportId}/enrich`,
  );
}

export function createShareLink(
  reportId: string,
): Promise<{ share_url: string; token: string }> {
  return request<{ share_url: string; token: string }>(
    `/api/reports/${reportId}/share`,
    { method: "POST" },
  );
}

export function getReportPdfUrl(reportId: string): string {
  return `${apiBaseUrl}/api/reports/${reportId}/export/pdf`;
}

export function generateEndgame(
  assessmentId: string,
): Promise<EndgameResponse> {
  return request<EndgameResponse>(
    `/api/assessments/${assessmentId}/endgame/generate`,
    { method: "POST" },
  );
}

export function getEndgame(
  assessmentId: string,
): Promise<EndgameResponse> {
  return request<EndgameResponse>(
    `/api/assessments/${assessmentId}/endgame`,
  );
}

export function getReportQuality(
  reportId: string,
): Promise<OverallQualityReport> {
  return request<OverallQualityReport>(
    `/api/reports/${reportId}/quality`,
  );
}

export function getFollowUpPlan(
  assessmentId: string,
): Promise<FollowUpPlan> {
  return request<FollowUpPlan>(
    `/api/assessments/${assessmentId}/follow-up`,
  );
}

export function updateFollowUpTask(
  assessmentId: string,
  taskId: string,
  payload: TaskUpdateRequest,
): Promise<FollowUpTaskItem> {
  return request<FollowUpTaskItem>(
    `/api/assessments/${assessmentId}/follow-up/tasks/${taskId}`,
    { method: "PATCH", body: JSON.stringify(payload) },
  );
}

export function recalibrateFollowUp(
  assessmentId: string,
  payload: { note: string; updated_tasks: Partial<FollowUpTaskItem>[] },
): Promise<FollowUpPlan> {
  return request<FollowUpPlan>(
    `/api/assessments/${assessmentId}/follow-up/recalibrate`,
    { method: "POST", body: JSON.stringify(payload) },
  );
}

export function triggerCasePush(
  assessmentId: string,
): Promise<PushCycleResult> {
  return request<PushCycleResult>(
    `/api/assessments/${assessmentId}/push`,
    { method: "POST" },
  );
}

export function getPushHistory(
  assessmentId: string,
): Promise<PushCycleResult[]> {
  return request<PushCycleResult[]>(
    `/api/assessments/${assessmentId}/push/history`,
  );
}

export function recalibratePlan(
  assessmentId: string,
  payload: RecalibratePlanRequest,
): Promise<{ status: string; note: string; completed_tasks: number; new_actions: number }> {
  return request(
    `/api/assessments/${assessmentId}/recalibrate`,
    { method: "POST", body: JSON.stringify(payload) },
  );
}

export function getInstructorDashboard(): Promise<InstructorDashboardResponse> {
  return request<InstructorDashboardResponse>("/api/instructor/dashboard");
}

export function batchComment(
  payload: { assessment_ids: string[]; comment: string },
): Promise<BatchCommentResponse> {
  return request<BatchCommentResponse>("/api/instructor/batch-comment", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function instructorExportCsv(): Promise<{ export_format: string; content: string; student_count: number }> {
  return request("/api/instructor/export?format=csv");
}
