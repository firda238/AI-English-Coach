"""OpenAI-compatible API client configuration."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_local_env() -> None:
    """Load simple KEY=VALUE pairs from .env without overwriting shell env."""
    if not ENV_FILE.exists():
        return
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def api_mode_available() -> bool:
    """Return True when an API key is present in the current environment."""
    load_local_env()
    return bool(os.getenv("OPENAI_API_KEY"))


def current_openai_model() -> str:
    """Return the configured chat model name."""
    load_local_env()
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def create_openai_client():
    """Create an OpenAI SDK client, optionally using an OpenAI-compatible base URL."""
    load_local_env()
    from openai import OpenAI

    base_url = os.getenv("OPENAI_BASE_URL", "").strip()
    if base_url:
        return OpenAI(base_url=base_url)
    return OpenAI()
