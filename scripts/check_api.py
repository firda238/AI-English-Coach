"""Check OpenAI-compatible API configuration without printing secrets."""

from __future__ import annotations

import os
import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from api_client import api_mode_available, create_openai_client, current_openai_model, load_local_env


def main() -> int:
    parser = argparse.ArgumentParser(description="Check API mode configuration.")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Send one real API request. Omit this flag for a no-cost dry run.",
    )
    args = parser.parse_args()

    load_local_env()
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = current_openai_model()
    print(f"OPENAI_API_KEY: {'set' if api_mode_available() else 'missing'}")
    print(f"OPENAI_BASE_URL: {base_url}")
    print(f"OPENAI_MODEL: {model}")
    print(f"Mode: {'live request' if args.live else 'dry run'}")

    if not api_mode_available():
        print("API check skipped: OPENAI_API_KEY is missing.")
        return 1 if args.live else 0

    if not args.live:
        print("API dry run passed: configuration is present, no request was sent.")
        return 0

    try:
        client = create_openai_client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Reply with only: api ok"},
                {"role": "user", "content": "connection test"},
            ],
            temperature=0,
            max_tokens=8,
        )
        content = (response.choices[0].message.content or "").strip()
        print(f"API response: {content}")
        return 0
    except Exception as exc:
        print(f"API check failed: {type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
