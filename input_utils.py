"""Input validation helpers."""

from __future__ import annotations


def normalize_user_input(value: str | None) -> str:
    """Trim user text and handle None safely."""
    return (value or "").strip()


def is_non_empty_input(value: str | None) -> bool:
    """Return True when the user provided usable text."""
    return bool(normalize_user_input(value))
