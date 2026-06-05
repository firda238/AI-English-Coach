"""Smoke test core AI-English-Coach flows without launching Streamlit."""

from __future__ import annotations

import io
import json
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import storage
from conversation_engine import (
    MIN_SUMMARY_ROUNDS,
    average_score,
    build_opening_question,
    build_session_record,
    history_for_summary,
    process_user_turn,
)
from report_generator import generate_lesson_summary
from scenarios import DIFFICULTIES, get_scenario, list_scenarios
from speech_utils import transcribe_audio


class NamedBytesIO(io.BytesIO):
    def __init__(self, content: bytes, name: str) -> None:
        super().__init__(content)
        self.name = name


def assert_score_shape(score: dict) -> None:
    expected_dimensions = {"pronunciation", "fluency", "grammar", "expression", "completeness"}
    assert isinstance(score.get("total_score"), int)
    assert set(score.get("dimensions", {})) == expected_dimensions
    for item in score["dimensions"].values():
        assert 0 <= item["score"] <= 100
        assert item["label"]
        assert item["explanation"]


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        storage.OUTPUT_DIR = Path(temp_dir)

        for scenario_key in list_scenarios():
            scenario = get_scenario(scenario_key)
            difficulty = scenario["default_difficulty"]
            assert difficulty in DIFFICULTIES

            conversation_history = [
                {
                    "role": "assistant",
                    "content": build_opening_question(scenario_key, difficulty),
                    "stage": "opening",
                }
            ]
            feedback_history = []
            score_history = []
            answers = [
                "I am a computer science student and I want to improve my spoken English.",
                "I worked on a campus web project and explained the result clearly.",
                "My main responsibility was to design the page and connect the data.",
                "The biggest challenge was time, so I made a plan and tested each part.",
                "I believe this practice helps me speak more clearly and confidently.",
            ]
            current_round = 0
            for answer in answers:
                result = process_user_turn(
                    answer,
                    scenario_key,
                    scenario,
                    difficulty,
                    conversation_history,
                    current_round,
                )
                turn = result["turn"]
                assert turn["ai_reply"]
                assert turn["correction"]["corrected_sentence"]
                assert turn["correction"]["issue_explanation"]
                assert_score_shape(turn["score"])
                conversation_history.append({"role": "user", "content": answer, "stage": result["stage"]["title"]})
                conversation_history.append(
                    {"role": "assistant", "content": turn["ai_reply"], "stage": result["next_stage"]["title"]}
                )
                feedback_history.append(turn["correction"])
                score_history.append(turn["score"])
                current_round = result["current_round"]

            assert current_round == MIN_SUMMARY_ROUNDS
            history = history_for_summary(conversation_history)
            combined_feedback = {
                "issue_explanation": [
                    issue for feedback in feedback_history for issue in feedback.get("issue_explanation", [])
                ]
            }
            combined_score = {"total_score": average_score(score_history)}
            summary = generate_lesson_summary(history, scenario, difficulty, combined_feedback, combined_score)
            assert summary.startswith("# AI 英语口语陪练课后总结")
            assert scenario["cn_label"] in summary
            assert "## 对话轮数" in summary
            assert "## 推荐表达" in summary

            record = build_session_record(
                scenario,
                difficulty,
                conversation_history,
                feedback_history,
                score_history,
                summary,
            )
            record_path = storage.save_or_update_practice_record(record)
            storage.update_error_book(record)
            saved = json.loads(record_path.read_text(encoding="utf-8"))
            assert saved["record_type"] == "multi_turn_session"
            assert saved["round_count"] == MIN_SUMMARY_ROUNDS
            assert len(saved["conversation_history"]) == 11
            assert saved["lesson_summary"] == summary

        error_book = storage.load_error_book()
        assert isinstance(error_book.get("errors"), list)

        audio_result = transcribe_audio(NamedBytesIO(b"not a real wav file", "demo.wav"))
        assert {"success", "text", "message", "engine", "confidence_label", "coach_tip"} <= set(audio_result)
        assert isinstance(audio_result["success"], bool)
        assert isinstance(audio_result["message"], str)

    print("smoke test passed")


if __name__ == "__main__":
    main()
