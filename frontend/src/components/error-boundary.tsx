"use client";

import type { ReactNode } from "react";
import { Component as ReactComponent } from "react";

type Props = { children: ReactNode; fallback?: ReactNode };
type State = { hasError: boolean; error: Error | null };

export class ErrorBoundary extends ReactComponent<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div className="rounded-xl msg-error p-6 text-sm">
          <p className="font-semibold">组件渲染异常</p>
          <p className="mt-2 opacity-85">{this.state.error?.message ?? "未知错误"}</p>
          <button
            type="button"
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-4 btn-secondary text-xs"
          >
            重试
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export function CollapsibleSection({
  title,
  subtitle,
  defaultOpen = true,
  children,
}: {
  title: string;
  subtitle?: string;
  defaultOpen?: boolean;
  children: ReactNode;
}) {
  return (
    <details open={defaultOpen} className="group">
      <summary className="flex cursor-pointer items-center gap-3 rounded-xl border border-warm-border bg-warm-surface px-4 py-3 transition hover:border-warm-accent/30 list-none">
        <svg
          className="h-4 w-4 flex-shrink-0 text-warm-muted transition-transform group-open:rotate-90"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <div>
          <p className="text-sm font-medium text-warm-text">{title}</p>
          {subtitle ? <p className="text-xs text-warm-muted">{subtitle}</p> : null}
        </div>
      </summary>
      <div className="mt-3">{children}</div>
    </details>
  );
}
