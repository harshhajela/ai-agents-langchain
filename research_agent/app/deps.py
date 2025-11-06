import logging
import os
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    tavily_api_key: SecretStr | None = None
    openrouter_api_key: SecretStr | None = None
    # Default to OpenRouter Grok Fast base model
    model_name: str = "x-ai/grok-4-fast"
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

# Allowed free models map: request values -> provider model identifiers
ALLOWED_FREE_MODELS: dict[str, str] = {
    "grok": "x-ai/grok-4-fast",
    "llama": "meta-llama/llama-3.1-8b-instruct:free",
    "deepseek": "deepseek/deepseek-chat:free",
    "google": "google/gemma-2-9b-it:free",
}


def resolve_model_name(request_model: str | None) -> str:
    """Resolve a request `model_name` to an allowed provider model string.

    - If `request_model` is None, fall back to env-configured `settings.model_name`.
    - If provided, it must be one of ALLOWED_FREE_MODELS keys.
    """
    if request_model is None:
        return settings.model_name
    key = request_model.lower()
    if key not in ALLOWED_FREE_MODELS:
        raise ValueError(
            "Model not allowed. Choose one of: grok, llama, deepseek, google"
        )
    return ALLOWED_FREE_MODELS[key]


# Order to try when the selected model fails at runtime (e.g. 404 on provider)
FALLBACK_ORDER: list[str] = ["llama", "deepseek", "google", "grok"]


def fallback_models(exclude_provider_id: str | None) -> list[str]:
    """Return a list of provider model IDs to try as fallbacks.

    Excludes the provided `exclude_provider_id` if present.
    """
    ordered = [
        ALLOWED_FREE_MODELS[k] for k in FALLBACK_ORDER if k in ALLOWED_FREE_MODELS
    ]
    if exclude_provider_id is None:
        return ordered
    return [m for m in ordered if m != exclude_provider_id]


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
