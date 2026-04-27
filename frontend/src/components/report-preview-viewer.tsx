"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { generateAssessmentReport, getAssessmentDetail } from "@/lib/api";
import type { AssessmentDetailResponse, ReportDocumentResponse } from "@/lib/types";

export function ReportPreviewViewer({
  assessmentId,
}: {
  assessmentId: string;
}) {
  const router = useRouter();
  const [detail, setDetail] = useState<AssessmentDetailResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportMode, setReportMode] = useState<"template" | "llm">("template");

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    setError(null);

    getAssessmentDetail(assessmentId)
      .then((payload) => {
        if (active) {
          setDetail(payload);
        }
      })
      .catch((nextError) => {
        if (active) {
          setError(
            nextError instanceof Error
              ? nextError.message
              : "报告状态加载失败。",
          );
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [assessmentId]);

  async function handleGenerateReport() {
    setIsGenerating(true);
    setError(null);

    try {
      const reportResponse: ReportDocumentResponse =
        await generateAssessmentReport(assessmentId, reportMode);
      router.push(`/reports/${reportResponse.report_id}`);
    } catch (nextError) {
      setError(
        nextError instanceof Error ? nextError.message : "报告生成失败。",
      );
    } finally {
      setIsGenerating(false);
    }
  }

  if (isLoading) {
    return (
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-sm text-slate-300 backdrop-blur">
        正在加载报告状态...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-[28px] border border-rose-300/30 bg-rose-300/10 p-6 text-sm text-rose-100">
        <p>{error}</p>
        <Link
          href={`/assessment/${assessmentId}`}
          className="mt-4 inline-flex rounded-full bg-white/10 px-4 py-2 text-sm text-white transition hover:bg-white/15"
        >
          返回 Assessment 工作台
        </Link>
      </div>
    );
  }

  if (!detail) {
    return null;
  }

  const assessment = detail.assessment;
  const profile = detail.company_profile;
  const canvas = detail.canvas_diagnosis;
  const scenarios = detail.scenario_recommendation;
  const existingReport = detail.generated_report;
  const caseStateText = detail.progress.has_cases
    ? "案例参考已准备，可直接回看或重生成。"
    : "案例参考尚未单独生成；点击生成报告时会自动匹配并保存匿名行业案例。";

  return (
    <div className="flex flex-col gap-6">
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
              Report Generator
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-white">
              报告生成页
            </h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-300">
              当前页面会基于已完成的企业画像、商业画布和 AI 场景推荐生成统一的结构化报告。
              报告生成后会保存 Markdown、HTML 和结构化 JSON，并支持 Word 导出与打印版打开。
            </p>
          </div>

          <div className="rounded-3xl border border-amber-300/30 bg-amber-300/10 px-5 py-4 text-sm text-amber-50">
            <p className="font-medium">Assessment ID</p>
            <p className="mt-2 break-all text-amber-100/90">{assessment.id}</p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="rounded-[28px] border border-white/10 bg-slate-900/70 p-6">
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Readiness
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            报告生成前检查
          </h2>

          <div className="mt-6 space-y-3 text-sm text-slate-200">
            <StatusRow
              label="企业画像"
              ready={detail.progress.has_profile}
              text={
                profile
                  ? "已生成，可直接纳入报告。"
                  : "尚未生成，当前无法进入报告。"
              }
            />
            <StatusRow
              label="商业画布诊断"
              ready={detail.progress.has_canvas}
              text={
                canvas
                  ? `已生成，整体评分 ${canvas.overall_score}。`
                  : "尚未生成，当前无法进入报告。"
              }
            />
            <StatusRow
              label="AI 场景推荐"
              ready={detail.progress.has_scenarios}
              text={
                scenarios
                  ? `已生成 Top ${scenarios.top_scenarios.length} 推荐。`
                  : "尚未生成，当前无法进入报告。"
              }
            />
            <StatusRow
              label="案例参考"
              ready={detail.progress.has_cases}
              text={caseStateText}
            />
            <StatusRow
              label="已有报告"
              ready={detail.progress.has_report}
              text={
                existingReport
                  ? `已存在报告：${existingReport.title}`
                  : "尚未生成报告。"
              }
            />
          </div>

          {!detail.progress.ready_for_report ? (
            <div className="mt-6 rounded-3xl border border-amber-300/30 bg-amber-300/10 px-5 py-4 text-sm leading-7 text-amber-50">
              还不能生成报告。请先完成企业画像、商业画布和 AI 场景推荐。
            </div>
          ) : null}
        </div>

        <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Actions
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            生成与回看
          </h2>

          <div className="mt-6 grid gap-3">
            {/* Mode Selection */}
            <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4">
              <p className="mb-3 font-medium text-white">报告生成模式</p>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="reportMode"
                    value="template"
                    checked={reportMode === "template"}
                    onChange={() => setReportMode("template")}
                    className="h-4 w-4 accent-cyan-300"
                  />
                  <span className="text-sm text-slate-200">模板生成（快速）</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="reportMode"
                    value="llm"
                    checked={reportMode === "llm"}
                    onChange={() => setReportMode("llm")}
                    className="h-4 w-4 accent-cyan-300"
                  />
                  <span className="text-sm text-slate-200">LLM 增强（智能）</span>
                </label>
              </div>
              <p className="mt-2 text-xs text-slate-400">
                {reportMode === "template"
                  ? "模板模式：使用结构化模板快速生成报告"
                  : "LLM模式：使用大语言模型生成更智能、更个性化的报告"}
              </p>
            </div>

            <button
              type="button"
              onClick={handleGenerateReport}
              disabled={!detail.progress.ready_for_report || isGenerating}
              className="inline-flex items-center justify-center rounded-full bg-cyan-300 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isGenerating
                ? "正在生成报告..."
                : existingReport
                  ? "重新生成报告"
                  : "生成报告"}
            </button>

            {existingReport ? (
              <Link
                href={`/reports/${existingReport.report_id}`}
                className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 px-6 py-3 text-sm font-medium text-white transition hover:bg-white/10"
              >
                查看已有报告
              </Link>
            ) : null}

            <Link
              href={`/report-context/${assessmentId}`}
              className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 px-6 py-3 text-sm font-medium text-white transition hover:bg-white/10"
            >
              查看报告上下文
            </Link>

            <Link
              href={`/assessment/${assessmentId}`}
              className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 px-6 py-3 text-sm font-medium text-white transition hover:bg-white/10"
            >
              返回 Assessment 工作台
            </Link>
          </div>

          <div className="mt-6 rounded-3xl border border-white/8 bg-slate-950/55 p-5 text-sm leading-7 text-slate-300">
            <p>
              报告生成逻辑当前为模板化生成，不依赖 API Key，也不会自由编造真实公司案例或 ROI 数字。
            </p>
            <p className="mt-3">
              如果后续接入 RAG 或案例检索增强，仍建议保持当前结构化章节为统一底座。
            </p>
          </div>

          {error ? (
            <p className="mt-5 rounded-2xl border border-rose-300/30 bg-rose-300/10 px-4 py-3 text-sm text-rose-100">
              {error}
            </p>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function StatusRow({
  label,
  ready,
  text,
}: {
  label: string;
  ready: boolean;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4">
      <div className="flex items-center justify-between gap-4">
        <p className="font-medium text-white">{label}</p>
        <span
          className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${
            ready
              ? "bg-emerald-300/15 text-emerald-100"
              : "bg-slate-200/10 text-slate-200"
          }`}
        >
          {ready ? "已就绪" : "未完成"}
        </span>
      </div>
      <p className="mt-3 leading-7 text-slate-300">{text}</p>
    </div>
  );
}
