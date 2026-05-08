"use client";

import Link from "next/link";
import { useIntakeStore } from "@/stores/intake-store";
import { useIntakeSession } from "@/hooks";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import {
  intakeFieldDefinitions,
  sourceTypeLabels,
  formatFileSize,
} from "@/lib/intake-utils";

export function IntakeSessionRecall() {
  const store = useIntakeStore();
  const sessionQuery = useIntakeSession(store.sessionIdInput || null);

  const completedCount = sessionQuery.data
    ? intakeFieldDefinitions.filter(({ key }) => {
        const value = sessionQuery.data.assessment_prefill[key];
        return typeof value === "string" && value.trim().length > 0;
      }).length
    : 0;

  return (
    <div className="card-inset">
      <button
        type="button"
        onClick={() => store.setShowSessionRecall(!store.showSessionRecall)}
        className="flex w-full items-center justify-between text-left"
      >
        <div>
          <p className="section-label">辅助功能</p>
          <h2 className="section-heading">回看导入会话</h2>
        </div>
        <span
          className="text-sm text-muted-foreground transition-transform"
          style={{ transform: store.showSessionRecall ? "rotate(90deg)" : "rotate(0deg)" }}
        >
          ▶
        </span>
      </button>

      {store.showSessionRecall && (
        <div className="mt-4">
          <p className="text-sm leading-6 text-muted-foreground">
            输入 import_session_id 可重新加载导入结果和已确认表单，方便刷新后继续处理。
          </p>

          <div className="mt-4 flex flex-col gap-3 sm:flex-row">
            <Input
              value={store.sessionIdInput}
              onChange={(e) => store.setSessionIdInput(e.target.value)}
              placeholder="请输入 import_session_id"
              className="flex-1"
            />
            <Button
              type="button"
              variant="outline"
              onClick={() => store.setImportSessionId(store.sessionIdInput)}
              disabled={sessionQuery.isLoading}
            >
              {sessionQuery.isLoading ? "加载中..." : "加载会话"}
            </Button>
          </div>

          {sessionQuery.isError ? (
            <div className="mt-4 rounded-xl msg-error p-4 text-sm">
              {sessionQuery.error instanceof Error ? sessionQuery.error.message : "导入会话加载失败"}
            </div>
          ) : null}

          {sessionQuery.data ? (
            <div className="mt-5 space-y-2 text-sm text-muted-foreground">
              <p>会话 ID：{sessionQuery.data.import_session_id}</p>
              <p>状态：{sessionQuery.data.status}</p>
              <p>来源类型：{sourceTypeLabels[sessionQuery.data.source_type]}</p>
              {sessionQuery.data.source_file ? (
                <p>源文件：{sessionQuery.data.source_file.name} ({sessionQuery.data.source_file.kind} / {formatFileSize(sessionQuery.data.source_file.size_bytes)})</p>
              ) : null}
              <p>已识别字段：{completedCount} / {intakeFieldDefinitions.length}</p>
              {sessionQuery.data.created_assessment_id ? (
                <p>
                  已创建问卷：
                  <Link href={`/assessment/${sessionQuery.data.created_assessment_id}`} className="ml-1 font-medium text-primary underline underline-offset-4">
                    {sessionQuery.data.created_assessment_id}
                  </Link>
                </p>
              ) : null}
            </div>
          ) : (
            <p className="mt-4 text-sm text-muted-foreground">
              尚未加载导入会话，导入完成后这里会显示持久化的回显结果。
            </p>
          )}
        </div>
      )}
    </div>
  );
}
