"""Audio transcription helpers with graceful fallback."""

from __future__ import annotations

import os
import tempfile
from typing import BinaryIO, Dict


SUPPORTED_AUDIO_TYPES = ["wav", "mp3", "m4a"]


def transcribe_audio(uploaded_file: BinaryIO) -> Dict:
    """Try to transcribe uploaded audio using optional local models.

    The app must keep running when speech libraries are unavailable. This
    function therefore returns a status dictionary instead of raising errors.
    """
    suffix = os.path.splitext(getattr(uploaded_file, "name", "audio.wav"))[1] or ".wav"

    try:
        try:
            uploaded_file.seek(0)
        except Exception:
            pass
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            temp_audio.write(uploaded_file.read())
            temp_path = temp_audio.name
    except Exception as exc:
        return {"success": False, "text": "", "message": f"音频文件读取失败：{exc}"}

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
            }
        except ImportError:
            return {
                "success": False,
                "text": "",
                "message": "当前为演示模式，请使用文本输入或示例转写文本。",
            }
    except Exception as exc:
        return {
            "success": False,
            "text": "",
            "message": f"语音转写不可用，已自动降级到文本输入模式：{exc}",
        }
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass
