"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import {
  ApiError,
  getReport,
  getReportDocxExportUrl,
  getReportMarkdownExportUrl,
  getReportPrintUrl,
} from "@/lib/api";
import type { ReportDocumentResponse } from "@/lib/types";

export function ReportDocumentViewer({
  reportId,
}: {
  reportId: string;
}) {
  const [report, setReport] = useState<ReportDocumentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    setError(null);

    getReport(reportId)
      .then((payload) => {
        if (active) {
          setReport(payload);
        }
      })
      .catch((nextError) => {
        if (active) {
          setError(formatReportLoadError(nextError));
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
  }, [reportId]);

  if (isLoading) {
    return (
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-sm text-slate-300 backdrop-blur">
        正在加载报告内容...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-[28px] border border-rose-300/30 bg-rose-300/10 p-6 text-sm text-rose-100">
        <p>{error}</p>
      </div>
    );
  }

  if (!report) {
    return null;
  }

  const markdownUrl = getReportMarkdownExportUrl(report.report_id);
  const docxUrl = getReportDocxExportUrl(report.report_id);
  const printUrl = getReportPrintUrl(report.report_id);

  return (
    <div className="flex flex-col gap-6">
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
              Rich Report Preview
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-white">
              {report.title}
            </h2>
            <p className="mt-3 text-sm leading-7 text-slate-300">
              该页面展示后端渲染后的 HTML 富文本版本，并保留 Markdown、Word 和打印版导出能力。
            </p>
          </div>

          <div className="rounded-3xl border border-emerald-300/30 bg-emerald-300/10 px-5 py-4 text-sm text-emerald-50">
            <p className="font-medium">Report ID</p>
            <p className="mt-2 break-all text-emerald-100/90">{report.report_id}</p>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <a
            href={markdownUrl}
            className="inline-flex items-center justify-center rounded-full bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
          >
            下载 Markdown
          </a>
          <a
            href={docxUrl}
            className="inline-flex items-center justify-center rounded-full bg-emerald-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-200"
          >
            下载 Word
          </a>
          <a
            href={printUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-medium text-white transition hover:bg-white/10"
          >
            打开打印版
          </a>
          <Link
            href={`/report/${report.assessment_id}`}
            className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-medium text-white transition hover:bg-white/10"
          >
            返回报告生成页
          </Link>
          <Link
            href={`/assessment/${report.assessment_id}`}
            className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-medium text-white transition hover:bg-white/10"
          >
            返回 Assessment
          </Link>
        </div>

        <div className="mt-6 rounded-3xl border border-white/8 bg-slate-950/55 p-5 text-sm leading-7 text-slate-300">
          <p>导出说明：Markdown 适合二次编辑，Word 适合提交或批注，打印版适合浏览器打印与 PDF 另存。</p>
          <p className="mt-3">
            如果导出按钮打开后无响应，请先确认后端服务在线，再重新进入当前报告页面触发导出文件生成。
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-[28px] border border-white/10 bg-slate-900/70 p-6">
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Generation Metadata
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            生成元信息
          </h2>

          <div className="mt-6 flex flex-wrap gap-3">
            <Badge label={`generation_mode: ${report.generation_mode}`} tone="cyan" />
            <Badge
              label={report.used_llm ? "used_llm: true" : "used_llm: false"}
              tone={report.used_llm ? "emerald" : "slate"}
            />
            <Badge
              label={report.used_rag ? "used_rag: true" : "used_rag: false"}
              tone={report.used_rag ? "violet" : "slate"}
            />
          </div>

          <div className="mt-6 grid gap-3 text-sm text-slate-200">
            <MetaItem label="企业名称" value={report.content_json.company_name} />
            <MetaItem label="所属行业" value={report.content_json.industry} />
            <MetaItem label="企业规模" value={report.content_json.company_size} />
            <MetaItem label="所在区域" value={report.content_json.region} />
            <MetaItem
              label="营收范围"
              value={report.content_json.annual_revenue_range}
            />
            <MetaItem
              label="AI 就绪度评分"
              value={String(report.content_json.ai_readiness_score)}
            />
            <MetaItem label="章节数量" value={String(report.sections.length)} />
            <MetaItem label="内容来源" value={report.content_json.generated_with} />
          </div>
        </div>

        <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Warnings & Sections
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            自检结果与章节结构
          </h2>

          <div className="mt-6 rounded-3xl border border-white/8 bg-slate-950/55 p-5">
            <p className="text-sm font-medium text-white">warnings</p>
            {report.warnings.length > 0 ? (
              <ul className="mt-4 space-y-2 text-sm leading-7 text-amber-50">
                {report.warnings.map((item, index) => (
                  <li
                    key={`${item}-${index}`}
                    className="rounded-2xl border border-amber-300/20 bg-amber-300/10 px-4 py-3"
                  >
                    {item}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-4 text-sm leading-7 text-slate-300">
                当前无告警。
              </p>
            )}
          </div>

          <ul className="mt-6 grid gap-3 text-sm leading-7 text-slate-200">
            {report.sections.map((section, index) => (
              <li
                key={section.key}
                className="rounded-2xl border border-white/8 bg-slate-950/55 px-4 py-3"
              >
                {index + 1}. {section.title}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="overflow-hidden rounded-[32px] border border-white/10 bg-white shadow-2xl shadow-slate-950/30">
        <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
          <p className="text-sm font-medium text-slate-600">HTML 富文本预览</p>
        </div>
        <div
          className="report-html-preview px-6 py-8"
          dangerouslySetInnerHTML={{ __html: report.content_html }}
        />
      </div>
    </div>
  );
}

function MetaItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4">
      <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
        {label}
      </p>
      <p className="mt-3 break-words text-base text-white">{value}</p>
    </div>
  );
}

function Badge({
  label,
  tone,
}: {
  label: string;
  tone: "cyan" | "emerald" | "violet" | "slate";
}) {
  const palette = {
    cyan: "bg-cyan-300/15 text-cyan-100",
    emerald: "bg-emerald-300/15 text-emerald-100",
    violet: "bg-violet-300/15 text-violet-100",
    slate: "bg-slate-200/10 text-slate-200",
  }[tone];

  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-sm font-medium ${palette}`}>
      {label}
    </span>
  );
}

function formatReportLoadError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 404) {
      return "未找到对应报告。请确认报告已生成，或从 Assessment 工作台重新进入。";
    }
    if (error.status >= 500) {
      return "报告内容读取失败，可能是已保存内容损坏或后端暂时异常。请稍后重试。";
    }
    return error.message;
  }

  if (error instanceof Error) {
    if (error.message.toLowerCase().includes("failed to fetch")) {
      return "无法连接后端服务，当前无法加载报告。请确认后端已启动。";
    }
    return error.message;
  }

  return "报告加载失败。";
}
