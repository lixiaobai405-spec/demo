import { CompetitivenessPageContent } from "@/components/competitiveness-page-content";

/**
 * 独立承载差异化竞争力结果，并将取数下沉到客户端以复用本地登录态。
 */
export default async function CompetitivenessPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = await params;
  return <CompetitivenessPageContent assessmentId={assessmentId} />;
}
