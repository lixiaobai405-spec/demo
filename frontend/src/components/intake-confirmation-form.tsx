"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useIntakeStore } from "@/stores/intake-store";
import { useIntakeSession, useCreateAssessmentFromIntake } from "@/hooks";
import { toast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  intakeFieldDefinitions,
  normalizeFieldValue,
  buildConfirmedForm,
  countConfirmedFields,
  countModifiedFields,
  emptyConfirmedForm,
} from "@/lib/intake-utils";

export function IntakeConfirmationForm() {
  const router = useRouter();
  const store = useIntakeStore();
  const sessionQuery = useIntakeSession(store.importSessionId);
  const createAssessmentMutation = useCreateAssessmentFromIntake();

  const sessionDetail = sessionQuery.data;

  const [confirmedForm, setConfirmedForm] = useState(emptyConfirmedForm);

  useEffect(() => {
    if (sessionDetail) {
      setConfirmedForm(buildConfirmedForm(sessionDetail));
    }
  }, [sessionDetail]);

  const confirmedCount = useMemo(() => countConfirmedFields(confirmedForm), [confirmedForm]);

  const modifiedCount = useMemo(() => {
    if (!sessionDetail) return 0;
    const original = buildConfirmedForm(sessionDetail);
    return countModifiedFields(confirmedForm, original);
  }, [confirmedForm, sessionDetail]);

  const handleContinueToAssessment = () => {
    if (!sessionDetail) return;
    if (sessionDetail.created_assessment_id) {
      router.push(`/assessment/${sessionDetail.created_assessment_id}`);
      return;
    }
    router.push(`/assessment?import_session_id=${encodeURIComponent(sessionDetail.import_session_id)}`);
  };

  const handleCreateAssessment = useCallback(
    async (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      if (!sessionDetail) {
        toast({ title: "请先完成导入", description: "请先完成导入或加载一个导入会话。", variant: "destructive" });
        return;
      }
      if (sessionDetail.created_assessment_id) {
        router.push(`/assessment/${sessionDetail.created_assessment_id}`);
        return;
      }
      try {
        const result = await createAssessmentMutation.mutateAsync({
          sessionId: sessionDetail.import_session_id,
          payload: {
            confirmed_assessment_input: {
              ...confirmedForm,
              notes: (confirmedForm.notes ?? "").trim() || null,
            },
          },
        });
        toast({ title: "问卷已创建", description: `ID: ${result.assessment.id}`, variant: "success" });
        router.push(`/assessment/${result.assessment.id}`);
      } catch (error) {
        toast({
          title: "创建失败",
          description: error instanceof Error ? error.message : "创建问卷失败，请稍后重试。",
          variant: "destructive",
        });
      }
    },
    [sessionDetail, confirmedForm, createAssessmentMutation, router],
  );

  const isCreating = createAssessmentMutation.isPending;

  return (
    <div className="card-inset">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">步骤三</p>
          <h2 className="section-heading">确认并创建问卷</h2>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            你可以在这里修改系统预填建议。所有字段都允许手动覆盖；
            即使还没补齐，也可以先带入企业问卷继续补录，或直接保存当前部分结果。
          </p>
        </div>
        <Badge variant="accent">
          已确认 {confirmedCount} / {intakeFieldDefinitions.length} 项
        </Badge>
      </div>

      {sessionDetail ? (
        <div className="mt-4 flex flex-wrap gap-2 text-xs">
          <Badge variant="success">已修改 {modifiedCount} 项</Badge>
          <Badge variant="muted">沿用建议 {intakeFieldDefinitions.length - modifiedCount} 项</Badge>
        </div>
      ) : null}

      {sessionQuery.isLoading ? (
        <div className="mt-6 space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-20 rounded-xl" />
          ))}
        </div>
      ) : sessionDetail ? (
        <form onSubmit={handleCreateAssessment} className="mt-6 space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {intakeFieldDefinitions.map(({ key, label, inputType, required }) => {
              const value = (confirmedForm[key] ?? "") as string;
              const meta = sessionDetail.field_meta[key];
              const originalValue = buildConfirmedForm(sessionDetail)[key];
              const isModified = normalizeFieldValue(value) !== normalizeFieldValue(originalValue);
              const fieldNote =
                meta?.status === "needs_user_confirmation"
                  ? "系统推断，请重点确认"
                  : meta?.status === "needs_user_input"
                    ? "系统未识别，请手动补充"
                    : "已从原文识别";

              return (
                <label key={key} className="flex flex-col gap-3 text-sm">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-medium">
                        {label}
                        {required ? <span className="ml-1 text-destructive">*</span> : null}
                      </span>
                      <Badge variant={isModified ? "success" : "muted"}>
                        {isModified ? "已修改" : "沿用建议"}
                      </Badge>
                      {isModified && (
                        <button
                          type="button"
                          onClick={() =>
                            setConfirmedForm((prev) => ({
                              ...prev,
                              [key]: normalizeFieldValue(originalValue),
                            }))
                          }
                          className="text-xs text-primary underline underline-offset-2 hover:text-foreground"
                        >
                          恢复建议值
                        </button>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground">{fieldNote}</span>
                  </div>
                  {inputType === "textarea" ? (
                    <Textarea
                      value={value}
                      onChange={(e) =>
                        setConfirmedForm((prev) => ({ ...prev, [key]: e.target.value }))
                      }
                    />
                  ) : (
                    <Input
                      value={value}
                      onChange={(e) =>
                        setConfirmedForm((prev) => ({ ...prev, [key]: e.target.value }))
                      }
                    />
                  )}
                </label>
              );
            })}
          </div>

          {sessionDetail.created_assessment_id ? (
            <div className="rounded-xl msg-info p-4 text-sm">
              当前导入会话已创建问卷。
              <button
                type="button"
                onClick={() => router.push(`/assessment/${sessionDetail.created_assessment_id}`)}
                className="ml-2 font-medium underline underline-offset-4"
              >
                进入已创建问卷
              </button>
            </div>
          ) : null}

          <div className="flex flex-wrap gap-3">
            <Button type="button" variant="outline" onClick={handleContinueToAssessment}>
              {sessionDetail.created_assessment_id ? "进入已创建问卷" : "带入企业问卷继续补充"}
            </Button>
            <Button
              type="submit"
              variant="success"
              disabled={isCreating || Boolean(sessionDetail.created_assessment_id)}
              loading={isCreating}
            >
              {isCreating ? "创建中..." : "确认并创建问卷"}
            </Button>
          </div>
        </form>
      ) : (
        <p className="mt-6 text-sm leading-6 text-muted-foreground">
          请先完成导入或加载一个已有会话，系统会把预填结果带入这里供你修改确认。
        </p>
      )}
    </div>
  );
}

