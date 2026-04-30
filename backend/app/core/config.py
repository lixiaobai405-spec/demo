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
        os.environ.setdefault(cleaned_key, cleaned_value)


load_env_file(ENV_FILE)


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Meitai AI Business Innovation Agent API")
    app_env: str = os.getenv("APP_ENV", "development")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3001")
    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}",
    )
    llm_mode: str = os.getenv("LLM_MODE", "mock").strip().lower()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    openai_base_url: str = os.getenv(
        "OPENAI_BASE_URL",
        "https://api.openai.com/v1",
    ).strip()
    openai_model: str = os.getenv("OPENAI_MODEL", "").strip()
    # RAG settings
    rag_enabled: bool = os.getenv("RAG_ENABLED", "false").strip().lower() == "true"
    chroma_persist_dir: str = os.getenv(
        "CHROMA_PERSIST_DIR",
        str(ROOT_DIR / "backend" / "data" / "chroma"),
    )
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    # LLM Report settings
    llm_report_enabled: bool = os.getenv("LLM_REPORT_ENABLED", "false").strip().lower() == "true"
    llm_report_timeout_seconds: int = int(os.getenv("LLM_REPORT_TIMEOUT_SECONDS", "60"))
    # Intake import settings
    intake_max_upload_size_mb: int = int(os.getenv("INTAKE_MAX_UPLOAD_SIZE_MB", "10"))
    intake_pdf_ocr_enabled: bool = (
        os.getenv("INTAKE_PDF_OCR_ENABLED", "true").strip().lower() == "true"
    )
    intake_pdf_ocr_min_text_chars: int = int(
        os.getenv("INTAKE_PDF_OCR_MIN_TEXT_CHARS", "20")
    )
    intake_pdf_ocr_max_pages: int = int(os.getenv("INTAKE_PDF_OCR_MAX_PAGES", "12"))


settings = Settings()
