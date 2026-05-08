import { Skeleton } from "@/components/ui/skeleton";

export default function IntakeLoading() {
  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8">
        <div className="page-header">
          <Skeleton className="h-6 w-32" />
          <Skeleton className="mt-4 h-10 w-64" />
          <Skeleton className="mt-3 h-5 w-96" />
        </div>
        <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <div className="flex flex-col gap-6">
            <Skeleton className="h-96 rounded-xl" />
            <Skeleton className="h-48 rounded-xl" />
          </div>
          <div className="flex flex-col gap-6">
            <Skeleton className="h-80 rounded-xl" />
            <Skeleton className="h-96 rounded-xl" />
          </div>
        </div>
      </div>
    </main>
  );
}
