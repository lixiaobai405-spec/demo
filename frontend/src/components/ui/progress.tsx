import { cn } from "@/lib/utils";
import * as React from "react";

const Progress = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { value?: number; max?: number }
>(({ className, value = 0, max = 100, ...props }, ref) => {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div
      ref={ref}
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={max}
      aria-valuenow={value}
      className={cn(
        "relative h-3 w-full overflow-hidden rounded-full bg-secondary",
        className,
      )}
      {...props}
    >
      <div
        className="h-full rounded-full bg-primary transition-all duration-500 ease-out"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
});
Progress.displayName = "Progress";

export { Progress };
