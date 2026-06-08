"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";

import {
  ApiError,
  downloadReportExport,
  formatMutationError,
  getReport,
  openReportPrintPage,
  type ReportExportFormat,
} from "@/lib/api";
import type { ReportDocumentResponse } from "@/lib/types";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";

function ReportSkeleton() {
  return (
    <div className="flex flex-col gap-6">
      <div className="card space-y-4">
        <Skeleton className="h-7 w-32 rounded-xl" />
        <Skeleton className="h-8 w-64 rounded-xl" />
        <div className="flex flex-wrap gap-3">
          <Skeleton className="h-12 w-36 rounded-full" />
          <Skeleton className="h-12 w-32 rounded-full" />
        </div>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Skeleton className="h-80 rounded-xl" />
        <Skeleton className="h-80 rounded-xl" />
      </div>
      <Skeleton className="h-96 rounded-xl" />
    </div>
  );
}

export function ReportDocumentViewer({ reportId }: { reportId: string }) {
  const [report, setReport] = useState<ReportDocumentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [exportingFormat, setExportingFormat] = useState<
    ReportExportFormat | "print" | null
  >(null);

  const loadReport = useCallback(() => {
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

  useEffect(() => {
    const cleanup = loadReport();
    return () => {
      cleanup();
    };
  }, [loadReport]);

  const handleExport = useCallback(
    async (format: ReportExportFormat | "print") => {
      if (!report) return;
      setExportingFormat(format);
      try {
        if (format === "print") {
          await openReportPrintPage(report.report_id);
        } else {
          await downloadReportExport(report.report_id, format);
        }
      } catch (nextError) {
        setError(formatMutationError(nextError, "报告导出"));
      } finally {
        setExportingFormat(null);
      }
    },
    [report],
  );

  if (isLoading) {
    return <ReportSkeleton />;
  }

  if (error) {
    return (
      <div className="space-y-4 rounded-xl p-6 text-sm msg-error">
        <div>
          <p className="font-medium">报告加载失败</p>
          <p className="mt-2 opacity-90">{error}</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Button variant="outline" size="sm" onClick={loadReport}>
            重试加载
          </Button>
          <Link href="/assessment" className="btn-secondary text-xs">
            返回主流程工作台
          </Link>
        </div>
      </div>
    );
  }

  if (!report) {
    return null;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="card">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="section-label">报告预览</p>
            <h2 className="section-heading">{report.title}</h2>
            <p className="mt-2 text-sm leading-7 text-warm-secondary">
              当前展示的是后端渲染后的 HTML 报告，可直接导出 PDF、Word、Markdown 或打开打印版。
            </p>
          </div>
          <div className="rounded-xl border border-green-200 bg-green-50/50 px-6 py-4 text-sm text-green-800">
            <p className="font-medium">Report ID</p>
            <p className="mt-2 break-all font-mono text-green-700/90">
              {report.report_id}
            </p>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <Button
            onClick={() => handleExport("pdf")}
            loading={exportingFormat === "pdf"}
            disabled={exportingFormat !== null}
          >
            下载 PDF
          </Button>
          <Button
            variant="success"
            onClick={() => handleExport("docx")}
            loading={exportingFormat === "docx"}
            disabled={exportingFormat !== null}
          >
            下载 Word
          </Button>
          <Button
            variant="outline"
            onClick={() => handleExport("markdown")}
            loading={exportingFormat === "markdown"}
            disabled={exportingFormat !== null}
          >
            下载 Markdown
          </Button>
          <Button
            variant="outline"
            onClick={() => handleExport("print")}
            loading={exportingFormat === "print"}
            disabled={exportingFormat !== null}
          >
            打开打印版
          </Button>
          <Link href={`/report/${report.assessment_id}`} className="btn-secondary">
            返回报告生成页
          </Link>
          <Link href={`/assessment/${report.assessment_id}`} className="btn-secondary">
            返回主流程工作台
          </Link>
        </div>
      </div>

      <div className="card shadow-card-hover">
        <p className="section-label">执行摘要</p>
        <h2 className="section-heading">报告结论</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <SummaryBadge label="企业" value={report.content_json.company_name} />
          <SummaryBadge label="行业" value={report.content_json.industry} />
          <SummaryBadge
            label="AI 就绪度"
            value={`${report.content_json.ai_readiness_score} 分`}
          />
          <SummaryBadge
            label="报告模式"
            value={report.generation_mode === "llm" ? "LLM 增强" : "模板生成"}
          />
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
          <div className="mt-6 rounded-xl border border-warm-border-light bg-warm-inset p-6">
            <p className="text-sm font-medium text-warm-text">warnings</p>
            {report.warnings.length > 0 ? (
              <ul className="mt-4 space-y-2 text-sm leading-7">
                {report.warnings.map((item, index) => (
                  <li key={`${item}-${index}`} className="rounded-xl p-4 text-sm msg-warning">
                    {item}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-4 text-sm leading-7 text-warm-muted">当前无告警。</p>
            )}
          </div>
          <ul className="mt-6 grid gap-3 text-sm leading-7">
            {report.sections.map((section, index) => (
              <li
                key={section.key}
                className="rounded-xl border border-warm-border-light bg-warm-inset px-4 py-3 text-warm-text"
              >
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
        <div
          className="report-html-preview px-6 py-8"
          dangerouslySetInnerHTML={{ __html: report.content_html }}
        />
      </div>
    </div>
  );
}

function SummaryBadge({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-secondary p-4">
      <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">{label}</p>
      <p className="mt-2 text-base font-semibold text-foreground">{value}</p>
    </div>
  );
}

function MetaItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-warm-border-light bg-warm-surface px-4 py-4">
      <p className="text-xs uppercase tracking-[0.14em] text-warm-muted">{label}</p>
      <p className="mt-3 break-words text-base text-warm-text">{value}</p>
    </div>
  );
}

function formatReportLoadError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 404) {
      return "未找到对应报告。请确认报告已生成，或从主流程工作台重新进入。";
    }
    if (error.status >= 500) {
      return "报告内容读取失败，可能是后端暂时异常。请稍后重试。";
    }
    return error.message;
  }
  if (error instanceof Error) {
    if (error.message.toLowerCase().includes("failed to fetch")) {
      return "无法连接后端服务，请确认后端已启动。";
    }
    return error.message;
  }
  return "报告加载失败。";
}
