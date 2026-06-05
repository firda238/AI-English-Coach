"""Verify repository-level delivery artifacts for competition review."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "app.py",
    "requirements.txt",
    "README.md",
    ".env.example",
    ".gitignore",
    "tests/test_core.py",
    "scripts/check_api.py",
    "scripts/smoke_test.py",
    "scripts/test_transcription.py",
    "docs/design_report.md",
    "docs/competition_demo_script.md",
    "docs/verification_checklist.md",
    "examples/sample_dialogue.json",
    "examples/sample_audio_note.md",
    "examples/test_meeting_audio.wav",
    "outputs/.gitkeep",
    "outputs/screenshot_voice_lab.png",
    "outputs/screenshot_browser_dictation.png",
    "outputs/screenshot_demo_session.png",
    "outputs/screenshot_coach_actions_full.png",
    "outputs/screenshot_competition_v1.png",
    "outputs/screenshot_competition_history.png",
    "outputs/screenshot_competition_stats.png",
    "outputs/screenshot_competition_export.png",
]


README_REQUIRED_TEXT = [
    "AI-English-Coach",
    "浏览器英文听写",
    "生成演示会话",
    "Coach Voice Lab",
    "pytest -q",
    "python scripts/smoke_test.py",
    "python scripts/check_api.py",
]


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (PROJECT_ROOT / path).exists()]
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    missing_readme_text = [text for text in README_REQUIRED_TEXT if text not in readme]

    if missing:
        print("Missing required delivery files:")
        for path in missing:
            print(f"- {path}")
    if missing_readme_text:
        print("README is missing required text:")
        for text in missing_readme_text:
            print(f"- {text}")

    if missing or missing_readme_text:
        return 1

    print("delivery verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
