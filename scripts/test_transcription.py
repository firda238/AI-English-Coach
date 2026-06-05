"""Run a local transcription check against the sample audio file."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from speech_utils import transcribe_audio


def main() -> int:
    os.environ.setdefault("WHISPER_MODEL_SIZE", "tiny.en")
    audio_path = PROJECT_ROOT / "examples" / "test_meeting_audio.wav"
    if not audio_path.exists():
        print(f"Missing sample audio: {audio_path}")
        return 1

    with audio_path.open("rb") as file:
        result = transcribe_audio(file)

    print(f"success: {result['success']}")
    print(f"message: {result['message']}")
    print(f"text: {result['text']}")
    return 0 if result["success"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
