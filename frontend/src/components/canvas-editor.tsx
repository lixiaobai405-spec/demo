"use client";

import { useCallback, useState } from "react";
import type { CanvasDiagnosisResult } from "@/lib/types";
import { updateAssessmentCanvas, type UpdateCanvasPayload } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";

type Props = {
  assessmentId: string;
  canvasDiagnosis: CanvasDiagnosisResult;
  onSaved: (updated: CanvasDiagnosisResult) => void;
};

export function CanvasEditor({ assessmentId, canvasDiagnosis, onSaved }: Props) {
  const canvas = canvasDiagnosis.canvas;
  const [overallSummary, setOverallSummary] = useState(canvas.overall_summary);
  const [blocks, setBlocks] = useState(
    canvas.blocks.map((b) => ({ ...b })),
  );
  const [isSaving, setIsSaving] = useState(false);

  const updateBlock = (key: string, field: string, value: string) => {
    setBlocks((prev) =>
      prev.map((b) => (b.key === key ? { ...b, [field]: value } : b)),
    );
  };

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    try {
      const payload: UpdateCanvasPayload = {
        overall_summary: overallSummary,
        blocks: blocks.map((b) => ({
          key: b.key,
          title: b.title,
          current_state: b.current_state,
          diagnosis: b.diagnosis,
          ai_opportunity: b.ai_opportunity,
        })),
      };
      const response = await updateAssessmentCanvas(assessmentId, payload);
      toast({ title: "画布已保存，下游数据已清除" });
      onSaved(response.canvas_diagnosis);
    } catch (e) {
      toast({ title: "保存失败", variant: "destructive" });
    } finally {
      setIsSaving(false);
    }
  }, [assessmentId, overallSummary, blocks, onSaved]);

  return (
    <div className="space-y-6">
      {/* Overall summary editor */}
      <div className="rounded-xl border border-warm-border-light bg-warm-inset p-6">
        <label className="flex flex-col gap-2">
          <span className="section-label">总体摘要</span>
          <textarea
            className="w-full rounded-lg border border-warm-border bg-warm-surface p-3 text-sm leading-6 text-warm-text resize-y min-h-[80px]"
            value={overallSummary}
            onChange={(e) => setOverallSummary(e.target.value)}
          />
        </label>
      </div>

      {/* 9-block editors */}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {blocks.map((block) => (
          <div
            key={block.key}
            className="rounded-xl border-2 border-warm-accent/30 bg-warm-accent/5 p-5 space-y-3"
          >
            <p className="text-sm font-semibold text-warm-accent">{block.title}</p>

            <label className="flex flex-col gap-1">
              <span className="text-[10px] uppercase text-warm-muted">当前状态</span>
              <textarea
                className="w-full rounded border border-warm-border bg-warm-surface p-2 text-xs leading-5 text-warm-text resize-y min-h-[60px]"
                value={block.current_state}
                onChange={(e) => updateBlock(block.key, "current_state", e.target.value)}
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-[10px] uppercase text-warm-muted">诊断</span>
              <textarea
                className="w-full rounded border border-warm-border bg-warm-surface p-2 text-xs leading-5 text-warm-text resize-y min-h-[60px]"
                value={block.diagnosis}
                onChange={(e) => updateBlock(block.key, "diagnosis", e.target.value)}
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-[10px] uppercase text-warm-muted">AI 机会</span>
              <textarea
                className="w-full rounded border border-warm-border bg-warm-surface p-2 text-xs leading-5 text-warm-text resize-y min-h-[60px]"
                value={block.ai_opportunity}
                onChange={(e) => updateBlock(block.key, "ai_opportunity", e.target.value)}
              />
            </label>
          </div>
        ))}
      </div>

      {/* Save button */}
      <div className="flex gap-3 items-center">
        <Button onClick={handleSave} loading={isSaving} disabled={isSaving}>
          {isSaving ? "保存中..." : "保存修改并清除下游"}
        </Button>
        <p className="text-xs text-muted-foreground">
          保存后，突破要素、创新方向、场景推荐等下游数据将全部清除，需基于新画布重新生成。
        </p>
      </div>
    </div>
  );
}
