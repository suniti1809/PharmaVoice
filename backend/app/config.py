"""Application configuration.

Every knob the app needs is read from the environment (see `.env.example`) so the
same image can run locally, in Docker, or in CI without code changes.
"""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# On Vercel the only writable directory is /tmp, so SQLite has to live there.
_ON_VERCEL = bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))
_DEFAULT_DB = "sqlite:////tmp/pharmavoice.db" if _ON_VERCEL else "sqlite:///./pharmavoice.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "PharmaVoice - AI Customer Complaint Management System"

    # --- Database -----------------------------------------------------------
    # SQLite by default so the app runs with zero setup, locally and on Vercel.
    # Point DATABASE_URL at Postgres to use a real server instead, e.g.
    # postgresql+psycopg2://pharmavoice:pharmavoice@localhost:5432/pharmavoice
    database_url: str = _DEFAULT_DB

    # Insert two historical complaints on first boot so the register is not
    # empty and duplicate detection has something to match against.
    auto_seed: bool = True

    # --- Groq / LLM ---------------------------------------------------------
    groq_api_key: str = ""

    # The assignment mandates gemma2-9b-it for extraction and mentions
    # llama-3.3-70b-versatile for longer context. Groq has since decommissioned
    # both ids, so each role keeps the mandated model first and falls back to a
    # model that is currently served. See app/agents/llm.py for the walk logic.
    groq_model: str = "gemma2-9b-it"
    groq_model_fallbacks: str = "openai/gpt-oss-20b,qwen/qwen3.8-27b"
    groq_reasoning_model: str = "llama-3.3-70b-versatile"
    groq_reasoning_fallbacks: str = "openai/gpt-oss-120b,openai/gpt-oss-20b"

    llm_temperature: float = 0.1
    llm_max_retries: int = 2

    # --- Uploads ------------------------------------------------------------
    max_upload_mb: int = 10
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @staticmethod
    def _chain(primary: str, fallbacks: str) -> list[str]:
        ordered = [primary.strip(), *(f.strip() for f in fallbacks.split(","))]
        seen: set[str] = set()
        return [m for m in ordered if m and not (m in seen or seen.add(m))]

    @property
    def extraction_chain(self) -> list[str]:
        return self._chain(self.groq_model, self.groq_model_fallbacks)

    @property
    def reasoning_chain(self) -> list[str]:
        return self._chain(self.groq_reasoning_model, self.groq_reasoning_fallbacks)

    @property
    def llm_enabled(self) -> bool:
        """When no key is configured the graph falls back to a rule-based path.

        This keeps the demo runnable offline instead of returning a 500.
        """
        return bool(self.groq_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
