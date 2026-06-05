"""Reusable Streamlit UI components for the dark chat product shell."""

from __future__ import annotations

import html
from typing import Iterable

import streamlit as st
import streamlit.components.v1 as components


DIMENSION_ORDER = [
    ("pronunciation", "Pronunciation"),
    ("fluency", "Fluency"),
    ("grammar", "Grammar"),
    ("expression", "Expression"),
    ("completeness", "Completeness"),
]


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def inject_chat_shell_css() -> None:
    """Apply the dark three-column product styling."""
    st.markdown(
        """
        <style>
        :root {
            --coach-bg: #0b0f14;
            --coach-panel: #111827;
            --coach-panel-2: #0f172a;
            --coach-panel-3: #0b1220;
            --coach-border: rgba(255,255,255,0.08);
            --coach-border-strong: rgba(148,163,184,0.24);
            --coach-text: #f8fafc;
            --coach-muted: #94a3b8;
            --coach-soft: #cbd5e1;
            --coach-red: #ff4d4f;
            --coach-blue: #4f8cff;
            --coach-purple: #7c3aed;
            --coach-green: #22c55e;
        }

        .stApp {
            background: var(--coach-bg);
            color: var(--coach-text);
        }
        .block-container {
            max-width: none;
            padding: 1rem 1.1rem 1.25rem;
        }
        header[data-testid="stHeader"] {
            background: transparent;
        }
        section[data-testid="stSidebar"] {
            display: none;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0.45rem;
        }
        div[data-testid="column"] > div {
            min-width: 0;
        }
        h1, h2, h3, h4, h5, h6, p, label, span, div {
            letter-spacing: 0;
        }
        label, .stMarkdown, .stCaption, [data-testid="stMarkdownContainer"] {
            color: var(--coach-text);
        }
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li {
            color: var(--coach-soft);
        }
        .stSelectbox label,
        .stTextArea label,
        .stFileUploader label,
        .stAudioInput label,
        .stCheckbox label,
        .stRadio label {
            color: var(--coach-soft) !important;
            font-size: 12px !important;
            font-weight: 700 !important;
        }
        .stSelectbox div[data-baseweb="select"] > div,
        textarea,
        input {
            background: #0b1220 !important;
            border-color: rgba(148,163,184,0.20) !important;
            color: var(--coach-text) !important;
            border-radius: 8px !important;
        }
        textarea {
            min-height: 68px !important;
            line-height: 1.5 !important;
            resize: vertical;
        }
        .stButton > button,
        .stDownloadButton > button {
            border-radius: 8px !important;
            border: 1px solid rgba(148,163,184,0.22) !important;
            background: #111827 !important;
            color: #f8fafc !important;
            font-weight: 750 !important;
            min-height: 38px;
        }
        .stButton > button *,
        .stDownloadButton > button * {
            color: inherit !important;
        }
        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {
            background: linear-gradient(135deg, #ff4d4f, #7c3aed 68%, #4f8cff) !important;
            border-color: rgba(255,255,255,0.16) !important;
            color: #ffffff !important;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: rgba(79,140,255,0.65) !important;
            color: #ffffff !important;
        }
        .stButton > button:disabled,
        .stDownloadButton > button:disabled {
            opacity: 0.48;
            cursor: not-allowed;
        }
        div[data-testid="stMetric"] {
            background: #0f172a;
            border: 1px solid var(--coach-border);
            border-radius: 8px;
            padding: 10px 12px;
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] span {
            color: var(--coach-muted) !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--coach-text) !important;
        }
        .stDataFrame,
        .stExpander {
            border-radius: 8px !important;
        }

        .coach-shell-card {
            background: linear-gradient(180deg, rgba(17,24,39,0.98), rgba(15,23,42,0.98));
            border: 1px solid var(--coach-border);
            border-radius: 8px;
            padding: 14px;
            box-shadow: 0 14px 34px rgba(0,0,0,0.24);
        }
        .coach-left-rail {
            margin-bottom: 10px;
        }
        .coach-brand {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            align-items: flex-start;
            margin-bottom: 14px;
        }
        h1.coach-brand-title,
        .coach-brand-title {
            margin: 0;
            font-size: 20px !important;
            line-height: 1.22 !important;
            font-weight: 850 !important;
            color: #ffffff !important;
        }
        .coach-brand-subtitle {
            margin-top: 5px;
            color: var(--coach-muted);
            font-size: 12px;
            line-height: 1.45;
        }
        .coach-status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            max-width: 100%;
            padding: 6px 8px;
            border-radius: 999px;
            background: rgba(79,140,255,0.12);
            border: 1px solid rgba(79,140,255,0.32);
            color: #bfdbfe;
            font-size: 11px;
            font-weight: 800;
            overflow-wrap: anywhere;
        }
        .coach-control-title {
            margin: 14px 0 8px;
            color: #e2e8f0;
            font-size: 12px;
            font-weight: 850;
            text-transform: uppercase;
        }
        .coach-goal-card,
        .coach-mini-card,
        .coach-stage-card,
        .coach-chat-panel,
        .coach-analysis-card,
        .coach-summary-card {
            background: #111827;
            border: 1px solid var(--coach-border);
            border-radius: 8px;
            padding: 12px;
        }
        .coach-goal-card {
            margin-top: 10px;
            color: #cbd5e1;
            font-size: 13px;
            line-height: 1.55;
        }
        .coach-stage-card {
            margin-top: 10px;
        }
        .coach-stage-head,
        .coach-card-head {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 10px;
            margin-bottom: 8px;
        }
        .coach-stage-head strong,
        .coach-card-head strong {
            color: #f8fafc;
            font-size: 14px;
            line-height: 1.25;
        }
        .coach-stage-head span,
        .coach-card-head span {
            color: var(--coach-muted);
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
        }
        .coach-progress-track {
            height: 7px;
            border-radius: 999px;
            overflow: hidden;
            background: #0b1220;
            border: 1px solid rgba(148,163,184,0.18);
        }
        .coach-progress-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #ff4d4f, #7c3aed, #4f8cff);
        }
        .coach-stage-card p {
            margin: 8px 0 0;
            color: #cbd5e1;
            font-size: 12px;
            line-height: 1.55;
        }
        .coach-nav-note {
            color: var(--coach-muted);
            font-size: 12px;
            line-height: 1.45;
            margin-top: 8px;
        }
        .coach-collapsed-brand {
            display: grid;
            gap: 8px;
            justify-items: center;
            padding: 6px 0;
        }
        .coach-collapsed-logo {
            width: 36px;
            height: 36px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            color: #ffffff;
            font-weight: 900;
            background: linear-gradient(135deg, #ff4d4f, #7c3aed);
        }

        .coach-chat-panel {
            min-height: calc(100vh - 36px);
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .coach-statusbar {
            display: grid;
            grid-template-columns: minmax(0, 1.15fr) minmax(250px, 0.85fr);
            gap: 8px;
            align-items: stretch;
        }
        .coach-status-main {
            background: #0f172a;
            border: 1px solid var(--coach-border);
            border-radius: 8px;
            padding: 10px;
        }
        .coach-status-main h1 {
            margin: 0;
            color: #ffffff;
            font-size: 20px;
            line-height: 1.2;
        }
        .coach-status-main p {
            margin: 5px 0 0;
            color: var(--coach-muted);
            font-size: 12px;
            line-height: 1.5;
        }
        .coach-status-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 6px;
        }
        .coach-status-metric {
            background: #0b1220;
            border: 1px solid var(--coach-border);
            border-radius: 8px;
            padding: 8px;
        }
        .coach-status-metric span {
            display: block;
            color: var(--coach-muted);
            font-size: 10px;
            font-weight: 800;
            margin-bottom: 4px;
        }
        .coach-status-metric strong {
            display: block;
            color: #f8fafc;
            font-size: 12px;
            line-height: 1.25;
            overflow-wrap: anywhere;
        }
        .coach-input-shell {
            background: #0f172a;
            border: 1px solid var(--coach-border);
            border-radius: 8px;
            padding: 10px;
        }
        .coach-input-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            color: #f8fafc;
            font-weight: 850;
            font-size: 13px;
            margin-bottom: 6px;
        }
        .coach-input-title span {
            color: var(--coach-muted);
            font-size: 12px;
            font-weight: 700;
        }
        .coach-voice-status {
            color: #cbd5e1;
            font-size: 12px;
            line-height: 1.45;
            padding: 8px 10px;
            background: #0b1220;
            border: 1px solid var(--coach-border);
            border-radius: 8px;
        }
        .coach-empty {
            background: #0b1220;
            border: 1px dashed rgba(148,163,184,0.25);
            border-radius: 8px;
            padding: 10px;
            color: #cbd5e1;
            font-size: 12px;
            line-height: 1.55;
        }
        .coach-empty strong {
            display: block;
            color: #f8fafc;
            margin-bottom: 4px;
        }

        .coach-analysis-stack {
            min-height: calc(100vh - 34px);
            display: grid;
            gap: 12px;
            align-content: start;
        }
        .coach-analysis-card h3,
        .coach-summary-card h3 {
            margin: 0 0 9px;
            color: #f8fafc;
            font-size: 15px;
            line-height: 1.25;
        }
        .coach-analysis-card p,
        .coach-summary-card p {
            margin: 0;
            color: #cbd5e1;
            font-size: 13px;
            line-height: 1.55;
        }
        .coach-field {
            margin-top: 10px;
        }
        .coach-field span {
            display: block;
            color: var(--coach-muted);
            font-size: 11px;
            font-weight: 850;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .coach-field div,
        .coach-field ul {
            color: #e2e8f0;
            font-size: 13px;
            line-height: 1.5;
            margin: 0;
        }
        .coach-field ul {
            padding-left: 17px;
        }
        .coach-score-total {
            display: flex;
            align-items: baseline;
            gap: 8px;
            padding: 10px;
            border-radius: 8px;
            background: linear-gradient(135deg, rgba(255,77,79,0.16), rgba(79,140,255,0.12));
            border: 1px solid rgba(255,255,255,0.10);
            margin-bottom: 10px;
        }
        .coach-score-total strong {
            color: #ffffff;
            font-size: 28px;
            line-height: 1;
        }
        .coach-score-total span {
            color: var(--coach-muted);
            font-size: 12px;
            font-weight: 800;
        }
        .coach-score-row {
            margin-top: 10px;
        }
        .coach-score-row-head {
            display: flex;
            justify-content: space-between;
            gap: 8px;
            color: #f8fafc;
            font-size: 12px;
            font-weight: 850;
            margin-bottom: 5px;
        }
        .coach-score-explain {
            margin-top: 5px;
            color: #94a3b8;
            font-size: 11px;
            line-height: 1.42;
        }
        .coach-note {
            margin-top: 9px;
            color: #94a3b8;
            font-size: 11px;
            line-height: 1.45;
        }
        .coach-summary-card {
            margin-top: 12px;
        }
        .coach-recommend-list {
            display: grid;
            gap: 8px;
        }
        .coach-recommend-item {
            padding: 9px 10px;
            border-radius: 8px;
            background: #0b1220;
            border: 1px solid var(--coach-border);
            color: #e2e8f0;
            font-size: 12px;
            line-height: 1.45;
        }

        @media (max-width: 980px) {
            .coach-statusbar,
            .coach-status-grid {
                grid-template-columns: 1fr;
            }
            .block-container {
                padding-left: 0.75rem;
                padding-right: 0.75rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    components.html(
        """
        <script>
        function lockCoachScroll() {
            const main = window.parent.document.querySelector('[data-testid="stMainBlockContainer"]');
            if (main) {
                main.style.scrollBehavior = "auto";
                main.scrollTop = 0;
            }
            window.parent.scrollTo(0, 0);
        }
        lockCoachScroll();
        window.parent.requestAnimationFrame(lockCoachScroll);
        window.parent.setTimeout(lockCoachScroll, 80);
        window.parent.setTimeout(lockCoachScroll, 300);
        window.parent.setTimeout(lockCoachScroll, 900);
        </script>
        """,
        height=0,
        width=0,
    )
    is_light = st.session_state.get("theme_mode") == "light"
    theme = {
        "bg": "#e9edf2" if is_light else "#16181d",
        "panel": "rgba(246,247,249,0.80)" if is_light else "rgba(34,37,44,0.76)",
        "panel_2": "rgba(226,231,238,0.66)" if is_light else "rgba(58,62,72,0.50)",
        "input": "rgba(218,224,233,0.78)" if is_light else "rgba(62,66,76,0.58)",
        "border": "rgba(50,58,68,0.16)" if is_light else "rgba(229,233,240,0.13)",
        "border_strong": "rgba(50,58,68,0.26)" if is_light else "rgba(229,233,240,0.24)",
        "text": "#20252d" if is_light else "#e8eaed",
        "muted": "#66707d" if is_light else "#a7afba",
        "soft": "#3b4350" if is_light else "#c7cdd6",
        "button": "rgba(229,234,241,0.76)" if is_light else "rgba(66,70,80,0.62)",
        "button_text": "#20252d" if is_light else "#e8eaed",
        "primary": "#687382" if is_light else "#b8c0cc",
        "primary_text": "#f7f8fa" if is_light else "#20252d",
        "shadow": "0 18px 44px rgba(66,75,88,0.16)" if is_light else "0 18px 44px rgba(0,0,0,0.28)",
    }
    st.markdown(
        f"""
        <style>
        :root {{
            --coach-bg: {theme["bg"]};
            --coach-panel: {theme["panel"]};
            --coach-panel-2: {theme["panel_2"]};
            --coach-panel-3: {theme["input"]};
            --coach-border: {theme["border"]};
            --coach-border-strong: {theme["border_strong"]};
            --coach-text: {theme["text"]};
            --coach-muted: {theme["muted"]};
            --coach-soft: {theme["soft"]};
            --coach-button: {theme["button"]};
            --coach-button-text: {theme["button_text"]};
            --coach-primary: {theme["primary"]};
            --coach-primary-text: {theme["primary_text"]};
            --coach-shadow: {theme["shadow"]};
        }}
        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] {{
            height: 100vh !important;
            max-height: 100vh !important;
            overflow: hidden !important;
        }}
        [data-testid="stMain"] {{
            align-items: flex-start !important;
        }}
        .stApp {{
            background: var(--coach-bg) !important;
            color: var(--coach-text) !important;
        }}
        .block-container {{
            height: 100vh !important;
            max-height: 100vh !important;
            padding: 0.65rem 0.8rem !important;
            overflow: hidden !important;
        }}
        .block-container > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-child {{
            height: calc(100vh - 1.3rem) !important;
            overflow: hidden !important;
            align-items: stretch !important;
        }}
        div[data-testid="column"] {{
            min-width: 0 !important;
        }}
        div[data-testid="column"] > div {{
            min-width: 0 !important;
            height: 100% !important;
            overflow: hidden !important;
        }}
        div[data-testid="column"] > div > div[data-testid="stVerticalBlock"] {{
            gap: 0.42rem !important;
        }}
        .coach-shell-card,
        .coach-goal-card,
        .coach-stage-card,
        .coach-status-main,
        .coach-status-metric,
        .coach-input-shell,
        .coach-analysis-card,
        .coach-summary-card,
        .voice-lab-card,
        div[data-testid="stMetric"] {{
            background: var(--coach-panel) !important;
            border-color: var(--coach-border) !important;
            color: var(--coach-text) !important;
            box-shadow: var(--coach-shadow) !important;
            backdrop-filter: blur(24px) saturate(1.25);
            -webkit-backdrop-filter: blur(24px) saturate(1.25);
        }}
        .coach-stage-card,
        .coach-empty,
        .lesson-prompt-grid div,
        .coach-voice-status,
        .score-dimension-card,
        .score-total-card {{
            background: var(--coach-panel-2) !important;
            border-color: var(--coach-border) !important;
            color: var(--coach-text) !important;
        }}
        .stButton > button,
        .stDownloadButton > button,
        button[kind="secondary"],
        button[data-testid="stBaseButton-secondary"] {{
            background: var(--coach-button) !important;
            color: var(--coach-button-text) !important;
            border-color: var(--coach-border-strong) !important;
            box-shadow: none !important;
            min-height: 36px !important;
        }}
        .stButton > button *,
        .stDownloadButton > button *,
        button[kind="secondary"] *,
        button[data-testid="stBaseButton-secondary"] *,
        button[kind="primary"] *,
        button[data-testid="stBaseButton-primary"] * {{
            color: inherit !important;
        }}
        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"],
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {{
            background: var(--coach-primary) !important;
            color: var(--coach-primary-text) !important;
            border-color: var(--coach-primary) !important;
        }}
        .stButton > button:disabled,
        .stDownloadButton > button:disabled,
        button:disabled {{
            background: color-mix(in srgb, var(--coach-button) 78%, transparent) !important;
            color: var(--coach-muted) !important;
            border-color: var(--coach-border) !important;
            opacity: 0.72 !important;
        }}
        .coach-progress-fill,
        .score-bar-fill {{
            background: var(--coach-primary) !important;
        }}
        .coach-collapsed-logo {{
            background: var(--coach-primary) !important;
            color: var(--coach-primary-text) !important;
        }}
        .coach-status-pill {{
            background: var(--coach-panel-2) !important;
            border-color: var(--coach-border-strong) !important;
            color: var(--coach-text) !important;
        }}
        .coach-brand-title,
        .coach-status-main h1,
        .coach-analysis-card h3,
        .coach-summary-card h3,
        .coach-stage-head strong,
        .coach-card-head strong,
        .coach-empty strong,
        .coach-score-row-head,
        .coach-score-total strong {{
            color: var(--coach-text) !important;
        }}
        .coach-brand-subtitle,
        .coach-status-main p,
        .coach-field span,
        .coach-score-explain,
        .coach-input-title span,
        .coach-control-title {{
            color: var(--coach-muted) !important;
        }}
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        .coach-field div,
        .coach-field ul,
        .coach-analysis-card p,
        .coach-summary-card p {{
            color: var(--coach-soft) !important;
        }}
        .stSelectbox div[data-baseweb="select"] > div,
        textarea,
        input {{
            background: var(--coach-panel-3) !important;
            color: var(--coach-text) !important;
            border-color: var(--coach-border-strong) !important;
        }}
        textarea {{
            min-height: 58px !important;
            resize: none !important;
        }}
        textarea::placeholder,
        input::placeholder {{
            color: var(--coach-muted) !important;
            opacity: 1 !important;
        }}
        .stSelectbox div[data-baseweb="select"] span,
        .stSelectbox div[data-baseweb="select"] svg {{
            color: var(--coach-text) !important;
            fill: var(--coach-text) !important;
        }}
        .stCheckbox label,
        .stCheckbox label span,
        .stTextArea label,
        .stAudioInput label,
        .stFileUploader label {{
            color: var(--coach-text) !important;
        }}
        .coach-input-title,
        .coach-input-title > div {{
            color: var(--coach-text) !important;
        }}
        .coach-analysis-card {{
            padding: 8px 9px !important;
        }}
        .coach-analysis-card h3,
        .coach-summary-card h3 {{
            font-size: 13px !important;
            margin-bottom: 5px !important;
        }}
        .coach-field {{
            margin-top: 5px !important;
        }}
        .coach-field div,
        .coach-field ul,
        .coach-analysis-card p {{
            font-size: 11px !important;
            line-height: 1.28 !important;
        }}
        .coach-field div,
        .coach-field li {{
            display: -webkit-box !important;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden !important;
        }}
        .coach-field span {{
            font-size: 9.5px !important;
            margin-bottom: 2px !important;
        }}
        .coach-field ul {{
            padding-left: 14px !important;
        }}
        .coach-score-total {{
            background: var(--coach-panel-2) !important;
            border-color: var(--coach-border) !important;
            padding: 5px 7px !important;
            margin-bottom: 5px !important;
        }}
        .coach-score-total strong {{
            font-size: 18px !important;
        }}
        .coach-score-total span {{
            font-size: 10px !important;
        }}
        .coach-score-grid {{
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: 4px !important;
        }}
        .coach-score-chip {{
            background: var(--coach-panel-2) !important;
            border: 1px solid var(--coach-border) !important;
            border-radius: 8px !important;
            padding: 5px 6px !important;
            min-width: 0 !important;
        }}
        .coach-score-chip-head {{
            display: flex !important;
            justify-content: space-between !important;
            gap: 4px !important;
            color: var(--coach-text) !important;
            font-size: 10.5px !important;
            font-weight: 850 !important;
            line-height: 1.1 !important;
        }}
        .coach-score-chip p {{
            color: var(--coach-muted) !important;
            font-size: 9px !important;
            line-height: 1.12 !important;
            margin: 3px 0 0 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        .coach-score-row {{
            margin-top: 4px !important;
        }}
        .coach-score-row-head {{
            font-size: 11px !important;
            margin-bottom: 3px !important;
        }}
        .coach-score-row .coach-progress-track {{
            height: 5px !important;
        }}
        .coach-score-explain {{
            font-size: 9.5px !important;
            line-height: 1.15 !important;
            margin-top: 3px !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        .coach-shell-card,
        .coach-goal-card,
        .coach-stage-card,
        .coach-status-main,
        .coach-status-metric,
        .coach-input-shell,
        .coach-analysis-card,
        .coach-summary-card {{
            border-radius: 8px !important;
        }}
        .coach-left-rail {{
            margin-bottom: 6px !important;
            padding: 12px !important;
        }}
        .coach-goal-card {{
            margin-top: 6px !important;
            padding: 10px !important;
        }}
        .coach-stage-card {{
            margin-top: 8px !important;
            padding: 9px !important;
        }}
        .coach-stage-card p,
        .coach-goal-card p {{
            font-size: 12px !important;
            line-height: 1.38 !important;
            margin-top: 7px !important;
        }}
        .coach-statusbar {{
            grid-template-columns: minmax(0, 1fr) minmax(230px, 0.78fr) !important;
            gap: 7px !important;
        }}
        .coach-status-main,
        .coach-status-metric {{
            padding: 9px !important;
        }}
        .coach-status-main h1 {{
            font-size: 18px !important;
        }}
        .coach-status-main p {{
            font-size: 11.5px !important;
            line-height: 1.35 !important;
        }}
        .coach-status-grid {{
            gap: 6px !important;
        }}
        .coach-input-shell {{
            padding: 9px !important;
        }}
        .coach-input-title {{
            margin-bottom: 4px !important;
        }}
        .coach-control-title {{
            margin: 10px 0 6px !important;
        }}
        .coach-ai-card {{
            max-height: 84px !important;
            overflow: hidden !important;
        }}
        .coach-feedback-card {{
            max-height: 188px !important;
            overflow: hidden !important;
        }}
        .coach-score-card {{
            max-height: 168px !important;
            overflow: hidden !important;
        }}
        .coach-suggestion-card {{
            max-height: 116px !important;
            overflow: hidden !important;
        }}
        .coach-feedback-card .coach-field div,
        .coach-feedback-card .coach-field li,
        .coach-suggestion-card .coach-field div,
        .coach-suggestion-card .coach-field li {{
            -webkit-line-clamp: 1;
        }}
        .coach-feedback-card .coach-field,
        .coach-suggestion-card .coach-field {{
            margin-top: 4px !important;
        }}

        /* Final product polish: keep the app native-feeling and neutral. */
        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        .stDeployButton,
        #MainMenu,
        footer {{
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }}
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            background:
                radial-gradient(circle at 50% -24%, color-mix(in srgb, var(--coach-text) 9%, transparent), transparent 42%),
                linear-gradient(180deg, color-mix(in srgb, var(--coach-bg) 84%, var(--coach-text) 4%), var(--coach-bg));
        }}
        .stApp > * {{
            position: relative;
            z-index: 1;
        }}
        .coach-shell-card,
        .coach-goal-card,
        .coach-stage-card,
        .coach-status-main,
        .coach-status-metric,
        .coach-input-shell,
        .coach-analysis-card,
        .coach-summary-card,
        .voice-lab-card,
        div[data-testid="stMetric"] {{
            background: color-mix(in srgb, var(--coach-panel) 82%, transparent) !important;
            border: 1px solid color-mix(in srgb, var(--coach-border) 78%, transparent) !important;
            box-shadow: 0 18px 46px rgba(0, 0, 0, 0.18) !important;
        }}
        .coach-left-rail,
        .coach-input-shell {{
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.14) !important;
        }}
        .coach-brand {{
            margin-bottom: 10px !important;
        }}
        .coach-brand-title {{
            font-size: 15.5px !important;
            font-weight: 760 !important;
            white-space: nowrap !important;
        }}
        .coach-brand-card {{
            padding: 11px !important;
        }}
        .coach-brand-row {{
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 8px !important;
        }}
        .coach-brand-row .coach-status-pill {{
            flex: 0 0 auto !important;
        }}
        .coach-status-pill {{
            padding: 5px 8px !important;
            font-size: 10.5px !important;
            border-radius: 999px !important;
        }}
        .coach-control-title {{
            display: none !important;
        }}
        .coach-goal-card p {{
            color: var(--coach-muted) !important;
        }}
        .coach-goal-card {{
            max-height: 86px !important;
            overflow: hidden !important;
        }}
        .coach-goal-card .coach-stage-head {{
            margin-bottom: 4px !important;
        }}
        .coach-goal-card p {{
            display: -webkit-box !important;
            -webkit-line-clamp: 1 !important;
            -webkit-box-orient: vertical !important;
            overflow: hidden !important;
            margin-top: 5px !important;
        }}
        .coach-statusbar {{
            display: grid !important;
            grid-template-columns: minmax(0, 1fr) minmax(260px, auto) !important;
            grid-template-areas:
                "main meta"
                "progress progress" !important;
            gap: 8px 16px !important;
            align-items: center !important;
            margin-bottom: 8px !important;
            padding: 11px 13px !important;
            min-height: 86px !important;
            background: color-mix(in srgb, var(--coach-panel) 82%, transparent) !important;
            border: 1px solid color-mix(in srgb, var(--coach-border) 78%, transparent) !important;
            border-radius: 8px !important;
            box-shadow: 0 18px 46px rgba(0, 0, 0, 0.18) !important;
            backdrop-filter: blur(24px) saturate(1.25) !important;
            -webkit-backdrop-filter: blur(24px) saturate(1.25) !important;
            overflow: hidden !important;
        }}
        .coach-topbar-main {{
            grid-area: main !important;
            min-width: 0 !important;
        }}
        .coach-topbar-kicker {{
            color: var(--coach-muted) !important;
            font-size: 10px !important;
            font-weight: 760 !important;
            letter-spacing: 0 !important;
            text-transform: uppercase !important;
            margin-bottom: 3px !important;
        }}
        .coach-topbar-title {{
            margin: 0 !important;
            color: var(--coach-text) !important;
            font-size: 19px !important;
            font-weight: 760 !important;
            line-height: 1.15 !important;
        }}
        .coach-topbar-main p {{
            margin: 5px 0 0 !important;
            color: var(--coach-muted) !important;
            font-size: 11.5px !important;
            line-height: 1.2 !important;
        }}
        .coach-topbar-meta {{
            grid-area: meta !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            flex-wrap: wrap !important;
            gap: 6px !important;
            min-width: 0 !important;
        }}
        .coach-topbar-meta span {{
            display: inline-flex !important;
            align-items: center !important;
            max-width: 132px !important;
            min-height: 24px !important;
            padding: 5px 8px !important;
            border: 1px solid var(--coach-border) !important;
            border-radius: 8px !important;
            background: color-mix(in srgb, var(--coach-panel-2) 78%, transparent) !important;
            color: var(--coach-muted) !important;
            font-size: 10px !important;
            font-weight: 720 !important;
            letter-spacing: 0 !important;
            line-height: 1 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        .coach-topbar-progress {{
            grid-area: progress !important;
        }}
        .coach-progress-track {{
            height: 5px !important;
            background: color-mix(in srgb, var(--coach-text) 8%, transparent) !important;
            border-color: color-mix(in srgb, var(--coach-text) 10%, transparent) !important;
        }}
        .coach-progress-fill,
        .score-bar-fill,
        .lesson-progress-fill {{
            background: var(--coach-text) !important;
            opacity: 0.82 !important;
        }}
        .stButton > button,
        .stDownloadButton > button,
        button[kind="secondary"],
        button[data-testid="stBaseButton-secondary"],
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {{
            border-radius: 9px !important;
            font-size: 12px !important;
            font-weight: 690 !important;
            min-height: 32px !important;
            padding-top: 6px !important;
            padding-bottom: 6px !important;
            transition: transform 120ms ease, border-color 120ms ease, background 120ms ease !important;
        }}
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        button:hover {{
            transform: translateY(-1px);
            border-color: var(--coach-border-strong) !important;
        }}
        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"],
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {{
            background: var(--coach-primary) !important;
            color: var(--coach-primary-text) !important;
            border-color: color-mix(in srgb, var(--coach-primary) 86%, var(--coach-border)) !important;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.14) !important;
        }}
        .stButton > button[kind="secondary"],
        .stDownloadButton > button[kind="secondary"],
        button[kind="secondary"],
        button[data-testid="stBaseButton-secondary"] {{
            background: color-mix(in srgb, var(--coach-button) 86%, transparent) !important;
        }}
        .stTextArea textarea {{
            min-height: 54px !important;
            padding: 12px 13px !important;
            border-radius: 12px !important;
            background: color-mix(in srgb, var(--coach-panel-3) 90%, transparent) !important;
            box-shadow: inset 0 1px 0 color-mix(in srgb, var(--coach-text) 7%, transparent) !important;
        }}
        .stSelectbox div[data-baseweb="select"] > div,
        input {{
            border-radius: 10px !important;
            background: color-mix(in srgb, var(--coach-panel-3) 86%, transparent) !important;
        }}
        [data-testid="stAudioInput"],
        [data-testid="stFileUploader"] {{
            background: color-mix(in srgb, var(--coach-panel-3) 84%, transparent) !important;
            border: 1px solid var(--coach-border) !important;
            border-radius: 10px !important;
            padding: 8px !important;
        }}
        .stCheckbox,
        [data-testid="stToggle"] {{
            transform: scale(0.92);
            transform-origin: left center;
        }}
        input[type="checkbox"],
        input[type="radio"] {{
            accent-color: var(--coach-text) !important;
        }}
        .stCheckbox [role="checkbox"],
        .stCheckbox [data-baseweb="checkbox"],
        [data-testid="stCheckbox"] [role="checkbox"],
        [data-testid="stCheckbox"] [data-baseweb="checkbox"] {{
            color: var(--coach-text) !important;
        }}
        [data-testid="stCheckbox"] label[data-baseweb="checkbox"] > div:first-child {{
            background: var(--coach-primary) !important;
            border-color: var(--coach-primary) !important;
        }}
        [data-testid="stCheckbox"] label[data-baseweb="checkbox"] > div:first-child > div {{
            background: var(--coach-primary-text) !important;
        }}
        [data-testid="stCheckbox"] label[data-baseweb="checkbox"]:has(input[aria-checked="false"]) > div:first-child {{
            background: var(--coach-button) !important;
            border-color: var(--coach-border-strong) !important;
        }}
        [data-testid="stCheckbox"] label[data-baseweb="checkbox"]:has(input[aria-checked="false"]) > div:first-child > div {{
            background: var(--coach-muted) !important;
        }}
        .coach-input-title {{
            font-size: 12.5px !important;
            font-weight: 720 !important;
        }}
        .coach-input-title span {{
            max-width: 70%;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .coach-analysis-stack {{
            gap: 9px !important;
        }}
        .coach-analysis-card h3 {{
            font-weight: 740 !important;
        }}
        .coach-empty {{
            border-style: solid !important;
            background: color-mix(in srgb, var(--coach-panel-2) 80%, transparent) !important;
            color: var(--coach-muted) !important;
        }}
        .coach-insight-panel {{
            background: color-mix(in srgb, var(--coach-panel) 84%, transparent) !important;
            border: 1px solid color-mix(in srgb, var(--coach-border) 86%, transparent) !important;
            border-radius: 10px !important;
            box-shadow: 0 18px 44px rgba(0, 0, 0, 0.16) !important;
            backdrop-filter: blur(24px) saturate(1.18) !important;
            -webkit-backdrop-filter: blur(24px) saturate(1.18) !important;
            min-height: 430px !important;
            overflow: hidden !important;
        }}
        .coach-insight-head {{
            padding: 11px 12px 9px !important;
            border-bottom: 1px solid var(--coach-border) !important;
        }}
        .coach-insight-head h3 {{
            margin: 0 !important;
            color: var(--coach-text) !important;
            font-size: 14px !important;
            line-height: 1.2 !important;
        }}
        .coach-insight-section {{
            padding: 12px 12px !important;
            border-bottom: 1px solid color-mix(in srgb, var(--coach-border) 70%, transparent) !important;
        }}
        .coach-insight-section:last-child {{
            border-bottom: 0 !important;
        }}
        .coach-insight-section h4 {{
            margin: 0 0 6px !important;
            color: var(--coach-text) !important;
            font-size: 12.5px !important;
            line-height: 1.2 !important;
        }}
        .coach-insight-section p,
        .coach-insight-section li {{
            color: var(--coach-soft) !important;
            font-size: 10.8px !important;
            line-height: 1.32 !important;
        }}
        .coach-insight-section strong {{
            color: var(--coach-text) !important;
            font-weight: 760 !important;
        }}
        .coach-insight-section p {{
            margin: 0 !important;
        }}
        .coach-insight-section ul {{
            margin: 0 !important;
            padding-left: 14px !important;
        }}
        .coach-insight-grid {{
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: 5px !important;
        }}
        .coach-insight-chip {{
            background: color-mix(in srgb, var(--coach-panel-2) 76%, transparent) !important;
            border: 1px solid var(--coach-border) !important;
            border-radius: 8px !important;
            padding: 5px 6px !important;
            min-width: 0 !important;
        }}
        .coach-insight-chip strong {{
            display: block !important;
            color: var(--coach-text) !important;
            font-size: 10.2px !important;
            line-height: 1.1 !important;
        }}
        .coach-insight-chip span {{
            display: block !important;
            color: var(--coach-muted) !important;
            font-size: 9.2px !important;
            line-height: 1.18 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            margin-top: 2px !important;
        }}
        .coach-insight-total {{
            display: flex !important;
            align-items: baseline !important;
            gap: 7px !important;
            margin-bottom: 6px !important;
        }}
        .coach-insight-total strong {{
            color: var(--coach-text) !important;
            font-size: 22px !important;
            line-height: 1 !important;
        }}
        .coach-insight-total span {{
            color: var(--coach-muted) !important;
            font-size: 10px !important;
        }}
        .coach-voice-tools-card {{
            margin-top: 8px !important;
            max-height: 76px !important;
            overflow: hidden !important;
        }}
        .coach-voice-tools-card p {{
            color: var(--coach-muted) !important;
            font-size: 10.5px !important;
            line-height: 1.2 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_left_brand(mode_label: str, collapsed: bool) -> None:
    if collapsed:
        st.markdown(
            """
            <div class="coach-shell-card coach-left-rail">
              <div class="coach-collapsed-brand">
                <div class="coach-collapsed-logo">AI</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"""
        <div class="coach-shell-card coach-left-rail coach-brand-card">
          <div class="coach-brand-row">
            <div class="coach-brand-title">AI 英语陪练</div>
            <div class="coach-status-pill">{esc(mode_label)}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_goal_card(scenario: dict, lesson: dict, difficulty: str, mode_label: str) -> None:
    step = lesson["current_step"]
    focus_text = step.get("target_expression") or step.get("goal", "")
    st.markdown(
        f"""
        <div class="coach-goal-card">
          <div class="coach-card-head">
            <strong>训练目标</strong>
            <span>{esc(difficulty)}</span>
          </div>
          <div class="coach-stage-head">
            <strong>{esc(step.get("title", ""))}</strong>
            <span>{int(lesson.get("progress", 0))}%</span>
          </div>
          <div class="coach-progress-track">
            <div class="coach-progress-fill" style="width: {int(lesson.get("progress", 0))}%;"></div>
          </div>
          <p>{esc(focus_text)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_status_bar(
    scenario: dict,
    lesson: dict,
    current_round: int,
    min_rounds: int,
    session_started: bool,
) -> None:
    step = lesson["current_step"]
    status_text = "训练中" if session_started else "未开始"
    progress = int(lesson.get("progress", 0))
    display_round = min(min_rounds, max(current_round, 1 if session_started else 0))
    st.markdown(
        f"""
        <div class="coach-statusbar">
          <div class="coach-topbar-main">
            <div class="coach-topbar-kicker">Speaking Practice</div>
            <div class="coach-topbar-title">{esc(scenario.get("cn_label", ""))}</div>
            <p>{esc(step.get("title", ""))} · Round {display_round} / {min_rounds}</p>
          </div>
          <div class="coach-topbar-meta">
            <span>阶段 · {esc(step.get("title", ""))}</span>
            <span>轮次 · {display_round}/{min_rounds}</span>
            <span>状态 · {esc(status_text)} · {progress}%</span>
          </div>
          <div class="coach-topbar-progress">
            <div class="coach-progress-track">
              <div class="coach-progress-fill" style="width: {progress}%;"></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_history(messages: list[dict], height: int = 500) -> None:
    """Render role-aligned chat bubbles inside a fixed-height scroll box."""
    is_light = st.session_state.get("theme_mode") == "light"
    chat_bg = "rgba(235,239,245,0.58)" if is_light else "rgba(28,31,37,0.66)"
    assistant_bg = "rgba(246,247,249,0.74)" if is_light else "rgba(48,52,61,0.72)"
    user_bg = "#353b45" if is_light else "#cfd4dd"
    user_text = "#f6f7f9" if is_light else "#1a1d23"
    user_meta = "rgba(246,247,249,0.72)" if is_light else "rgba(26,29,35,0.54)"
    text_color = "#20252d" if is_light else "#e8eaed"
    muted_color = "#687382" if is_light else "#a8b0bc"
    border_color = "rgba(50,58,68,0.16)" if is_light else "rgba(229,233,240,0.12)"
    if not messages:
        body = """
          <div class="empty-state">
            <strong>还没有对话记录</strong>
            <span>点击开始练习后进入场景对话。</span>
          </div>
        """
    else:
        body_parts = []
        user_round = 0
        for index, item in enumerate(messages, start=1):
            role = str(item.get("role", "assistant")).lower()
            content = esc(item.get("content", ""))
            stage = esc(item.get("stage", ""))
            if role == "user":
                user_round += 1
                bubble_class = "user"
                role_label = "User"
                meta = f"Round {user_round}"
                avatar = "You"
            elif role in {"system", "notice"}:
                bubble_class = "system"
                role_label = "System Notice"
                meta = f"Notice {index}"
                avatar = ""
            else:
                bubble_class = "assistant"
                role_label = "AI Coach"
                meta = f"Stage {stage}" if stage else f"Message {index}"
                avatar = "AI"
            stage_part = f"<span>{stage}</span>" if stage else ""
            avatar_part = f'<div class="avatar">{avatar}</div>' if avatar else ""
            body_parts.append(
                f"""
                <div class="message-row {bubble_class}">
                  {avatar_part}
                  <div class="bubble">
                    <div class="meta">
                      <strong>{role_label}</strong>
                      <span>{esc(meta)}</span>
                      {stage_part}
                    </div>
                    <div class="content">{content}</div>
                  </div>
                </div>
                """
            )
        body = "\n".join(body_parts)

    components.html(
        f"""
        <div id="chat-scroll" class="chat-scroll">
          {body}
        </div>
        <script>
        const chatScroll = document.getElementById("chat-scroll");
        if (chatScroll) {{
            chatScroll.scrollTop = chatScroll.scrollHeight;
        }}
        </script>
        <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}
        .chat-scroll {{
            height: {height}px;
            overflow-y: auto;
            padding: 18px 16px;
            background: {chat_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            scrollbar-color: rgba(148,163,184,0.42) transparent;
            backdrop-filter: blur(24px) saturate(1.25);
            -webkit-backdrop-filter: blur(24px) saturate(1.25);
        }}
        .message-row {{
            display: flex;
            align-items: flex-end;
            gap: 8px;
            margin: 0 0 14px;
        }}
        .message-row.assistant {{ justify-content: flex-start; }}
        .message-row.user {{ justify-content: flex-end; }}
        .message-row.system {{ justify-content: center; }}
        .avatar {{
            flex: 0 0 auto;
            width: 28px;
            height: 28px;
            display: grid;
            place-items: center;
            border-radius: 999px;
            border: 1px solid {border_color};
            background: rgba(255,255,255,0.06);
            color: {muted_color};
            font-size: 10px;
            font-weight: 800;
        }}
        .user .avatar {{
            order: 2;
            background: {user_bg};
            color: {user_text};
        }}
        .bubble {{
            max-width: min(74%, 680px);
            padding: 12px 13px;
            border-radius: 13px;
            border: 1px solid {border_color};
            box-shadow: 0 10px 22px rgba(0,0,0,0.10);
        }}
        .assistant .bubble {{
            background: {assistant_bg};
            color: {text_color};
            border-bottom-left-radius: 5px;
        }}
        .user .bubble {{
            order: 1;
            background: {user_bg};
            color: {user_text};
            border-color: rgba(0,0,0,0.10);
            border-bottom-right-radius: 5px;
        }}
        .system .bubble {{
            max-width: 86%;
            background: rgba(148,163,184,0.12);
            color: {text_color};
            text-align: center;
        }}
        .meta {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 7px;
            margin-bottom: 5px;
            font-size: 11px;
            line-height: 1.3;
            color: {muted_color};
        }}
        .user .meta {{ color: {user_meta}; }}
        .meta strong {{
            color: inherit;
            font-weight: 760;
        }}
        .content {{
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            font-size: 14.5px;
            line-height: 1.58;
        }}
        .empty-state {{
            height: 100%;
            display: grid;
            place-content: center;
            justify-items: center;
            text-align: center;
            gap: 6px;
            color: {muted_color};
            border: 1px dashed {border_color};
            border-radius: 12px;
            padding: 22px;
        }}
        .empty-state strong {{
            color: {text_color};
            font-size: 16px;
        }}
        .empty-state span {{
            color: {muted_color};
            font-size: 13px;
            line-height: 1.5;
        }}
        </style>
        """,
        height=height + 2,
        scrolling=False,
    )


def render_input_header(round_full: bool, voice_status: str = "") -> None:
    status = "已到上限" if round_full else (voice_status or "")
    st.markdown(
        f"""
        <div class="coach-input-title">
          <div>回答</div>
          <span>{esc(status)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis_panel(
    ai_reply: str,
    feedback: dict | None,
    score: dict | None,
    suggestion: dict | None,
    average: int | None = None,
) -> None:
    """Render current-round feedback, score, and learning tips."""
    ai_text = esc(_short_text(ai_reply, 136)) if ai_reply else "等待 AI 开场。"

    if feedback:
        issues = _list_html(feedback.get("issue_explanation", []), limit=1, max_chars=58)
        alternatives = _list_html(feedback.get("alternative_expressions", []), limit=1, max_chars=58)
        feedback_html = f"""
          <p><strong>原句</strong> {esc(_short_text(feedback.get("original_sentence", ""), 54))}</p>
          <p><strong>修改</strong> {esc(_short_text(feedback.get("corrected_sentence", ""), 54))}</p>
          <p><strong>原因</strong></p>{issues}
          <p><strong>替代表达</strong></p>{alternatives}
        """
    else:
        feedback_html = "<p>等待回答后显示纠错和表达优化。</p>"

    if score:
        total_score = _safe_score(score.get("total_score"))
        dimensions = score.get("dimensions", {})
        chips = []
        for key, fallback_label in DIMENSION_ORDER:
            item = dimensions.get(key, {})
            value = _safe_score(item.get("score"))
            label = str(item.get("label") or fallback_label).split(" ")[0]
            explanation = "演示发音评分" if key == "pronunciation" else _short_text(item.get("explanation", ""), 24)
            chips.append(
                f"""
                <div class="coach-insight-chip">
                  <strong>{esc(label)} · {value}</strong>
                  <span>{esc(explanation)}</span>
                </div>
                """
            )
        score_html = (
            f'<div class="coach-insight-total"><strong>{total_score}</strong><span>Overall Score / 100</span></div>'
            f'<div class="coach-insight-grid">{"".join(chips)}</div>'
        )
    else:
        score_html = "<p>等待评分。</p>"

    if not suggestion:
        suggestion = {}
    suggestion_html = f"""
      <p><strong>主要问题</strong> {esc(_short_text(suggestion.get("main_issue", "等待本轮反馈。"), 58))}</p>
      <p><strong>跟读句</strong> {esc(_short_text(suggestion.get("practice_sentence", "提交回答后生成跟读句。"), 58))}</p>
      <p><strong>下一轮</strong> {esc(_short_text(suggestion.get("next_tip", "先回答 AI 当前问题，再补充一个原因或例子。"), 58))}</p>
    """

    st.html(
        f"""
        <div class="coach-insight-panel">
          <div class="coach-insight-head">
            <h3>学习分析</h3>
          </div>
          <div class="coach-insight-section">
            <h4>本轮 AI 追问</h4>
            <p>{ai_text}</p>
          </div>
          <div class="coach-insight-section">
            <h4>纠错反馈</h4>
            {feedback_html}
          </div>
          <div class="coach-insight-section">
            <h4>五维评分</h4>
            {score_html}
          </div>
          <div class="coach-insight-section">
            <h4>学习建议</h4>
            {suggestion_html}
          </div>
        </div>
        """
    )


def render_summary_report(summary: str, scenario_name: str, difficulty: str, round_count: int, overall: int) -> None:
    if summary:
        body = _markdownish(summary)
    else:
        body = "<p>暂无课后总结。完成至少 5 轮后，在练习页生成课后总结。</p>"
    is_light = st.session_state.get("theme_mode") == "light"
    page_bg = "rgba(255,255,255,0.62)" if is_light else "rgba(255,255,255,0.08)"
    border = "rgba(15,23,42,0.14)" if is_light else "rgba(148,163,184,0.18)"
    text = "#111827" if is_light else "#f5f5f7"
    muted = "#667085" if is_light else "#a1a1aa"
    soft = "#374151" if is_light else "#e5e7eb"
    components.html(
        f"""
        <div class="summary-page">
          <div class="summary-head">
            <div>
              <span>Lesson Report</span>
              <h1>课后总结</h1>
            </div>
            <div class="summary-meta">
              <strong>{esc(scenario_name)}</strong>
              <span>{esc(difficulty)} · {round_count} rounds · {overall}/100</span>
            </div>
          </div>
          <div class="summary-body">{body}</div>
        </div>
        <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}
        .summary-page {{
            height: 568px;
            padding: 18px;
            border-radius: 8px;
            border: 1px solid {border};
            background: {page_bg};
            backdrop-filter: blur(24px) saturate(1.25);
            -webkit-backdrop-filter: blur(24px) saturate(1.25);
            color: {text};
            overflow: hidden;
        }}
        .summary-head {{
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: flex-start;
            padding-bottom: 14px;
            border-bottom: 1px solid {border};
        }}
        .summary-head span {{
            color: {muted};
            font-size: 12px;
            font-weight: 800;
        }}
        .summary-head h1 {{
            margin: 4px 0 0;
            font-size: 26px;
            line-height: 1.15;
        }}
        .summary-meta {{
            text-align: right;
            display: grid;
            gap: 5px;
        }}
        .summary-meta strong {{
            font-size: 14px;
        }}
        .summary-body {{
            height: 468px;
            overflow-y: auto;
            padding: 16px 8px 8px 0;
            line-height: 1.6;
        }}
        .summary-body p {{
            margin: 0 0 10px;
            color: {soft};
            font-size: 14px;
        }}
        .summary-body strong {{
            color: {text};
        }}
        </style>
        """,
        height=570,
        scrolling=False,
    )


def _render_ai_followup(ai_reply: str) -> None:
    if ai_reply:
        content = f"<p>{esc(_short_text(ai_reply, 150))}</p>"
    else:
        content = """
        <div class="coach-empty">
          <strong>等待开场</strong>
        </div>
        """
    st.markdown(
        f"""
        <div class="coach-analysis-card coach-ai-card">
          <h3>本轮 AI 追问</h3>
          {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_feedback_card(feedback: dict | None) -> None:
    if not feedback:
        st.markdown(
            """
            <div class="coach-analysis-card coach-feedback-card">
              <h3>纠错反馈</h3>
              <div class="coach-empty">
                <strong>等待回答</strong>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    issues = _list_html(feedback.get("issue_explanation", []), limit=1, max_chars=68)
    alternatives = _list_html(feedback.get("alternative_expressions", []), limit=1, max_chars=68)
    st.markdown(
        f"""
        <div class="coach-analysis-card coach-feedback-card">
          <h3>纠错反馈</h3>
          <div class="coach-field"><span>原句</span><div>{esc(_short_text(feedback.get("original_sentence", ""), 68))}</div></div>
          <div class="coach-field"><span>修改后句子</span><div>{esc(_short_text(feedback.get("corrected_sentence", ""), 68))}</div></div>
          <div class="coach-field"><span>错误原因</span>{issues}</div>
          <div class="coach-field"><span>更自然表达</span><div>{esc(_short_text(feedback.get("natural_expression", ""), 72))}</div></div>
          <div class="coach-field"><span>推荐替代表达</span>{alternatives}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_score_card(score: dict | None) -> None:
    if not score:
        st.markdown(
            """
            <div class="coach-analysis-card coach-score-card">
              <h3>五维评分</h3>
              <div class="coach-empty">
                <strong>等待评分</strong>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    rows = []
    dimensions = score.get("dimensions", {})
    for key, fallback_label in DIMENSION_ORDER:
        item = dimensions.get(key, {})
        value = _safe_score(item.get("score"))
        label = str(item.get("label") or fallback_label).split(" ")[0]
        explanation = _short_text(item.get("explanation", ""), 42)
        if key == "pronunciation":
            explanation = "演示发音评分，非真实音素级评测。"
        rows.append(
            (
                '<div class="coach-score-chip">'
                f'<div class="coach-score-chip-head"><span>{esc(label)}</span><strong>{value}</strong></div>'
                f'<p>{esc(explanation)}</p>'
                "</div>"
            )
        )

    rows_html = "".join(rows)
    total_score = _safe_score(score.get("total_score"))
    st.markdown(
        (
            '<div class="coach-analysis-card coach-score-card">'
            "<h3>五维评分</h3>"
            '<div class="coach-score-total">'
            f"<strong>{total_score}</strong>"
            "<span>Overall Score / 100</span>"
            "</div>"
            f'<div class="coach-score-grid">{rows_html}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _render_suggestion_card(suggestion: dict | None) -> None:
    if not suggestion:
        suggestion = {}
    st.markdown(
        f"""
        <div class="coach-analysis-card coach-suggestion-card">
          <h3>学习建议</h3>
          <div class="coach-field"><span>主要问题</span><div>{esc(_short_text(suggestion.get("main_issue", "等待本轮反馈。"), 72))}</div></div>
          <div class="coach-field"><span>跟读句</span><div>{esc(_short_text(suggestion.get("practice_sentence", "提交回答后生成跟读句。"), 72))}</div></div>
          <div class="coach-field"><span>下一轮提示</span><div>{esc(_short_text(suggestion.get("next_tip", "先回答 AI 当前问题，再补充一个原因或例子。"), 72))}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _list_html(items: Iterable[object], limit: int | None = None, max_chars: int = 110) -> str:
    selected_items = list(items)
    if limit is not None:
        selected_items = selected_items[:limit]
    clean_items = [esc(_short_text(item, max_chars)) for item in selected_items if str(item).strip()]
    if not clean_items:
        return "<div>暂无。</div>"
    return "<ul>" + "".join(f"<li>{item}</li>" for item in clean_items) + "</ul>"


def _short_text(value: object, limit: int = 120) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _markdownish(text: str) -> str:
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            lines.append(f"<p><strong>{esc(line.lstrip('#').strip())}</strong></p>")
        elif line.startswith("- "):
            lines.append(f"<p>{esc(line)}</p>")
        else:
            lines.append(f"<p>{esc(line)}</p>")
    return "".join(lines) or "<p>暂无总结。</p>"


def _safe_score(value: object) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        score = 0
    return max(0, min(100, score))
