"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { getReportContext } from "@/lib/api";
import type { ReportContextResponse } from "@/lib/types";

export function ReportContextViewer({
  assessmentId,
}: {
  assessmentId: string;
}) {
  const [context, setContext] = useState<ReportContextResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    setError(null);

    getReportContext(assessmentId)
      .then((payload) => {
        if (active) {
          setContext(payload);
        }
      })
      .catch((nextError) => {
        if (active) {
          setError(
            nextError instanceof Error
              ? nextError.message
              : "报告上下文加载失败。",
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

  if (isLoading) {
    return (
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-sm text-slate-300 backdrop-blur">
        正在加载报告上下文...
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

  if (!context) {
    return null;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
              Report Context
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-white">
              报告草稿上下文
            </h2>
          </div>

          <div className="flex flex-wrap gap-3">
            <Link
              href={`/assessment/${assessmentId}`}
              className="inline-flex rounded-full bg-white/10 px-4 py-2 text-sm text-white transition hover:bg-white/15"
            >
              返回工作台
            </Link>
            <Link
              href={`/report/${assessmentId}`}
              className="inline-flex rounded-full bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
            >
              进入报告生成
            </Link>
          </div>
        </div>

        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          <Block title="企业基本输入">
            <pre className={preClassName}>
              {JSON.stringify(context.company_input, null, 2)}
            </pre>
          </Block>
          <Block title="企业画像">
            <pre className={preClassName}>
              {JSON.stringify(context.company_profile, null, 2)}
            </pre>
          </Block>
          <Block title="商业画布诊断">
            <pre className={preClassName}>
              {JSON.stringify(context.canvas_diagnosis, null, 2)}
            </pre>
          </Block>
          <Block title="Top Scenarios">
            <pre className={preClassName}>
              {JSON.stringify(context.top_scenarios, null, 2)}
            </pre>
          </Block>
        </div>
      </div>

      <div className="rounded-[28px] border border-white/10 bg-slate-900/70 p-6">
        <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
          Report Outline
        </p>
        <h2 className="mt-3 text-2xl font-semibold text-white">
          下一步报告章节
        </h2>
        <ul className="mt-5 grid gap-3 text-sm leading-7 text-slate-200 md:grid-cols-2">
          {context.report_outline.map((item, index) => (
            <li
              key={item}
              className="rounded-2xl border border-white/8 bg-white/5 px-4 py-3"
            >
              {index + 1}. {item}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function Block({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-3xl border border-white/8 bg-slate-950/55 p-5">
      <p className="text-sm uppercase tracking-[0.18em] text-slate-400">
        {title}
      </p>
      <div className="mt-3">{children}</div>
    </div>
  );
}

const preClassName =
  "overflow-x-auto rounded-2xl bg-white/5 p-4 text-xs leading-6 text-slate-200";
