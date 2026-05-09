import { AssessmentSkeleton } from "@/components/assessment-skeleton";

export default function AssessmentDetailLoading() {
  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto max-w-7xl">
        <AssessmentSkeleton />
      </div>
    </main>
  );
}
