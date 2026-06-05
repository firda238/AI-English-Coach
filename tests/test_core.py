from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

import storage
from analytics import dimension_averages, error_frequency, filter_records, load_records, score_trend, summarize_records
from course_plan import get_course_steps, lesson_status, progress_percent
from conversation_engine import (
    MIN_SUMMARY_ROUNDS,
    build_opening_question,
    build_session_record,
    empty_session_state,
    history_for_summary,
    process_user_turn,
)
from evaluator import evaluate_speaking
from feedback import _extract_json_object, _normalize_api_turn, build_turn_response, local_correction
from input_utils import is_non_empty_input, normalize_user_input
from report_exporter import build_html_report, save_html_report
from report_generator import generate_lesson_summary
from scenarios import DIFFICULTIES, get_scenario, list_scenarios
from speech_utils import get_speech_runtime_status, transcribe_audio


class NamedBytesIO(io.BytesIO):
    def __init__(self, content: bytes, name: str) -> None:
        super().__init__(content)
        self.name = name


def assert_score_shape(score: dict) -> None:
    assert isinstance(score["total_score"], int)
    assert set(score["dimensions"]) == {
        "pronunciation",
        "fluency",
        "grammar",
        "expression",
        "completeness",
    }
    for item in score["dimensions"].values():
        assert 0 <= item["score"] <= 100
        assert item["label"]
        assert item["explanation"]


@pytest.mark.parametrize("scenario_key", list_scenarios())
def test_all_scenarios_generate_reply_feedback_and_score(monkeypatch, scenario_key):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    scenario = get_scenario(scenario_key)
    assert scenario["default_difficulty"] in DIFFICULTIES

    turn = build_turn_response(
        "I worked on a campus web project and explained the result clearly.",
        scenario,
        scenario["default_difficulty"],
        [],
    )

    assert turn["mode"] == "本地演示模式"
    assert turn["ai_reply"]
    assert turn["correction"]["corrected_sentence"]
    assert turn["correction"]["issue_explanation"]
    assert_score_shape(turn["score"])


def test_local_correction_required_rules():
    feedback = local_correction("i am agree we should discuss about this topic")

    assert "I agree" in feedback["corrected_sentence"]
    assert "discuss this topic" in feedback["corrected_sentence"]
    assert feedback["corrected_sentence"].endswith(".")
    assert len(feedback["issue_explanation"]) >= 3


def test_long_clean_text_feedback_is_structured_not_repeated():
    text = """My College Life

I am a college student majoring in computer science. Every day, I spend a lot of time studying programming, English, and professional courses. Sometimes I feel tired, but I know these skills are important for my future.

In my free time, I like running and working out. Exercise helps me relax and makes me feel more confident. I also try to improve my spoken English because I want to communicate better in interviews and daily life.

College life is not always easy. There are exams, projects, and many deadlines. However, I believe that if I keep learning step by step, I can become better. My goal is to improve both my technical skills and communication skills before graduation."""
    feedback = local_correction(text)

    assert not feedback["has_grammar_errors"]
    assert len(feedback["original_preview"]) < len(text)
    assert feedback["natural_expression"].startswith("Suggested spoken version:")
    assert any("Read aloud only the suggested spoken version" in item for item in feedback["practice_sentences"])
    assert "structure and speaking delivery" in " ".join(feedback["focus_points"])


def test_score_dimension_shape():
    correction = local_correction("He go")
    score = evaluate_speaking("He go", correction["issues"], audio_used=False)
    assert_score_shape(score)
    assert score["voice_profile"]["audio_used"] is False


def test_voice_score_profile_explains_transcription_flow():
    correction = local_correction("I agree with this proposal because it reduces risk.")
    score = evaluate_speaking(
        "I agree with this proposal because it reduces risk.",
        correction["issues"],
        audio_used=True,
        voice_profile={"success": True, "engine": "faster-whisper", "confidence_label": "usable"},
    )

    assert_score_shape(score)
    assert score["voice_profile"]["audio_used"] is True
    assert score["voice_profile"]["transcript_success"] is True
    assert "语音识别" in score["dimensions"]["pronunciation"]["explanation"]


def test_api_json_parsing_and_normalization():
    parsed = _extract_json_object(
        """```json
        {
          "ai_reply": "Could you give one specific example?",
          "corrected_sentence": "I agree with this idea.",
          "issue_explanation": ["Use 'I agree' instead of 'I am agree'."],
          "natural_expression": "I agree with this idea because it is practical.",
          "alternative_expressions": ["I agree because..."],
          "scores": {
            "pronunciation": {"score": 82, "explanation": "Clear enough for practice."},
            "fluency": {"score": 78, "explanation": "Some pauses are expected."},
            "grammar": {"score": 90, "explanation": "Grammar is mostly accurate."},
            "expression": {"score": 85, "explanation": "Expression is natural."},
            "completeness": {"score": 80, "explanation": "Add one example."}
          }
        }
        ```"""
    )
    assert parsed and parsed["ai_reply"]
    normalized = _normalize_api_turn("I am agree with this idea", parsed)

    assert normalized["correction"]["corrected_sentence"] == "I agree with this idea."
    assert normalized["correction"]["has_grammar_errors"]
    assert_score_shape(normalized["score"])


def test_empty_input_validation():
    assert normalize_user_input(None) == ""
    assert normalize_user_input("   ") == ""
    assert normalize_user_input("  hello  ") == "hello"
    assert not is_non_empty_input("")
    assert not is_non_empty_input("   ")
    assert is_non_empty_input("I agree.")


def test_course_plan_progress():
    steps = get_course_steps("meeting")
    assert len(steps) == 5
    assert progress_percent(2, 5) == 40
    status = lesson_status(3, "meeting")
    assert status["progress"] == 60
    assert status["current_step"]["title"] == "补充方案"
    assert not lesson_status(3, "meeting")["completed"]
    assert lesson_status(5, "meeting")["completed"]


def test_conversation_engine_runs_five_rounds(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    scenario = get_scenario("interview")
    state = empty_session_state()
    opening = build_opening_question("interview", "中等")
    assert "Please introduce yourself" in opening
    state["conversation_history"].append({"role": "assistant", "content": opening, "stage": "自我介绍"})
    state["session_started"] = True

    answers = [
        "I am a computer science student and I want to work as a developer.",
        "I built a campus web project with my classmates last semester.",
        "My main responsibility was to design the page and connect the data.",
        "The biggest challenge was time, so I made a simple plan.",
        "I believe I am a good fit because I learn fast and communicate clearly.",
    ]
    for answer in answers:
        result = process_user_turn(
            answer,
            "interview",
            scenario,
            "中等",
            state["conversation_history"],
            state["current_round"],
        )
        turn = result["turn"]
        state["conversation_history"].append({"role": "user", "content": answer, "stage": result["stage"]["title"]})
        state["conversation_history"].append(
            {"role": "assistant", "content": turn["ai_reply"], "stage": result["next_stage"]["title"]}
        )
        state["feedback_history"].append(turn["correction"])
        state["score_history"].append(turn["score"])
        state["current_round"] = result["current_round"]

    assert state["current_round"] == MIN_SUMMARY_ROUNDS
    assert len(history_for_summary(state["conversation_history"])) == MIN_SUMMARY_ROUNDS
    record = build_session_record(
        scenario,
        "中等",
        state["conversation_history"],
        state["feedback_history"],
        state["score_history"],
    )
    assert record["record_type"] == "multi_turn_session"
    assert record["round_count"] == MIN_SUMMARY_ROUNDS
    assert record["overall_score"] > 0


def test_summary_and_storage_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "OUTPUT_DIR", tmp_path)
    scenario = get_scenario("interview")
    turn = build_turn_response("I am agree about my project", scenario, "中等", [])
    history = [{"user": "I am agree about my project", "assistant": turn["ai_reply"]}]
    summary = generate_lesson_summary(history, scenario, "中等", turn["correction"], turn["score"])

    record_path = storage.save_practice_record(
        {
            "time": "2026-06-05T00:00:00",
            "scenario": scenario["cn_label"],
            "difficulty": "中等",
            "user_input": history[0]["user"],
            "ai_reply": history[0]["assistant"],
            "correction_feedback": turn["correction"],
            "score_result": turn["score"],
            "lesson_summary": "",
        }
    )
    storage.update_practice_record(record_path, {"lesson_summary": summary})
    loaded = storage.load_practice_record(record_path)
    summary_path = storage.save_markdown_summary(summary)

    assert loaded["lesson_summary"] == summary
    assert Path(summary_path).exists()
    assert json.loads(record_path.read_text(encoding="utf-8"))["scenario"] == scenario["cn_label"]
    assert storage.delete_practice_record(record_path)
    assert not record_path.exists()


def test_analytics_and_html_report(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "OUTPUT_DIR", tmp_path)
    scenario = get_scenario("meeting")
    turn = build_turn_response("I am agree we should discuss about this topic", scenario, "困难", [])
    summary = generate_lesson_summary(
        [{"user": "I am agree we should discuss about this topic", "assistant": turn["ai_reply"]}],
        scenario,
        "困难",
        turn["correction"],
        turn["score"],
    )
    first = storage.save_practice_record(
        {
            "time": "2026-06-05T00:00:00",
            "scenario": scenario["cn_label"],
            "difficulty": "困难",
            "user_input": "I am agree we should discuss about this topic",
            "ai_reply": turn["ai_reply"],
            "correction_feedback": turn["correction"],
            "score_result": turn["score"],
            "lesson_summary": summary,
        }
    )
    records = load_records([first])
    aggregate = summarize_records(records)

    assert aggregate["total_records"] == 1
    assert aggregate["summary_count"] == 1
    assert filter_records(records, scenario["cn_label"]) == records
    assert score_trend(records)[0]["score"] == turn["score"]["total_score"]
    assert dimension_averages(records)["grammar"] >= 0
    assert error_frequency(records)

    html = build_html_report(summary)
    assert "<html" in html and "AI 英语口语陪练课后总结" in html
    html_path = save_html_report(summary)
    assert html_path.exists()


def test_audio_fallback_shape_without_valid_audio():
    result = transcribe_audio(NamedBytesIO(b"not a real wav file", "demo.wav"))
    assert {"success", "text", "message", "engine", "confidence_label", "coach_tip"} <= set(result)
    assert isinstance(result["success"], bool)
    assert isinstance(result["text"], str)
    assert isinstance(result["message"], str)
    assert isinstance(result["coach_tip"], str)


def test_recorded_audio_object_can_be_reused_without_crashing():
    recorded = NamedBytesIO(b"not a real recorded wav file", "recorded_answer.wav")
    first = transcribe_audio(recorded)
    second = transcribe_audio(recorded)

    assert {"success", "text", "message", "engine", "confidence_label", "coach_tip"} <= set(first)
    assert {"success", "text", "message", "engine", "confidence_label", "coach_tip"} <= set(second)
    assert isinstance(second["message"], str)


def test_speech_runtime_status_shape():
    status = get_speech_runtime_status()
    assert set(status) == {
        "ready",
        "engine",
        "faster_whisper",
        "whisper",
        "model_size",
        "install_hint",
    }
    assert isinstance(status["ready"], bool)
