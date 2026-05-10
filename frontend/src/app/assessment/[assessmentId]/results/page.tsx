import Link from "next/link";

import {
  getAssessmentDetail,
  getCompetitiveness,
  getEndgame,
} from "@/lib/api";
import { ProfileResultsSection } from "@/components/profile-results-section";
import { CompetitivenessPanel } from "@/components/competitiveness-panel";
import { EndgamePanel } from "@/components/endgame-panel";
import { ScenarioRecommendationsPanel } from "@/components/scenario-recommendations-panel";

export default async function ResultsPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = await params;

  // Fetch all data in parallel
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
  const companyProfile = detailData?.company_profile;
  const scenarioRecommendation = detailData?.scenario_recommendation;
  const readyForReport = detailData?.progress.ready_for_report || false;

  const hasAny =
    companyProfile ||
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
                <Link
                  href={`/report/${assessmentId}`}
                  className="btn-primary"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  进入报告生成
                </Link>
                <Link
                  href={`/report-context/${assessmentId}`}
                  className="btn-secondary"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  查看报告上下文
                </Link>
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
            {/* Profile */}
            {companyProfile && (
              <ProfileResultsSection
                companyProfile={companyProfile}
                profileMode={null}
              />
            )}

            {/* Canvas summary — link to full page */}
            {detailData?.canvas_diagnosis && (
              <div className="card">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="section-label">画布诊断</p>
                    <h2 className="section-heading">商业画布 9 格</h2>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="badge badge-success">
                      评分 {detailData.canvas_diagnosis.overall_score}
                    </span>
                    <Link
                      href={`/assessment/${assessmentId}/canvas`}
                      className="btn-secondary text-xs"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      查看完整画布 →
                    </Link>
                  </div>
                </div>
                <p className="mt-4 text-sm leading-7 text-warm-secondary">
                  {detailData.canvas_diagnosis.canvas.overall_summary}
                </p>
              </div>
            )}

            {/* Scenarios */}
            {scenarioRecommendation && detailData?.assessment && (
              <ScenarioRecommendationsPanel
                assessmentId={assessmentId}
                readyForReport={readyForReport}
                scenarioRecommendation={scenarioRecommendation}
              />
            )}

            {/* Competitiveness */}
            {compData && <CompetitivenessPanel data={compData} />}

            {/* Endgame */}
            {endgameData && <EndgamePanel data={endgameData} />}
          </>
        )}
      </div>
    </main>
  );
}
