import { ScenariosPageContent } from "@/components/scenarios-page-content";

/**
 * 独立承载 AI 场景推荐结果，并将取数下沉到客户端以复用本地登录态。
 */
export default async function ScenariosPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = await params;
  return <ScenariosPageContent assessmentId={assessmentId} />;
}
