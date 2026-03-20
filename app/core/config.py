from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")
    telegram_manager_chat_id: str = Field(alias="TELEGRAM_MANAGER_CHAT_ID")

    supabase_url: str = Field(alias="SUPABASE_URL")
    supabase_key: str = Field(alias="SUPABASE_KEY")

    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(default="", alias="OPENROUTER_BASE_URL")
    openrouter_model: str = Field(default="", alias="OPENROUTER_MODEL")

    ai_enabled: bool = Field(default=False, alias="AI_ENABLED")
    ai_system_prompt: str = Field(default="", alias="AI_SYSTEM_PROMPT")

    app_env: str = Field(default="dev", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=10000, alias="APP_PORT")

    company_name: str = "Бетон Семей"
    city: str = "Семей"
    business_hours: str = "09:00-18:00"
    min_order_m3: float = 1.0
    has_delivery: bool = True
    has_pickup: bool = True
    has_pump: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()