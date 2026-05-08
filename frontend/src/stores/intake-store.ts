import { create } from "zustand";
import type { AssessmentCreateRequest, IntakeSourceType } from "@/lib/types";
import { emptyConfirmedForm } from "@/lib/intake-utils";

export type UploadStage =
  | "idle"
  | "validating"
  | "uploading"
  | "parsing"
  | "completed";

interface IntakeState {
  // Input
  sourceType: IntakeSourceType;
  rawContent: string;
  selectedFileName: string | null;
  selectedUploadFile: File | null;
  sessionIdInput: string;
  uploadStage: UploadStage;
  showSessionRecall: boolean;

  // Structured form fields
  structuredFields: AssessmentCreateRequest;

  // Session result
  importSessionId: string | null;

  // Loading flags (UI-only; server state is in React Query)
  isImporting: boolean;

  // Actions
  setSourceType: (t: IntakeSourceType) => void;
  setRawContent: (c: string) => void;
  setSelectedFile: (file: File | null, name: string | null) => void;
  setSessionIdInput: (id: string) => void;
  setUploadStage: (stage: UploadStage) => void;
  setShowSessionRecall: (show: boolean) => void;
  updateStructuredField: (key: keyof AssessmentCreateRequest, value: string) => void;
  setImportSessionId: (id: string | null) => void;
  setIsImporting: (v: boolean) => void;
  resetImportState: () => void;
}

export const useIntakeStore = create<IntakeState>((set) => ({
  sourceType: "markdown",
  rawContent: `企业名称：测试连锁零售企业
所属行业：零售
企业规模：100-499人
所在区域：华东
核心产品/服务：社区零售门店、会员运营与到家服务
目标客户：社区家庭用户、周边白领与会员客户
希望通过 AI 达成的目标：提升门店运营效率，增强会员复购
当前可用数据/系统基础：POS、会员系统、商品主数据`,
  selectedFileName: null,
  selectedUploadFile: null,
  sessionIdInput: "",
  structuredFields: { ...emptyConfirmedForm },
  uploadStage: "idle",
  showSessionRecall: false,
  importSessionId: null,
  isImporting: false,

  setSourceType: (t) =>
    set((s) => ({
      sourceType: t,
      selectedUploadFile: t !== "file" ? null : s.selectedUploadFile,
      selectedFileName: t !== "file" ? null : s.selectedFileName,
      uploadStage: t !== "file" ? "idle" : s.uploadStage,
    })),
  setRawContent: (c) => set({ rawContent: c }),
  setSelectedFile: (file, name) =>
    set({ selectedUploadFile: file, selectedFileName: name }),
  setSessionIdInput: (id) => set({ sessionIdInput: id }),
  setUploadStage: (stage) => set({ uploadStage: stage }),
  setShowSessionRecall: (show) => set({ showSessionRecall: show }),
  updateStructuredField: (key, value) =>
    set((s) => ({ structuredFields: { ...s.structuredFields, [key]: value } })),
  setImportSessionId: (id) => set({ importSessionId: id }),
  setIsImporting: (v) => set({ isImporting: v }),
  resetImportState: () =>
    set({
      sourceType: "markdown",
      rawContent: "",
      selectedFileName: null,
      selectedUploadFile: null,
      uploadStage: "idle",
      importSessionId: null,
      isImporting: false,
    }),
}));
