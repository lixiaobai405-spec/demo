"use client";

import { useEffect, useMemo, useRef } from "react";
import { useRouter } from "next/navigation";
import { useIntakeStore } from "@/stores/intake-store";
import { useIntakeSession } from "@/hooks";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { IntakeFieldCard } from "@/components/intake-field-card";
import { intakeFieldDefinitions } from "@/lib/intake-utils";

export function IntakePrefillDisplay() {
  const router = useRouter();
  const store = useIntakeStore();
  const sessionQuery = useIntakeSession(store.importSessionId);
  const prefillRef = useRef<HTMLDivElement>(null);

  const sessionDetail = sessionQuery.data;

  const completedCount = useMemo(() => {
    if (!sessionDetail) return 0;
    return intakeFieldDefinitions.filter(({ key }) => {
      const value = sessionDetail.assessment_prefill[key];
      return typeof value === "string" && value.trim().length > 0;
    }).length;
  }, [sessionDetail]);

  useEffect(() => {
    if (sessionDetail && prefillRef.current) {
      prefillRef.current.scrollIntoView?.({ behavior: "smooth", block: "start" });
    }
  }, [sessionDetail]);

  const handleContinueToAssessment = () => {
    if (!sessionDetail) return;
    if (sessionDetail.created_assessment_id) {
      router.push(`/assessment/${sessionDetail.created_assessment_id}`);
      return;
    }
    router.push(`/assessment?import_session_id=${encodeURIComponent(sessionDetail.import_session_id)}`);
  };

  return (
    <div className="card" ref={prefillRef}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">步骤二</p>
          <h2 className="section-heading">问卷预填建议</h2>
        </div>
        {sessionDetail ? (
          <Button variant="outline" size="sm" onClick={handleContinueToAssessment}>
            {sessionDetail.created_assessment_id ? "进入已创建问卷" : "带入企业问卷继续补充"}
          </Button>
        ) : null}
      </div>

      {sessionQuery.isLoading ? (
        <div className="mt-5 space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))}
        </div>
      ) : sessionDetail ? (
        <div className="mt-5 space-y-6">
          {sessionDetail.warnings.length > 0 ? (
            <div className="rounded-xl msg-warning p-4 text-sm">
              <p className="font-medium">提示信息</p>
              <ul className="mt-3 space-y-2">
                {sessionDetail.warnings.map((warning) => (
                  <li key={warning}>{warning}</li>
                ))}
              </ul>
            </div>
          ) : null}

          <div className="grid gap-4">
            {intakeFieldDefinitions.map(({ key, label }) => {
              const value = sessionDetail.assessment_prefill[key];
              const meta = sessionDetail.field_meta[key];
              const candidate = sessionDetail.field_candidates[key];
              return (
                <IntakeFieldCard
                  key={key}
                  label={label}
                  value={value}
                  meta={meta}
                  candidate={candidate}
                />
              );
            })}
          </div>

          {sessionDetail.unmapped_notes.length > 0 ? (
            <div className="rounded-xl border border-border bg-secondary p-4 text-sm text-muted-foreground">
              <p className="font-medium text-foreground">未映射备注</p>
              <ul className="mt-3 space-y-2">
                {sessionDetail.unmapped_notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : sessionQuery.isError ? (
        <div className="mt-5 rounded-xl msg-error p-4 text-sm">
          {sessionQuery.error instanceof Error ? sessionQuery.error.message : "加载失败"}
        </div>
      ) : (
        <p className="mt-5 text-sm leading-6 text-muted-foreground">
          导入成功后，这里会展示每个问卷字段的预填值、来源标签、确认状态和证据。
        </p>
      )}
    </div>
  );
}
