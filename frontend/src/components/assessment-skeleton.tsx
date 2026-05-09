"use client";

import { Skeleton } from "@/components/ui/skeleton";

export function AssessmentSkeleton() {
  return (
    <div className="flex flex-col gap-6">
      {/* Progress stepper */}
      <Skeleton className="h-16 w-full rounded-xl" />

      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        {/* Form skeleton */}
        <div className="rounded-xl border bg-card p-6 space-y-6">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-32" />
          <div className="grid gap-6 md:grid-cols-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-12 w-full" />
              </div>
            ))}
          </div>
          <div className="grid gap-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-28 w-full" />
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar skeleton */}
        <div className="flex flex-col gap-6">
          <div className="rounded-xl border bg-card p-6 space-y-4">
            <Skeleton className="h-5 w-24" />
            <Skeleton className="h-6 w-32" />
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-full rounded-xl" />
            ))}
          </div>
          <div className="rounded-xl border bg-card p-6 space-y-3">
            <Skeleton className="h-5 w-16" />
            <Skeleton className="h-6 w-20" />
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full rounded-full" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
