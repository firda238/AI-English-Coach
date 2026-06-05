"""AI reply generation and grammar feedback."""

from __future__ import annotations

import json
import re
from typing import Dict, List, Tuple

from api_client import api_mode_available, create_openai_client, current_openai_model
from evaluator import evaluate_speaking


def _sentence_case(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def _ensure_period(text: str) -> str:
    if not text:
        return text
    return text if text[-1] in ".!?" else f"{text}."


def _preview_text(text: str, limit: int = 260) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[:limit].rstrip() + "..."


def _split_sentences(text: str) -> List[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]


def _extract_json_object(content: str) -> Dict | None:
    """Parse JSON even when a model wraps it in Markdown fences."""
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        parsed = json.loads(cleaned[start : end + 1])
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _coerce_list(value, fallback: List[str] | None = None, limit: int = 6) -> List[str]:
    fallback = fallback or []
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        return items[:limit] or fallback
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return fallback


def _bounded_score(value, default: int = 75) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        score = default
    return max(0, min(100, score))


def _build_expression_suggestions(corrected: str, word_count: int, has_errors: bool) -> Dict:
    sentences = _split_sentences(corrected)
    suggestions: List[str] = []
    alternatives: List[str] = []
    focus_points: List[str] = []

    if word_count >= 80:
        focus_points.extend(
            [
                "This is a complete paragraph-level answer, so the feedback focuses on structure and speaking delivery.",
                "For oral practice, split the answer into shorter spoken chunks instead of reading the whole essay at once.",
            ]
        )
        suggestions.extend(
            [
                "Use a clearer speaking structure: background -> challenge -> action -> goal.",
                "Add one concrete example, such as a project, interview experience, or English practice result.",
                "End with a stronger interview-style conclusion about what you can contribute.",
            ]
        )
        alternatives.extend(
            [
                "One specific example is that I built a small programming project and learned how to solve problems step by step.",
                "Before graduation, I want to improve my technical skills and communicate my ideas more confidently in English.",
                "These experiences make me better prepared for interviews and teamwork.",
            ]
        )
    elif word_count >= 20:
        suggestions.extend(
            [
                "The answer is understandable. Add one specific example to make it more convincing.",
                "Use transition phrases such as 'for example', 'however', and 'as a result'.",
            ]
        )
        alternatives.extend(
            [
                "For example, I practiced English by answering interview questions every week.",
                "As a result, I became more confident when explaining my ideas.",
            ]
        )
    elif not has_errors:
        suggestions.append("No major grammar issue was found. Try adding more detail to make the answer complete.")
        alternatives.append("For example, I can explain one reason and one result more clearly.")

    if not suggestions:
        suggestions.append("Fix the grammar issue first, then say the corrected sentence aloud.")
    if not alternatives:
        alternatives.append("Try using a complete sentence with a reason and an example.")

    natural_expression = corrected
    if word_count >= 80:
        natural_expression = (
            "Suggested spoken version: I am a computer science student. I spend much of my time learning "
            "programming, English, and professional courses. Although college life can be stressful, I keep "
            "improving step by step. My goal is to strengthen both my technical skills and communication skills "
            "so that I can perform better in interviews and future teamwork."
        )
    elif word_count >= 20:
        natural_expression = corrected
    elif word_count >= 6 and has_errors:
        natural_expression = corrected

    return {
        "natural_expression": natural_expression,
        "expression_suggestions": suggestions,
        "alternative_expressions": alternatives[:4],
        "focus_points": focus_points,
    }


def local_correction(user_text: str) -> Dict:
    """Apply lightweight demo correction rules."""
    corrected = user_text.strip()
    issues: List[str] = []
    alternatives: List[str] = []
    error_tags: List[str] = []

    rules: List[Tuple[str, str, str, str, str]] = [
        (
            r"\bI am agree\b",
            "I agree",
            "'I am agree' is incorrect because 'agree' is a verb.",
            "I agree with this idea.",
            "verb_usage",
        ),
        (
            r"\bdiscuss about\b",
            "discuss",
            "'Discuss' is a transitive verb, so it does not need 'about'.",
            "We should discuss this topic.",
            "collocation",
        ),
        (
            r"\bHe go\b",
            "He goes",
            "Use third-person singular verb form after 'He'.",
            "He goes to work early.",
            "subject_verb_agreement",
        ),
        (
            r"\bI has\b",
            "I have",
            "Use 'have' after the subject 'I'.",
            "I have experience in this area.",
            "subject_verb_agreement",
        ),
        (
            r"\bmore better\b",
            "better",
            "'Better' is already comparative, so it does not need 'more'.",
            "This solution is better for our team.",
            "comparative",
        ),
        (
            r"\ba lot of risk\b",
            "many risks",
            "Use 'many risks' for countable plural nouns.",
            "There are many risks we should consider.",
            "countable_noun",
        ),
    ]

    for pattern, replacement, explanation, alternative, tag in rules:
        if re.search(pattern, corrected, flags=re.IGNORECASE):
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
            issues.append(explanation)
            alternatives.append(alternative)
            error_tags.append(tag)

    if re.search(r"\bwant to\s+(food|coffee|tea|water|rice|noodles|beef|chicken|a [A-Za-z]+)\b", corrected, flags=re.IGNORECASE):
        issues.append("When 'want to' is followed by a noun, use 'want' or 'would like' instead.")
        alternatives.append("I would like some coffee.")
        error_tags.append("word_choice")

    if corrected and corrected[0].islower():
        corrected = _sentence_case(corrected)
        issues.append("Start an English sentence with a capital letter.")
        error_tags.append("capitalization")

    if corrected and corrected[-1] not in ".!?":
        corrected = _ensure_period(corrected)
        issues.append("End a complete sentence with proper punctuation.")
        error_tags.append("punctuation")

    word_count = len(re.findall(r"[A-Za-z']+", corrected))
    if word_count < 6:
        issues.append("The sentence is too short for speaking practice; add details, reasons, or examples.")
        alternatives.append("Could you add one reason or one example to make the answer more complete?")
        error_tags.append("completeness")

    expression_feedback = _build_expression_suggestions(corrected, word_count, bool(issues))
    if alternatives:
        expression_feedback["alternative_expressions"] = alternatives[:4]

    return {
        "original_sentence": user_text,
        "corrected_sentence": corrected or user_text,
        "original_preview": _preview_text(user_text),
        "corrected_preview": _preview_text(corrected or user_text),
        "has_grammar_errors": bool(issues),
        "issue_explanation": issues or ["No obvious grammar error was found by the local rule checker."],
        "natural_expression": expression_feedback["natural_expression"],
        "expression_suggestions": expression_feedback["expression_suggestions"],
        "focus_points": expression_feedback["focus_points"],
        "alternative_expressions": expression_feedback["alternative_expressions"],
        "practice_sentences": build_practice_sentences(error_tags, corrected, word_count),
        "error_tags": sorted(set(error_tags)),
        "issues": issues,
    }


def build_practice_sentences(error_tags: List[str], corrected: str, word_count: int = 0) -> List[str]:
    """Return short follow-up drills based on detected error types."""
    drills = {
        "verb_usage": "Write one sentence with 'I agree that...'.",
        "collocation": "Write one sentence with 'We should discuss...'.",
        "subject_verb_agreement": "Write one sentence using 'he/she + verb-s'.",
        "word_choice": "Rewrite the request with 'I would like...'.",
        "capitalization": "Copy the corrected sentence with the first letter capitalized.",
        "punctuation": "Copy the corrected sentence and add proper punctuation.",
        "completeness": "Add one reason and one example to make the answer longer.",
        "comparative": "Write one sentence using 'better' without 'more'.",
        "countable_noun": "Write one sentence using a plural countable noun such as 'risks'.",
    }
    selected = [drills[tag] for tag in sorted(set(error_tags)) if tag in drills]
    if not selected:
        selected = [
            "Add one specific example to your answer.",
            "Use one linking word such as because, therefore, or for example.",
        ]
    if corrected:
        if word_count >= 80:
            selected.append("Read aloud only the suggested spoken version, not the whole essay.")
        else:
            selected.append(f"Read aloud: {_preview_text(corrected, 180)}")
    return selected[:5]


def local_ai_reply(
    user_text: str,
    scenario: Dict,
    difficulty: str,
    history: List[Dict],
    stage: Dict | None = None,
    next_stage: Dict | None = None,
) -> str:
    """Generate a varied fallback role-play reply."""
    text = user_text.lower()
    replies = []
    if next_stage:
        replies.extend(
            [
                f"Thanks. Now let's move to {next_stage['title']}: {next_stage['prompt']}",
                f"Good. For the next part, {next_stage['prompt']}",
                f"Let's go deeper. {next_stage['prompt']}",
            ]
        )
    replies.extend(scenario["fallback_replies"])

    if "project" in text or "experience" in text:
        replies.append("Could you describe your role in that experience and what result you achieved?")
    if "responsible" in text or "role" in text or "task" in text:
        replies.append("What was one concrete action you personally took, and why was it important?")
    if "risk" in text or "problem" in text:
        replies.append("That risk is important. What solution would you suggest?")
    if "challenge" in text or "difficult" in text or "hard" in text:
        replies.append("How did you handle that challenge, and what did you learn from it?")
    if "drink" in text or "food" in text or "order" in text:
        replies.append("Certainly. Would you like that for here or to go?")
    if "spicy" in text or "allergy" in text or "allergic" in text or "prefer" in text:
        replies.append("No problem. Could you confirm your preference one more time?")
    if "agree" in text or "suggest" in text:
        replies.append("I see. Could you support your opinion with one specific reason?")
    if "because" in text or "reason" in text:
        replies.append("That reason is clear. What would be the next action based on it?")
    if stage and stage.get("evaluation_focus"):
        replies.append(f"Please add more detail. Focus on this point: {stage['evaluation_focus']}")

    difficulty_suffix = {
        "简单": " Please answer in one or two simple sentences.",
        "中等": " Please add one reason or example.",
        "困难": " Please give a structured answer with a reason, example, and next step.",
    }.get(difficulty, "")

    index = (len(history) + sum(ord(c) for c in user_text)) % len(replies)
    return replies[index] + difficulty_suffix


def _try_openai_turn(
    user_text: str,
    scenario: Dict,
    difficulty: str,
    history: List[Dict],
    audio_used: bool = False,
    stage: Dict | None = None,
    next_stage: Dict | None = None,
) -> Dict | None:
    if not api_mode_available():
        return None

    try:
        client = create_openai_client()
        model = current_openai_model()
        compact_history = []
        for item in history[-8:]:
            if "role" in item:
                compact_history.append({"role": item.get("role", ""), "content": item.get("content", "")})
            else:
                compact_history.append({"user": item.get("user", ""), "assistant": item.get("assistant", "")})
        prompt = {
            "scenario": scenario["label"],
            "scenario_cn": scenario.get("cn_label", scenario["label"]),
            "ai_role": scenario["ai_role"],
            "user_goal": scenario.get("user_goal", ""),
            "difficulty": difficulty,
            "current_stage": stage,
            "next_stage": next_stage,
            "history": compact_history,
            "user_text": user_text,
            "audio_used": audio_used,
            "task": (
                "Act as a realistic English speaking role-play partner and coach. "
                "First continue the scenario with one natural follow-up question based on the user's answer, "
                "the current stage, and the next stage. Do not repeat recent questions. "
                "Then provide correction and scoring. Return only one JSON object with keys: "
                "ai_reply, corrected_sentence, issue_explanation, natural_expression, "
                "expression_suggestions, focus_points, alternative_expressions, practice_sentences, "
                "error_tags, scores. scores must include pronunciation, fluency, grammar, "
                "expression, completeness; each score item must include score and explanation. "
                "Keep ai_reply under 35 English words. Keep explanations concise and useful for Chinese learners."
            ),
        }
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior English speaking coach for a competition-grade training app. "
                        "You must return valid JSON only. The AI reply must stay in role. "
                        "Corrections should be practical for spoken English, not academic essay feedback. "
                        "Scores must be integers from 0 to 100 with one short explanation each."
                    ),
                },
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
            temperature=0.7,
            max_tokens=1400,
        )
        content = response.choices[0].message.content or ""
        parsed = _extract_json_object(content)
        if not parsed or not parsed.get("ai_reply"):
            return None
        return parsed
    except Exception:
        return None


def _normalize_api_turn(
    user_text: str,
    api_result: Dict,
    audio_used: bool = False,
    voice_profile: Dict | None = None,
) -> Dict:
    corrected_sentence = str(api_result.get("corrected_sentence") or user_text).strip() or user_text
    issue_explanation = _coerce_list(
        api_result.get("issue_explanation"),
        ["No obvious grammar error was found, but the answer can still be improved for spoken English."],
    )
    detected_issues = [
        issue for issue in issue_explanation if not issue.lower().startswith("no obvious grammar error")
    ]
    alternatives = _coerce_list(
        api_result.get("alternative_expressions"),
        ["Try adding one clear reason and one concrete example."],
        limit=5,
    )
    practice_sentences = _coerce_list(
        api_result.get("practice_sentences"),
        [f"Read aloud: {_preview_text(corrected_sentence, 180)}"],
        limit=5,
    )
    correction = {
        "original_sentence": user_text,
        "corrected_sentence": corrected_sentence,
        "original_preview": _preview_text(user_text),
        "corrected_preview": _preview_text(corrected_sentence),
        "has_grammar_errors": bool(detected_issues),
        "issue_explanation": issue_explanation,
        "natural_expression": str(api_result.get("natural_expression") or corrected_sentence),
        "expression_suggestions": _coerce_list(
            api_result.get("expression_suggestions"),
            ["Make the answer more specific and easier to say aloud."],
            limit=5,
        ),
        "focus_points": _coerce_list(api_result.get("focus_points"), [], limit=4),
        "alternative_expressions": alternatives,
        "practice_sentences": practice_sentences,
        "error_tags": _coerce_list(api_result.get("error_tags"), [], limit=6),
        "issues": detected_issues,
    }

    raw_scores = api_result.get("scores", {})
    dimensions = {}
    for key, label in [
        ("pronunciation", "Pronunciation 发音清晰度"),
        ("fluency", "Fluency 流利度"),
        ("grammar", "Grammar 语法准确度"),
        ("expression", "Expression 表达自然度"),
        ("completeness", "Completeness 回答完整度"),
    ]:
        item = raw_scores.get(key, {}) if isinstance(raw_scores, dict) else {}
        dimensions[key] = {
            "label": label,
            "score": _bounded_score(item.get("score"), 75),
            "explanation": str(item.get("explanation") or "Generated by API mode."),
        }

    if not isinstance(raw_scores, dict) or not raw_scores:
        return {
            "correction": correction,
            "score": evaluate_speaking(user_text, correction.get("issues", []), audio_used, voice_profile),
        }
    total = round(sum(item["score"] for item in dimensions.values()) / len(dimensions))
    return {"correction": correction, "score": {"total_score": total, "dimensions": dimensions}}


def build_turn_response(
    user_text: str,
    scenario: Dict,
    difficulty: str,
    history: List[Dict],
    audio_used: bool = False,
    voice_profile: Dict | None = None,
    stage: Dict | None = None,
    next_stage: Dict | None = None,
) -> Dict:
    """Build AI reply, correction feedback, and score for one user turn."""
    api_result = _try_openai_turn(user_text, scenario, difficulty, history, audio_used, stage, next_stage)
    if api_result:
        normalized = _normalize_api_turn(user_text, api_result, audio_used, voice_profile)
        return {
            "mode": "API 模式",
            "ai_reply": api_result["ai_reply"],
            "correction": normalized["correction"],
            "score": normalized["score"],
        }

    correction = local_correction(user_text)
    return {
        "mode": "本地演示模式",
        "ai_reply": local_ai_reply(user_text, scenario, difficulty, history, stage, next_stage),
        "correction": correction,
        "score": evaluate_speaking(user_text, correction.get("issues", []), audio_used, voice_profile),
    }
