"""Configuration loader using environment variables."""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from the environment or .env file."""

    api_base_url: str = "https://api.example.com"
    api_key: str = "changeme"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
