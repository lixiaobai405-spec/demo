"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { ApiError, getReport, getReportDocxExportUrl, getReportMarkdownExportUrl, getReportPrintUrl } from "@/lib/api";
import type { ReportDocumentResponse } from "@/lib/types";

export function ReportDocumentViewer({ reportId }: { reportId: string }) {
  const [report, setReport] = useState<ReportDocumentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setIsLoading(true); setError(null);
    getReport(reportId)
      .then((payload) => { if (active) setReport(payload); })
      .catch((nextError) => { if (active) setError(formatReportLoadError(nextError)); })
      .finally(() => { if (active) setIsLoading(false); });
    return () => { active = false; };
  }, [reportId]);

  if (isLoading) return <div className="card text-sm text-warm-secondary">正在加载报告内容...</div>;
  if (error) return <div className="rounded-xl msg-error p-6 text-sm"><p>{error}</p></div>;
  if (!report) return null;

  const markdownUrl = getReportMarkdownExportUrl(report.report_id);
  const docxUrl = getReportDocxExportUrl(report.report_id);
  const printUrl = getReportPrintUrl(report.report_id);

  return (
    <div className="flex flex-col gap-6">
      <div className="card">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="section-label">报告预览</p>
            <h2 className="section-heading">{report.title}</h2>
            <p className="mt-2 text-sm leading-7 text-warm-secondary">该页面展示后端渲染后的 HTML 富文本版本，并保留 Markdown、Word 和打印版导出能力。</p>
          </div>
          <div className="rounded-xl border border-green-200 bg-green-50/50 px-5 py-4 text-sm text-green-800">
            <p className="font-medium">Report ID</p>
            <p className="mt-2 break-all font-mono text-green-700/90">{report.report_id}</p>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <a href={markdownUrl} className="btn-primary">下载 Markdown</a>
          <a href={docxUrl} className="btn-success">下载 Word</a>
          <a href={printUrl} target="_blank" rel="noreferrer" className="btn-secondary">打开打印版</a>
          <Link href={`/report/${report.assessment_id}`} className="btn-secondary">返回报告生成页</Link>
          <Link href={`/assessment/${report.assessment_id}`} className="btn-secondary">返回 Assessment</Link>
        </div>

        <div className="mt-6 rounded-xl border border-warm-border-light bg-warm-inset p-5 text-sm leading-7 text-warm-secondary">
          <p>导出说明：Markdown 适合二次编辑，Word 适合提交或批注，打印版适合浏览器打印与 PDF 另存。</p>
          <p className="mt-3">如果导出按钮打开后无响应，请先确认后端服务在线，再重新进入当前报告页面触发导出文件生成。</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="card-inset">
          <p className="section-label">生成信息</p>
          <h2 className="section-heading">生成元信息</h2>
          <div className="mt-6 flex flex-wrap gap-3">
            <span className="badge badge-accent">generation_mode: {report.generation_mode}</span>
            <span className={`badge ${report.used_llm ? "badge-success" : "badge-muted"}`}>
              used_llm: {String(report.used_llm)}
            </span>
            <span className={`badge ${report.used_rag ? "badge-accent" : "badge-muted"}`}>
              used_rag: {String(report.used_rag)}
            </span>
          </div>
          <div className="mt-6 grid gap-3 text-sm">
            <MetaItem label="企业名称" value={report.content_json.company_name} />
            <MetaItem label="所属行业" value={report.content_json.industry} />
            <MetaItem label="企业规模" value={report.content_json.company_size} />
            <MetaItem label="所在区域" value={report.content_json.region} />
            <MetaItem label="营收范围" value={report.content_json.annual_revenue_range} />
            <MetaItem label="AI 就绪度评分" value={String(report.content_json.ai_readiness_score)} />
            <MetaItem label="章节数量" value={String(report.sections.length)} />
            <MetaItem label="内容来源" value={report.content_json.generated_with} />
          </div>
        </div>

        <div className="card">
          <p className="section-label">Warnings & Sections</p>
          <h2 className="section-heading">自检结果与章节结构</h2>
          <div className="mt-6 rounded-xl border border-warm-border-light bg-warm-inset p-5">
            <p className="text-sm font-medium text-warm-text">warnings</p>
            {report.warnings.length > 0 ? (
              <ul className="mt-4 space-y-2 text-sm leading-7">
                {report.warnings.map((item, index) => (
                  <li key={`${item}-${index}`} className="rounded-lg msg-warning p-4 text-sm">{item}</li>
                ))}
              </ul>
            ) : <p className="mt-4 text-sm leading-7 text-warm-muted">当前无告警。</p>}
          </div>
          <ul className="mt-6 grid gap-3 text-sm leading-7">
            {report.sections.map((section, index) => (
              <li key={section.key} className="rounded-lg border border-warm-border-light bg-warm-inset px-4 py-3 text-warm-text">
                {index + 1}. {section.title}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-warm-border bg-warm-surface shadow-card">
        <div className="border-b border-warm-border-light bg-warm-inset px-6 py-4">
          <p className="text-sm font-medium text-warm-text">HTML 富文本预览</p>
        </div>
        <div className="report-html-preview px-6 py-8" dangerouslySetInnerHTML={{ __html: report.content_html }} />
      </div>
    </div>
  );
}

function MetaItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-warm-border-light bg-warm-surface px-4 py-4">
      <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">{label}</p>
      <p className="mt-3 break-words text-base text-warm-text">{value}</p>
    </div>
  );
}

function formatReportLoadError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 404) return "未找到对应报告。请确认报告已生成，或从 Assessment 工作台重新进入。";
    if (error.status >= 500) return "报告内容读取失败，可能是已保存内容损坏或后端暂时异常。请稍后重试。";
    return error.message;
  }
  if (error instanceof Error) {
    if (error.message.toLowerCase().includes("failed to fetch")) return "无法连接后端服务，当前无法加载报告。请确认后端已启动。";
    return error.message;
  }
  return "报告加载失败。";
}
