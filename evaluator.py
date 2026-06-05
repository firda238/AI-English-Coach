"""Rule-based speaking evaluation for local demo mode."""

from __future__ import annotations

import re
from typing import Dict, List


SCORE_DIMENSIONS = [
    ("pronunciation", "Pronunciation 发音清晰度"),
    ("fluency", "Fluency 流利度"),
    ("grammar", "Grammar 语法准确度"),
    ("expression", "Expression 表达自然度"),
    ("completeness", "Completeness 回答完整度"),
]


def _bounded(value: int) -> int:
    return max(0, min(100, value))


def evaluate_speaking(
    user_text: str,
    correction_issues: List[str] | None = None,
    audio_used: bool = False,
    voice_profile: Dict | None = None,
) -> Dict:
    """Return five-dimension speaking scores with explanations.

    Pronunciation is simulated unless a real pronunciation service is added.
    When audio metadata is available, the score explanation reflects whether
    the user actually completed the voice-recognition flow.
    """

    correction_issues = correction_issues or []
    voice_profile = voice_profile or {}
    words = re.findall(r"[A-Za-z']+", user_text)
    word_count = len(words)
    sentence_count = max(1, len(re.findall(r"[.!?]", user_text)))
    avg_sentence_len = word_count / sentence_count
    transcript_success = bool(voice_profile.get("success")) or bool(audio_used and user_text.strip())
    confidence_label = voice_profile.get("confidence_label", "")

    grammar_penalty = min(35, len(correction_issues) * 8)
    length_penalty = 18 if word_count < 8 else 8 if word_count < 15 else 0
    fluency_penalty = 12 if avg_sentence_len < 5 else 0
    expression_penalty = 10 if len(set(w.lower() for w in words)) < max(4, word_count // 2) else 0

    audio_bonus = 7 if transcript_success else 0
    unclear_penalty = 8 if audio_used and confidence_label in {"unclear", "failed"} else 0
    pronunciation = 76 + audio_bonus - unclear_penalty - (10 if word_count < 5 else 0)
    fluency = 86 - length_penalty - fluency_penalty
    grammar = 90 - grammar_penalty
    expression = 84 - expression_penalty - (6 if word_count < 8 else 0)
    completeness = 88 - length_penalty + (4 if word_count >= 20 else 0)

    scores = {
        "pronunciation": {
            "label": "Pronunciation 发音清晰度",
            "score": _bounded(pronunciation),
            "explanation": _pronunciation_explanation(audio_used, transcript_success, voice_profile),
        },
        "fluency": {
            "label": "Fluency 流利度",
            "score": _bounded(fluency),
            "explanation": "回答较连贯。" if word_count >= 12 else "回答偏短，建议补充更多细节提升流利度。",
        },
        "grammar": {
            "label": "Grammar 语法准确度",
            "score": _bounded(grammar),
            "explanation": "语法整体可理解。" if not correction_issues else "存在可改进的语法或表达问题。",
        },
        "expression": {
            "label": "Expression 表达自然度",
            "score": _bounded(expression),
            "explanation": "表达基本自然。" if expression_penalty == 0 else "可加入更具体、更地道的表达。",
        },
        "completeness": {
            "label": "Completeness 回答完整度",
            "score": _bounded(completeness),
            "explanation": "回答包含较完整信息。" if word_count >= 15 else "回答信息量不足，建议加入原因、例子或结果。",
        },
    }

    total_score = round(sum(item["score"] for item in scores.values()) / len(scores))
    return {
        "total_score": total_score,
        "dimensions": scores,
        "voice_profile": {
            "audio_used": audio_used,
            "transcript_success": transcript_success,
            "engine": voice_profile.get("engine", "text"),
            "confidence_label": confidence_label or ("usable" if transcript_success else "text_only"),
        },
    }


def _pronunciation_explanation(audio_used: bool, transcript_success: bool, voice_profile: Dict) -> str:
    engine = voice_profile.get("engine", "")
    if not audio_used:
        return "本轮使用文本输入，发音分为模拟基准；建议用录音回答触发语音教练流程。"
    if transcript_success:
        engine_label = f"（{engine}）" if engine else ""
        return f"已完成语音识别{engine_label}，系统根据转写成功、回答长度和表达完整度给出本地模拟发音分；尚未接入真实音素级评测。"
    return "已检测到音频输入，但未成功转写；发音分为保守模拟值，建议重新录制清晰英文回答。"
