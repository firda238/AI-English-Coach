"""Streamlit app for AI English speaking practice."""

from __future__ import annotations

import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from analytics import dimension_averages, error_frequency, filter_records, load_records, score_trend, summarize_records
from conversation_engine import (
    MAX_TRAINING_ROUNDS,
    MIN_SUMMARY_ROUNDS,
    average_score,
    build_demo_session,
    build_opening_question,
    build_session_record,
    empty_session_state,
    history_for_summary,
    process_user_turn,
    stage_progress,
)
from feedback import api_mode_available
from input_utils import normalize_user_input
from report_exporter import save_html_report
from report_generator import generate_lesson_summary
from scenarios import DIFFICULTIES, get_scenario, list_scenarios, scenario_label
from speech_utils import SUPPORTED_AUDIO_TYPES, get_speech_runtime_status, transcribe_audio
from storage import (
    delete_practice_record,
    list_all_history_files,
    list_history_files,
    load_error_book,
    load_practice_record,
    save_markdown_summary,
    save_or_update_practice_record,
    update_error_book,
)
from ui_components import (
    inject_chat_shell_css,
    render_analysis_panel,
    render_chat_history,
    render_chat_status_bar,
    render_goal_card,
    render_input_header,
    render_left_brand,
    render_summary_report,
)


def init_state() -> None:
    default_scene = list_scenarios()[0]
    default_difficulty = get_scenario(default_scene)["default_difficulty"]
    defaults = {
        "history": [],
        **empty_session_state(),
        "last_feedback": None,
        "last_score": None,
        "latest_feedback": None,
        "latest_score": None,
        "last_ai_reply": "",
        "latest_summary": "",
        "latest_summary_path": "",
        "latest_html_path": "",
        "current_record_path": "",
        "audio_text": "",
        "user_input": "",
        "voice_transcript": "",
        "voice_status": "",
        "voice_profile": {},
        "last_spoken_reply": "",
        "voice_reply_enabled": True,
        "pending_user_input": "",
        "pending_input_clear": False,
        "sidebar_collapsed": False,
        "active_view": "practice",
        "input_text": "",
        "input_mode": "text",
        "recording_status": "",
        "analysis_view": "correction",
        "latest_suggestion": {},
        "theme_mode": "dark",
        "selected_scenario": default_scene,
        "selected_difficulty": default_difficulty,
        "current_scene": default_scene,
        "current_difficulty": default_difficulty,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_conversation_state() -> None:
    for key, value in empty_session_state().items():
        st.session_state[key] = value
    st.session_state.history = []
    st.session_state.last_feedback = None
    st.session_state.last_score = None
    st.session_state.latest_feedback = None
    st.session_state.latest_score = None
    st.session_state.last_ai_reply = ""
    st.session_state.latest_summary = ""
    st.session_state.latest_summary_path = ""
    st.session_state.latest_html_path = ""
    st.session_state.current_record_path = ""
    st.session_state.audio_text = ""
    st.session_state.user_input = ""
    st.session_state.voice_transcript = ""
    st.session_state.voice_status = ""
    st.session_state.voice_profile = {}
    st.session_state.last_spoken_reply = ""
    st.session_state.pending_user_input = ""
    st.session_state.pending_input_clear = False
    st.session_state.input_text = ""
    st.session_state.recording_status = ""
    st.session_state.latest_suggestion = {}


def escape_text(value: object) -> str:
    return html.escape(str(value))


def render_app_header(scenario: dict, difficulty: str, mode_label: str, progress: int) -> None:
    st.markdown(
        f"""
        <section class="coach-hero">
          <div>
            <div class="coach-eyebrow">AI-English-Coach V1.0</div>
            <h1>AI 英语口语陪练</h1>
            <p>按结构化练习任务完成场景对话，获得纠错反馈、五维评分、学习统计和练习报告。</p>
          </div>
          <div class="hero-status-grid">
            <div class="hero-status-item"><span>模式</span><strong>{escape_text(mode_label)}</strong></div>
            <div class="hero-status-item"><span>场景</span><strong>{escape_text(scenario["cn_label"])}</strong></div>
            <div class="hero-status-item"><span>难度</span><strong>{escape_text(difficulty)}</strong></div>
            <div class="hero-status-item"><span>进度</span><strong>{progress}%</strong></div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_intro(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="section-intro">
          <h2>{escape_text(title)}</h2>
          <p>{escape_text(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_score(score: dict) -> None:
    total_score = int(score.get("total_score", 0))
    voice_profile = score.get("voice_profile") or {}
    st.markdown(
        f"""
        <div class="score-total-card" style="background: linear-gradient(135deg, #0f172a, #111f32) !important; color: #f8fafc !important;">
          <div class="score-total-label">综合评分</div>
          <div class="score-total-value">{total_score}/100</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for item in score.get("dimensions", {}).values():
        item_score = int(item.get("score", 0))
        label = html.escape(str(item.get("label", "")))
        explanation = html.escape(str(item.get("explanation", "")))
        st.markdown(
            f"""
            <div class="score-dimension-card">
              <div class="score-dimension-head">
                <span>{label}</span>
                <strong>{item_score}/100</strong>
              </div>
              <div class="score-bar-track">
                <div class="score-bar-fill" style="width: {max(0, min(100, item_score))}%;"></div>
              </div>
              <div class="score-explanation">{explanation}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if voice_profile.get("audio_used"):
        duration = voice_profile.get("duration_seconds")
        wpm = voice_profile.get("words_per_minute")
        metric_parts = []
        if duration:
            metric_parts.append(f"录音时长：{duration} 秒")
        if wpm:
            metric_parts.append(f"估算语速：{wpm} WPM")
        metric_parts.append(f"识别引擎：{voice_profile.get('engine', 'unknown')}")
        st.info(" | ".join(metric_parts))

    coach_actions = score.get("coach_actions") or []
    if coach_actions:
        st.markdown("**本轮 Coach 训练动作**")
        for action in coach_actions:
            st.write(f"- {action}")


def render_history_record(record: dict) -> None:
    """Render a compact saved-record preview in the sidebar."""
    st.write(f"**时间：** {record.get('time', '未知')}")
    st.write(f"**场景：** {record.get('scenario', '未知')}")
    st.write(f"**难度：** {record.get('difficulty', '未知')}")
    if record.get("round_count"):
        st.write(f"**对话轮数：** {record.get('round_count')}")
    st.write(f"**用户输入：** {record.get('user_input', '')}")
    st.write(f"**AI 回复：** {record.get('ai_reply', '')}")
    score = record.get("score_result", {})
    overall = record.get("overall_score")
    if isinstance(overall, int):
        st.write(f"**会话综合评分：** {overall}/100")
    if score:
        st.write(f"**最近一轮评分：** {score.get('total_score', 0)}/100")
    if record.get("lesson_summary"):
        st.caption("该记录已包含课后总结。")


def render_saved_conversation(record: dict) -> None:
    messages = record.get("conversation_history", [])
    if not messages:
        return
    with st.expander("完整多轮对话", expanded=True):
        for item in messages:
            role = "用户" if item.get("role") == "user" else "AI"
            stage = item.get("stage", "")
            st.write(f"**{role} {f'· {stage}' if stage else ''}**")
            st.write(item.get("content", ""))


def render_saved_feedback_and_scores(record: dict) -> None:
    feedback_items = record.get("feedback_history") or [record.get("correction_feedback", {})]
    score_items = record.get("score_history") or [record.get("score_result", {})]
    with st.expander("每轮纠错与评分", expanded=False):
        for index, feedback in enumerate(feedback_items, start=1):
            if not feedback:
                continue
            st.write(f"**第 {index} 轮纠错**")
            st.write(f"- 原句：{feedback.get('original_sentence', '')}")
            st.write(f"- 修改后句子：{feedback.get('corrected_sentence', '')}")
            for issue in feedback.get("issue_explanation", []):
                st.write(f"- 错误原因：{issue}")
            if index <= len(score_items):
                st.write(f"- Overall Score：{score_items[index - 1].get('total_score', 0)}/100")


def render_error_book_panel() -> None:
    book = load_error_book()
    errors = book.get("errors", [])
    with st.expander("错误本 error_book.json", expanded=False):
        if not errors:
            st.caption("暂无错误本记录。完成包含错误反馈的练习后会自动汇总。")
            return
        st.caption(f"更新时间：{book.get('updated_at', '未知')}，累计 {len(errors)} 条")
        rows = [
            {
                "time": item.get("time", ""),
                "scenario": item.get("scenario", ""),
                "round": item.get("round", ""),
                "issue": item.get("issue", ""),
                "corrected_sentence": item.get("corrected_sentence", ""),
            }
            for item in errors[-20:]
        ]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_course_panel(scenario_key: str) -> None:
    status = stage_progress(scenario_key, st.session_state.current_round)
    step = status["current_step"]
    st.markdown(
        f"""
        <section class="lesson-card">
          <div class="lesson-card-head">
            <div>
              <div class="coach-eyebrow">当前练习任务</div>
              <h3>{escape_text(step["title"])}</h3>
            </div>
            <strong>{status["progress"]}%</strong>
          </div>
          <div class="lesson-progress-track">
            <div class="lesson-progress-fill" style="width: {status["progress"]}%;"></div>
          </div>
          <p>{escape_text(step["goal"])}</p>
          <div class="lesson-prompt-grid">
            <div><span>建议追问</span><strong>{escape_text(step["prompt"])}</strong></div>
            <div><span>目标表达</span><strong>{escape_text(step["target_expression"])}</strong></div>
            <div><span>评价重点</span><strong>{escape_text(step.get("evaluation_focus", ""))}</strong></div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("完整练习步骤"):
        for index, step in enumerate(status["steps"], start=1):
            marker = "已完成" if index <= st.session_state.current_round else "待练习"
            st.write(f"**{index}. {step['title']}**（{marker}）")
            st.caption(step["goal"])


def render_feedback(feedback: dict | None) -> None:
    if not feedback:
        st.markdown(
            """
            <div class="empty-panel">
              <strong>等待用户输入</strong>
              <span>提交练习后，这里会显示语法检查、表达优化、替代表达和跟练句。</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    if feedback.get("has_grammar_errors"):
        st.error("发现可修改的语法或表达问题。")
    else:
        st.success("本地规则未发现明显语法错误。")

    with st.expander("原句与修改后句子", expanded=True):
        st.write(f"**原句：** {feedback.get('original_sentence', '')}")
        st.write(f"**修改后句子：** {feedback.get('corrected_sentence', '')}")

    st.write("**错误原因：**")
    for issue in feedback.get("issue_explanation", []):
        st.write(f"- {issue}")
    if feedback.get("error_tags"):
        st.write("**错误类型：** " + ", ".join(feedback["error_tags"]))

    if feedback.get("focus_points"):
        st.write("**口语表达重点：**")
        for point in feedback["focus_points"]:
            st.write(f"- {point}")

    st.write("**表达优化建议：**")
    for suggestion in feedback.get("expression_suggestions", []):
        st.write(f"- {suggestion}")

    st.write(f"**更自然的口语版本：** {feedback['natural_expression']}")
    st.write("**推荐替代表达：**")
    for expression in feedback["alternative_expressions"]:
        st.write(f"- {expression}")
    st.write("**跟读练习句：**")
    for sentence in feedback.get("practice_sentences", []):
        st.write(f"- {sentence}")


def render_voice_lab_status() -> None:
    """Show speech-recognition readiness and the latest voice coaching state."""
    runtime = get_speech_runtime_status()
    status_class = "voice-ready" if runtime["ready"] else "voice-missing"
    status_text = "可进行真实语音转写" if runtime["ready"] else "未安装本地语音模型"
    st.markdown(
        f"""
        <div class="voice-lab-card {status_class}">
          <div class="voice-lab-head">
            <span>Speech Coach</span>
            <strong>{escape_text(status_text)}</strong>
          </div>
          <div class="voice-lab-grid">
            <div><span>识别引擎</span><strong>{escape_text(runtime["engine"])}</strong></div>
            <div><span>模型</span><strong>{escape_text(runtime["model_size"])}</strong></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    profile = st.session_state.get("voice_profile") or {}
    if profile:
        st.caption(
            f"最近语音状态：{profile.get('message', st.session_state.get('voice_status', ''))} "
            f"| confidence={profile.get('confidence_label', 'unknown')}"
        )
        if profile.get("coach_tip"):
            st.info(profile["coach_tip"])
    elif not runtime["ready"]:
        st.caption(f"要启用真实识别：`{runtime['install_hint']}`，建议演示模型 `tiny.en`。")


def transcribe_to_input(audio_file, source_label: str = "录音") -> bool:
    """Transcribe an uploaded or recorded audio object into the answer box."""
    result = transcribe_audio(audio_file)
    st.session_state.voice_status = result["message"]
    st.session_state.recording_status = result["message"]
    st.session_state.voice_profile = result
    if result["success"]:
        st.session_state.voice_transcript = result["text"]
        st.session_state.audio_text = result["text"]
        st.session_state.pending_user_input = result["text"]
        st.success(f"{source_label}转写完成。")
        return True
    st.warning(result["message"])
    return False


def consume_enter_submit_text() -> str:
    """Read and clear text submitted through the Enter-key browser bridge."""
    try:
        text = st.query_params.get("coach_enter_submit", "")
    except Exception:
        return ""
    if isinstance(text, list):
        text = text[0] if text else ""
    text = str(text or "")
    if text:
        try:
            del st.query_params["coach_enter_submit"]
        except Exception:
            pass
    return text


def build_latest_suggestion(feedback: dict | None, lesson: dict, scenario: dict) -> dict:
    """Build a compact current-round learning suggestion for the right panel."""
    step = lesson.get("current_step", {})
    if not feedback:
        return {
            "main_issue": "等待本轮回答。",
            "recommended_expressions": scenario.get("recommended_expressions", [])[:2],
            "practice_sentence": step.get("target_expression", ""),
            "next_tip": step.get("prompt", "先回答当前问题，再补充一个原因或例子。"),
        }

    issues = feedback.get("issue_explanation") or []
    expressions = feedback.get("alternative_expressions") or scenario.get("recommended_expressions", [])
    drills = feedback.get("practice_sentences") or []
    focus_points = feedback.get("focus_points") or feedback.get("expression_suggestions") or []
    return {
        "main_issue": issues[0] if issues else "本轮没有明显语法错误，重点提高细节和自然度。",
        "recommended_expressions": expressions[:3],
        "practice_sentence": drills[0] if drills else feedback.get("corrected_sentence", ""),
        "next_tip": focus_points[0] if focus_points else step.get("evaluation_focus", step.get("prompt", "")),
    }


def refresh_latest_suggestion(scenario_key: str, scenario: dict) -> None:
    lesson = stage_progress(scenario_key, st.session_state.current_round)
    st.session_state.latest_suggestion = build_latest_suggestion(st.session_state.last_feedback, lesson, scenario)


def start_practice_session(scenario_key: str, difficulty: str, session_key: str) -> None:
    """Reset and start a new proactive AI-led practice session."""
    reset_conversation_state()
    st.session_state.current_stage_key = session_key
    opening = build_opening_question(scenario_key, difficulty)
    lesson = stage_progress(scenario_key, 0)
    st.session_state.conversation_history.append(
        {"role": "assistant", "content": opening, "stage": lesson["current_step"]["title"]}
    )
    st.session_state.last_ai_reply = opening
    st.session_state.session_started = True


def generate_current_summary(scenario: dict, difficulty: str) -> None:
    """Generate and persist the current lesson summary/report record."""
    summary_history = history_for_summary(st.session_state.conversation_history)
    combined_feedback = {
        "issue_explanation": [
            issue
            for feedback in st.session_state.feedback_history
            for issue in feedback.get("issue_explanation", [])
        ]
    }
    combined_score = {"total_score": average_score(st.session_state.score_history)}
    summary = generate_lesson_summary(
        summary_history,
        scenario,
        difficulty,
        combined_feedback,
        combined_score,
    )
    st.session_state.latest_summary = summary
    summary_path = save_markdown_summary(summary)
    st.session_state.latest_summary_path = str(summary_path)
    record = build_session_record(
        scenario,
        difficulty,
        st.session_state.conversation_history,
        st.session_state.feedback_history,
        st.session_state.score_history,
        summary,
    )
    record_path = save_or_update_practice_record(record, st.session_state.current_session_path)
    st.session_state.current_session_path = str(record_path)
    st.session_state.current_record_path = str(record_path)
    update_error_book(record)
    st.success(f"课后总结已生成：{Path(summary_path).name}")


def submit_user_answer(
    clean_text: str,
    scenario_key: str,
    scenario: dict,
    difficulty: str,
    audio_used: bool = False,
    voice_profile: dict | None = None,
) -> bool:
    """Submit one answer through the shared multi-turn conversation flow."""
    if st.session_state.current_round >= MAX_TRAINING_ROUNDS:
        st.warning("本次训练已达到 8 轮上限，可以生成课后总结或清空后重新开始。")
        return False
    if not clean_text:
        st.warning("请输入或转写英文句子后再提交。")
        return False
    if not st.session_state.session_started:
        st.session_state.current_stage_key = f"{scenario_key}:{difficulty}"
        if not st.session_state.conversation_history:
            opening = build_opening_question(scenario_key, difficulty)
            lesson = stage_progress(scenario_key, 0)
            st.session_state.conversation_history.append(
                {"role": "assistant", "content": opening, "stage": lesson["current_step"]["title"]}
            )
            st.session_state.last_ai_reply = opening
        st.session_state.session_started = True

    result = process_user_turn(
        clean_text,
        scenario_key,
        scenario,
        difficulty,
        st.session_state.conversation_history,
        st.session_state.current_round,
        audio_used=audio_used,
        voice_profile=voice_profile,
    )
    turn = result["turn"]
    st.session_state.conversation_history.append(
        {
            "role": "user",
            "content": clean_text,
            "stage": result["stage"]["title"],
            "input_mode": "voice" if audio_used else "text",
            "voice_profile": voice_profile or {},
        }
    )
    st.session_state.conversation_history.append(
        {"role": "assistant", "content": turn["ai_reply"], "stage": result["next_stage"]["title"]}
    )
    st.session_state.feedback_history.append(turn["correction"])
    st.session_state.score_history.append(turn["score"])
    st.session_state.current_round = result["current_round"]
    st.session_state.current_stage = result["current_stage"]
    st.session_state.session_completed = result["session_completed"]
    st.session_state.history = history_for_summary(st.session_state.conversation_history)
    st.session_state.last_feedback = turn["correction"]
    st.session_state.last_score = turn["score"]
    st.session_state.latest_feedback = turn["correction"]
    st.session_state.latest_score = turn["score"]
    st.session_state.last_ai_reply = turn["ai_reply"]
    refresh_latest_suggestion(scenario_key, scenario)

    record = build_session_record(
        scenario,
        difficulty,
        st.session_state.conversation_history,
        st.session_state.feedback_history,
        st.session_state.score_history,
        st.session_state.latest_summary,
    )
    record_path = save_or_update_practice_record(record, st.session_state.current_session_path)
    update_error_book(record)
    st.session_state.current_session_path = str(record_path)
    st.session_state.current_record_path = str(record_path)
    st.session_state.pending_input_clear = True
    st.toast(f"练习记录已保存：{record_path.name}")
    return True


def load_demo_session(scenario_key: str, scenario: dict, difficulty: str, session_key: str) -> None:
    """Populate the UI with a complete five-round demo session."""
    reset_conversation_state()
    demo = build_demo_session(scenario_key, scenario, difficulty)
    st.session_state.current_stage_key = session_key
    st.session_state.conversation_history = demo["conversation_history"]
    st.session_state.feedback_history = demo["feedback_history"]
    st.session_state.score_history = demo["score_history"]
    st.session_state.current_round = demo["current_round"]
    st.session_state.current_stage = demo["current_stage"]
    st.session_state.session_started = demo["session_started"]
    st.session_state.session_completed = demo["session_completed"]
    st.session_state.history = history_for_summary(st.session_state.conversation_history)
    st.session_state.last_feedback = demo["last_feedback"]
    st.session_state.last_score = demo["last_score"]
    st.session_state.latest_feedback = demo["last_feedback"]
    st.session_state.latest_score = demo["last_score"]
    st.session_state.last_ai_reply = demo["last_ai_reply"]
    refresh_latest_suggestion(scenario_key, scenario)

    combined_feedback = {
        "issue_explanation": [
            issue
            for feedback in st.session_state.feedback_history
            for issue in feedback.get("issue_explanation", [])
        ]
    }
    combined_score = {"total_score": average_score(st.session_state.score_history)}
    summary = generate_lesson_summary(
        st.session_state.history,
        scenario,
        difficulty,
        combined_feedback,
        combined_score,
    )
    st.session_state.latest_summary = summary
    summary_path = save_markdown_summary(summary)
    st.session_state.latest_summary_path = str(summary_path)

    record = build_session_record(
        scenario,
        difficulty,
        st.session_state.conversation_history,
        st.session_state.feedback_history,
        st.session_state.score_history,
        summary,
    )
    record["demo_session"] = True
    record_path = save_or_update_practice_record(record, st.session_state.current_session_path)
    update_error_book(record)
    st.session_state.current_session_path = str(record_path)
    st.session_state.current_record_path = str(record_path)
    st.toast(f"演示会话已生成：{record_path.name}")


def render_ai_voice_reply(reply: str) -> None:
    """Use browser SpeechSynthesis to read the latest AI reply once."""
    if not reply or not st.session_state.voice_reply_enabled:
        return
    if st.session_state.last_spoken_reply == reply:
        return
    st.session_state.last_spoken_reply = reply
    components.html(
        f"""
        <script>
        const text = {json.dumps(reply)};
        const preferredVoiceNames = [
            "Samantha",
            "Google US English",
            "Microsoft Jenny",
            "Microsoft Aria",
            "Microsoft Zira",
            "Microsoft Ava",
            "Victoria",
            "Susan",
            "Karen",
            "Serena",
            "Tessa",
            "Moira"
        ];

        function pickVoice(voices) {{
            const englishVoices = voices.filter((voice) => (voice.lang || "").toLowerCase().startsWith("en"));
            for (const preferred of preferredVoiceNames) {{
                const match = englishVoices.find((voice) =>
                    (voice.name || "").toLowerCase().includes(preferred.toLowerCase())
                );
                if (match) return match;
            }}
            return englishVoices.find((voice) =>
                /(female|woman|girl|samantha|jenny|aria|zira|ava|victoria|susan|karen|serena|tessa|moira)/i.test(voice.name || "")
            ) || englishVoices[0] || voices[0];
        }}

        function speakReply() {{
            const synth = window.parent.speechSynthesis;
            const voices = synth.getVoices();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "en-US";
            utterance.voice = pickVoice(voices);
            utterance.rate = 0.88;
            utterance.pitch = 1.05;
            synth.cancel();
            synth.speak(utterance);
        }}

        if ("speechSynthesis" in window.parent) {{
            const synth = window.parent.speechSynthesis;
            if (synth.getVoices().length) {{
                speakReply();
            }} else {{
                synth.onvoiceschanged = speakReply;
                window.parent.setTimeout(speakReply, 300);
            }}
        }}
        </script>
        """,
        height=0,
        width=0,
    )


def render_browser_speech_dictation(disabled: bool = False) -> None:
    """Render a Chrome Web Speech API helper that writes into the answer box."""
    disabled_json = json.dumps(disabled)
    is_light = st.session_state.get("theme_mode") == "light"
    card_bg = "rgba(255,255,255,0.68)" if is_light else "rgba(31,31,34,0.72)"
    card_border = "rgba(0,0,0,0.14)" if is_light else "rgba(255,255,255,0.14)"
    card_text = "#111111" if is_light else "#f5f5f7"
    muted_text = "#6b7280" if is_light else "#a3a3a3"
    button_bg = "rgba(255,255,255,0.60)" if is_light else "rgba(255,255,255,0.08)"
    primary_bg = "#111111" if is_light else "#f5f5f7"
    primary_text = "#ffffff" if is_light else "#09090b"
    input_bg = "rgba(255,255,255,0.56)" if is_light else "rgba(255,255,255,0.06)"
    components.html(
        f"""
        <div class="dictation-card">
          <div class="dictation-head">
            <strong>浏览器听写</strong>
            <span id="dictation-status">等待开始</span>
          </div>
          <div class="dictation-actions">
            <button id="dictation-start" type="button">开始</button>
            <button id="dictation-stop" type="button">停止</button>
            <button id="dictation-write" type="button">写入</button>
          </div>
          <div id="dictation-text" class="dictation-text">识别结果会显示在这里。</div>
          <div class="dictation-help">Chrome 支持时可直接调用浏览器语音识别；若不可用，请使用录音转写或文本输入。</div>
        </div>
        <script>
        const disabled = {disabled_json};
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const statusEl = document.getElementById("dictation-status");
        const textEl = document.getElementById("dictation-text");
        const startBtn = document.getElementById("dictation-start");
        const stopBtn = document.getElementById("dictation-stop");
        const writeBtn = document.getElementById("dictation-write");
        let recognition = null;
        let finalText = "";

        function setStatus(text, state) {{
            statusEl.textContent = text;
            statusEl.dataset.state = state || "";
        }}

        function answerBox() {{
            return window.parent.document.querySelector('input[aria-label="用户英文输入"]') ||
                window.parent.document.querySelector('textarea[aria-label="用户英文输入"]');
        }}

        function writeToStreamlitTextarea(text) {{
            const target = answerBox();
            if (!target) {{
                setStatus("未找到输入框", "error");
                return false;
            }}
            const prototype = target.tagName === "TEXTAREA"
                ? window.parent.HTMLTextAreaElement.prototype
                : window.parent.HTMLInputElement.prototype;
            const setter = Object.getOwnPropertyDescriptor(prototype, "value").set;
            setter.call(target, text);
            target.dispatchEvent(new Event("input", {{ bubbles: true }}));
            target.dispatchEvent(new Event("change", {{ bubbles: true }}));
            target.focus();
            setStatus("已写入输入框", "ok");
            return true;
        }}

        function updateButtons(isListening) {{
            startBtn.disabled = disabled || !SpeechRecognition || isListening;
            stopBtn.disabled = disabled || !SpeechRecognition || !isListening;
            writeBtn.disabled = disabled || !finalText.trim();
        }}

        if (disabled) {{
            setStatus("请先开始练习", "error");
            updateButtons(false);
        }} else if (!SpeechRecognition) {{
            setStatus("当前浏览器不支持", "error");
            updateButtons(false);
        }} else {{
            recognition = new SpeechRecognition();
            recognition.lang = "en-US";
            recognition.interimResults = true;
            recognition.continuous = true;

            recognition.onstart = () => {{
                setStatus("正在听写", "active");
                updateButtons(true);
            }};
            recognition.onresult = (event) => {{
                let interimText = "";
                for (let i = event.resultIndex; i < event.results.length; i += 1) {{
                    const transcript = event.results[i][0].transcript.trim();
                    if (event.results[i].isFinal) {{
                        finalText = `${{finalText}} ${{transcript}}`.trim();
                    }} else {{
                        interimText = transcript;
                    }}
                }}
                textEl.textContent = [finalText, interimText].filter(Boolean).join(" ");
                writeBtn.disabled = !finalText.trim();
            }};
            recognition.onerror = (event) => {{
                setStatus(event.error === "not-allowed" ? "麦克风未授权" : `识别错误：${{event.error}}`, "error");
                updateButtons(false);
            }};
            recognition.onend = () => {{
                if (finalText.trim()) {{
                    writeToStreamlitTextarea(finalText.trim());
                }}
                setStatus(finalText.trim() ? "听写完成" : "已停止", finalText.trim() ? "ok" : "");
                updateButtons(false);
            }};
            setStatus("可用", "ok");
            updateButtons(false);
        }}

        startBtn.addEventListener("click", () => {{
            if (!recognition) return;
            finalText = "";
            textEl.textContent = "正在听写...";
            recognition.start();
        }});
        stopBtn.addEventListener("click", () => {{
            if (recognition) recognition.stop();
        }});
        writeBtn.addEventListener("click", () => {{
            if (finalText.trim()) writeToStreamlitTextarea(finalText.trim());
        }});
        </script>
        <style>
        .dictation-card {{
            box-sizing: border-box;
            width: 100%;
            padding: 12px;
            border: 1px solid {card_border};
            border-radius: 8px;
            background: {card_bg};
            color: {card_text};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            backdrop-filter: blur(24px) saturate(1.25);
            -webkit-backdrop-filter: blur(24px) saturate(1.25);
        }}
        .dictation-head {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            margin-bottom: 10px;
        }}
        .dictation-head strong {{
            font-size: 13px;
            white-space: nowrap;
        }}
        #dictation-status {{
            color: {muted_text};
            font-size: 12px;
            font-weight: 700;
        }}
        #dictation-status[data-state="ok"],
        #dictation-status[data-state="active"],
        #dictation-status[data-state="error"] {{ color: {card_text}; }}
        .dictation-actions {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 7px;
        }}
        .dictation-actions button {{
            border: 1px solid {card_border};
            border-radius: 8px;
            padding: 8px 6px;
            background: {button_bg};
            color: {card_text};
            font-size: 12px;
            font-weight: 800;
            cursor: pointer;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .dictation-actions button:first-child {{
            background: {primary_bg};
            border-color: {primary_bg};
            color: {primary_text};
        }}
        .dictation-actions button:disabled {{
            opacity: 0.45;
            cursor: not-allowed;
        }}
        .dictation-text {{
            margin-top: 9px;
            min-height: 34px;
            padding: 9px;
            border: 1px solid {card_border};
            border-radius: 8px;
            background: {input_bg};
            color: {card_text};
            font-size: 12px;
            line-height: 1.45;
        }}
        .dictation-help {{
            margin-top: 7px;
            color: {muted_text};
            font-size: 11px;
            line-height: 1.45;
        }}
        </style>
        """,
        height=205,
    )


def render_enter_submit_bridge() -> None:
    """Keep Enter and button submit in sync with the current browser input value."""
    components.html(
        """
        <script>
        function bindEnterSubmit() {
            const doc = window.parent.document;
            const answerInput =
                doc.querySelector('input[aria-label="用户英文输入"]') ||
                doc.querySelector('textarea[aria-label="用户英文输入"]');
            const sendButton = [...doc.querySelectorAll("button")].find((button) =>
                button.innerText.trim() === "发送" &&
                button.getBoundingClientRect().width > 0 &&
                button.getBoundingClientRect().height > 0
            );

            function syncAnswerToUrl() {
                if (!answerInput) return false;
                const currentValue = answerInput.value || "";
                if (!currentValue.trim()) return;
                const url = new URL(window.parent.location.href);
                url.searchParams.set("coach_enter_submit", currentValue);
                window.parent.history.replaceState(null, "", url.toString());
                return true;
            }

            if (answerInput && answerInput.dataset.coachEnterBound !== "1") {
                answerInput.dataset.coachEnterBound = "1";
                answerInput.addEventListener("keydown", (event) => {
                    if (event.key !== "Enter" || event.shiftKey) return;
                    event.preventDefault();
                    if (!syncAnswerToUrl()) return;
                    window.parent.setTimeout(() => {
                        const freshSendButton = [...doc.querySelectorAll("button")].find((button) =>
                            button.innerText.trim() === "发送" &&
                            !button.disabled &&
                            button.getBoundingClientRect().width > 0 &&
                            button.getBoundingClientRect().height > 0
                        );
                        if (freshSendButton) freshSendButton.click();
                    }, 140);
                });
            }

            if (sendButton && sendButton.dataset.coachClickBound !== "1") {
                sendButton.dataset.coachClickBound = "1";
                sendButton.addEventListener("pointerdown", syncAnswerToUrl, { capture: true });
                sendButton.addEventListener("click", syncAnswerToUrl, { capture: true });
            }
        }
        bindEnterSubmit();
        window.parent.requestAnimationFrame(bindEnterSubmit);
        window.parent.setTimeout(bindEnterSubmit, 250);
        window.parent.setTimeout(bindEnterSubmit, 800);
        </script>
        """,
        height=0,
        width=0,
    )

def render_voice_tools_panel(
    disabled: bool,
    scenario_key: str,
    scenario: dict,
    difficulty: str,
) -> None:
    """Render secondary voice tools in the right utility rail."""
    st.markdown(
        """
        <div class="coach-analysis-card coach-voice-tools-card">
          <h3>语音工具</h3>
          <p>辅助输入放在右侧，不占用主聊天区。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    dictation_col, upload_col = st.columns([1, 1])
    with dictation_col:
        if hasattr(st, "popover"):
            with st.popover("听写"):
                render_browser_speech_dictation(disabled=disabled)
        else:
            with st.expander("听写", expanded=False):
                render_browser_speech_dictation(disabled=disabled)
    with upload_col:
        if hasattr(st, "popover"):
            upload_context = st.popover("上传")
        else:
            upload_context = st.expander("上传", expanded=False)
        with upload_context:
            uploaded_file = st.file_uploader(
                "上传音频文件",
                type=SUPPORTED_AUDIO_TYPES,
                help="支持 wav、mp3、m4a。本地语音模型不可用时会保留文本输入主流程。",
                key="right_uploaded_audio",
            )
            file_col1, file_col2 = st.columns([1, 1])
            if file_col1.button(
                "转文字",
                width="stretch",
                disabled=uploaded_file is None,
                key="right_transcribe_file",
            ):
                if transcribe_to_input(uploaded_file, "音频文件"):
                    st.session_state.input_mode = "text"
                st.rerun()
            if file_col2.button(
                "提交",
                width="stretch",
                disabled=uploaded_file is None or disabled,
                key="right_submit_file",
            ):
                if transcribe_to_input(uploaded_file, "音频文件"):
                    submit_user_answer(
                        normalize_user_input(st.session_state.voice_transcript),
                        scenario_key,
                        scenario,
                        difficulty,
                        audio_used=True,
                        voice_profile=st.session_state.voice_profile,
                    )
                    st.rerun()


def render_history_tab() -> None:
    render_section_intro("历史记录管理", "筛选、查看、下载或删除每一次练习记录。")
    files = list_all_history_files()
    records = load_records(files)
    if not records:
        st.info("暂无历史记录。完成练习后会自动保存。")
        return

    scenario_options = ["全部"] + sorted({record.get("scenario", "未知") for record in records})
    selected_scenario = st.selectbox("按场景筛选", scenario_options, key="history_filter")
    visible_records = filter_records(records, selected_scenario)
    st.caption(f"当前显示 {len(visible_records)} / {len(records)} 条记录")
    if not visible_records:
        st.warning("该筛选条件下没有记录。")
        return

    selected_record = st.selectbox(
        "选择记录",
        visible_records,
        format_func=lambda record: (
            f"{record.get('time', '未知时间')} | {record.get('scenario', '未知')} | "
            f"{record.get('round_count', 1)}轮 | "
            f"{record.get('overall_score', record.get('score_result', {}).get('total_score', 0))}分"
        ),
        key="history_record_select",
    )
    left, right = st.columns([1, 1])
    with left:
        render_history_record(selected_record)
        st.download_button(
            "下载该 JSON 记录",
            data=Path(selected_record["_path"]).read_text(encoding="utf-8"),
            file_name=selected_record["_file_name"],
            mime="application/json",
            width="stretch",
        )
    with right:
        correction = selected_record.get("correction_feedback", {})
        st.write("**纠错摘要**")
        for issue in correction.get("issue_explanation", []):
            st.write(f"- {issue}")
        if selected_record.get("lesson_summary"):
            st.write("**课后总结预览**")
            st.markdown(selected_record["lesson_summary"])
    render_saved_conversation(selected_record)
    render_saved_feedback_and_scores(selected_record)
    render_error_book_panel()
    confirm_delete = st.checkbox("确认删除所选历史记录", key="confirm_delete_history")
    if st.button("删除所选记录", disabled=not confirm_delete, type="secondary"):
        if delete_practice_record(selected_record["_path"]):
            st.success("历史记录已删除。")
            st.rerun()
        st.warning("历史记录删除失败。")


def render_analytics_tab() -> None:
    render_section_intro("学习数据统计", "用练习次数、分数趋势、场景分布和高频问题观察学习进展。")
    records = load_records(list_all_history_files())
    if not records:
        st.info("暂无统计数据。完成几次练习后可查看趋势。")
        return

    summary = summarize_records(records)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("练习次数", summary["total_records"])
    col2.metric("平均分", summary["average_score"])
    col3.metric("最高分", summary["best_score"])
    col4.metric("已生成总结", summary["summary_count"])

    trend = score_trend(records)
    if trend:
        st.markdown("**分数趋势**")
        st.line_chart(pd.DataFrame(trend).set_index("time")["score"])

    scenario_rows = [{"scenario": key, "count": value} for key, value in summary["scenario_counts"].items()]
    if scenario_rows:
        st.markdown("**场景练习分布**")
        st.bar_chart(pd.DataFrame(scenario_rows).set_index("scenario")["count"])

    averages = dimension_averages(records)
    if averages:
        st.markdown("**五维平均分**")
        st.dataframe(
            pd.DataFrame(
                [{"dimension": key, "average_score": value} for key, value in averages.items()]
            ),
            width="stretch",
            hide_index=True,
        )

    errors = error_frequency(records)
    if errors:
        st.markdown("**高频问题**")
        st.dataframe(
            pd.DataFrame([{"issue": key, "count": value} for key, value in errors.items()]),
            width="stretch",
            hide_index=True,
        )


def render_report_tab() -> None:
    render_section_intro("报告导出中心", "从当前总结或历史总结中导出 Markdown / HTML 学习报告。")
    records = load_records(list_all_history_files())
    summaries = [record for record in records if record.get("lesson_summary")]
    source_options = ["当前会话总结"] + summaries
    source = st.selectbox(
        "选择报告来源",
        source_options,
        format_func=lambda item: item if isinstance(item, str) else f"{item.get('time', '未知时间')} | {item.get('scenario', '未知')}",
    )
    if isinstance(source, str):
        markdown = st.session_state.latest_summary
    else:
        markdown = source.get("lesson_summary", "")

    if not markdown:
        st.info("暂无可导出的总结。请先在练习中心生成课后总结。")
        return

    st.markdown(markdown)
    col1, col2 = st.columns(2)
    col1.download_button(
        "下载 Markdown",
        data=markdown.encode("utf-8"),
        file_name="lesson_summary.md",
        mime="text/markdown",
        width="stretch",
    )
    if col2.button("生成 HTML 报告", width="stretch"):
        path = save_html_report(markdown)
        st.session_state.latest_html_path = str(path)
        st.success(f"HTML 报告已保存：{path.name}")
    if st.session_state.latest_html_path:
        html_path = Path(st.session_state.latest_html_path)
        if html_path.exists():
            st.download_button(
                "下载 HTML 报告",
                data=html_path.read_text(encoding="utf-8").encode("utf-8"),
                file_name=html_path.name,
                mime="text/html",
                width="stretch",
            )


def render_settings_tab(mode_label: str) -> None:
    render_section_intro("运行设置与说明", "查看 API、语音转写和自动化测试命令。")
    st.write(f"**当前模式：** {mode_label}")
    speech_status = get_speech_runtime_status()
    st.write("**项目定位：** 比赛成品原型，重点展示多轮场景训练、语音识别、教练反馈和学习报告。")
    st.write("**语音模式：** Coach Voice Lab 录音提交式语音对话。用户录一段英文回答后转写并提交，AI 追问可由浏览器朗读。")
    st.write(f"**语音识别引擎：** {speech_status['engine']}，模型：{speech_status['model_size']}。")
    st.write("**语音边界：** 当前不是全双工实时通话；Pronunciation 为本地模拟评分，真实音素级评测可作为下一阶段增强。")
    st.write("**API dry-run：** `python scripts/check_api.py`")
    st.write("**API live 测试：** `python scripts/check_api.py --live`")
    st.write("**本地语音转写测试：** `WHISPER_MODEL_SIZE=tiny.en python scripts/test_transcription.py`")
    st.write("**完整自动化测试：** `pytest -q && python scripts/smoke_test.py`")
    st.info("无 API Key 时系统保持本地演示模式；API 调用失败时会自动回退到本地逻辑。")


def configure_browser_behavior() -> None:
    """Reduce Chrome Translate DOM rewrites that can break Streamlit rerenders."""
    st.markdown(
        """
        <meta name="google" content="notranslate">
        """,
        unsafe_allow_html=True,
    )
    components.html(
        """
        <script>
        const root = window.parent.document.documentElement;
        const body = window.parent.document.body;
        root.setAttribute("translate", "no");
        root.setAttribute("lang", "zh-CN");
        root.classList.add("notranslate");
        body.setAttribute("translate", "no");
        body.classList.add("notranslate");

        if (!window.parent.document.querySelector('meta[name="google"][content="notranslate"]')) {
            const meta = window.parent.document.createElement("meta");
            meta.name = "google";
            meta.content = "notranslate";
            window.parent.document.head.appendChild(meta);
        }
        </script>
        """,
        height=0,
        width=0,
    )


def main() -> None:
    st.set_page_config(page_title="AI 英语口语陪练", page_icon="🎙️", layout="wide")
    init_state()
    configure_browser_behavior()
    inject_chat_shell_css()

    mode_label = "API 模式" if api_mode_available() else "本地演示模式"
    if st.session_state.selected_scenario not in list_scenarios():
        st.session_state.selected_scenario = list_scenarios()[0]
    if st.session_state.selected_difficulty not in DIFFICULTIES:
        st.session_state.selected_difficulty = get_scenario(st.session_state.selected_scenario)["default_difficulty"]

    collapsed = bool(st.session_state.sidebar_collapsed)
    layout = [0.07, 0.68, 0.25] if collapsed else [0.16, 0.60, 0.24]
    left_rail, center, right = st.columns(layout, gap="small")

    with left_rail:
        render_left_brand(mode_label, collapsed)
        if st.button("展开" if collapsed else "收起", key="toggle_left_rail", width="stretch"):
            st.session_state.sidebar_collapsed = not collapsed
            st.rerun()

        if not collapsed:
            st.markdown('<div class="coach-nav-label">导航</div>', unsafe_allow_html=True)
        view_defs = [
            ("practice", "01 练习终端", "练习"),
            ("history", "02 历史记录", "历史"),
            ("analytics", "03 学习数据", "统计"),
            ("report", "04 报告中心", "报告"),
            ("settings", "05 运行设置", "设置"),
        ]
        for view_key, full_label, short_label in view_defs:
            button_label = short_label if collapsed else full_label
            if st.button(
                button_label,
                key=f"view_{view_key}",
                type="primary" if st.session_state.active_view == view_key else "secondary",
                width="stretch",
            ):
                st.session_state.active_view = view_key

        scenario_key = st.session_state.selected_scenario
        scenario = get_scenario(scenario_key)
        difficulty = st.session_state.selected_difficulty
        if not collapsed:
            st.markdown(
                f"""
                <div class="coach-mode-card">
                  <strong>训练席位</strong>
                  <span>{escape_text(mode_label)} · {escape_text(scenario.get("cn_label", ""))}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('<div class="coach-rail-label">训练参数</div>', unsafe_allow_html=True)
            scenario_key = st.selectbox(
                "场景选择",
                list_scenarios(),
                format_func=scenario_label,
                key="selected_scenario",
            )
            scenario = get_scenario(scenario_key)
            difficulty = st.selectbox(
                "难度选择",
                DIFFICULTIES,
                key="selected_difficulty",
            )
        st.session_state.current_scene = scenario_key
        st.session_state.current_difficulty = difficulty

        session_key = f"{scenario_key}:{difficulty}"
        if st.session_state.current_stage_key and st.session_state.current_stage_key != session_key:
            reset_conversation_state()
        if not st.session_state.current_stage_key:
            st.session_state.current_stage_key = session_key
        current_lesson = stage_progress(scenario_key, st.session_state.current_round)
        refresh_latest_suggestion(scenario_key, scenario)

        if not collapsed:
            render_goal_card(scenario, current_lesson, difficulty, mode_label)

        if st.session_state.active_view == "practice":
            side_start, side_demo = st.columns(2)
            if side_start.button(
                "开始",
                type="primary",
                width="stretch",
                disabled=st.session_state.session_started,
                key="side_start_practice",
            ):
                start_practice_session(scenario_key, difficulty, session_key)
                refresh_latest_suggestion(scenario_key, scenario)
                st.rerun()
            if side_demo.button("演示", width="stretch", key="side_demo_session"):
                load_demo_session(scenario_key, scenario, difficulty, session_key)
                st.rerun()
            side_summary, side_clear = st.columns(2)
            can_summarize = st.session_state.current_round >= MIN_SUMMARY_ROUNDS
            if side_summary.button(
                "总结",
                width="stretch",
                disabled=not can_summarize,
                key="side_summary",
            ):
                if not st.session_state.latest_summary:
                    generate_current_summary(scenario, difficulty)
                st.session_state.active_view = "summary"
                st.rerun()
            if side_clear.button("清空", width="stretch", key="side_clear"):
                reset_conversation_state()
                st.session_state.current_stage_key = session_key
                refresh_latest_suggestion(scenario_key, scenario)
                st.rerun()

    average = average_score(st.session_state.score_history) if st.session_state.score_history else None

    if st.session_state.active_view == "practice":
        round_full = st.session_state.current_round >= MAX_TRAINING_ROUNDS
        with right:
            _, theme_col = st.columns([0.56, 0.44])
            with theme_col:
                st.segmented_control(
                    "主题",
                    options=["dark", "light"],
                    format_func=lambda value: "☾" if value == "dark" else "☼",
                    key="theme_mode",
                    label_visibility="collapsed",
                )
            render_analysis_panel(
                st.session_state.last_ai_reply,
                st.session_state.last_feedback,
                st.session_state.last_score,
                st.session_state.latest_suggestion,
                average,
            )
            render_ai_voice_reply(st.session_state.last_ai_reply)
            render_voice_tools_panel(
                disabled=round_full,
                scenario_key=scenario_key,
                scenario=scenario,
                difficulty=difficulty,
            )

        with center:
            render_chat_status_bar(
                scenario,
                current_lesson,
                st.session_state.current_round,
                MIN_SUMMARY_ROUNDS,
                st.session_state.session_started,
            )

            render_chat_history(st.session_state.conversation_history, height=430)

            render_input_header(round_full, st.session_state.get("recording_status") or st.session_state.get("voice_status", ""))

            if st.session_state.pending_user_input:
                st.session_state.input_text = st.session_state.pending_user_input
                st.session_state.user_input = st.session_state.pending_user_input
                st.session_state.pending_user_input = ""
            if st.session_state.get("pending_input_clear"):
                st.session_state.input_text = ""
                st.session_state.user_input = ""
                st.session_state.pending_input_clear = False

            if st.session_state.input_mode not in {"text", "voice"}:
                st.session_state.input_mode = "text"
            submitted = False
            user_text = st.session_state.input_text

            if st.session_state.input_mode == "text":
                mode_col, answer_col, send_col = st.columns([0.12, 0.70, 0.18])
                with mode_col:
                    if st.button("语音", width="stretch"):
                        st.session_state.input_mode = "voice"
                        st.rerun()
                with answer_col:
                    user_text = st.text_area(
                        "用户英文输入",
                        key="input_text",
                        placeholder="在这里输入英文回答，Enter 发送；长句会自动换行",
                        label_visibility="collapsed",
                        height=76,
                        disabled=round_full,
                    )
                    render_enter_submit_bridge()
                with send_col:
                    st.toggle(
                        "朗读",
                        key="voice_reply_enabled",
                    )
                    submitted = st.button(
                        "发送",
                        type="primary",
                        width="stretch",
                        disabled=round_full,
                    )
            else:
                mode_col, voice_col, send_col = st.columns([0.12, 0.70, 0.18])
                with mode_col:
                    if st.button("键盘", width="stretch"):
                        st.session_state.input_mode = "text"
                        st.rerun()
                with voice_col:
                    recorded_audio = st.audio_input(
                        "语音回答",
                        key="recorded_answer",
                        label_visibility="collapsed",
                    )
                    if st.session_state.voice_transcript:
                        st.markdown(
                            f'<div class="coach-voice-status">最近转写：{escape_text(st.session_state.voice_transcript)}</div>',
                            unsafe_allow_html=True,
                        )
                with send_col:
                    st.toggle(
                        "朗读",
                        key="voice_reply_enabled",
                    )
                    if st.button("转文字", width="stretch", disabled=recorded_audio is None):
                        if transcribe_to_input(recorded_audio, "录音"):
                            st.session_state.input_mode = "text"
                        st.rerun()
                    if st.button(
                        "发送语音",
                        type="primary",
                        width="stretch",
                        disabled=recorded_audio is None
                        or round_full,
                    ):
                        if transcribe_to_input(recorded_audio, "录音"):
                            submit_user_answer(
                                normalize_user_input(st.session_state.voice_transcript),
                                scenario_key,
                                scenario,
                                difficulty,
                                audio_used=True,
                                voice_profile=st.session_state.voice_profile,
                            )
                            st.rerun()
            if submitted:
                bridged_text = consume_enter_submit_text()
                clean_text = normalize_user_input(bridged_text or user_text)
                if submit_user_answer(clean_text, scenario_key, scenario, difficulty, audio_used=False, voice_profile={}):
                    st.rerun()

    else:
        with right:
            if st.session_state.active_view == "summary":
                st.markdown(
                    f"""
                    <div class="coach-analysis-card">
                      <h3>报告信息</h3>
                      <div class="coach-field"><span>场景</span><div>{escape_text(scenario.get("cn_label", ""))}</div></div>
                      <div class="coach-field"><span>难度</span><div>{escape_text(difficulty)}</div></div>
                      <div class="coach-field"><span>轮次</span><div>{st.session_state.current_round}</div></div>
                      <div class="coach-field"><span>平均分</span><div>{average or 0}/100</div></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                render_analysis_panel(
                    st.session_state.last_ai_reply,
                    st.session_state.last_feedback,
                    st.session_state.last_score,
                    st.session_state.latest_suggestion,
                    average,
                )

        with center:
            if st.session_state.active_view == "history":
                render_history_tab()
            elif st.session_state.active_view == "analytics":
                render_analytics_tab()
            elif st.session_state.active_view == "summary":
                back_col, download_col = st.columns([1, 1])
                with back_col:
                    if st.button("返回练习", width="stretch"):
                        st.session_state.active_view = "practice"
                        st.rerun()
                with download_col:
                    if st.session_state.latest_summary_path:
                        summary_path = Path(st.session_state.latest_summary_path)
                        if summary_path.exists():
                            st.download_button(
                                "导出 Markdown 报告",
                                data=summary_path.read_text(encoding="utf-8").encode("utf-8"),
                                file_name=summary_path.name,
                                mime="text/markdown",
                                width="stretch",
                            )
                render_summary_report(
                    st.session_state.latest_summary,
                    scenario.get("cn_label", ""),
                    difficulty,
                    st.session_state.current_round,
                    average or 0,
                )
            elif st.session_state.active_view == "report":
                render_report_tab()
            elif st.session_state.active_view == "settings":
                render_settings_tab(mode_label)
            else:
                st.session_state.active_view = "practice"
                st.rerun()


if __name__ == "__main__":
    main()
