"""Audio transcription helpers with graceful fallback."""

from __future__ import annotations

import os
import tempfile
import wave
from importlib.util import find_spec
from typing import BinaryIO, Dict


SUPPORTED_AUDIO_TYPES = ["wav", "mp3", "m4a"]


def get_speech_runtime_status() -> Dict:
    """Report local speech-recognition capability without loading heavy models."""
    faster_whisper_available = find_spec("faster_whisper") is not None
    whisper_available = find_spec("whisper") is not None
    if faster_whisper_available:
        engine = "faster-whisper"
        ready = True
    elif whisper_available:
        engine = "whisper"
        ready = True
    else:
        engine = "not installed"
        ready = False

    return {
        "ready": ready,
        "engine": engine,
        "faster_whisper": faster_whisper_available,
        "whisper": whisper_available,
        "model_size": os.getenv("WHISPER_MODEL_SIZE", "base"),
        "install_hint": "pip install faster-whisper",
    }


def transcribe_audio(uploaded_file: BinaryIO) -> Dict:
    """Try to transcribe uploaded audio using optional local models.

    The app must keep running when speech libraries are unavailable. This
    function therefore returns a status dictionary instead of raising errors.
    """
    suffix = os.path.splitext(getattr(uploaded_file, "name", "audio.wav"))[1] or ".wav"
    runtime = get_speech_runtime_status()

    try:
        try:
            uploaded_file.seek(0)
        except Exception:
            pass
        audio_bytes = uploaded_file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name
        duration_seconds = _audio_duration_seconds(temp_path)
    except Exception as exc:
        return {
            "success": False,
            "text": "",
            "message": f"音频文件读取失败：{exc}",
            "engine": runtime["engine"],
            "audio_bytes": 0,
            "duration_seconds": None,
            "words_per_minute": None,
            "confidence_label": "failed",
            "coach_tip": "请重新录制一段更清晰的英文回答，或先使用文本输入。",
        }

    try:
        try:
            from faster_whisper import WhisperModel

            model_name = os.getenv("WHISPER_MODEL_SIZE", "base")
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
            segments, _ = model.transcribe(temp_path, language="en")
            text = " ".join(segment.text.strip() for segment in segments).strip()
            return {
                "success": bool(text),
                "text": text,
                "message": "已使用 faster-whisper 完成英文转写。" if text else "未识别到清晰英文内容。",
                "engine": "faster-whisper",
                "audio_bytes": len(audio_bytes),
                "duration_seconds": duration_seconds,
                "words_per_minute": _words_per_minute(text, duration_seconds),
                "confidence_label": "usable" if text else "unclear",
                "coach_tip": _coach_tip_for_transcript(text, duration_seconds),
            }
        except ImportError:
            pass

        try:
            import whisper

            model_name = os.getenv("WHISPER_MODEL_SIZE", "base")
            model = whisper.load_model(model_name)
            result = model.transcribe(temp_path, language="en")
            text = (result.get("text") or "").strip()
            return {
                "success": bool(text),
                "text": text,
                "message": "已使用 whisper 完成英文转写。" if text else "未识别到清晰英文内容。",
                "engine": "whisper",
                "audio_bytes": len(audio_bytes),
                "duration_seconds": duration_seconds,
                "words_per_minute": _words_per_minute(text, duration_seconds),
                "confidence_label": "usable" if text else "unclear",
                "coach_tip": _coach_tip_for_transcript(text, duration_seconds),
            }
        except ImportError:
            return {
                "success": False,
                "text": "",
                "message": "当前未安装 Whisper 语音模型，请安装 faster-whisper 后再进行真实语音识别；文本训练流程不受影响。",
                "engine": runtime["engine"],
                "audio_bytes": len(audio_bytes),
                "duration_seconds": duration_seconds,
                "words_per_minute": None,
                "confidence_label": "model_missing",
                "coach_tip": "比赛演示建议先运行 `pip install faster-whisper`，再用 `WHISPER_MODEL_SIZE=tiny.en streamlit run app.py` 启动。",
            }
    except Exception as exc:
        return {
            "success": False,
            "text": "",
            "message": f"语音转写不可用，已自动降级到文本输入模式：{exc}",
            "engine": runtime["engine"],
            "audio_bytes": len(audio_bytes),
            "duration_seconds": duration_seconds,
            "words_per_minute": None,
            "confidence_label": "failed",
            "coach_tip": "请确认音频格式为 wav/mp3/m4a，并尽量录制 5-20 秒清晰英文回答。",
        }
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass


def _audio_duration_seconds(path: str) -> float | None:
    """Return WAV duration when it can be read locally."""
    try:
        with wave.open(path, "rb") as audio:
            frame_count = audio.getnframes()
            frame_rate = audio.getframerate()
            if frame_rate <= 0:
                return None
            return round(frame_count / float(frame_rate), 2)
    except Exception:
        return None


def _words_per_minute(text: str, duration_seconds: float | None) -> int | None:
    if not text or not duration_seconds or duration_seconds <= 0:
        return None
    words = [word for word in text.split() if word.strip()]
    if not words:
        return None
    return round(len(words) / (duration_seconds / 60))


def _coach_tip_for_transcript(text: str, duration_seconds: float | None = None) -> str:
    if not text:
        return "没有识别到清晰英文内容。请靠近麦克风，放慢语速，再录一次。"
    word_count = len(text.split())
    wpm = _words_per_minute(text, duration_seconds)
    if wpm is not None and wpm < 80:
        return "转写成功，但语速偏慢。下一轮可以先想好关键词，再用更连贯的语速回答。"
    if wpm is not None and wpm > 180:
        return "转写成功，但语速偏快。下一轮请放慢一点，保证每个关键词清楚。"
    if word_count < 6:
        return "转写成功，但回答偏短。下一轮请补充一个原因或例子。"
    if word_count > 80:
        return "转写成功。回答信息较多，建议用 2-3 个重点组织表达。"
    return "转写成功。可以直接提交，也可以先检查文本后再提交。"
