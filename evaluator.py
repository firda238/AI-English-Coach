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
) -> Dict:
    """Return five-dimension speaking scores with explanations.

    Pronunciation is simulated unless a real pronunciation service is added.
    The score is still useful for a course demo because it shows how the
    interface and data flow behave.
    """

    correction_issues = correction_issues or []
    words = re.findall(r"[A-Za-z']+", user_text)
    word_count = len(words)
    sentence_count = max(1, len(re.findall(r"[.!?]", user_text)))
    avg_sentence_len = word_count / sentence_count

    grammar_penalty = min(35, len(correction_issues) * 8)
    length_penalty = 18 if word_count < 8 else 8 if word_count < 15 else 0
    fluency_penalty = 12 if avg_sentence_len < 5 else 0
    expression_penalty = 10 if len(set(w.lower() for w in words)) < max(4, word_count // 2) else 0

    pronunciation = 78 + (6 if audio_used else 0) - (10 if word_count < 5 else 0)
    fluency = 86 - length_penalty - fluency_penalty
    grammar = 90 - grammar_penalty
    expression = 84 - expression_penalty - (6 if word_count < 8 else 0)
    completeness = 88 - length_penalty + (4 if word_count >= 20 else 0)

    scores = {
        "pronunciation": {
            "label": "Pronunciation 发音清晰度",
            "score": _bounded(pronunciation),
            "explanation": (
                "当前未接入真实发音评测，分数为模拟结果；如上传音频，可作为流程演示。"
                if not audio_used
                else "已使用音频输入流程，发音分数仍为本地模拟结果。"
            ),
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
    return {"total_score": total_score, "dimensions": scores}
