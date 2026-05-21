import { ResultsDashboardPageContent } from "@/components/results-dashboard-page-content";

export default async function ResultsPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = await params;

  return <ResultsDashboardPageContent assessmentId={assessmentId} />;
}
