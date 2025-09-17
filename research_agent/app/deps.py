import logging


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    tavily_api_key: str = ""
    openrouter_api_key: str = ""
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.2
    openai_api_key: str | None = None  # allow OpenAI key if present

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()


# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ai-agents")
