import type {
  AssessmentCreateRequest,
  AssessmentDetailResponse,
  AssessmentPrefillDraft,
  AssessmentProgress,
  AssessmentResponse,
  BreakthroughSelectionResponse,
  CanvasDiagnosisResult,
  CompanyProfileResult,
  ScenarioRecommendationResult,
} from "@/lib/types";

export const initialForm: AssessmentCreateRequest = {
  company_name: "", industry: "", company_size: "", region: "",
  annual_revenue_range: "", core_products: "", target_customers: "",
  current_challenges: "", ai_goals: "", available_data: "", notes: "",
};

export const initialProgress: AssessmentProgress = {
  has_profile: false, has_canvas: false, has_breakthrough: false,
  has_directions: false, has_competitiveness: false, has_scenarios: false,
  has_cases: false, has_report: false, ready_for_report: false,
};

export const companySizeOptions = [
  "10人以下", "10-50人", "50-200人", "200-500人", "500人以上",
];

export const revenueOptions = [
  "500万以下", "500万-3000万", "3000万-1亿", "1亿-10亿", "10亿以上",
];

export function mapAssessmentToForm(
  assessment: AssessmentResponse,
): AssessmentCreateRequest {
  return {
    company_name: assessment.company_name,
    industry: assessment.industry,
    company_size: assessment.company_size,
    region: assessment.region,
    annual_revenue_range: assessment.annual_revenue_range,
    core_products: assessment.core_products,
    target_customers: assessment.target_customers,
    current_challenges: assessment.current_challenges,
    ai_goals: assessment.ai_goals,
    available_data: assessment.available_data,
    notes: assessment.notes ?? "",
  };
}

export function mergePrefillIntoForm(
  currentForm: AssessmentCreateRequest,
  prefill: AssessmentPrefillDraft,
): AssessmentCreateRequest {
  const mergedEntries = Object.entries(prefill).map(([key, value]) => {
    const formKey = key as keyof AssessmentCreateRequest;
    const currentValue =
      typeof currentForm[formKey] === "string"
        ? (currentForm[formKey] as string)
        : (currentForm[formKey] ?? "");
    const normalizedCurrent = (currentValue as string).trim();
    const normalizedPrefill = ((value ?? "") as string).trim();

    if (normalizedCurrent || !normalizedPrefill) {
      return [formKey, currentForm[formKey]];
    }
    return [formKey, normalizedPrefill];
  });

  return {
    ...currentForm,
    ...Object.fromEntries(mergedEntries),
  };
}

export function countPrefillFields(prefill: AssessmentPrefillDraft): number {
  return Object.values(prefill).filter(
    (value) => typeof value === "string" && value.trim().length > 0,
  ).length;
}

export function computeProgress(opts: {
  hasAssessment: boolean;
  hasProfile: boolean;
  hasCanvas: boolean;
  hasBreakthrough?: boolean;
  hasDirections?: boolean;
  hasCompetitiveness?: boolean;
  hasScenarios: boolean;
  hasCases?: boolean;
  hasReport?: boolean;
}): AssessmentProgress {
  return {
    has_profile: opts.hasAssessment && opts.hasProfile,
    has_canvas: opts.hasAssessment && opts.hasCanvas,
    has_breakthrough: opts.hasAssessment && (opts.hasBreakthrough ?? false),
    has_directions: opts.hasAssessment && (opts.hasDirections ?? false),
    has_competitiveness: opts.hasAssessment && (opts.hasCompetitiveness ?? false),
    has_scenarios: opts.hasAssessment && opts.hasScenarios,
    has_cases: opts.hasAssessment && (opts.hasCases ?? false),
    has_report: opts.hasAssessment && (opts.hasReport ?? false),
    ready_for_report:
      opts.hasAssessment &&
      opts.hasProfile &&
      opts.hasCanvas &&
      (opts.hasBreakthrough ?? false) &&
      opts.hasScenarios,
  };
}

export function applyAssessmentDetailToStore(
  detail: AssessmentDetailResponse,
  store: {
    setAssessment: (a: AssessmentResponse | null) => void;
    setCompanyProfile: (p: CompanyProfileResult | null) => void;
    setProfileMode: (m: "mock" | "live" | null) => void;
    setCanvasDiagnosis: (d: CanvasDiagnosisResult | null) => void;
    setSelectedBreakthroughKeys: (keys: string[]) => void;
    setScenarioRecommendation: (r: ScenarioRecommendationResult | null) => void;
  },
) {
  store.setAssessment(detail.assessment);
  store.setCompanyProfile(detail.company_profile);
  store.setProfileMode(
    detail.company_profile
      ? ((detail.assessment.profile_generation_mode as "mock" | "live" | null) ?? "mock")
      : null,
  );
  store.setCanvasDiagnosis(detail.canvas_diagnosis);

  if (detail.breakthrough_selection && detail.breakthrough_selection.length >= 2) {
    store.setSelectedBreakthroughKeys(detail.breakthrough_selection);
  } else {
    store.setSelectedBreakthroughKeys([]);
  }
  store.setScenarioRecommendation(detail.scenario_recommendation);
}
