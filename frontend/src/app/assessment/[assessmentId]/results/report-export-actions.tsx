"use client";

import { useCallback, useState } from "react";

import {
  generateAssessmentReport,
  getReportDocxExportUrl,
  getReportMarkdownExportUrl,
  getReportPdfUrl,
  getReportPrintUrl,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";

export function ReportExportActions({
  assessmentId,
  initialReportId,
}: {
  assessmentId: string;
  initialReportId?: string | null;
}) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportId, setReportId] = useState<string | null>(initialReportId ?? null);

  const handleGenerateAndExport = useCallback(async () => {
    if (reportId) return;
    setIsGenerating(true);
    try {
      const reportResponse = await generateAssessmentReport(assessmentId, "template");
      setReportId(reportResponse.report_id);
      toast({ title: "报告已生成，可以直接导出 PDF / Word" });
    } catch {
      toast({ title: "报告生成失败", variant: "destructive" });
    } finally {
      setIsGenerating(false);
    }
  }, [assessmentId, reportId]);

  return (
    <div className="flex flex-wrap items-center gap-2">
      {!reportId ? (
        <Button
          onClick={handleGenerateAndExport}
          disabled={isGenerating}
          loading={isGenerating}
          size="sm"
        >
          {isGenerating ? "正在生成报告..." : "生成导出报告"}
        </Button>
      ) : (
        <>
          <a
            href={getReportPdfUrl(reportId)}
            className="btn-primary text-xs"
            download
          >
            下载 PDF
          </a>
          <a
            href={getReportDocxExportUrl(reportId)}
            className="btn-secondary text-xs"
            download
          >
            下载 Word
          </a>
          <a
            href={getReportMarkdownExportUrl(reportId)}
            className="btn-secondary text-xs"
            download
          >
            下载 Markdown
          </a>
          <a
            href={getReportPrintUrl(reportId)}
            className="btn-secondary text-xs"
            target="_blank"
            rel="noopener noreferrer"
          >
            打开打印版
          </a>
        </>
      )}
    </div>
  );
}
