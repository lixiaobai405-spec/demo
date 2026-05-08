import { z } from "zod";

export const assessmentFormSchema = z.object({
  company_name: z.string().min(1, "请填写企业名称"),
  industry: z.string().min(1, "请填写所属行业"),
  company_size: z.string().min(1, "请选择企业规模"),
  region: z.string().min(1, "请填写所在区域"),
  annual_revenue_range: z.string().min(1, "请选择年营收范围"),
  core_products: z.string().min(1, "请填写核心产品/服务"),
  target_customers: z.string().min(1, "请填写目标客户"),
  current_challenges: z.string().min(1, "请填写当前经营/管理挑战"),
  ai_goals: z.string().min(1, "请填写希望通过 AI 达成的目标"),
  available_data: z.string().min(1, "请填写可用数据/系统基础"),
  notes: z.string().optional(),
});

export type AssessmentFormValues = z.infer<typeof assessmentFormSchema>;

export const intakeStructuredSchema = assessmentFormSchema.partial();

export const intakeConfirmationSchema = assessmentFormSchema;
