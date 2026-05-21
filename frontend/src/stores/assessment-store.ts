import { create } from "zustand";
import type {
  AssessmentBreakthroughResponse,
  AssessmentDirectionResponse,
  AssessmentResponse,
  BreakthroughSelectionResponse,
  CanvasDiagnosisResult,
  CaseRecommendationResult,
  CompanyProfileResult,
  CompetitivenessResponse,
  DirectionSelectionResponse,
  EndgameResponse,
  FollowUpPlan,
  ScenarioRecommendationResult,
} from "@/lib/types";

interface AssessmentState {
  // Current assessment
  assessment: AssessmentResponse | null;
  assessmentId: string | null;

  // Generated results
  companyProfile: CompanyProfileResult | null;
  profileMode: "mock" | "live" | null;
  canvasDiagnosis: CanvasDiagnosisResult | null;
  breakthroughData: AssessmentBreakthroughResponse | null;
  breakthroughSelection: BreakthroughSelectionResponse | null;
  scenarioRecommendation: ScenarioRecommendationResult | null;
  directionData: AssessmentDirectionResponse | null;
  directionSelection: DirectionSelectionResponse | null;
  competitivenessData: CompetitivenessResponse | null;
  endgameData: EndgameResponse | null;
  followUpPlan: FollowUpPlan | null;

  // Selection
  selectedBreakthroughKeys: string[];
  selectedDirectionIds: string[];

  // Actions
  setAssessment: (a: AssessmentResponse | null) => void;
  setCompanyProfile: (p: CompanyProfileResult | null) => void;
  setProfileMode: (m: "mock" | "live" | null) => void;
  setCanvasDiagnosis: (d: CanvasDiagnosisResult | null) => void;
  setBreakthroughData: (d: AssessmentBreakthroughResponse | null) => void;
  setBreakthroughSelection: (s: BreakthroughSelectionResponse | null) => void;
  setScenarioRecommendation: (r: ScenarioRecommendationResult | null) => void;
  setDirectionData: (d: AssessmentDirectionResponse | null) => void;
  setDirectionSelection: (s: DirectionSelectionResponse | null) => void;
  setCompetitivenessData: (d: CompetitivenessResponse | null) => void;
  setEndgameData: (d: EndgameResponse | null) => void;
  setFollowUpPlan: (p: FollowUpPlan | null) => void;
  setSelectedBreakthroughKeys: (keys: string[]) => void;
  toggleBreakthroughKey: (key: string) => void;
  setSelectedDirectionIds: (ids: string[]) => void;
  toggleDirectionId: (id: string) => void;

  // Cascade reset
  resetDownstream: (fromStep: string) => void;
  resetAll: () => void;
}

export const useAssessmentStore = create<AssessmentState>((set, get) => ({
  assessment: null,
  assessmentId: null,
  companyProfile: null,
  profileMode: null,
  canvasDiagnosis: null,
  breakthroughData: null,
  breakthroughSelection: null,
  scenarioRecommendation: null,
  directionData: null,
  directionSelection: null,
  competitivenessData: null,
  endgameData: null,
  caseRecommendation: null,
  followUpPlan: null,
  selectedBreakthroughKeys: [],
  selectedDirectionIds: [],

  setAssessment: (a) => set({ assessment: a, assessmentId: a?.id ?? null }),
  setCompanyProfile: (p) => set({ companyProfile: p }),
  setProfileMode: (m) => set({ profileMode: m }),
  setCanvasDiagnosis: (d) => set({ canvasDiagnosis: d }),
  setBreakthroughData: (d) => set({ breakthroughData: d }),
  setBreakthroughSelection: (s) => set({ breakthroughSelection: s }),
  setScenarioRecommendation: (r) => set({ scenarioRecommendation: r }),
  setDirectionData: (d) => set({ directionData: d }),
  setDirectionSelection: (s) => set({ directionSelection: s }),
  setCompetitivenessData: (d) => set({ competitivenessData: d }),
  setEndgameData: (d) => set({ endgameData: d }),
  setFollowUpPlan: (p) => set({ followUpPlan: p }),
  setSelectedBreakthroughKeys: (keys) => set({ selectedBreakthroughKeys: keys }),
  toggleBreakthroughKey: (key) =>
    set((s) => {
      if (s.selectedBreakthroughKeys.includes(key)) {
        return { selectedBreakthroughKeys: s.selectedBreakthroughKeys.filter((k) => k !== key) };
      }
      if (s.selectedBreakthroughKeys.length >= 3) return s;
      return { selectedBreakthroughKeys: [...s.selectedBreakthroughKeys, key] };
    }),
  setSelectedDirectionIds: (ids) => set({ selectedDirectionIds: ids }),
  toggleDirectionId: (id) =>
    set((s) => {
      if (s.selectedDirectionIds.includes(id)) {
        return { selectedDirectionIds: s.selectedDirectionIds.filter((d) => d !== id) };
      }
      if (s.selectedDirectionIds.length >= 6) return s;
      return { selectedDirectionIds: [...s.selectedDirectionIds, id] };
    }),

  resetDownstream: (fromStep) => {
    const steps = ["profile", "canvas", "breakthrough", "directions", "scenarios", "competitiveness", "endgame"];
    const fromIdx = steps.indexOf(fromStep);
    if (fromIdx === -1) return;

    const reset: Partial<AssessmentState> = {};
    for (let i = fromIdx + 1; i < steps.length; i++) {
      const step = steps[i];
      switch (step) {
        case "canvas":
          reset.canvasDiagnosis = null;
          break;
        case "breakthrough":
          reset.breakthroughData = null;
          reset.breakthroughSelection = null;
          reset.selectedBreakthroughKeys = [];
          break;
        case "directions":
          reset.directionData = null;
          reset.directionSelection = null;
          reset.selectedDirectionIds = [];
          break;
        case "competitiveness":
          reset.competitivenessData = null;
          break;
        case "endgame":
          reset.endgameData = null;
          break;
        case "scenarios":
          reset.scenarioRecommendation = null;
          break;
      }
    }
    set(reset);
  },

  resetAll: () =>
    set({
      assessment: null,
      assessmentId: null,
      companyProfile: null,
      profileMode: null,
      canvasDiagnosis: null,
      breakthroughData: null,
      breakthroughSelection: null,
      scenarioRecommendation: null,
      directionData: null,
      directionSelection: null,
      competitivenessData: null,
      endgameData: null,
      followUpPlan: null,
      selectedBreakthroughKeys: [],
      selectedDirectionIds: [],
    }),
}));
