"""Multi-turn scenario conversation orchestration."""

from __future__ import annotations

from datetime import datetime
from statistics import mean
from typing import Dict, List

from course_plan import get_course_steps
from feedback import build_turn_response

MIN_SUMMARY_ROUNDS = 5
MAX_TRAINING_ROUNDS = 8


def empty_session_state() -> Dict:
    """Return the default Streamlit-compatible conversation state."""
    return {
        "conversation_history": [],
        "feedback_history": [],
        "score_history": [],
        "current_round": 0,
        "current_stage": 0,
        "current_stage_key": "",
        "current_session_path": "",
        "session_started": False,
        "session_completed": False,
    }


def get_stage(scenario_key: str, round_index: int) -> Dict:
    """Return the stage for the given user-answer round."""
    steps = get_course_steps(scenario_key)
    return steps[min(max(round_index, 0), len(steps) - 1)]


def stage_progress(scenario_key: str, current_round: int) -> Dict:
    """Return current stage metadata for UI rendering."""
    steps = get_course_steps(scenario_key)
    stage_index = min(max(current_round, 0), len(steps) - 1)
    return {
        "steps": steps,
        "current_step": steps[stage_index],
        "current_index": stage_index,
        "progress": min(100, round((current_round / MIN_SUMMARY_ROUNDS) * 100)),
        "completed": current_round >= MIN_SUMMARY_ROUNDS,
    }


def build_opening_question(scenario_key: str, difficulty: str) -> str:
    """Create the AI's first proactive question."""
    stage = get_stage(scenario_key, 0)
    suffix = _difficulty_instruction(difficulty)
    return f"{stage['prompt']} {suffix}".strip()


def process_user_turn(
    user_text: str,
    scenario_key: str,
    scenario: Dict,
    difficulty: str,
    conversation_history: List[Dict],
    current_round: int,
    audio_used: bool = False,
    voice_profile: Dict | None = None,
) -> Dict:
    """Generate one full user-answer turn: follow-up, correction, and score."""
    stage = get_stage(scenario_key, current_round)
    next_stage = get_stage(scenario_key, current_round + 1)
    turn = build_turn_response(
        user_text,
        scenario,
        difficulty,
        conversation_history,
        audio_used=audio_used,
        voice_profile=voice_profile,
        stage=stage,
        next_stage=next_stage,
    )
    new_round = current_round + 1
    return {
        "turn": turn,
        "stage": stage,
        "next_stage": next_stage,
        "current_round": new_round,
        "current_stage": min(new_round, len(get_course_steps(scenario_key)) - 1),
        "session_completed": new_round >= MIN_SUMMARY_ROUNDS,
    }


def average_score(score_history: List[Dict]) -> int:
    scores = [item.get("total_score") for item in score_history if isinstance(item.get("total_score"), int)]
    return round(mean(scores)) if scores else 0


def build_session_record(
    scenario: Dict,
    difficulty: str,
    conversation_history: List[Dict],
    feedback_history: List[Dict],
    score_history: List[Dict],
    lesson_summary: str = "",
) -> Dict:
    """Build one JSON record for a complete multi-turn practice session."""
    latest_user = next((item.get("content", "") for item in reversed(conversation_history) if item.get("role") == "user"), "")
    latest_ai = next((item.get("content", "") for item in reversed(conversation_history) if item.get("role") == "assistant"), "")
    latest_feedback = feedback_history[-1] if feedback_history else {}
    latest_score = score_history[-1] if score_history else {}
    return {
        "time": datetime.now().isoformat(timespec="seconds"),
        "record_type": "multi_turn_session",
        "scenario": scenario["cn_label"],
        "difficulty": difficulty,
        "round_count": len(feedback_history),
        "overall_score": average_score(score_history),
        "conversation_history": conversation_history,
        "feedback_history": feedback_history,
        "score_history": score_history,
        "lesson_summary": lesson_summary,
        "user_input": latest_user,
        "ai_reply": latest_ai,
        "correction_feedback": latest_feedback,
        "score_result": latest_score,
    }


def history_for_summary(conversation_history: List[Dict]) -> List[Dict]:
    """Convert role-based messages into summary-friendly user/assistant turns."""
    turns: List[Dict] = []
    pending_user = ""
    for item in conversation_history:
        role = item.get("role")
        content = item.get("content", "")
        if role == "user":
            pending_user = content
        elif role == "assistant" and pending_user:
            turns.append({"user": pending_user, "assistant": content})
            pending_user = ""
    return turns


def _difficulty_instruction(difficulty: str) -> str:
    return {
        "简单": "Please answer in one or two simple sentences.",
        "中等": "Please add one reason or example.",
        "困难": "Please give a structured answer with a reason, example, and next step.",
    }.get(difficulty, "")
