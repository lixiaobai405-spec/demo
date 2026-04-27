import type {
  AssessmentCanvasResponse,
  AssessmentCaseResponse,
  AssessmentCreateRequest,
  AssessmentDetailResponse,
  AssessmentProfileResponse,
  AssessmentResponse,
  AssessmentScenarioRecommendationResponse,
  ReportContextResponse,
  ReportDocumentResponse,
} from "@/lib/types";

export const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    cache: "no-store",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const text = await response.text();
    let message = text || `HTTP ${response.status}`;

    try {
      const payload = JSON.parse(text) as { detail?: string };
      message = payload.detail ?? message;
    } catch {
      // Keep raw text when response is not JSON.
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}

export function createAssessment(
  payload: AssessmentCreateRequest,
): Promise<AssessmentResponse> {
  return request<AssessmentResponse>("/api/assessments", {
    method: "POST",
    body: JSON.stringify(payload),
  });
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
