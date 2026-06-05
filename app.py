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
from speech_utils import SUPPORTED_AUDIO_TYPES, transcribe_audio
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


def init_state() -> None:
    defaults = {
        "history": [],
        **empty_session_state(),
        "last_feedback": None,
        "last_score": None,
        "last_ai_reply": "",
        "latest_summary": "",
        "latest_summary_path": "",
        "latest_html_path": "",
        "current_record_path": "",
        "audio_text": "",
        "user_input": "",
        "voice_transcript": "",
        "voice_status": "",
        "last_spoken_reply": "",
        "voice_reply_enabled": True,
        "pending_user_input": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_conversation_state() -> None:
    for key, value in empty_session_state().items():
        st.session_state[key] = value
    st.session_state.history = []
    st.session_state.last_feedback = None
    st.session_state.last_score = None
    st.session_state.last_ai_reply = ""
    st.session_state.latest_summary = ""
    st.session_state.latest_summary_path = ""
    st.session_state.latest_html_path = ""
    st.session_state.current_record_path = ""
    st.session_state.audio_text = ""
    st.session_state.user_input = ""
    st.session_state.voice_transcript = ""
    st.session_state.voice_status = ""
    st.session_state.last_spoken_reply = ""
    st.session_state.pending_user_input = ""


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


def transcribe_to_input(audio_file, source_label: str = "录音") -> bool:
    """Transcribe an uploaded or recorded audio object into the answer box."""
    result = transcribe_audio(audio_file)
    st.session_state.voice_status = result["message"]
    if result["success"]:
        st.session_state.voice_transcript = result["text"]
        st.session_state.audio_text = result["text"]
        st.session_state.pending_user_input = result["text"]
        st.success(f"{source_label}转写完成。")
        return True
    st.warning(result["message"])
    return False


def submit_user_answer(
    clean_text: str,
    scenario_key: str,
    scenario: dict,
    difficulty: str,
    audio_used: bool = False,
) -> bool:
    """Submit one answer through the shared multi-turn conversation flow."""
    if not st.session_state.session_started:
        st.warning("请先点击“开始练习”，让 AI 提出第一个问题。")
        return False
    if st.session_state.current_round >= MAX_TRAINING_ROUNDS:
        st.warning("本次训练已达到 8 轮上限，可以生成课后总结或清空后重新开始。")
        return False
    if not clean_text:
        st.warning("请输入或转写英文句子后再提交。")
        return False

    result = process_user_turn(
        clean_text,
        scenario_key,
        scenario,
        difficulty,
        st.session_state.conversation_history,
        st.session_state.current_round,
        audio_used=audio_used,
    )
    turn = result["turn"]
    st.session_state.conversation_history.append(
        {"role": "user", "content": clean_text, "stage": result["stage"]["title"]}
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
    st.session_state.last_ai_reply = turn["ai_reply"]

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
    st.toast(f"练习记录已保存：{record_path.name}")
    return True


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
    st.write("**语音模式：** 录音提交式语音对话。用户录一段英文回答后转写并提交，AI 追问可由浏览器朗读。")
    st.write("**语音边界：** 当前不是全双工实时通话；语音失败时文本输入仍是主流程。")
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
        <style>
        :root {
            --coach-bg: #0b1220;
            --coach-panel: #101827;
            --coach-panel-2: #111f32;
            --coach-border: #243244;
            --coach-muted: #9fb0c3;
            --coach-text: #f8fafc;
            --coach-blue: #38bdf8;
            --coach-green: #22c55e;
            --coach-amber: #f59e0b;
        }
        .block-container { padding-top: 1.4rem; }
        .stChatMessage { border: 1px solid #edf0f2; border-radius: 10px; }
        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(148, 163, 184, 0.18);
        }
        .coach-hero {
            display: grid;
            grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.9fr);
            gap: 18px;
            background:
                radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 30%),
                linear-gradient(135deg, #0f172a, #111827 65%, #0b1220);
            border: 1px solid #233244;
            border-radius: 18px;
            padding: 26px 28px;
            margin-bottom: 20px;
            color: var(--coach-text);
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.24);
        }
        .coach-hero h1 {
            margin: 4px 0 8px;
            font-size: 38px;
            line-height: 1.12;
            color: #ffffff;
            letter-spacing: 0;
        }
        .coach-hero p {
            margin: 0;
            max-width: 720px;
            color: #cbd5e1;
            font-size: 15px;
            line-height: 1.7;
        }
        .coach-eyebrow {
            color: #67e8f9;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0;
            text-transform: uppercase;
        }
        .hero-status-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
        }
        .hero-status-item {
            background: rgba(15, 23, 42, 0.82);
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 12px;
            padding: 12px 14px;
        }
        .hero-status-item span,
        .lesson-prompt-grid span {
            display: block;
            color: #94a3b8;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .hero-status-item strong,
        .lesson-prompt-grid strong {
            color: #f8fafc;
            font-size: 15px;
            line-height: 1.35;
        }
        .section-intro {
            margin: 6px 0 18px;
        }
        .section-intro h2 {
            margin: 0 0 4px;
            color: #f8fafc;
            font-size: 25px;
            line-height: 1.2;
        }
        .section-intro p {
            margin: 0;
            color: #aebed0;
            font-size: 14px;
        }
        .lesson-card {
            background: linear-gradient(135deg, #101827, #102033);
            border: 1px solid #26364a;
            border-radius: 16px;
            padding: 18px 20px;
            margin: 4px 0 18px;
            color: #e5e7eb;
        }
        .lesson-card-head {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
        }
        .lesson-card h3 {
            margin: 3px 0 0;
            color: #ffffff;
            font-size: 22px;
        }
        .lesson-card-head > strong {
            color: #f8fafc;
            background: #0b1220;
            border: 1px solid #334155;
            border-radius: 999px;
            padding: 6px 10px;
            min-width: 64px;
            text-align: center;
        }
        .lesson-progress-track {
            height: 9px;
            background: #0b1220;
            border: 1px solid #334155;
            border-radius: 999px;
            overflow: hidden;
            margin: 14px 0;
        }
        .lesson-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--coach-blue), var(--coach-green));
        }
        .lesson-card p {
            color: #cbd5e1;
            margin: 10px 0 14px;
            line-height: 1.65;
        }
        .lesson-prompt-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
        }
        .lesson-prompt-grid div,
        .empty-panel {
            background: #0b1220;
            border: 1px solid #26364a;
            border-radius: 12px;
            padding: 12px 14px;
        }
        .empty-panel {
            color: #cbd5e1;
            display: grid;
            gap: 4px;
        }
        .empty-panel strong {
            color: #f8fafc;
        }
        div[data-testid="stTabs"] button[role="tab"] {
            font-weight: 750;
            border-radius: 10px 10px 0 0;
        }
        .score-total-card {
            background: linear-gradient(135deg, #0f172a, #111f32) !important;
            border: 1px solid #475569 !important;
            border-radius: 12px;
            padding: 18px 20px;
            margin: 8px 0 18px;
            color: #f8fafc !important;
            box-shadow: 0 8px 18px rgba(0, 0, 0, 0.20);
        }
        .score-total-card * {
            color: inherit !important;
        }
        .score-total-label {
            color: #cbd5e1 !important;
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 6px;
        }
        .score-total-value {
            color: #ffffff !important;
            font-size: 34px;
            font-weight: 800;
            line-height: 1.1;
            text-shadow: 0 1px 0 rgba(0, 0, 0, 0.22);
        }
        .score-dimension-card {
            background: #0f172a !important;
            border: 1px solid #334155 !important;
            border-radius: 10px;
            padding: 14px 16px;
            margin: 12px 0;
            color: #e5e7eb !important;
        }
        .score-dimension-head {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            color: #f8fafc !important;
            font-size: 16px;
            font-weight: 750;
            margin-bottom: 10px;
        }
        .score-dimension-head span,
        .score-dimension-head strong {
            color: #f8fafc !important;
        }
        .score-bar-track {
            height: 9px;
            background: #1e293b;
            border-radius: 999px;
            overflow: hidden;
            border: 1px solid #334155;
        }
        .score-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #38bdf8, #22c55e);
            border-radius: 999px;
        }
        .score-explanation {
            color: #cbd5e1 !important;
            font-size: 13px;
            line-height: 1.5;
            margin-top: 9px;
        }
        @media (max-width: 900px) {
            .coach-hero,
            .lesson-prompt-grid {
                grid-template-columns: 1fr;
            }
            .coach-hero h1 {
                font-size: 30px;
            }
        }
        </style>
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

    scenario_key = st.sidebar.selectbox(
        "场景选择",
        list_scenarios(),
        format_func=scenario_label,
    )
    scenario = get_scenario(scenario_key)
    difficulty = st.sidebar.selectbox(
        "难度选择",
        DIFFICULTIES,
        index=DIFFICULTIES.index(scenario["default_difficulty"]),
    )
    session_key = f"{scenario_key}:{difficulty}"
    if st.session_state.current_stage_key and st.session_state.current_stage_key != session_key:
        reset_conversation_state()
    if not st.session_state.current_stage_key:
        st.session_state.current_stage_key = session_key
    mode_label = "API 模式" if api_mode_available() else "本地演示模式"

    st.sidebar.title("AI-English-Coach")
    st.sidebar.info(f"当前模式：{mode_label}")
    st.sidebar.markdown("**练习目标**")
    st.sidebar.write(scenario["user_goal"])
    with st.sidebar.expander("常见问题与推荐表达", expanded=True):
        st.write("**常见问题**")
        for question in scenario["common_questions"]:
            st.write(f"- {question}")
        st.write("**推荐表达**")
        for expression in scenario["recommended_expressions"]:
            st.write(f"- {expression}")
    with st.sidebar.expander("最近保存记录", expanded=True):
        files = list_history_files()
        if not files:
            st.caption("暂无历史记录。")
        else:
            selected_history = st.selectbox(
                "选择历史记录",
                files,
                format_func=lambda file: file.name,
            )
            try:
                render_history_record(load_practice_record(selected_history))
            except Exception as exc:
                st.warning(f"历史记录读取失败：{exc}")

    current_lesson = stage_progress(scenario_key, st.session_state.current_round)
    render_app_header(scenario, difficulty, mode_label, current_lesson["progress"])

    practice_tab, history_tab, analytics_tab, report_tab, settings_tab = st.tabs(
        ["练习中心", "历史记录", "学习统计", "报告导出", "设置说明"]
    )

    with practice_tab:
        left_sidebar, center, right = st.columns([0.9, 1.45, 1])

        with left_sidebar:
            render_section_intro("训练状态", "场景、难度、训练目标和当前模式。")
            st.metric("已完成轮次", f"{st.session_state.current_round}/{MIN_SUMMARY_ROUNDS}")
            st.write(f"**场景：** {scenario['cn_label']}")
            st.write(f"**难度：** {difficulty}")
            st.write(f"**模式：** {mode_label}")
            st.write(f"**状态：** {'已开始' if st.session_state.session_started else '未开始'}")
            render_course_panel(scenario_key)

        with center:
            render_section_intro("多轮场景对话", "点击开始后由 AI 主动开场；每次回答后进入下一轮追问。")
            start_col, clear_col = st.columns([1, 1])
            if start_col.button(
                "开始练习",
                type="primary",
                width="stretch",
                disabled=st.session_state.session_started,
            ):
                reset_conversation_state()
                st.session_state.current_stage_key = session_key
                opening = build_opening_question(scenario_key, difficulty)
                st.session_state.conversation_history.append(
                    {"role": "assistant", "content": opening, "stage": current_lesson["current_step"]["title"]}
                )
                st.session_state.last_ai_reply = opening
                st.session_state.session_started = True
                st.rerun()
            if clear_col.button("清空当前对话", width="stretch"):
                reset_conversation_state()
                st.session_state.current_stage_key = session_key
                st.rerun()

            text_col, voice_col = st.columns([1.15, 0.95])
            with text_col:
                st.markdown("**文本回答**")
                quick_col1, quick_col2 = st.columns([1, 1])
                if quick_col1.button("填入当前任务问题", width="stretch"):
                    st.session_state.user_input = current_lesson["current_step"]["prompt"]
                    st.rerun()
                if quick_col2.button("填入示例回答", width="stretch"):
                    st.session_state.user_input = (
                        f"{current_lesson['current_step']['target_expression']} "
                        "I can explain this with one specific example."
                    )
                    st.rerun()

                if st.session_state.pending_user_input:
                    st.session_state.user_input = st.session_state.pending_user_input
                    st.session_state.pending_user_input = ""

                user_text = st.text_area(
                    "用户英文输入",
                    key="user_input",
                    height=150,
                    placeholder="Example: I am agree we should discuss about this topic",
                )
                submitted = st.button(
                    "提交回答",
                    type="primary",
                    width="stretch",
                    disabled=not st.session_state.session_started
                    or st.session_state.current_round >= MAX_TRAINING_ROUNDS,
                )

            with voice_col:
                st.markdown("**语音回答**")
                st.toggle(
                    "AI 朗读追问",
                    key="voice_reply_enabled",
                    help="使用浏览器 SpeechSynthesis 朗读 AI 的最新追问。",
                )
                recorded_audio = st.audio_input(
                    "录制英文回答",
                    key="recorded_answer",
                    help="录一段英文回答后，可转写到输入框或直接提交。",
                )
                rec_col1, rec_col2 = st.columns([1, 1])
                if rec_col1.button("转写到输入框", width="stretch", disabled=recorded_audio is None):
                    transcribe_to_input(recorded_audio, "录音")
                    st.rerun()
                if rec_col2.button(
                    "转写并提交回答",
                    width="stretch",
                    disabled=recorded_audio is None
                    or not st.session_state.session_started
                    or st.session_state.current_round >= MAX_TRAINING_ROUNDS,
                ):
                    if transcribe_to_input(recorded_audio, "录音"):
                        submit_user_answer(
                            normalize_user_input(st.session_state.voice_transcript),
                            scenario_key,
                            scenario,
                            difficulty,
                            audio_used=True,
                        )
                        st.rerun()

                uploaded_file = st.file_uploader(
                    "上传音频文件（可选）",
                    type=SUPPORTED_AUDIO_TYPES,
                    help="支持 wav、mp3、m4a。若本地语音模型不可用，系统会自动降级到文本输入。",
                )
                file_col1, file_col2 = st.columns([1, 1])
                if file_col1.button("转写文件", width="stretch", disabled=uploaded_file is None):
                    transcribe_to_input(uploaded_file, "音频文件")
                    st.rerun()
                if file_col2.button(
                    "转写文件并提交",
                    width="stretch",
                    disabled=uploaded_file is None
                    or not st.session_state.session_started
                    or st.session_state.current_round >= MAX_TRAINING_ROUNDS,
                ):
                    if transcribe_to_input(uploaded_file, "音频文件"):
                        submit_user_answer(
                            normalize_user_input(st.session_state.voice_transcript),
                            scenario_key,
                            scenario,
                            difficulty,
                            audio_used=True,
                        )
                        st.rerun()

                if st.session_state.voice_status:
                    st.caption(st.session_state.voice_status)
                if st.session_state.voice_transcript:
                    st.info(f"最近转写：{st.session_state.voice_transcript}")

            button_col2 = st.container()
            can_summarize = st.session_state.current_round >= MIN_SUMMARY_ROUNDS
            if button_col2.button("生成课后总结", width="stretch", disabled=not can_summarize):
                if not can_summarize:
                    st.warning(f"请至少完成 {MIN_SUMMARY_ROUNDS} 轮对话后再生成总结。")
                else:
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

            if submitted:
                clean_text = normalize_user_input(user_text)
                if submit_user_answer(clean_text, scenario_key, scenario, difficulty, audio_used=False):
                    st.rerun()

            st.subheader("对话历史")
            if not st.session_state.conversation_history:
                st.markdown(
                    """
                    <div class="empty-panel">
                      <strong>还没有对话记录</strong>
                      <span>点击开始练习后，AI 会主动提出第一个问题。</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            for item in st.session_state.conversation_history:
                with st.chat_message(item["role"]):
                    if item.get("stage"):
                        st.caption(item["stage"])
                    st.write(item["content"])
            if st.session_state.current_round >= MIN_SUMMARY_ROUNDS and not st.session_state.latest_summary:
                st.info("已完成 5 轮训练，可以生成课后总结。")

        with right:
            st.subheader("本轮 AI 追问")
            if st.session_state.last_ai_reply:
                st.success(st.session_state.last_ai_reply)
                render_ai_voice_reply(st.session_state.last_ai_reply)
            else:
                st.markdown(
                    """
                    <div class="empty-panel">
                      <strong>等待 AI 角色回复</strong>
                      <span>提交练习后会显示贴合当前场景的追问。</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.subheader("纠错反馈")
            render_feedback(st.session_state.last_feedback)

            st.subheader("评分")
            if st.session_state.last_score:
                render_score(st.session_state.last_score)
            else:
                st.markdown(
                    """
                    <div class="empty-panel">
                      <strong>等待评分</strong>
                      <span>提交练习后显示综合分和五个维度评分。</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if st.session_state.latest_summary:
                st.subheader("本次总结")
                st.markdown(st.session_state.latest_summary)
            if st.session_state.score_history:
                st.caption(f"会话平均分：{average_score(st.session_state.score_history)}/100")

        st.divider()
        summary_col, expression_col = st.columns([1.4, 1])
        with summary_col:
            st.subheader("课后总结")
            if st.session_state.latest_summary:
                st.markdown(st.session_state.latest_summary)
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
            else:
                st.info(f"完成至少 {MIN_SUMMARY_ROUNDS} 轮后，可在输入区生成课后总结。")
        with expression_col:
            st.subheader("推荐表达")
            for expression in scenario.get("recommended_expressions", []):
                st.write(f"- {expression}")
            if st.session_state.last_feedback:
                st.write("**本轮可替代表达**")
                for expression in st.session_state.last_feedback.get("alternative_expressions", []):
                    st.write(f"- {expression}")

    with history_tab:
        render_history_tab()

    with analytics_tab:
        render_analytics_tab()

    with report_tab:
        render_report_tab()

    with settings_tab:
        render_settings_tab(mode_label)


if __name__ == "__main__":
    main()
