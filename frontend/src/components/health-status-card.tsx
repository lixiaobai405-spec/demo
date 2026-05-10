"use client";

import { useEffect, useState } from "react";

import { apiBaseUrl } from "@/lib/api";

type HealthResponse = {
  status: string;
  service: string;
  environment: string;
};

type RequestState = {
  data: HealthResponse | null;
  error: string | null;
  errorDetails: {
    name: string;
    message: string;
    requestUrl: string;
    frontendOrigin: string;
    apiBaseUrl: string;
  } | null;
  loading: boolean;
};

export function HealthStatusCard() {
  const [state, setState] = useState<RequestState>({
    data: null,
    error: null,
    errorDetails: null,
    loading: true,
  });

  const [debugResult, setDebugResult] = useState<string | null>(null);

  async function loadHealth() {
    const requestUrl = `${apiBaseUrl}/health`;
    const frontendOrigin =
      typeof window !== "undefined" ? window.location.origin : "N/A";

    setState({
      data: null,
      error: null,
      errorDetails: null,
      loading: true,
    });

    try {
      const response = await fetch(requestUrl, {
        cache: "no-store",
        headers: { "ngrok-skip-browser-warning": "true" },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data: HealthResponse = await response.json();

      setState({
        data,
        error: null,
        errorDetails: null,
        loading: false,
      });
    } catch (error) {
      const errorName =
        error instanceof Error ? error.constructor.name : "UnknownError";
      const errorMessage =
        error instanceof Error ? error.message : "Unknown request error";

      setState({
        data: null,
        error: errorMessage,
        errorDetails: {
          name: errorName,
          message: errorMessage,
          requestUrl,
          frontendOrigin,
          apiBaseUrl,
        },
        loading: false,
      });
    }
  }

  async function runDebugTest() {
    setDebugResult("Testing...");

    const results: string[] = [];
    results.push(
      `Frontend Origin: ${typeof window !== "undefined" ? window.location.origin : "N/A"}`,
    );
    results.push(`API Base URL: ${apiBaseUrl}`);
    results.push(`Test URL: ${apiBaseUrl}/health`);
    results.push("");

    try {
      results.push("Fetching...");
      const resp = await fetch(`${apiBaseUrl}/health`, {
        cache: "no-store",
        headers: { "ngrok-skip-browser-warning": "true" },
      });
      results.push(`Response Status: ${resp.status}`);
      results.push(`Response OK: ${resp.ok}`);
      results.push(
        `Response Headers: ${JSON.stringify(Object.fromEntries(resp.headers.entries()), null, 2)}`,
      );

      if (resp.ok) {
        const data = await resp.json();
        results.push(`Response Data: ${JSON.stringify(data, null, 2)}`);
      } else {
        const text = await resp.text();
        results.push(`Response Body: ${text}`);
      }
    } catch (err) {
      results.push(
        `Error Name: ${err instanceof Error ? err.constructor.name : typeof err}`,
      );
      results.push(
        `Error Message: ${err instanceof Error ? err.message : String(err)}`,
      );
      if (err instanceof Error && "cause" in err) {
        results.push(
          `Error Cause: ${String((err as Error & { cause?: unknown }).cause)}`,
        );
      }
    }

    setDebugResult(results.join("\n"));
  }

  useEffect(() => {
    loadHealth();
  }, []);

  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">健康检查</p>
          <p className="mt-0.5 font-mono text-xs text-warm-muted">
            API Base: {process.env.NEXT_PUBLIC_API_BASE_URL || "not set"}
          </p>
          <h2 className="section-heading">基础健康检查</h2>
        </div>

        <span
          className={`badge ${
            state.loading
              ? "badge-muted"
              : state.error
                ? "badge-danger"
                : "badge-success"
          }`}
        >
          {state.loading ? "检查中" : state.error ? "请求失败" : "后端在线"}
        </span>
      </div>

      <div className="mt-6 rounded-xl border border-warm-border-light bg-warm-inset px-4 py-3">
        <p className="text-xs text-warm-muted">请求地址</p>
        <p className="mt-1 break-all font-mono text-sm text-warm-accent">
          {apiBaseUrl}/health
        </p>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <Metric label="service" value={state.data?.service ?? "--"} />
        <Metric label="status" value={state.data?.status ?? "--"} />
        <Metric label="environment" value={state.data?.environment ?? "--"} />
      </div>

      {state.loading ? (
        <p className="mt-4 text-sm text-warm-secondary">
          正在从浏览器请求后端 /health 接口。
        </p>
      ) : null}

      {state.error ? (
        <div className="mt-4 space-y-3">
          <p className="text-sm text-warm-danger">请求失败：{state.error}</p>
          {state.errorDetails && (
            <div className="rounded-xl border border-red-200 bg-red-50/60 p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-warm-danger">
                Debug Info
              </p>
              <div className="mt-2 space-y-1 font-mono text-xs text-warm-secondary">
                <p>
                  Error Type:{" "}
                  <span className="text-warm-danger">
                    {state.errorDetails.name}
                  </span>
                </p>
                <p>
                  Message:{" "}
                  <span className="text-warm-danger">
                    {state.errorDetails.message}
                  </span>
                </p>
                <p>
                  Request URL:{" "}
                  <span className="text-warm-accent">
                    {state.errorDetails.requestUrl}
                  </span>
                </p>
                <p>
                  Frontend Origin:{" "}
                  <span className="text-warm-accent">
                    {state.errorDetails.frontendOrigin}
                  </span>
                </p>
                <p>
                  API Base URL:{" "}
                  <span className="text-warm-accent">
                    {state.errorDetails.apiBaseUrl}
                  </span>
                </p>
              </div>
            </div>
          )}
        </div>
      ) : null}

      <details className="mt-4 group">
        <summary className="cursor-pointer list-none text-xs text-warm-muted hover:text-warm-text transition-colors">
          ▶ 开发者工具
        </summary>
        <div className="mt-3">
          <button onClick={runDebugTest} className="btn-secondary text-xs">
            Run Debug Test
          </button>
          {debugResult && (
            <pre className="mt-3 overflow-x-auto rounded-xl border border-warm-border-light bg-warm-inset p-4 font-mono text-xs text-warm-secondary leading-relaxed">
              {debugResult}
            </pre>
          )}
        </div>

        {state.data ? (
          <pre className="mt-4 overflow-x-auto rounded-xl border border-warm-border-light bg-warm-inset p-4 font-mono text-sm text-warm-secondary leading-relaxed">
            {JSON.stringify(state.data, null, 2)}
          </pre>
        ) : null}
      </details>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-warm-border-light bg-warm-surface px-4 py-3">
      <p className="text-xs uppercase tracking-[0.16em] text-warm-muted">
        {label}
      </p>
      <p className="mt-2 text-lg font-medium text-warm-text">{value}</p>
    </div>
  );
}
