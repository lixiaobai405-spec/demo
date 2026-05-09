#!/usr/bin/env python3
"""
Smoke Pipeline — minimal frontend-backend connectivity detection.

Checks (in order):
  1. Backend /health endpoint
  2. Frontend root page
  3. Frontend proxy / API path reachability
  4. Backend CORS preflight (OPTIONS)
  5. Browser runtime fetch (via Playwright, SKIP if not installed)

Usage:
  python tools/smoke_pipeline.py
  python tools/smoke_pipeline.py --backend-url http://localhost:8000 --frontend-url http://localhost:3001

Environment variables:
  SMOKE_BACKEND_URL   — override backend URL (default http://localhost:8000)
  SMOKE_FRONTEND_URL  — override frontend URL (default http://localhost:3001)
  SMOKE_TIMEOUT       — request timeout in seconds (default 10)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.client import HTTPConnection, HTTPSConnection, HTTPResponse
from typing import Optional

# ── Config ──────────────────────────────────────────────────────────
def _parse_args() -> tuple[str, str, int]:
    """Parse --backend-url / --frontend-url / --timeout from argv, then env, then defaults."""
    backend = os.environ.get("SMOKE_BACKEND_URL", "http://localhost:8000")
    frontend = os.environ.get("SMOKE_FRONTEND_URL", "http://localhost:3001")
    timeout = int(os.environ.get("SMOKE_TIMEOUT", "10"))

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--backend-url" and i + 1 < len(args):
            backend = args[i + 1]; i += 2
        elif args[i] == "--frontend-url" and i + 1 < len(args):
            frontend = args[i + 1]; i += 2
        elif args[i] == "--timeout" and i + 1 < len(args):
            timeout = int(args[i + 1]); i += 2
        elif args[i] in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        else:
            i += 1
    return backend, frontend, timeout


BACKEND_URL, FRONTEND_URL, TIMEOUT = _parse_args()

# ── Failure tiers ───────────────────────────────────────────────────
FAIL_BACKEND_DOWN = "BACKEND_DOWN_OR_WRONG_PORT"
FAIL_FRONTEND_DOWN = "FRONTEND_DOWN_OR_WRONG_PORT"
FAIL_PROXY_API = "FRONTEND_PROXY_OR_API_PATH_FAILURE"
FAIL_BROWSER = "BROWSER_RUNTIME_CONNECTIVITY_FAILURE"

_COMMON_HEADERS = {"ngrok-skip-browser-warning": "true"}


# ── Helpers ─────────────────────────────────────────────────────────
class Result:
    __slots__ = ("name", "status", "detail", "failure_tier")

    def __init__(self, name: str) -> None:
        self.name = name
        self.status = "PASS"  # PASS | FAIL | WARN | SKIP
        self.detail = ""
        self.failure_tier: Optional[str] = None


_results: list[Result] = []


def http_get(url: str) -> tuple[int, bytes]:
    """GET *url*, return (status, body_bytes).  Raises ConnectionError on network failure."""
    req = urllib.request.Request(url, headers=_COMMON_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:  # type: ignore[arg-type]
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except urllib.error.URLError as e:
        raise ConnectionError(f"Cannot reach {url}: {e.reason}") from e


def _http_conn(url: str) -> HTTPConnection:
    """Return an HTTPConnection or HTTPSConnection for *url*."""
    p = urllib.parse.urlparse(url)
    if p.scheme == "https":
        return HTTPSConnection(p.hostname, p.port or 443, timeout=TIMEOUT)
    return HTTPConnection(p.hostname, p.port or 80, timeout=TIMEOUT)


def http_options(url: str) -> tuple[int, dict[str, str]]:
    """Send OPTIONS preflight request.  Returns (status, headers_dict)."""
    conn = _http_conn(url)
    try:
        conn.request(
            "OPTIONS",
            urllib.parse.urlparse(url).path or "/",
            headers={
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "GET",
                **_COMMON_HEADERS,
            },
        )
        resp: HTTPResponse = conn.getresponse()
        return resp.status, {k.lower(): v for k, v in resp.getheaders()}
    finally:
        conn.close()


# ── Checks ──────────────────────────────────────────────────────────
def check_backend_health() -> None:
    """1. Backend Health — GET /health must return {"status":"ok",...}."""
    r = Result("1. Backend Health")
    url = f"{BACKEND_URL}/health"
    try:
        status, body = http_get(url)
    except ConnectionError as e:
        r.status = "FAIL"
        r.detail = str(e)
        r.failure_tier = FAIL_BACKEND_DOWN
        _results.append(r)
        return

    if status != 200:
        r.status = "FAIL"
        r.detail = f"GET {url} → HTTP {status} (expected 200)"
        r.failure_tier = FAIL_BACKEND_DOWN
        _results.append(r)
        return

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        r.status = "FAIL"
        r.detail = f"GET {url} → HTTP 200 but response is not valid JSON"
        r.failure_tier = FAIL_BACKEND_DOWN
        _results.append(r)
        return

    svc = data.get("service", "?")
    env = data.get("environment", "?")
    st = data.get("status", "?")
    if st == "ok":
        r.status = "PASS"
        r.detail = f"Backend healthy — status=ok, service={svc}, env={env}"
    else:
        r.status = "WARN"
        r.detail = f"Backend reachable but /health status={st!r} (expected 'ok'), service={svc}, env={env}"
    _results.append(r)


def check_frontend_root() -> None:
    """2. Frontend Root — GET / must return HTTP 200 (HTML)."""
    r = Result("2. Frontend Root")
    try:
        status, body = http_get(FRONTEND_URL)
    except ConnectionError as e:
        r.status = "FAIL"
        r.detail = str(e)
        r.failure_tier = FAIL_FRONTEND_DOWN
        _results.append(r)
        return

    if status == 200:
        r.status = "PASS"
        r.detail = f"Frontend serving at {FRONTEND_URL} (HTTP 200, {len(body)} bytes)"
    else:
        r.status = "FAIL"
        r.detail = f"GET {FRONTEND_URL} → HTTP {status} (expected 200)"
        r.failure_tier = FAIL_FRONTEND_DOWN
    _results.append(r)


def check_frontend_proxy() -> None:
    """3. Frontend Proxy / API Path.

    The frontend uses NEXT_PUBLIC_API_BASE_URL to reach the backend directly from
    the browser (no Next.js rewrite proxy).  This check verifies that the
    configured API base URL is reachable from the machine running the smoke test.
    """
    r = Result("3. Frontend Proxy / API Path")

    # First, verify the backend is reachable at the configured URL
    url = f"{BACKEND_URL}/health"
    try:
        status, body = http_get(url)
    except ConnectionError:
        env_val = os.environ.get("NEXT_PUBLIC_API_BASE_URL", "")
        if env_val:
            r.status = "FAIL"
            r.detail = (
                f"Cannot reach API base URL {BACKEND_URL}. "
                f"NEXT_PUBLIC_API_BASE_URL={env_val}. "
                "Is the backend running at this address?"
            )
            r.failure_tier = FAIL_PROXY_API
        else:
            r.status = "FAIL"
            r.detail = (
                f"Cannot reach API base URL {BACKEND_URL}. "
                "NEXT_PUBLIC_API_BASE_URL is not set (using default). "
                "Is the backend running?"
            )
            r.failure_tier = FAIL_PROXY_API
        _results.append(r)
        return

    if status == 200:
        r.status = "PASS"
        r.detail = f"API base URL reachable: {BACKEND_URL} → backend /health OK. "
        r.detail += "(Note: project uses direct browser-to-backend fetch, no Next.js proxy.)"
    elif 400 <= status < 500:
        r.status = "WARN"
        r.detail = f"API base URL {BACKEND_URL} responds (HTTP {status}) but /health is not 200. Check backend routes."
    else:
        r.status = "FAIL"
        r.detail = f"API base URL {BACKEND_URL} reachable but /health returned HTTP {status}"
        r.failure_tier = FAIL_PROXY_API
    _results.append(r)


def check_cors_preflight() -> None:
    """4. Backend CORS Preflight — OPTIONS /health must return CORS headers."""
    r = Result("4. Backend CORS Preflight")
    try:
        # Quick liveness check first
        http_get(f"{BACKEND_URL}/health")
    except ConnectionError as e:
        r.status = "SKIP"
        r.detail = f"Backend not reachable, skipping CORS check ({e})"
        _results.append(r)
        return

    url = f"{BACKEND_URL}/health"
    try:
        status, headers = http_options(url)
    except Exception as e:
        r.status = "FAIL"
        r.detail = f"OPTIONS preflight request failed: {e}"
        r.failure_tier = FAIL_PROXY_API
        _results.append(r)
        return

    acao = headers.get("access-control-allow-origin", "")
    acam = headers.get("access-control-allow-methods", "")

    if not acao:
        r.status = "FAIL"
        r.detail = (
            f"CORS preflight failed: OPTIONS {url} → HTTP {status}, "
            f"no Access-Control-Allow-Origin header. "
            f"Browser requests from {FRONTEND_URL} will be blocked."
        )
        r.failure_tier = FAIL_PROXY_API
    elif acao == "*":
        r.status = "PASS"
        r.detail = f"CORS allows all origins (Access-Control-Allow-Origin: *), Methods: {acam or '(none)'}"
    elif FRONTEND_URL in acao or _origin_matches(acao, FRONTEND_URL):
        r.status = "PASS"
        r.detail = f"CORS allows frontend origin {FRONTEND_URL}, Methods: {acam or '(none)'}"
    else:
        r.status = "FAIL"
        r.detail = (
            f"CORS misconfigured: Access-Control-Allow-Origin={acao!r}, "
            f"but frontend origin is {FRONTEND_URL}. Browser requests will be blocked."
        )
        r.failure_tier = FAIL_PROXY_API
    _results.append(r)


def _origin_matches(acao_value: str, origin: str) -> bool:
    """Check whether *origin* matches a value in a comma-separated ACAO header."""
    for part in acao_value.split(","):
        if part.strip() == origin:
            return True
    return False


def check_browser_runtime() -> None:
    """5. Browser Runtime Fetch — real browser fetch to backend /health."""
    r = Result("5. Browser Runtime Fetch")

    # Check if playwright is installed
    try:
        from importlib import import_module
        import_module("playwright")
    except ImportError:
        r.status = "SKIP"
        r.detail = "Playwright not installed. Install: pip install playwright && playwright install chromium"
        _results.append(r)
        return

    # Check if chromium is installed for playwright
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        r.status = "SKIP"
        r.detail = f"Playwright found but cannot import sync_api: {e}"
        _results.append(r)
        return

    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as e:
                r.status = "SKIP"
                r.detail = f"Playwright found but cannot launch chromium: {e}. Run: playwright install chromium"
                _results.append(r)
                return

            page = browser.new_page()
            health_url = f"{BACKEND_URL}/health"

            result_js: dict = page.evaluate(
                """
                async (url) => {
                    try {
                        const resp = await fetch(url, {
                            headers: { 'ngrok-skip-browser-warning': 'true' }
                        });
                        const data = await resp.json();
                        return { ok: true, status: resp.status, data: data };
                    } catch (e) {
                        return { ok: false, error: e.message, name: e.name };
                    }
                }
                """,
                health_url,
            )
            browser.close()

            if result_js.get("ok"):
                data = result_js.get("data", {})
                r.status = "PASS"
                r.detail = (
                    f"Browser fetch OK — backend /health → "
                    f"status={data.get('status','?')}, service={data.get('service','?')}"
                )
            else:
                r.status = "FAIL"
                r.detail = (
                    f"Browser fetch failed: {result_js.get('error','?')} "
                    f"({result_js.get('name','')}). "
                    f"Check CORS config — origin may not be allowed for {BACKEND_URL}."
                )
                r.failure_tier = FAIL_BROWSER
    except Exception as e:
        r.status = "FAIL"
        r.detail = f"Playwright runtime error: {e}"
        r.failure_tier = FAIL_BROWSER

    _results.append(r)


# ── Main ────────────────────────────────────────────────────────────
def main() -> None:
    print()
    print("=" * 64)
    print("  Smoke Pipeline — Frontend-Backend Connectivity")
    print(f"  Backend  : {BACKEND_URL}")
    print(f"  Frontend : {FRONTEND_URL}")
    print("=" * 64)
    print()

    # Run all checks in dependency order
    check_backend_health()
    check_frontend_root()
    check_frontend_proxy()
    check_cors_preflight()
    check_browser_runtime()

    # ── Summary ──────────────────────────────────────────────────
    stats = {"PASS": 0, "FAIL": 0, "WARN": 0, "SKIP": 0}
    for r in _results:
        stats[r.status] += 1

    print()
    print("-" * 64)
    for r in _results:
        icon = {"PASS": "PASS", "FAIL": "FAIL", "WARN": "WARN", "SKIP": "SKIP"}[r.status]
        tag = f"[{icon}]"
        print(f"  {tag:<7s}  {r.name}")
        if r.detail:
            print(f"           {r.detail}")
        if r.failure_tier:
            print(f"           TIER → {r.failure_tier}")
    print("-" * 64)
    print(f"  PASS: {stats['PASS']}  FAIL: {stats['FAIL']}  WARN: {stats['WARN']}  SKIP: {stats['SKIP']}")
    print("-" * 64)

    if stats["FAIL"] > 0:
        tiers = [r.failure_tier for r in _results if r.failure_tier]
        if tiers:
            print(f"  Failure tier(s): {', '.join(tiers)}")
        print()
        sys.exit(1)
    else:
        print("  OK")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
