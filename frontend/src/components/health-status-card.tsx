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
    const frontendOrigin = typeof window !== "undefined" ? window.location.origin : "N/A";

    setState({
      data: null,
      error: null,
      errorDetails: null,
      loading: true,
    });

    try {
      const response = await fetch(requestUrl, {
        cache: "no-store",
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
      const errorName = error instanceof Error ? error.constructor.name : "UnknownError";
      const errorMessage = error instanceof Error ? error.message : "Unknown request error";

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
    results.push(`Frontend Origin: ${typeof window !== "undefined" ? window.location.origin : "N/A"}`);
    results.push(`API Base URL: ${apiBaseUrl}`);
    results.push(`Test URL: ${apiBaseUrl}/health`);
    results.push("");
    
    try {
      results.push("Fetching...");
      const resp = await fetch(`${apiBaseUrl}/health`, { cache: "no-store" });
      results.push(`Response Status: ${resp.status}`);
      results.push(`Response OK: ${resp.ok}`);
      results.push(`Response Headers: ${JSON.stringify(Object.fromEntries(resp.headers.entries()), null, 2)}`);
      
      if (resp.ok) {
        const data = await resp.json();
        results.push(`Response Data: ${JSON.stringify(data, null, 2)}`);
      } else {
        const text = await resp.text();
        results.push(`Response Body: ${text}`);
      }
    } catch (err) {
      results.push(`Error Name: ${err instanceof Error ? err.constructor.name : typeof err}`);
      results.push(`Error Message: ${err instanceof Error ? err.message : String(err)}`);
      if (err instanceof Error && "cause" in err) {
        results.push(`Error Cause: ${String((err as Error & { cause?: unknown }).cause)}`);
      }
    }
    
    setDebugResult(results.join("\n"));
  }

  useEffect(() => {
    loadHealth();
  }, []);

  return (
    <div className="rounded-[28px] border border-white/10 bg-white/6 p-6 backdrop-blur">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Backend Connectivity
          </p>
          <p className="text-xs text-emerald-300 font-mono mt-1">
            DEBUG VERSION: health-check-v2
          </p>
          <p className="text-xs text-cyan-300 font-mono">
            API Base URL: {process.env.NEXT_PUBLIC_API_BASE_URL || "not set"}
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            基础健康检查
          </h2>
        </div>

        <span
          className={`inline-flex rounded-full px-3 py-1 text-sm font-medium ${
            state.loading
              ? "bg-slate-200/10 text-slate-200"
              : state.error
                ? "bg-rose-300/15 text-rose-100"
                : "bg-emerald-300/15 text-emerald-100"
          }`}
        >
          {state.loading ? "检查中" : state.error ? "请求失败" : "后端在线"}
        </span>
      </div>

      <div className="mt-6 rounded-3xl border border-white/8 bg-slate-950/55 p-5">
        <p className="text-sm text-slate-400">请求地址</p>
        <p className="mt-2 break-all font-mono text-sm text-cyan-100">
          {apiBaseUrl}/health
        </p>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-3">
        <Metric label="service" value={state.data?.service ?? "--"} />
        <Metric label="status" value={state.data?.status ?? "--"} />
        <Metric label="environment" value={state.data?.environment ?? "--"} />
      </div>

      {state.loading ? (
        <p className="mt-5 text-sm text-slate-300">
          正在从浏览器请求后端 `/health` 接口。
        </p>
      ) : null}

      {state.error ? (
        <div className="mt-5 space-y-3">
          <p className="text-sm text-rose-200">
            请求失败：{state.error}
          </p>
          {state.errorDetails && (
            <div className="rounded-3xl border border-rose-500/30 bg-rose-950/20 p-4">
              <p className="text-xs uppercase tracking-wide text-rose-300 mb-2">Debug Info</p>
              <div className="space-y-1 font-mono text-xs text-slate-300">
                <p>Error Type: <span className="text-rose-200">{state.errorDetails.name}</span></p>
                <p>Message: <span className="text-rose-200">{state.errorDetails.message}</span></p>
                <p>Request URL: <span className="text-cyan-200">{state.errorDetails.requestUrl}</span></p>
                <p>Frontend Origin: <span className="text-cyan-200">{state.errorDetails.frontendOrigin}</span></p>
                <p>API Base URL: <span className="text-cyan-200">{state.errorDetails.apiBaseUrl}</span></p>
              </div>
            </div>
          )}
        </div>
      ) : null}

      {/* Debug Button */}
      <div className="mt-5">
        <button
          onClick={runDebugTest}
          className="rounded-full border border-white/20 bg-white/5 px-4 py-2 text-sm text-slate-300 hover:bg-white/10 transition"
        >
          Run Debug Test
        </button>
        {debugResult && (
          <pre className="mt-3 overflow-x-auto rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-xs text-slate-300">
            {debugResult}
          </pre>
        )}
      </div>

      {state.data ? (
        <pre className="mt-5 overflow-x-auto rounded-3xl border border-white/8 bg-slate-950/70 p-5 text-sm text-slate-200">
          {JSON.stringify(state.data, null, 2)}
        </pre>
      ) : null}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-3xl border border-white/8 bg-white/5 p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
        {label}
      </p>
      <p className="mt-3 text-lg font-medium text-white">{value}</p>
    </div>
  );
}
