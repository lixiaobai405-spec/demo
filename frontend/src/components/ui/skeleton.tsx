import { cn } from "@/lib/utils";
import * as React from "react";

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-xl bg-muted",
        className,
      )}
      {...props}
    />
  );
}

export { Skeleton };
