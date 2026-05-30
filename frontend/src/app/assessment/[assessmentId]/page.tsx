import Link from "next/link";
import { dehydrate, HydrationBoundary, QueryClient } from "@tanstack/react-query";
import { getAssessmentDetail } from "@/lib/api";
import { assessmentKeys } from "@/hooks/use-assessment";
import { AssessmentWorkspace } from "@/components/assessment-workspace";

export function formatShortAssessmentId(assessmentId: string) {
  return assessmentId.slice(0, 8);
}

export default async function AssessmentDetailPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = await params;

  // Server-side prefetch
  const queryClient = new QueryClient();
  try {
    await queryClient.prefetchQuery({
      queryKey: assessmentKeys.detail(assessmentId),
      queryFn: () => getAssessmentDetail(assessmentId),
    });
  } catch {
    // Let the client handle the error
  }

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <main className="min-h-screen px-6 py-10">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 stagger">
          <section className="page-header">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
              <div className="max-w-4xl space-y-4">
                <Link href="/" className="btn-secondary text-xs">
                  ← 返回首页
                </Link>
                <span className="badge badge-accent">
                  Assessment 回看 / 状态恢复
                </span>
                <h1 className="font-heading text-4xl font-bold tracking-tight text-warm-text">
                  主流程工作台
                </h1>
              </div>

              <div className="rounded-xl border border-amber-200 bg-amber-50/70 px-6 py-4 text-sm text-amber-800">
                <p className="font-medium">当前 Assessment</p>
                <p className="mt-2 font-mono text-amber-700/90">
                  {formatShortAssessmentId(assessmentId)}
                </p>
              </div>
            </div>
          </section>

          <AssessmentWorkspace assessmentId={assessmentId} />
        </div>
      </main>
    </HydrationBoundary>
  );
}
