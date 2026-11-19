"""Application settings, read from environment variables and the repository's .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# This file is backend/app/core/config.py, so parents[3] is the repository root, where .env lives.
ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_ignore_empty=True,
        extra="ignore",
        hide_input_in_errors=True,
    )

    PROJECT_NAME: str = "poe2-trade-agent"
    DATABASE_URL: str


settings = Settings()  # type: ignore[call-arg]  # pydantic-settings fills DATABASE_URL from the environment