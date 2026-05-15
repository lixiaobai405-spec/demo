import Link from "next/link";

import {
  getAssessmentDetail,
  getCompetitiveness,
  getEndgame,
} from "@/lib/api";
import { BusinessCanvasGrid } from "@/components/business-canvas-grid";
import { CompetitivenessPanel } from "@/components/competitiveness-panel";
import { EndgamePanel } from "@/components/endgame-panel";
import { ScenarioRecommendationsPanel } from "@/components/scenario-recommendations-panel";
import { ReportExportActions } from "./report-export-actions";

export default async function ResultsPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = await params;

  const [detail, competitiveness, endgame] = await Promise.allSettled([
    getAssessmentDetail(assessmentId),
    getCompetitiveness(assessmentId),
    getEndgame(assessmentId),
  ]);

  const detailData = detail.status === "fulfilled" ? detail.value : null;
  const compData =
    competitiveness.status === "fulfilled" ? competitiveness.value : null;
  const endgameData =
    endgame.status === "fulfilled" ? endgame.value : null;

  const assessment = detailData?.assessment;
  const companyName = assessment?.company_name || "企业";
  const industry = assessment?.industry || "";
  const scenarioRecommendation = detailData?.scenario_recommendation;
  const readyForReport = detailData?.progress.ready_for_report || false;

  const hasAny =
    detailData?.canvas_diagnosis ||
    scenarioRecommendation ||
    compData ||
    endgameData;

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8">
        {/* Header */}
        <section className="page-header">
          <div className="flex flex-col gap-4">
            <div className="flex flex-wrap items-center gap-2">
              <Link href="/" className="btn-secondary text-xs">
                ← 返回首页
              </Link>
              <Link
                href={`/assessment/${assessmentId}`}
                className="btn-secondary text-xs"
              >
                ← 返回工作台
              </Link>
              <Link
                href={`/assessment/${assessmentId}/canvas`}
                className="btn-secondary text-xs"
                target="_blank"
                rel="noopener noreferrer"
              >
                画布 9 格 →
              </Link>
            </div>
            <span className="badge badge-accent">评估结果仪表盘</span>
            <h1 className="font-heading text-4xl font-bold tracking-tight text-warm-text">
              {companyName} AI 商业创新评估
            </h1>
            {industry ? (
              <p className="text-base leading-7 text-warm-secondary">
                {industry}
              </p>
            ) : null}
            {readyForReport && detailData ? (
              <div className="mt-4 flex flex-wrap gap-3">
                <ReportExportActions assessmentId={assessmentId} />
              </div>
            ) : null}
          </div>
        </section>

        {/* Results Grid */}
        {!hasAny ? (
          <div className="card-inset">
            <p className="section-label">评估结果</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              尚未生成任何评估结果。
              <Link
                href={`/assessment/${assessmentId}`}
                className="ml-1 font-medium text-primary underline underline-offset-4"
              >
                返回工作台生成
              </Link>
            </p>
          </div>
        ) : (
          <>
            {/* 1. 点：商业画布 */}
            {detailData?.canvas_diagnosis && (
              <section>
                <div className="mb-2">
                  <p className="section-label">点 · 商业画布</p>
                </div>
                <BusinessCanvasGrid canvasDiagnosis={detailData.canvas_diagnosis} />
                {/* Scene recommendations embedded within canvas context */}
                {scenarioRecommendation && detailData?.assessment && (
                  <div className="mt-6 card">
                    <ScenarioRecommendationsPanel
                      assessmentId={assessmentId}
                      readyForReport={readyForReport}
                      scenarioRecommendation={scenarioRecommendation}
                    />
                  </div>
                )}
              </section>
            )}

            {/* 2. 线：差异化竞争力 */}
            {compData && (
              <section>
                <div className="mb-2">
                  <p className="section-label">线 · 差异化竞争力</p>
                </div>
                <CompetitivenessPanel data={compData} />
              </section>
            )}

            {/* 3. 面：商业终局 */}
            {endgameData && (
              <section>
                <div className="mb-2">
                  <p className="section-label">面 · 商业终局</p>
                </div>
                <EndgamePanel data={endgameData} />
              </section>
            )}
          </>
        )}
      </div>
    </main>
  );
}
