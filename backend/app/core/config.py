import os
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"
DEFAULT_DATABASE_PATH = ROOT_DIR / "backend" / "data" / "meitai_demo.db"


def load_env_file(env_file: Path) -> None:
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        cleaned_key = key.strip()
        cleaned_value = value.strip().strip('"').strip("'")
        os.environ[cleaned_key] = cleaned_value


def _load_mykey() -> dict:
    """Load LLM credentials from <project_root>/mykey.py (optional, .gitignored).

    Falls back gracefully if the file doesn't exist or can't be imported.
    """
    import importlib.util

    mykey_path = ROOT_DIR / "mykey.py"
    if not mykey_path.exists():
        return {}

    try:
        spec = importlib.util.spec_from_file_location("mykey", str(mykey_path))
        if spec is None or spec.loader is None:
            return {}
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, "llm_config", {})
    except Exception:
        return {}


load_env_file(ENV_FILE)
_mykey = _load_mykey()


def _resolve(key: str, env_key: str, default) -> str:
    """.env takes precedence over mykey.py, mykey.py over default."""
    env_val = os.getenv(env_key)
    if env_val is not None and env_val != "":
        return env_val.strip()
    val = _mykey.get(key)
    if val is not None and val != "":
        return str(val).strip()
    return default.strip() if isinstance(default, str) else default


def _resolve_bool(key: str, env_key: str, default: bool) -> bool:
    env_val = os.getenv(env_key)
    if env_val is not None and env_val != "":
        return env_val.strip().lower() == "true"
    val = _mykey.get(key)
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() == "true"


def _resolve_int(key: str, env_key: str, default: int) -> int:
    env_val = os.getenv(env_key)
    if env_val is not None and env_val != "":
        return int(env_val)
    val = _mykey.get(key)
    return int(val) if val is not None else default


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Meitai AI Business Innovation Agent API")
    app_env: str = os.getenv("APP_ENV", "development")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3001")
    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}",
    )
    # .env takes precedence over mykey.py, mykey.py over default
    llm_mode: str = _resolve("llm_mode", "LLM_MODE", "mock").strip().lower()
    openai_api_key: str = _resolve("openai_api_key", "OPENAI_API_KEY", "").strip()
    openai_base_url: str = _resolve("openai_base_url", "OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    openai_model: str = _resolve("openai_model", "OPENAI_MODEL", "").strip()
    # RAG settings
    rag_enabled: bool = os.getenv("RAG_ENABLED", "false").strip().lower() == "true"
    chroma_persist_dir: str = os.getenv(
        "CHROMA_PERSIST_DIR",
        str(ROOT_DIR / "backend" / "data" / "chroma"),
    )
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    # LightRAG graph-enhanced retrieval (optional, replaces ChromaDB when enabled)
    lightrag_enabled: bool = (
        os.getenv("LIGHTRAG_ENABLED", "false").strip().lower() == "true"
    )
    lightrag_working_dir: str = os.getenv(
        "LIGHTRAG_WORKING_DIR",
        str(ROOT_DIR / "backend" / "data" / "lightrag"),
    )
    lightrag_top_k: int = int(os.getenv("LIGHTRAG_TOP_K", "5"))
    # LLM Report settings
    llm_report_enabled: bool = _resolve_bool("llm_report_enabled", "LLM_REPORT_ENABLED", False)
    llm_report_timeout_seconds: int = _resolve_int("llm_report_timeout_seconds", "LLM_REPORT_TIMEOUT_SECONDS", 60)
    # Intake import settings
    intake_max_upload_size_mb: int = int(os.getenv("INTAKE_MAX_UPLOAD_SIZE_MB", "10"))
    intake_pdf_ocr_enabled: bool = (
        os.getenv("INTAKE_PDF_OCR_ENABLED", "true").strip().lower() == "true"
    )
    intake_pdf_ocr_min_text_chars: int = int(
        os.getenv("INTAKE_PDF_OCR_MIN_TEXT_CHARS", "20")
    )
    intake_pdf_ocr_max_pages: int = int(os.getenv("INTAKE_PDF_OCR_MAX_PAGES", "12"))
    # JWT Auth settings
    jwt_secret_key: str = _resolve("jwt_secret_key", "JWT_SECRET_KEY", "meitai-demo-dev-secret-change-in-prod")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = _resolve_int("jwt_expire_minutes", "JWT_EXPIRE_MINUTES", 1440)


settings = Settings()


def reload_settings() -> None:
    """Re-read .env and mykey.py, then replace the global settings object."""
    global _mykey, settings
    load_env_file(ENV_FILE)
    _mykey = _load_mykey()
    settings = Settings()
