"use client";

import { useCallback, useState } from "react";

import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";
import {
  downloadReportExport,
  formatMutationError,
  generateAssessmentReport,
  openReportPrintPage,
  type ReportExportFormat,
} from "@/lib/api";

export function ReportExportActions({
  assessmentId,
  initialReportId,
}: {
  assessmentId: string;
  initialReportId?: string | null;
}) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportId, setReportId] = useState<string | null>(
    initialReportId ?? null,
  );
  const [exportingFormat, setExportingFormat] = useState<
    ReportExportFormat | "print" | null
  >(null);

  const handleGenerateAndExport = useCallback(async () => {
    if (reportId) return;
    setIsGenerating(true);
    try {
      const reportResponse = await generateAssessmentReport(
        assessmentId,
        "template",
      );
      setReportId(reportResponse.report_id);
      toast({ title: "报告已生成，可以直接导出 PDF / Word" });
    } catch (error) {
      toast({
        title: "报告生成失败",
        description: formatMutationError(error, "报告生成"),
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  }, [assessmentId, reportId]);

  const handleExport = useCallback(
    async (format: ReportExportFormat | "print") => {
      if (!reportId) return;
      setExportingFormat(format);
      try {
        if (format === "print") {
          await openReportPrintPage(reportId);
        } else {
          await downloadReportExport(reportId, format);
        }
      } catch (error) {
        toast({
          title: "导出失败",
          description: formatMutationError(error, "报告导出"),
          variant: "destructive",
        });
      } finally {
        setExportingFormat(null);
      }
    },
    [reportId],
  );

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
          <Button
            size="sm"
            onClick={() => handleExport("pdf")}
            loading={exportingFormat === "pdf"}
            disabled={exportingFormat !== null}
          >
            下载 PDF
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport("docx")}
            loading={exportingFormat === "docx"}
            disabled={exportingFormat !== null}
          >
            下载 Word
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport("markdown")}
            loading={exportingFormat === "markdown"}
            disabled={exportingFormat !== null}
          >
            下载 Markdown
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport("print")}
            loading={exportingFormat === "print"}
            disabled={exportingFormat !== null}
          >
            打开打印版
          </Button>
        </>
      )}
    </div>
  );
}
