"""Application configuration helpers.

Small helper to centralize environment variables used by the app.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    google_api_key: str | None = os.getenv("GOOGLE_API_KEY")
    disable_llm: bool = os.getenv("DISABLE_LLM", "false").lower() in ("1", "true", "yes")
    chromedriver_path: str | None = os.getenv("CHROMEDRIVER_PATH")
    streamlit_port: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))


settings = Settings()
