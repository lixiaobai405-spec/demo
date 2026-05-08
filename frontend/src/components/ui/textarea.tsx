import { cn } from "@/lib/utils";
import * as React from "react";

const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        "flex min-h-[7rem] w-full rounded-xl border border-input bg-card px-4 py-3 text-sm font-body text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:border-primary focus-visible:ring-[3px] focus-visible:ring-[rgba(212,168,83,0.10)] disabled:cursor-not-allowed disabled:opacity-50 resize-y transition-colors",
        className,
      )}
      ref={ref}
      {...props}
    />
  );
});
Textarea.displayName = "Textarea";

export { Textarea };
