import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import type { AssessmentCardItem } from "@/lib/types";

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

export function AssessmentCard({ item }: { item: AssessmentCardItem }) {
  return (
    <Link href={`/assessment/${item.id}`} className="block card card-clickable group">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="font-heading text-lg font-semibold text-warm-text truncate group-hover:text-primary transition-colors">
            {item.company_name || "未命名企业"}
          </h3>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            <Badge variant="muted">{item.industry || "未分类"}</Badge>
            <span className="text-xs text-muted-foreground">{item.company_size}</span>
          </div>
        </div>
        <span className="text-xs text-muted-foreground whitespace-nowrap">
          {fmtDate(item.created_at)}
        </span>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <StatusDot done={item.has_profile} label="画像" />
        <StatusDot done={item.has_report} label="报告" />
      </div>
    </Link>
  );
}

function StatusDot({ done, label }: { done: boolean; label: string }) {
  return (
    <span className={`inline-flex items-center gap-1 text-xs rounded-full px-2 py-0.5 ${
      done
        ? "bg-[rgba(107,154,74,0.08)] text-[#6B9A4A] border border-[rgba(107,154,74,0.18)]"
        : "bg-[rgba(107,95,80,0.04)] text-muted-foreground border border-warm-border-light"
    }`}>
      <span className={`inline-block w-1.5 h-1.5 rounded-full ${done ? "bg-[#6B9A4A]" : "bg-muted-foreground"}`} aria-hidden="true" />
      {label}
    </span>
  );
}
