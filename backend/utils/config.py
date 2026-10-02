"""Reads settings from environment variables (.env in the project root)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def get_api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()


def get_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()


def get_allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
    return [o.strip() for o in raw.split(",") if o.strip()]
