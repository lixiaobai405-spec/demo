import { cn } from "@/lib/utils";
import { type VariantProps, cva } from "class-variance-authority";
import * as React from "react";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-full text-sm font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none font-body shadow-sm",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_2px_8px_rgba(212,168,83,0.22)]",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline:
          "border border-input bg-transparent text-muted-foreground hover:bg-accent hover:text-accent-foreground shadow-none",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80 shadow-none",
        ghost:
          "hover:bg-accent hover:text-accent-foreground shadow-none",
        link: "text-primary underline-offset-4 hover:underline shadow-none",
        success:
          "bg-[#6B9A4A] text-white hover:brightness-90",
      },
      size: {
        default: "h-12 px-6 py-3",
        sm: "h-9 rounded-full px-4 text-xs",
        lg: "h-14 rounded-full px-8 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  /**
   * 渲染统一按钮，并在 loading 态下保持视觉高亮而不是降灰。
   */
  ({ className, variant, size, loading, children, disabled, ...props }, ref) => {
    const isSemanticallyDisabled = disabled || loading;

    return (
      <button
        className={cn(
          buttonVariants({ variant, size }),
          disabled && !loading ? "opacity-50" : "",
          isSemanticallyDisabled ? "pointer-events-none" : "",
          className,
        )}
        ref={ref}
        disabled={disabled}
        aria-busy={loading || undefined}
        aria-disabled={isSemanticallyDisabled || undefined}
        {...props}
      >
        {loading ? (
          <>
            <svg
              className="mr-2 h-4 w-4 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            {children ?? "处理中..."}
          </>
        ) : (
          children
        )}
      </button>
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
