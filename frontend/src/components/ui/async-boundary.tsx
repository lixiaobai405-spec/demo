"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

type AsyncBoundaryProps = {
  /** Whether data is currently loading */
  isLoading: boolean;
  /** Whether an error occurred */
  isError: boolean;
  /** The error object or message */
  error?: Error | string | null;
  /** Called when user clicks retry */
  onRetry?: () => void;
  /** Custom loading skeleton. Falls back to default. */
  loadingSkeleton?: React.ReactNode;
  /** Custom empty state. Rendered when !isLoading && !isError && !hasData */
  empty?: React.ReactNode;
  /** Optional back-link for error state */
  backLink?: React.ReactNode;
  /** Children (rendered when data is available) */
  children: React.ReactNode;
  /** Whether data is present (controls the empty state) */
  hasData?: boolean;
  className?: string;
};

/**
 * Generic async boundary — handles Loading / Error / Empty / Success states
 * in a consistent way across all data-fetching components.
 *
 * States:
 * - Loading:  renders loadingSkeleton (or default Skeleton)
 * - Error:    error message + retry button + optional back link
 * - Empty:    empty state placeholder
 * - Success:  renders children
 */
export function AsyncBoundary({
  isLoading,
  isError,
  error,
  onRetry,
  loadingSkeleton,
  empty,
  backLink,
  children,
  hasData = true,
  className,
}: AsyncBoundaryProps) {
  // Loading
  if (isLoading) {
    if (loadingSkeleton) return <>{loadingSkeleton}</>;
    return (
      <div className={cn("space-y-4", className)}>
        <Skeleton className="h-8 w-1/3 rounded-xl" />
        <Skeleton className="h-6 w-1/2 rounded-xl" />
        <Skeleton className="h-48 w-full rounded-xl" />
        <Skeleton className="h-48 w-full rounded-xl" />
      </div>
    );
  }

  // Error
  if (isError) {
    const message =
      typeof error === "string"
        ? error
        : error instanceof Error
          ? error.message
          : "加载失败，请稍后重试。";

    return (
      <div className="rounded-xl msg-error p-6 text-sm space-y-4">
        <div>
          <p className="font-medium">加载失败</p>
          <p className="mt-2 opacity-90">{message}</p>
        </div>
        <div className="flex flex-wrap gap-3">
          {onRetry && (
            <Button variant="outline" size="sm" onClick={onRetry}>
              重试加载
            </Button>
          )}
          {backLink}
        </div>
      </div>
    );
  }

  // Empty
  if (!hasData) {
    if (empty) return <>{empty}</>;
    return (
      <div className="rounded-xl border border-dashed border-border bg-secondary p-8 text-center">
        <p className="text-sm text-muted-foreground">暂无数据</p>
      </div>
    );
  }

  // Success
  return <>{children}</>;
}
