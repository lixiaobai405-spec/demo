"use client";

import { Badge } from "@/components/ui/badge";
import type {
  AssessmentCreateRequest,
  IntakeFieldCandidate,
  IntakeFieldMeta,
} from "@/lib/types";

const metaStatusLabels: Record<string, string> = {
  confirmed: "已确认",
  needs_user_confirmation: "需要确认",
  needs_user_input: "需要补充",
};

const metaSourceLabels: Record<string, string> = {
  raw: "原文",
  inferred: "推断",
  missing: "缺失",
};

export function IntakeFieldCard({
  label,
  value,
  meta,
  candidate,
}: {
  label: string;
  value: string | undefined | null;
  meta?: IntakeFieldMeta | null;
  candidate?: IntakeFieldCandidate | null;
}) {
  return (
    <div className="rounded-xl border bg-card p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-foreground">{label}</p>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            {value?.trim() ? value : "尚未识别，需用户补充"}
          </p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          <Badge variant="accent">
            来源：{meta ? metaSourceLabels[meta.source_type] ?? "未知" : "未知"}
          </Badge>
          <Badge variant="muted">
            状态：{meta ? metaStatusLabels[meta.status] ?? "未知" : "未知"}
          </Badge>
        </div>
      </div>
      {candidate ? (
        <p className="mt-3 text-xs leading-5 text-muted-foreground">
          证据：{candidate.evidence}
        </p>
      ) : null}
    </div>
  );
}
