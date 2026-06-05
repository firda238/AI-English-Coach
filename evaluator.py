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
    duration_seconds = voice_profile.get("duration_seconds")
    words_per_minute = voice_profile.get("words_per_minute")

    grammar_penalty = min(35, len(correction_issues) * 8)
    length_penalty = 18 if word_count < 8 else 8 if word_count < 15 else 0
    fluency_penalty = 12 if avg_sentence_len < 5 else 0
    rate_penalty = _speech_rate_penalty(words_per_minute)
    expression_penalty = 10 if len(set(w.lower() for w in words)) < max(4, word_count // 2) else 0

    audio_bonus = 7 if transcript_success else 0
    unclear_penalty = 8 if audio_used and confidence_label in {"unclear", "failed"} else 0
    pronunciation = 76 + audio_bonus - unclear_penalty - (10 if word_count < 5 else 0)
    fluency = 86 - length_penalty - fluency_penalty - rate_penalty
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
            "explanation": _fluency_explanation(word_count, words_per_minute),
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
        "coach_actions": _build_coach_actions(scores, word_count, correction_issues, audio_used, words_per_minute),
        "voice_profile": {
            "audio_used": audio_used,
            "transcript_success": transcript_success,
            "engine": voice_profile.get("engine", "text"),
            "confidence_label": confidence_label or ("usable" if transcript_success else "text_only"),
            "duration_seconds": duration_seconds,
            "words_per_minute": words_per_minute,
        },
    }


def _pronunciation_explanation(audio_used: bool, transcript_success: bool, voice_profile: Dict) -> str:
    engine = voice_profile.get("engine", "")
    duration_seconds = voice_profile.get("duration_seconds")
    words_per_minute = voice_profile.get("words_per_minute")
    if not audio_used:
        return "本轮使用文本输入，发音分为模拟基准；建议用录音回答触发语音教练流程。"
    if transcript_success:
        engine_label = f"（{engine}）" if engine else ""
        metric_text = ""
        if duration_seconds and words_per_minute:
            metric_text = f"录音约 {duration_seconds} 秒，估算语速 {words_per_minute} WPM。"
        return f"已完成语音识别{engine_label}，{metric_text}系统根据转写成功、回答长度和表达完整度给出本地模拟发音分；尚未接入真实音素级评测。"
    return "已检测到音频输入，但未成功转写；发音分为保守模拟值，建议重新录制清晰英文回答。"


def _speech_rate_penalty(words_per_minute: int | None) -> int:
    if words_per_minute is None:
        return 0
    if words_per_minute < 70 or words_per_minute > 190:
        return 10
    if words_per_minute < 90 or words_per_minute > 170:
        return 5
    return 0


def _fluency_explanation(word_count: int, words_per_minute: int | None) -> str:
    if words_per_minute is not None:
        if words_per_minute < 70:
            return f"估算语速 {words_per_minute} WPM，偏慢；建议提前准备关键词，减少停顿。"
        if words_per_minute > 190:
            return f"估算语速 {words_per_minute} WPM，偏快；建议放慢语速，让关键词更清楚。"
        if 90 <= words_per_minute <= 170:
            return f"估算语速 {words_per_minute} WPM，整体接近自然口语节奏。"
        return f"估算语速 {words_per_minute} WPM，基本可理解，但还可以更稳定。"
    return "回答较连贯。" if word_count >= 12 else "回答偏短，建议补充更多细节提升流利度。"


def _build_coach_actions(
    scores: Dict,
    word_count: int,
    correction_issues: List[str],
    audio_used: bool,
    words_per_minute: int | None,
) -> List[str]:
    actions: List[str] = []
    dimension_scores = {
        key: item.get("score", 0)
        for key, item in scores.items()
        if isinstance(item, dict)
    }
    weakest = sorted(dimension_scores.items(), key=lambda item: item[1])[:2]
    weak_keys = {key for key, _ in weakest}

    if "grammar" in weak_keys or correction_issues:
        actions.append("先朗读修改后句子一遍，再用自己的话重新回答同一个问题。")
    if "completeness" in weak_keys or word_count < 15:
        actions.append("下一轮回答至少包含三部分：观点、原因、一个具体例子。")
    if "expression" in weak_keys:
        actions.append("选择一个推荐替代表达，直接套入下一轮回答。")
    if audio_used and words_per_minute is not None:
        if words_per_minute < 90:
            actions.append("语速偏慢时，先写下 3 个关键词，再连续说完一句完整回答。")
        elif words_per_minute > 170:
            actions.append("语速偏快时，每个句子结尾停顿半秒，突出关键词。")
    elif not audio_used:
        actions.append("下一轮建议使用录音回答，系统会记录语音识别状态和语速指标。")

    if not actions:
        actions.append("保持当前表达方式，下一轮加入一个更具体的例子提升说服力。")
    return actions[:3]
