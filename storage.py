"""JSON and Markdown persistence helpers."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

OUTPUT_DIR = Path("outputs")
ERROR_BOOK_FILE = "error_book.json"


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def timestamp_slug() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def save_practice_record(record: Dict) -> Path:
    ensure_output_dir()
    path = OUTPUT_DIR / f"practice_{timestamp_slug()}.json"
    with path.open("w", encoding="utf-8") as file:
        json.dump(record, file, ensure_ascii=False, indent=2)
    return path


def save_or_update_practice_record(record: Dict, path: str | Path | None = None) -> Path:
    """Create a new practice record or replace an existing one."""
    ensure_output_dir()
    if path:
        target = Path(path)
        if target.exists():
            with target.open("w", encoding="utf-8") as file:
                json.dump(record, file, ensure_ascii=False, indent=2)
            return target
    return save_practice_record(record)


def update_practice_record(path: str | Path, updates: Dict) -> None:
    target = Path(path)
    if not target.exists():
        return
    with target.open("r", encoding="utf-8") as file:
        data = json.load(file)
    data.update(updates)
    with target.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_practice_record(path: str | Path) -> Dict:
    """Load one saved practice record."""
    target = Path(path)
    with target.open("r", encoding="utf-8") as file:
        return json.load(file)


def delete_practice_record(path: str | Path) -> bool:
    """Delete one saved practice record if it exists."""
    target = Path(path)
    if not target.exists() or not target.name.startswith("practice_"):
        return False
    target.unlink()
    return True


def save_markdown_summary(markdown: str) -> Path:
    ensure_output_dir()
    path = OUTPUT_DIR / f"lesson_summary_{timestamp_slug()}.md"
    path.write_text(markdown, encoding="utf-8")
    return path


def error_book_path() -> Path:
    ensure_output_dir()
    return OUTPUT_DIR / ERROR_BOOK_FILE


def load_error_book() -> Dict:
    path = error_book_path()
    if not path.exists():
        return {"updated_at": "", "errors": []}
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, dict) and isinstance(data.get("errors"), list):
            return data
    except Exception:
        pass
    return {"updated_at": "", "errors": []}


def update_error_book(record: Dict) -> Path:
    """Append feedback issues from a session to the aggregate error book."""
    book = load_error_book()
    existing = book.get("errors", [])
    seen = {
        (
            item.get("scenario", ""),
            item.get("difficulty", ""),
            item.get("round", 0),
            item.get("issue", ""),
            item.get("original_sentence", ""),
            item.get("corrected_sentence", ""),
        )
        for item in existing
    }
    scenario = record.get("scenario", "未知")
    difficulty = record.get("difficulty", "未知")
    feedback_items = record.get("feedback_history") or [record.get("correction_feedback", {})]
    for index, feedback in enumerate(feedback_items, start=1):
        for issue in feedback.get("issue_explanation", []):
            if "No obvious grammar error" in issue or "本地规则未发现" in issue:
                continue
            entry = {
                "time": record.get("time", ""),
                "scenario": scenario,
                "difficulty": difficulty,
                "round": index,
                "issue": issue,
                "original_sentence": feedback.get("original_sentence", ""),
                "corrected_sentence": feedback.get("corrected_sentence", ""),
                "natural_expression": feedback.get("natural_expression", ""),
                "error_tags": feedback.get("error_tags", []),
            }
            key = (
                entry["scenario"],
                entry["difficulty"],
                entry["round"],
                entry["issue"],
                entry["original_sentence"],
                entry["corrected_sentence"],
            )
            if key in seen:
                continue
            seen.add(key)
            existing.append(entry)
    book = {"updated_at": datetime.now().isoformat(timespec="seconds"), "errors": existing[-200:]}
    path = error_book_path()
    with path.open("w", encoding="utf-8") as file:
        json.dump(book, file, ensure_ascii=False, indent=2)
    return path


def list_history_files(limit: int = 5) -> List[Path]:
    ensure_output_dir()
    return sorted(OUTPUT_DIR.glob("practice_*.json"), reverse=True)[:limit]


def list_all_history_files() -> List[Path]:
    """Return all saved practice records in newest-first order."""
    ensure_output_dir()
    return sorted(OUTPUT_DIR.glob("practice_*.json"), reverse=True)
