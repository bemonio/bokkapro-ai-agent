"""Loads environment configuration and defines global constants."""

import os
from dotenv import load_dotenv

load_dotenv()

BOKKA_API_BASE_URL: str = os.getenv("BOKKA_API_BASE_URL", "https://api.bokkapro.com")
HTTP_TIMEOUT_SECONDS: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "15"))
HTTP_RETRY_ATTEMPTS: int = int(os.getenv("HTTP_RETRY_ATTEMPTS", "3"))
HTTP_RETRY_BACKOFF_SECONDS: float = float(
    os.getenv("HTTP_RETRY_BACKOFF_SECONDS", "0.5")
)
