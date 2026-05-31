"use client";

import React from "react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import type { UpdateCompetitivenessPayload } from "@/lib/types";

type Props = {
  value: UpdateCompetitivenessPayload;
  isSaving?: boolean;
  onSave: (payload: UpdateCompetitivenessPayload) => Promise<void> | void;
  onCancel: () => void;
};

function listToText(value: string[]) {
  return value.join("\n");
}

function textToList(value: string) {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function cloneValue(value: UpdateCompetitivenessPayload): UpdateCompetitivenessPayload {
  return {
    vp_reconstruction: {
      ...value.vp_reconstruction,
      differentiation_points: [...value.vp_reconstruction.differentiation_points],
    },
    connections: value.connections.map((connection) => ({
      ...connection,
      point_ids: [...connection.point_ids],
      point_titles: [...connection.point_titles],
      key_metrics: [...connection.key_metrics],
    })),
    advantages: value.advantages.map((advantage) => ({
      ...advantage,
      source_elements: [...advantage.source_elements],
    })),
    delivery_strategy: {
      ...value.delivery_strategy,
      key_risks: [...value.delivery_strategy.key_risks],
    },
    overall_narrative: value.overall_narrative,
  };
}

export function CompetitivenessEditor({
  value,
  isSaving,
  onSave,
  onCancel,
}: Props) {
  const [draft, setDraft] = useState(() => cloneValue(value));

  function updateVp<K extends keyof UpdateCompetitivenessPayload["vp_reconstruction"]>(
    key: K,
    nextValue: UpdateCompetitivenessPayload["vp_reconstruction"][K],
  ) {
    setDraft((current) => ({
      ...current,
      vp_reconstruction: {
        ...current.vp_reconstruction,
        [key]: nextValue,
      },
    }));
  }

  function updateConnection(
    index: number,
    patch: Partial<UpdateCompetitivenessPayload["connections"][number]>,
  ) {
    setDraft((current) => ({
      ...current,
      connections: current.connections.map((connection, currentIndex) =>
        currentIndex === index ? { ...connection, ...patch } : connection,
      ),
    }));
  }

  function updateAdvantage(
    index: number,
    patch: Partial<UpdateCompetitivenessPayload["advantages"][number]>,
  ) {
    setDraft((current) => ({
      ...current,
      advantages: current.advantages.map((advantage, currentIndex) =>
        currentIndex === index ? { ...advantage, ...patch } : advantage,
      ),
    }));
  }

  function updateDelivery(
    patch: Partial<UpdateCompetitivenessPayload["delivery_strategy"]>,
  ) {
    setDraft((current) => ({
      ...current,
      delivery_strategy: {
        ...current.delivery_strategy,
        ...patch,
      },
    }));
  }

  return (
    <section className="card">
      <div>
        <p className="section-label">手动修订</p>
        <h2 className="section-heading">差异化竞争力</h2>
        <p className="mt-2 text-sm leading-7 text-warm-secondary">
          像商业画布诊断一样直接修改框内文字，保存后仍会写回原有结构化数据。
        </p>
      </div>

      <div className="mt-6 space-y-6">
        <div className="rounded-xl border border-warm-border-light bg-warm-inset p-6">
          <label className="flex flex-col gap-2">
            <span className="section-label">总体方案摘要</span>
            <textarea
              className="w-full min-h-[90px] resize-y rounded-lg border border-warm-border bg-warm-surface p-3 text-sm leading-6 text-warm-text"
              value={draft.overall_narrative}
              onChange={(event) =>
                setDraft((current) => ({
                  ...current,
                  overall_narrative: event.target.value,
                }))
              }
            />
          </label>
        </div>

        <div className="rounded-xl border-2 border-warm-accent/30 bg-warm-accent/5 p-5">
          <h3 className="font-heading text-base font-bold text-warm-text">VP 重构</h3>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <TextAreaField
              label="当前 VP"
              value={draft.vp_reconstruction.current_vp}
              onChange={(nextValue) => updateVp("current_vp", nextValue)}
            />
            <TextAreaField
              label="强化 VP"
              value={draft.vp_reconstruction.enhanced_vp}
              onChange={(nextValue) => updateVp("enhanced_vp", nextValue)}
            />
            <TextAreaField
              label="差异化定位"
              value={listToText(draft.vp_reconstruction.differentiation_points)}
              onChange={(nextValue) =>
                updateVp("differentiation_points", textToList(nextValue))
              }
              helper="每行一个定位点。"
            />
            <TextAreaField
              label="客户价值转移"
              value={draft.vp_reconstruction.customer_value_shift}
              onChange={(nextValue) => updateVp("customer_value_shift", nextValue)}
            />
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          {draft.connections.map((connection, index) => (
            <div
              key={`connection-${index}`}
              className="rounded-xl border border-warm-border-light bg-warm-surface p-5"
            >
              <h3 className="font-heading text-base font-bold text-warm-text">
                竞争力提升路径 {index + 1}
              </h3>
              <div className="mt-4 space-y-3">
                <TextAreaField
                  label={`系统方案命名 ${index + 1}`}
                  value={connection.line_name}
                  minHeight="min-h-[48px]"
                  onChange={(nextValue) =>
                    updateConnection(index, { line_name: nextValue })
                  }
                />
                <TextAreaField
                  label={`关联方向 ${index + 1}`}
                  value={listToText(connection.point_titles)}
                  onChange={(nextValue) =>
                    updateConnection(index, { point_titles: textToList(nextValue) })
                  }
                  helper="每行一个方向。"
                />
                <TextAreaField
                  label={`战略叙事 ${index + 1}`}
                  value={connection.strategic_narrative}
                  onChange={(nextValue) =>
                    updateConnection(index, { strategic_narrative: nextValue })
                  }
                />
                <TextAreaField
                  label={`竞争影响 ${index + 1}`}
                  value={connection.competitive_impact}
                  onChange={(nextValue) =>
                    updateConnection(index, { competitive_impact: nextValue })
                  }
                />
                <TextAreaField
                  label={`关键指标 ${index + 1}`}
                  value={listToText(connection.key_metrics)}
                  onChange={(nextValue) =>
                    updateConnection(index, { key_metrics: textToList(nextValue) })
                  }
                  helper="每行一个指标。"
                />
                <TextAreaField
                  label={`串联逻辑 ${index + 1}`}
                  value={connection.linkage_logic}
                  onChange={(nextValue) =>
                    updateConnection(index, { linkage_logic: nextValue })
                  }
                />
                <TextAreaField
                  label={`竞争壁垒 ${index + 1}`}
                  value={connection.competitive_moat}
                  onChange={(nextValue) =>
                    updateConnection(index, { competitive_moat: nextValue })
                  }
                />
              </div>
            </div>
          ))}
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          {draft.advantages.map((advantage, index) => (
            <div
              key={`advantage-${index}`}
              className="rounded-xl border border-warm-border-light bg-warm-surface p-5"
            >
              <h3 className="font-heading text-base font-bold text-warm-text">
                核心优势 {index + 1}
              </h3>
              <div className="mt-4 space-y-3">
                <TextAreaField
                  label={`优势名称 ${index + 1}`}
                  value={advantage.advantage_name}
                  minHeight="min-h-[48px]"
                  onChange={(nextValue) =>
                    updateAdvantage(index, { advantage_name: nextValue })
                  }
                />
                <TextAreaField
                  label={`来源要素 ${index + 1}`}
                  value={listToText(advantage.source_elements)}
                  onChange={(nextValue) =>
                    updateAdvantage(index, { source_elements: textToList(nextValue) })
                  }
                  helper="每行一个要素。"
                />
                <TextAreaField
                  label={`优势描述 ${index + 1}`}
                  value={advantage.description}
                  onChange={(nextValue) =>
                    updateAdvantage(index, { description: nextValue })
                  }
                />
                <label className="flex flex-col gap-1">
                  <span className="text-[10px] uppercase text-warm-muted">
                    壁垒等级 {index + 1}
                  </span>
                  <select
                    className="w-full rounded border border-warm-border bg-warm-surface p-2 text-xs leading-5 text-warm-text"
                    value={advantage.barrier_level}
                    onChange={(event) =>
                      updateAdvantage(index, {
                        barrier_level: event.target.value as "低" | "中" | "高",
                      })
                    }
                  >
                    <option value="低">低</option>
                    <option value="中">中</option>
                    <option value="高">高</option>
                  </select>
                </label>
              </div>
            </div>
          ))}
        </div>

        <div className="rounded-xl border border-warm-border-light bg-warm-surface p-5">
          <h3 className="font-heading text-base font-bold text-warm-text">
            三阶段提升路径
          </h3>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <TextAreaField
              label="第一阶段：快速验证"
              value={draft.delivery_strategy.phase_1_quick_win}
              onChange={(nextValue) =>
                updateDelivery({ phase_1_quick_win: nextValue })
              }
            />
            <TextAreaField
              label="第二阶段：规模化复制"
              value={draft.delivery_strategy.phase_2_scale}
              onChange={(nextValue) => updateDelivery({ phase_2_scale: nextValue })}
            />
            <TextAreaField
              label="第三阶段：壁垒沉淀"
              value={draft.delivery_strategy.phase_3_moat}
              onChange={(nextValue) => updateDelivery({ phase_3_moat: nextValue })}
            />
            <TextAreaField
              label="关键风险"
              value={listToText(draft.delivery_strategy.key_risks)}
              onChange={(nextValue) =>
                updateDelivery({ key_risks: textToList(nextValue) })
              }
              helper="每行一个风险。"
            />
          </div>
        </div>

        <div className="rounded-xl border border-warm-warning/20 bg-warm-warning/5 p-4 text-sm leading-7 text-warm-secondary">
          保存后，下游结论会按依赖链自动失效，需要重新生成。
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button onClick={() => onSave(draft)} loading={isSaving} disabled={isSaving}>
            {isSaving ? "保存中..." : "保存修改并清除下游"}
          </Button>
          <Button variant="outline" onClick={onCancel} disabled={isSaving}>
            取消
          </Button>
        </div>
      </div>
    </section>
  );
}

function TextAreaField({
  label,
  value,
  onChange,
  helper,
  minHeight = "min-h-[70px]",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  helper?: string;
  minHeight?: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="flex flex-col gap-1">
        <span className="text-[10px] uppercase text-warm-muted">{label}</span>
        <textarea
          className={`w-full resize-y rounded border border-warm-border bg-warm-surface p-2 text-xs leading-5 text-warm-text ${minHeight}`}
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
      </label>
      {helper ? <span className="text-[10px] text-warm-muted">{helper}</span> : null}
    </div>
  );
}
