"""Configuration management using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Supabase
    supabase_url: str
    supabase_service_key: str

    # Research APIs
    exa_api_key: str | None = None
    brave_api_key: str | None = None  # Replaces SerpAPI - simpler, already in Claude Code
    tavily_api_key: str | None = None

    # AI
    anthropic_api_key: str

    # Image Generation (3-tier fallback)
    google_api_key: str | None = None  # Tier 1: Gemini
    glif_api_key: str | None = None  # Tier 2: Nano Banana Pro
    replicate_api_token: str | None = None  # Tier 3: Flux Schnell

    # Google Places API (UGC photos)
    google_places_api_key: str | None = None

    # Budget Controls
    daily_budget_limit: float = 5.00  # Daily API spend limit
    daily_budget_usd: float = 5.00  # Alias for compatibility
    alert_email: str | None = None

    # Agent Settings
    default_model: str = "claude-sonnet-4-20250514"  # Fast decisions
    content_model: str = "claude-opus-4-5-20251101"  # Quality content
    max_retries: int = 3
    request_timeout: int = 60

    # Vercel (for ISR revalidation)
    vercel_url: str | None = None
    vercel_revalidate_token: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience alias
settings = get_settings()
