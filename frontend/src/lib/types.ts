export type AssessmentCreateRequest = {
  company_name: string;
  industry: string;
  company_size: string;
  region: string;
  annual_revenue_range: string;
  core_products: string;
  target_customers: string;
  current_challenges: string;
  ai_goals: string;
  available_data: string;
  notes: string | null;
};

export type AssessmentInputSnapshot = {
  company_name: string;
  industry: string;
  company_size: string;
  region: string;
  annual_revenue_range: string;
  core_products: string;
  target_customers: string;
  current_challenges: string;
  ai_goals: string;
  available_data: string;
  notes: string | null;
};

export type AssessmentResponse = {
  id: string;
  company_name: string;
  industry: string;
  company_size: string;
  region: string;
  annual_revenue_range: string;
  core_products: string;
  target_customers: string;
  current_challenges: string;
  ai_goals: string;
  available_data: string;
  notes: string | null;
  has_profile: boolean;
  profile_generation_mode: string | null;
  profile_generated_at: string | null;
  created_at: string;
  updated_at: string;
};

export type CompanyProfileResult = {
  company_name: string;
  company_summary: string;
  value_proposition: string;
  customer_and_market: string;
  operations_and_resources: string;
  digital_and_ai_readiness: string;
  key_challenges: string[];
  priority_ai_directions: string[];
  missing_information: string[];
};

export type AssessmentProfileResponse = {
  assessment: AssessmentResponse;
  generation_mode: "mock" | "live";
  profile: CompanyProfileResult;
};

export type CanvasBlockResult = {
  key: string;
  title: string;
  current_state: string;
  diagnosis: string;
  ai_opportunity: string;
  missing_information: string;
};

export type BusinessModelCanvasResult = {
  overall_summary: string;
  blocks: CanvasBlockResult[];
};

export type CanvasDiagnosisResult = {
  generation_mode: "mock" | "live";
  overall_score: number;
  weakest_blocks: string[];
  recommended_focus: string[];
  canvas: BusinessModelCanvasResult;
  created_at: string | null;
  updated_at: string | null;
};

export type AssessmentCanvasResponse = {
  assessment: AssessmentResponse;
  canvas_diagnosis: CanvasDiagnosisResult;
};

export type ScenarioRecommendationItem = {
  scenario_id: string;
  name: string;
  category: string;
  summary: string;
  score: number;
  reasons: string[];
  data_requirements: string[];
};

export type ScenarioRecommendationResult = {
  scoring_method: "rule_based_v1";
  evaluated_count: number;
  top_scenarios: ScenarioRecommendationItem[];
  created_at: string | null;
  updated_at: string | null;
};

export type AssessmentScenarioRecommendationResponse = {
  assessment: AssessmentResponse;
  scenario_recommendation: ScenarioRecommendationResult;
};

export type CaseMatchItem = {
  case_id: string;
  title: string;
  industry: string;
  summary: string;
  fit_score: number;
  matched_pain_points: string[];
  matched_canvas_blocks: string[];
  matched_scenarios: string[];
  match_reasons: string[];
  reference_points: string[];
  data_foundation: string[];
  cautions: string[];
};

export type CaseRecommendationResult = {
  scoring_method: "rule_based_case_v1";
  evaluated_count: number;
  top_cases: CaseMatchItem[];
  created_at: string | null;
  updated_at: string | null;
};

export type AssessmentCaseResponse = {
  assessment: AssessmentResponse;
  case_recommendation: CaseRecommendationResult;
};

export type ReportTableData = {
  columns: string[];
  rows: string[][];
};

export type ReportCardData = {
  title: string;
  subtitle: string | null;
  content: string;
  bullets: string[];
  highlight: string | null;
};

export type ReportSectionData = {
  key: string;
  title: string;
  content: string;
  bullets: string[];
  table: ReportTableData | null;
  cards: ReportCardData[];
  note: string | null;
};

export type ReportData = {
  title: string;
  subtitle: string;
  company_name: string;
  industry: string;
  company_size: string;
  region: string;
  annual_revenue_range: string;
  ai_readiness_score: number;
  ai_readiness_summary: string;
  generated_with: "template" | "llm";
  sections: ReportSectionData[];
};

export type ReportSummaryResponse = {
  report_id: string;
  assessment_id: string;
  title: string;
  created_at: string | null;
  updated_at: string | null;
};

export type ReportDocumentResponse = {
  report_id: string;
  assessment_id: string;
  title: string;
  generation_mode: string;
  used_llm: boolean;
  used_rag: boolean;
  warnings: string[];
  content_markdown: string;
  content_html: string;
  content_json: ReportData;
  sections: ReportSectionData[];
  export_markdown_path: string | null;
  export_docx_path: string | null;
  export_pdf_path: string | null;
  created_at: string | null;
  updated_at: string | null;
};

export type AssessmentProgress = {
  has_profile: boolean;
  has_canvas: boolean;
  has_scenarios: boolean;
  has_cases: boolean;
  has_report: boolean;
  ready_for_report: boolean;
};

export type AssessmentDetailResponse = {
  assessment: AssessmentResponse;
  company_profile: CompanyProfileResult | null;
  canvas_diagnosis: CanvasDiagnosisResult | null;
  scenario_recommendation: ScenarioRecommendationResult | null;
  case_recommendation: CaseRecommendationResult | null;
  generated_report: ReportSummaryResponse | null;
  progress: AssessmentProgress;
};

export type ReportContextResponse = {
  assessment_id: string;
  company_input: AssessmentInputSnapshot;
  company_profile: CompanyProfileResult;
  canvas_diagnosis: CanvasDiagnosisResult;
  top_scenarios: ScenarioRecommendationItem[];
  report_outline: string[];
};
