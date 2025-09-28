import logging
import os
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    tavily_api_key: SecretStr | None = None
    openrouter_api_key: SecretStr | None = None
    model_name: str = "x-ai/grok-4-fast:free"
    temperature: float = 0.2
    openai_api_key: SecretStr | None = None  # allow OpenAI key if present

    # Google Sheets (simple env loading)
    google_service_account_json: str | None = None
    gspread_sheet_id: str | None = None
    gspread_worksheet: str = "history"

    # Logging
    log_dir: str = "/var/log/ai-agents"
    log_level: str = "INFO"
    log_rotation_when: str = "midnight"
    log_rotation_backup_count: int = 7

    # Persistence toggle
    persist_results: bool = True

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()


def configure_logging() -> logging.Logger:
    from logging.handlers import TimedRotatingFileHandler

    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Ensure log directory exists (works in container too)
    try:
        os.makedirs(settings.log_dir, exist_ok=True)
    except Exception:
        # Fall back to current directory if not permitted
        fallback_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(fallback_dir, exist_ok=True)
        settings.log_dir = fallback_dir

    logger = logging.getLogger("ai-agents")
    logger.setLevel(level)
    logger.handlers.clear()

    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # Rotating file handler
    file_path = os.path.join(settings.log_dir, "app.log")
    fh = TimedRotatingFileHandler(
        file_path,
        when=settings.log_rotation_when,
        backupCount=settings.log_rotation_backup_count,
    )
    fh.setLevel(level)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logger.info(f"Logging initialized at level {settings.log_level} -> {file_path}")
    return logger


logger = configure_logging()
