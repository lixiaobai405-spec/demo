import type {
  AssessmentCreateRequest,
  IntakeSessionDetailResponse,
} from "@/lib/types";
import { ApiError } from "@/lib/api";

export const intakeFieldDefinitions: Array<{
  key: keyof AssessmentCreateRequest;
  label: string;
  inputType: "input" | "textarea";
  required?: boolean;
}> = [
  { key: "company_name", label: "企业名称", inputType: "input", required: true },
  { key: "industry", label: "所属行业", inputType: "input", required: true },
  { key: "company_size", label: "企业规模", inputType: "input", required: true },
  { key: "region", label: "所在区域", inputType: "input", required: true },
  { key: "annual_revenue_range", label: "年营收范围", inputType: "input", required: true },
  { key: "core_products", label: "核心产品/服务", inputType: "textarea", required: true },
  { key: "target_customers", label: "目标客户", inputType: "textarea", required: true },
  { key: "current_challenges", label: "当前经营/管理挑战", inputType: "textarea", required: true },
  { key: "ai_goals", label: "希望通过 AI 达成的目标", inputType: "textarea", required: true },
  { key: "available_data", label: "当前可用数据/系统基础", inputType: "textarea", required: true },
  { key: "notes", label: "其他补充说明", inputType: "textarea" },
];

export const sourceTypeLabels: Record<string, string> = {
  text: "纯文本",
  markdown: "Markdown",
  form: "结构化表单",
  file: "文件上传",
};

export const maxUploadSizeBytes = 10 * 1024 * 1024;
export const allowedUploadExtensions = [".txt", ".md", ".markdown", ".pdf", ".docx"];

export const emptyConfirmedForm: AssessmentCreateRequest = {
  company_name: "", industry: "", company_size: "", region: "",
  annual_revenue_range: "", core_products: "", target_customers: "",
  current_challenges: "", ai_goals: "", available_data: "", notes: "",
};

export function normalizeFieldValue(value: string | null | undefined): string {
  return (value ?? "").trim();
}

export function buildConfirmedForm(
  detail: IntakeSessionDetailResponse,
): AssessmentCreateRequest {
  return {
    company_name: detail.assessment_prefill.company_name ?? "",
    industry: detail.assessment_prefill.industry ?? "",
    company_size: detail.assessment_prefill.company_size ?? "",
    region: detail.assessment_prefill.region ?? "",
    annual_revenue_range: detail.assessment_prefill.annual_revenue_range ?? "",
    core_products: detail.assessment_prefill.core_products ?? "",
    target_customers: detail.assessment_prefill.target_customers ?? "",
    current_challenges: detail.assessment_prefill.current_challenges ?? "",
    ai_goals: detail.assessment_prefill.ai_goals ?? "",
    available_data: detail.assessment_prefill.available_data ?? "",
    notes: detail.assessment_prefill.notes ?? "",
  };
}

export function buildStructuredFieldPayload(
  fields: AssessmentCreateRequest,
): Partial<Record<keyof AssessmentCreateRequest, string>> {
  const entries = intakeFieldDefinitions.flatMap(({ key }) => {
    const value = normalizeFieldValue(fields[key]);
    return value ? [[key, value] as const] : [];
  });
  return Object.fromEntries(entries);
}

export function formatFileSize(sizeBytes: number): string {
  if (sizeBytes < 1024) return `${sizeBytes} B`;
  if (sizeBytes < 1024 * 1024) return `${(sizeBytes / 1024).toFixed(1)} KB`;
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function validateUploadFile(file: File): string | null {
  const fileName = file.name.toLowerCase();
  const isAllowed = allowedUploadExtensions.some((ext) => fileName.endsWith(ext));
  if (!isAllowed) return "文件类型不支持，请选择 txt、md、markdown、pdf 或 docx 文件。";
  if (file.size === 0) return "上传文件为空，请重新选择。";
  if (file.size > maxUploadSizeBytes)
    return `文件过大，当前文件为 ${formatFileSize(file.size)}，请控制在 ${formatFileSize(maxUploadSizeBytes)} 以内。`;
  return null;
}

export function getUploadStageLabel(stage: string): string {
  switch (stage) {
    case "validating": return "文件校验完成，等待上传";
    case "uploading": return "正在上传到后端";
    case "parsing": return "后端正在提取文本并解析";
    case "completed": return "解析完成";
    default: return "尚未开始";
  }
}

export function getUploadStageButtonLabel(stage: string): string {
  switch (stage) {
    case "uploading": return "上传中...";
    case "parsing": return "解析中...";
    default: return "处理中...";
  }
}

export function formatImportError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 413)
      return typeof error.message === "string" && error.message.trim()
        ? error.message
        : "上传文件超过大小限制，请压缩后重试。";
    if (error.status === 415) return "文件类型不支持，请上传 txt、md、markdown、pdf 或 docx 文件。";
    if (error.status === 422)
      return typeof error.message === "string" && error.message.trim()
        ? error.message
        : "文件解析失败，请确认内容清晰可读或改用文本粘贴。";
  }
  return error instanceof Error ? error.message : "导入解析失败，请稍后重试。";
}

export function countConfirmedFields(form: AssessmentCreateRequest): number {
  return intakeFieldDefinitions.filter(({ key }) => {
    const value = form[key];
    return typeof value === "string" && value.trim().length > 0;
  }).length;
}

export function countModifiedFields(
  confirmedForm: AssessmentCreateRequest,
  originalForm: AssessmentCreateRequest,
): number {
  return intakeFieldDefinitions.filter(
    ({ key }) =>
      normalizeFieldValue(confirmedForm[key]) !== normalizeFieldValue(originalForm[key]),
  ).length;
}
