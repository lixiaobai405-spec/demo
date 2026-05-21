"use client";

import React, { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";

export function GeneratedJsonEditor({
  title,
  description,
  value,
  isSaving,
  onSave,
  isEditing: controlledIsEditing,
  onEditingChange,
  showToggleButton = true,
  defaultEditing = false,
}: {
  title: string;
  description: string;
  value: unknown;
  isSaving?: boolean;
  onSave: (payload: unknown) => Promise<void> | void;
  isEditing?: boolean;
  onEditingChange?: (next: boolean) => void;
  showToggleButton?: boolean;
  defaultEditing?: boolean;
}) {
  const formattedValue = useMemo(() => JSON.stringify(value, null, 2), [value]);
  const [internalIsEditing, setInternalIsEditing] = useState(defaultEditing);
  const [draft, setDraft] = useState(formattedValue);
  const [parseError, setParseError] = useState<string | null>(null);
  const isEditing = controlledIsEditing ?? internalIsEditing;

  function setEditing(next: boolean) {
    onEditingChange?.(next);
    if (controlledIsEditing === undefined) {
      setInternalIsEditing(next);
    }
  }

  useEffect(() => {
    if (!isEditing) {
      setDraft(formattedValue);
      setParseError(null);
    }
  }, [formattedValue, isEditing]);

  async function handleSave() {
    try {
      const parsed = JSON.parse(draft);
      setParseError(null);
      await onSave(parsed);
      setEditing(false);
    } catch (error) {
      if (error instanceof SyntaxError) {
        setParseError(`JSON 解析失败：${error.message}`);
        return;
      }
      throw error;
    }
  }

  return (
    <section className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">手动修订</p>
          <h2 className="section-heading">{title}</h2>
          <p className="mt-2 text-sm leading-7 text-warm-secondary">
            {description}
          </p>
        </div>
        {showToggleButton ? (
          <Button
            variant={isEditing ? "default" : "outline"}
            size="sm"
            onClick={() => setEditing(!isEditing)}
          >
            {isEditing ? "收起编辑器" : "编辑生成结果"}
          </Button>
        ) : null}
      </div>

      {isEditing ? (
        <div className="mt-6 space-y-4">
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            className="input-field min-h-[420px] font-mono text-xs leading-6"
            spellCheck={false}
          />
          <div className="rounded-xl border border-warm-warning/20 bg-warm-warning/5 p-4 text-sm leading-7 text-warm-secondary">
            保存后，下游结论会按依赖链自动失效，需要重新生成。
          </div>
          {parseError ? (
            <div className="rounded-xl p-4 text-sm msg-error">{parseError}</div>
          ) : null}
          <div className="flex flex-wrap gap-3">
            <Button onClick={handleSave} loading={isSaving} disabled={isSaving}>
              {isSaving ? "保存中..." : "保存修改"}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setDraft(formattedValue);
                setParseError(null);
                setEditing(false);
              }}
            >
              取消
            </Button>
          </div>
        </div>
      ) : null}
    </section>
  );
}
