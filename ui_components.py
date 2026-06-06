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
            caret-color: var(--coach-accent) !important;
            white-space: pre-wrap !important;
            overflow-wrap: anywhere !important;
        }
        textarea:focus,
        input:focus {
            border-color: var(--coach-accent) !important;
            box-shadow: 0 0 0 1px var(--coach-accent-soft) !important;
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
        .coach-latency-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 7px;
            margin: 9px 0;
        }
        .coach-latency-grid div {
            padding: 8px;
            border-radius: 8px;
            background: var(--coach-panel-2);
            border: 1px solid var(--coach-border);
        }
        .coach-latency-grid span {
            display: block;
            color: var(--coach-muted);
            font-size: 10px;
            font-weight: 800;
            margin-bottom: 4px;
        }
        .coach-latency-grid strong {
            display: block;
            color: var(--coach-text);
            font-size: 12px;
            line-height: 1.2;
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
    is_light = st.session_state.get("theme_mode") == "light"
    theme = {
        "bg": "#d9dde3" if is_light else "#070b10",
        "panel": "rgba(246,247,249,0.78)" if is_light else "rgba(15,22,29,0.82)",
        "panel_2": "rgba(233,236,240,0.76)" if is_light else "rgba(19,29,38,0.76)",
        "input": "rgba(225,229,234,0.82)" if is_light else "rgba(8,13,18,0.84)",
        "border": "rgba(35,40,48,0.11)" if is_light else "rgba(255,255,255,0.085)",
        "border_strong": "rgba(122,97,45,0.26)" if is_light else "rgba(217,168,79,0.30)",
        "text": "#20252b" if is_light else "#f2f3f0",
        "muted": "#6f7780" if is_light else "#87919c",
        "soft": "#3b444d" if is_light else "#c4ccd3",
        "button": "rgba(239,241,244,0.78)" if is_light else "rgba(18,27,36,0.88)",
        "button_text": "#20252b" if is_light else "#e7ecf0",
        "primary": "#7a612d" if is_light else "#d9a84f",
        "primary_text": "#fffaf0" if is_light else "#110f09",
        "accent": "#7a612d" if is_light else "#d9a84f",
        "accent_soft": "rgba(122,97,45,0.16)" if is_light else "rgba(217,168,79,0.13)",
        "shadow": "0 20px 48px rgba(66,76,90,0.16)" if is_light else "0 24px 54px rgba(0,0,0,0.34)",
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
            --coach-accent: {theme["accent"]};
            --coach-accent-soft: {theme["accent_soft"]};
            --coach-shadow: {theme["shadow"]};
        }}
        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] {{
            min-height: 100vh !important;
            max-height: none !important;
            overflow-x: hidden !important;
        }}
        [data-testid="stMain"] {{
            align-items: flex-start !important;
        }}
        .stApp {{
            background: var(--coach-bg) !important;
            color: var(--coach-text) !important;
        }}
        .block-container {{
            min-height: 100vh !important;
            max-height: none !important;
            padding: 0.25rem 0.65rem !important;
            overflow: visible !important;
        }}
        .block-container > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-child {{
            min-height: calc(100vh - 0.5rem) !important;
            overflow: visible !important;
            align-items: stretch !important;
        }}
        div[data-testid="column"] {{
            min-width: 0 !important;
        }}
        div[data-testid="column"] > div {{
            min-width: 0 !important;
            height: 100% !important;
            overflow: visible !important;
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
        .stButton > button p,
        .stDownloadButton > button p,
        button p {{
            font-size: 11px !important;
            line-height: 1 !important;
            margin: 0 !important;
            letter-spacing: 0 !important;
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
            font-size: 12px !important;
        }}
        textarea {{
            min-height: 72px !important;
            resize: none !important;
            line-height: 1.45 !important;
            white-space: pre-wrap !important;
            overflow-wrap: anywhere !important;
            caret-color: var(--coach-accent) !important;
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
            font-size: 12px !important;
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
            margin-bottom: 5px !important;
            padding: 7px !important;
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
            margin-bottom: 4px !important;
        }}
        .coach-brand-title {{
            font-size: 12.5px !important;
            font-weight: 730 !important;
            white-space: nowrap !important;
        }}
        .coach-brand-card {{
            padding: 8px !important;
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
            padding: 4px 6px !important;
            font-size: 9px !important;
            border-radius: 999px !important;
        }}
        .coach-control-title {{
            display: none !important;
        }}
        .coach-goal-card p {{
            color: var(--coach-muted) !important;
        }}
        .coach-goal-card {{
            max-height: 70px !important;
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
            margin-bottom: 4px !important;
            padding: 8px 11px !important;
            min-height: 62px !important;
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
            font-size: 9px !important;
            font-weight: 760 !important;
            letter-spacing: 0 !important;
            text-transform: uppercase !important;
            margin-bottom: 3px !important;
        }}
        .coach-topbar-title {{
            margin: 0 !important;
            color: var(--coach-text) !important;
            font-size: 16px !important;
            font-weight: 760 !important;
            line-height: 1.15 !important;
        }}
        .coach-topbar-main p {{
            margin: 3px 0 0 !important;
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
            min-height: 20px !important;
            padding: 4px 7px !important;
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
            font-size: 10.5px !important;
            font-weight: 690 !important;
            min-height: 29px !important;
            padding-top: 4px !important;
            padding-bottom: 4px !important;
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
            min-height: 72px !important;
            padding: 9px 12px !important;
            border-radius: 0 0 13px 13px !important;
            background: color-mix(in srgb, var(--coach-panel-3) 90%, transparent) !important;
            box-shadow: inset 0 1px 0 color-mix(in srgb, var(--coach-text) 7%, transparent) !important;
            line-height: 1.45 !important;
            white-space: pre-wrap !important;
            overflow-wrap: anywhere !important;
        }}
        .stSelectbox div[data-baseweb="select"] > div,
        input {{
            border-radius: 10px !important;
            background: color-mix(in srgb, var(--coach-panel-3) 86%, transparent) !important;
        }}
        .stSelectbox label,
        .stTextArea label,
        .stAudioInput label,
        .stFileUploader label {{
            font-size: 10.5px !important;
            line-height: 1.15 !important;
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
            display: none !important;
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
            margin-top: 6px !important;
            max-height: 48px !important;
            overflow: hidden !important;
        }}
        .coach-voice-tools-card p {{
            color: var(--coach-muted) !important;
            font-size: 10.5px !important;
            line-height: 1.2 !important;
        }}

        /* Final glass UI overrides. Keep the practice page calm, neutral, and readable. */
        .coach-shell-card,
        .coach-goal-card,
        .coach-stage-card,
        .coach-statusbar,
        .coach-input-shell,
        .coach-analysis-card,
        .coach-summary-card,
        .coach-insight-panel,
        .voice-lab-card,
        [data-testid="stAudioInput"],
        [data-testid="stFileUploader"] {{
            border-radius: 13px !important;
            background: var(--coach-panel) !important;
            border: 1px solid var(--coach-border) !important;
            box-shadow: var(--coach-shadow) !important;
            backdrop-filter: blur(28px) saturate(1.18) !important;
            -webkit-backdrop-filter: blur(28px) saturate(1.18) !important;
        }}
        .coach-statusbar {{
            min-height: 62px !important;
            margin-bottom: 4px !important;
            padding: 8px 11px !important;
        }}
        .coach-topbar-title {{
            font-size: 16px !important;
        }}
        .coach-topbar-main p,
        .coach-topbar-meta span {{
            font-size: 10.5px !important;
        }}
        .coach-topbar-meta span {{
            background: var(--coach-panel-2) !important;
            border-color: var(--coach-border) !important;
            max-width: 150px !important;
        }}
        .coach-progress-fill,
        .score-bar-fill,
        .lesson-progress-fill {{
            background: color-mix(in srgb, var(--coach-text) 82%, transparent) !important;
            opacity: 1 !important;
        }}
        .stButton > button,
        .stDownloadButton > button,
        button[kind="secondary"],
        button[data-testid="stBaseButton-secondary"],
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {{
            border-radius: 11px !important;
            letter-spacing: 0 !important;
            height: 28px !important;
            min-height: 28px !important;
            padding-top: 3px !important;
            padding-bottom: 3px !important;
        }}
        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"],
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {{
            background: var(--coach-primary) !important;
            color: var(--coach-primary-text) !important;
            border-color: color-mix(in srgb, var(--coach-primary) 72%, var(--coach-border)) !important;
        }}
        .stTextArea textarea {{
            min-height: 72px !important;
            height: 72px !important;
            border-radius: 0 0 13px 13px !important;
            border-top-color: transparent !important;
            padding: 10px 12px !important;
        }}
        input[aria-label="用户英文输入"],
        textarea[aria-label="用户英文输入"] {{
            min-height: 72px !important;
            height: 72px !important;
            border-radius: 0 0 13px 13px !important;
            border-top-color: transparent !important;
            padding: 10px 12px !important;
            line-height: 1.45 !important;
            white-space: pre-wrap !important;
            overflow-wrap: anywhere !important;
            caret-color: var(--coach-accent) !important;
        }}
        .coach-input-shell {{
            padding: 0 !important;
        }}
        .coach-input-title {{
            margin-bottom: 3px !important;
        }}
        .coach-collapsed-logo {{
            background: var(--coach-primary) !important;
            color: var(--coach-primary-text) !important;
        }}
        .coach-goal-card {{
            max-height: 70px !important;
            padding: 7px !important;
        }}
        .coach-goal-card p {{
            -webkit-line-clamp: 2 !important;
        }}
        .coach-insight-panel {{
            min-height: 0 !important;
            overflow: hidden !important;
            box-shadow: 0 14px 34px rgba(0, 0, 0, 0.14) !important;
        }}
        .coach-insight-detail {{
            height: 354px !important;
            margin-top: 6px !important;
            overflow-y: auto !important;
            scrollbar-color: color-mix(in srgb, var(--coach-text) 28%, transparent) transparent !important;
        }}
        .coach-insight-head {{
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            gap: 8px !important;
            padding: 10px 12px 8px !important;
            border-bottom: 1px solid var(--coach-border) !important;
        }}
        .coach-insight-head h3 {{
            font-size: 14px !important;
            font-weight: 760 !important;
        }}
        .coach-insight-head span {{
            color: var(--coach-muted) !important;
            font-size: 10.5px !important;
            font-weight: 720 !important;
        }}
        .coach-insight-section {{
            padding: 11px 12px !important;
            border-bottom: 0 !important;
        }}
        .coach-insight-section h4 {{
            font-size: 12.5px !important;
            margin-bottom: 7px !important;
            font-weight: 760 !important;
        }}
        .coach-insight-section p,
        .coach-insight-section li {{
            color: var(--coach-soft) !important;
            font-size: 12px !important;
            line-height: 1.45 !important;
        }}
        .coach-insight-field {{
            margin-top: 10px !important;
        }}
        .coach-insight-field:first-child {{
            margin-top: 0 !important;
        }}
        .coach-insight-field span {{
            display: block !important;
            color: var(--coach-muted) !important;
            font-size: 10px !important;
            font-weight: 760 !important;
            margin-bottom: 4px !important;
        }}
        .coach-insight-field p,
        .coach-insight-field ul,
        .coach-insight-field li {{
            display: block !important;
            margin: 0 !important;
            color: var(--coach-soft) !important;
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: normal !important;
            -webkit-line-clamp: unset !important;
            -webkit-box-orient: unset !important;
        }}
        .coach-insight-field ul {{
            padding-left: 15px !important;
        }}
        .coach-insight-empty {{
            min-height: 92px !important;
            display: grid !important;
            align-content: center !important;
            gap: 4px !important;
        }}
        .coach-score-lines {{
            display: grid !important;
            gap: 8px !important;
        }}
        .coach-score-line {{
            padding: 8px !important;
            border: 1px solid var(--coach-border) !important;
            border-radius: 10px !important;
            background: var(--coach-panel-2) !important;
        }}
        .coach-score-line-head {{
            display: flex !important;
            justify-content: space-between !important;
            gap: 8px !important;
            margin-bottom: 5px !important;
        }}
        .coach-score-line-head strong,
        .coach-score-line-head span {{
            color: var(--coach-text) !important;
            font-size: 11px !important;
            font-weight: 760 !important;
        }}
        .coach-score-line p {{
            margin-top: 5px !important;
            color: var(--coach-muted) !important;
            font-size: 10px !important;
            line-height: 1.28 !important;
        }}
        .coach-insight-total strong {{
            font-size: 24px !important;
        }}
        div[data-testid="stSegmentedControl"] {{
            background: transparent !important;
            border: 0 !important;
            border-radius: 12px !important;
            padding: 0 !important;
            box-shadow: none !important;
        }}
        div[data-testid="stSegmentedControl"] label,
        div[data-testid="stSegmentedControl"] button {{
            color: var(--coach-text) !important;
            border-radius: 9px !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            background: transparent !important;
            border-color: transparent !important;
            box-shadow: none !important;
            min-height: 28px !important;
            height: 28px !important;
        }}
        div[data-testid="stSegmentedControl"] button p {{
            font-size: 13px !important;
            line-height: 1 !important;
        }}
        div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
        div[data-testid="stSegmentedControl"] button[aria-selected="true"] {{
            background: color-mix(in srgb, var(--coach-text) 12%, transparent) !important;
            border-color: transparent !important;
        }}
        .coach-voice-tools-card {{
            margin-top: 6px !important;
            max-height: 48px !important;
            padding: 8px 9px !important;
        }}
        .coach-voice-tools-card h3 {{
            font-size: 12.5px !important;
            margin-bottom: 2px !important;
        }}
        .coach-voice-tools-card p {{
            display: none !important;
        }}
        iframe[title="st.iframe"] {{
            border-radius: 13px 13px 0 0 !important;
        }}
        div[data-testid="stTextArea"] {{
            margin-top: -6px !important;
        }}
        div[data-testid="stTextInput"] {{
            margin-top: -6px !important;
        }}

        /* AI-Trader inspired terminal finish. */
        html,
        body,
        .stApp {{
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif !important;
            font-size: 12px !important;
        }}
        .stApp::before {{
            background:
                radial-gradient(circle at 78% -16%, color-mix(in srgb, var(--coach-accent) 18%, transparent), transparent 31%),
                radial-gradient(circle at 8% 18%, color-mix(in srgb, var(--coach-text) 7%, transparent), transparent 30%),
                linear-gradient(135deg, color-mix(in srgb, var(--coach-bg) 92%, #000 8%), var(--coach-bg) 62%, color-mix(in srgb, var(--coach-bg) 88%, var(--coach-accent) 4%)) !important;
        }}
        .stApp::after {{
            content: "" !important;
            position: fixed !important;
            inset: 0 !important;
            z-index: 0 !important;
            pointer-events: none !important;
            opacity: 0.022 !important;
            background-image:
                radial-gradient(circle at 20% 20%, var(--coach-text) 0 0.38px, transparent 0.7px),
                radial-gradient(circle at 80% 70%, var(--coach-accent) 0 0.32px, transparent 0.72px) !important;
            background-size: 8px 8px, 11px 11px !important;
            mix-blend-mode: screen !important;
        }}
        .block-container {{
            padding: 0.55rem 0.75rem !important;
        }}
        .block-container > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-child {{
            height: calc(100vh - 1.1rem) !important;
        }}
        div[data-testid="column"] > div > div[data-testid="stVerticalBlock"] {{
            gap: 0.38rem !important;
        }}
        h1, h2, h3, h4, h5, h6,
        p, label, span, div {{
            letter-spacing: 0 !important;
            text-wrap: pretty;
        }}
        .coach-topbar-title,
        .coach-brand-title,
        .coach-insight-head h3,
        .coach-card-head strong {{
            text-wrap: balance;
        }}
        .coach-shell-card,
        .coach-goal-card,
        .coach-stage-card,
        .coach-statusbar,
        .coach-input-shell,
        .coach-analysis-card,
        .coach-summary-card,
        .coach-insight-panel,
        .voice-lab-card,
        [data-testid="stAudioInput"],
        [data-testid="stFileUploader"],
        div[data-testid="stMetric"] {{
            border-radius: 16px !important;
            background:
                linear-gradient(180deg, color-mix(in srgb, var(--coach-panel) 94%, var(--coach-text) 3%), var(--coach-panel)) !important;
            border: 1px solid var(--coach-border) !important;
            box-shadow:
                inset 0 1px 0 color-mix(in srgb, var(--coach-text) 7%, transparent),
                inset 0 -1px 0 rgba(0,0,0,0.18),
                var(--coach-shadow) !important;
            backdrop-filter: blur(30px) saturate(1.2) !important;
            -webkit-backdrop-filter: blur(30px) saturate(1.2) !important;
            outline: 1px solid color-mix(in srgb, var(--coach-text) 2.5%, transparent) !important;
        }}
        .coach-left-rail {{
            margin-bottom: 7px !important;
            padding: 10px !important;
            border-radius: 18px !important;
            background:
                linear-gradient(180deg, color-mix(in srgb, var(--coach-panel) 96%, #000 8%), color-mix(in srgb, var(--coach-panel) 88%, #000 10%)) !important;
            box-shadow: 0 20px 46px rgba(0,0,0,0.24) !important;
        }}
        .coach-brand-card {{
            min-height: 72px !important;
        }}
        .coach-brand-row {{
            align-items: flex-start !important;
            gap: 9px !important;
        }}
        .coach-logo-line {{
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            min-width: 0 !important;
        }}
        .coach-logo-mark,
        .coach-collapsed-logo {{
            width: 32px !important;
            height: 32px !important;
            display: grid !important;
            place-items: center !important;
            border-radius: 10px !important;
            color: var(--coach-primary-text) !important;
            background: var(--coach-primary) !important;
            font-size: 11px !important;
            font-weight: 860 !important;
            letter-spacing: 0 !important;
            box-shadow: 0 10px 26px color-mix(in srgb, var(--coach-accent) 28%, transparent) !important;
        }}
        .coach-logo-copy {{
            min-width: 0 !important;
        }}
        .coach-brand-title {{
            color: var(--coach-text) !important;
            font-size: 13px !important;
            font-weight: 780 !important;
            line-height: 1.08 !important;
            white-space: nowrap !important;
        }}
        .coach-brand-subtitle {{
            margin-top: 4px !important;
            color: var(--coach-muted) !important;
            font-size: 9.5px !important;
            line-height: 1.25 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        .coach-status-pill {{
            background: var(--coach-accent-soft) !important;
            border-color: var(--coach-border-strong) !important;
            color: color-mix(in srgb, var(--coach-accent) 74%, var(--coach-text)) !important;
            font-size: 9px !important;
            font-weight: 760 !important;
            padding: 4px 6px !important;
        }}
        .coach-nav-label,
        .coach-rail-label {{
            color: var(--coach-muted) !important;
            font-size: 9.5px !important;
            font-weight: 760 !important;
            text-transform: uppercase !important;
            margin: 4px 3px 5px !important;
        }}
        .coach-mode-card {{
            margin-top: 7px !important;
            padding: 8px 9px !important;
            border: 1px solid var(--coach-border) !important;
            border-radius: 14px !important;
            background: color-mix(in srgb, var(--coach-panel-2) 74%, transparent) !important;
        }}
        .coach-mode-card strong {{
            display: block !important;
            color: var(--coach-text) !important;
            font-size: 11px !important;
            line-height: 1.15 !important;
        }}
        .coach-mode-card span {{
            display: block !important;
            margin-top: 3px !important;
            color: var(--coach-muted) !important;
            font-size: 9.5px !important;
            line-height: 1.2 !important;
        }}
        .stButton > button,
        .stDownloadButton > button,
        button[kind="secondary"],
        button[data-testid="stBaseButton-secondary"],
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {{
            height: 30px !important;
            min-height: 30px !important;
            border-radius: 12px !important;
            font-size: 11px !important;
            font-weight: 720 !important;
            border-color: var(--coach-border) !important;
            background: color-mix(in srgb, var(--coach-button) 90%, transparent) !important;
            color: var(--coach-button-text) !important;
            box-shadow: inset 0 1px 0 color-mix(in srgb, var(--coach-text) 5%, transparent) !important;
            transition:
                transform 220ms cubic-bezier(0.32, 0.72, 0, 1),
                background 220ms cubic-bezier(0.32, 0.72, 0, 1),
                border-color 220ms cubic-bezier(0.32, 0.72, 0, 1),
                box-shadow 220ms cubic-bezier(0.32, 0.72, 0, 1) !important;
        }}
        .stButton > button p,
        .stDownloadButton > button p,
        button p {{
            font-size: 11px !important;
            line-height: 1 !important;
            font-weight: 720 !important;
        }}
        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"],
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {{
            background: linear-gradient(180deg, color-mix(in srgb, var(--coach-primary) 92%, #fff 8%), var(--coach-primary)) !important;
            color: var(--coach-primary-text) !important;
            border-color: color-mix(in srgb, var(--coach-primary) 82%, #fff 12%) !important;
            box-shadow: 0 10px 24px color-mix(in srgb, var(--coach-primary) 18%, transparent) !important;
        }}
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        button:hover {{
            transform: translateY(-1px);
            border-color: var(--coach-border-strong) !important;
        }}
        .stButton > button:active,
        .stDownloadButton > button:active,
        button:active {{
            transform: translateY(1px) scale(0.985) !important;
        }}
        .stButton > button:focus-visible,
        .stDownloadButton > button:focus-visible,
        button:focus-visible,
        input:focus-visible,
        textarea:focus-visible {{
            outline: 2px solid color-mix(in srgb, var(--coach-accent) 56%, transparent) !important;
            outline-offset: 2px !important;
        }}
        .stSelectbox label,
        .stTextArea label,
        .stAudioInput label,
        .stFileUploader label,
        .stCheckbox label {{
            color: var(--coach-muted) !important;
            font-size: 10px !important;
            font-weight: 720 !important;
        }}
        .stSelectbox div[data-baseweb="select"] > div,
        input,
        textarea {{
            min-height: 32px !important;
            border-radius: 12px !important;
            background: color-mix(in srgb, var(--coach-panel-3) 94%, transparent) !important;
            border: 1px solid var(--coach-border) !important;
            box-shadow: inset 0 1px 0 color-mix(in srgb, var(--coach-text) 5%, transparent) !important;
            transition:
                border-color 220ms cubic-bezier(0.32, 0.72, 0, 1),
                background 220ms cubic-bezier(0.32, 0.72, 0, 1),
                box-shadow 220ms cubic-bezier(0.32, 0.72, 0, 1) !important;
        }}
        .coach-goal-card {{
            padding: 10px !important;
            max-height: 92px !important;
            border-radius: 16px !important;
        }}
        .coach-goal-card .coach-card-head strong,
        .coach-stage-head strong {{
            font-size: 12px !important;
        }}
        .coach-goal-card p {{
            color: var(--coach-muted) !important;
            font-size: 10.5px !important;
            line-height: 1.3 !important;
        }}
        .coach-statusbar {{
            min-height: 82px !important;
            padding: 13px 15px 10px !important;
            border-radius: 18px 18px 14px 14px !important;
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--coach-panel) 96%, #000 6%), color-mix(in srgb, var(--coach-panel-2) 86%, var(--coach-accent) 3%)) !important;
            border-color: color-mix(in srgb, var(--coach-border) 86%, var(--coach-accent) 14%) !important;
        }}
        .coach-topbar-kicker {{
            color: var(--coach-accent) !important;
            font-size: 9.5px !important;
            font-weight: 800 !important;
        }}
        .coach-topbar-title {{
            color: var(--coach-text) !important;
            font-size: 19px !important;
            font-weight: 820 !important;
            line-height: 1.1 !important;
        }}
        .coach-topbar-main p {{
            color: var(--coach-muted) !important;
            font-size: 11px !important;
            margin-top: 5px !important;
        }}
        .coach-topbar-meta span {{
            min-height: 22px !important;
            max-width: 160px !important;
            padding: 5px 8px !important;
            border-radius: 999px !important;
            background: color-mix(in srgb, var(--coach-panel-2) 80%, transparent) !important;
            border-color: var(--coach-border) !important;
            color: var(--coach-muted) !important;
            font-size: 10px !important;
            font-variant-numeric: tabular-nums !important;
        }}
        .coach-progress-track {{
            height: 4px !important;
            background: color-mix(in srgb, var(--coach-text) 8%, transparent) !important;
            border: 0 !important;
        }}
        .coach-progress-fill,
        .score-bar-fill,
        .lesson-progress-fill {{
            background: linear-gradient(90deg, var(--coach-accent), color-mix(in srgb, var(--coach-accent) 74%, var(--coach-text))) !important;
        }}
        iframe[title="st.iframe"] {{
            border-radius: 16px 16px 0 0 !important;
        }}
        .coach-input-shell {{
            border-radius: 0 0 16px 16px !important;
            background: color-mix(in srgb, var(--coach-panel) 96%, #000 3%) !important;
            border-top-color: transparent !important;
            padding: 8px !important;
        }}
        .stTextInput input,
        input[aria-label="用户英文输入"],
        textarea[aria-label="用户英文输入"] {{
            height: 72px !important;
            min-height: 72px !important;
            border-radius: 13px !important;
            font-size: 12px !important;
        }}
        div[data-testid="stTextInput"] {{
            margin-top: 0 !important;
        }}
        .coach-insight-panel {{
            border-radius: 18px !important;
            background:
                linear-gradient(180deg, color-mix(in srgb, var(--coach-panel) 96%, #000 5%), color-mix(in srgb, var(--coach-panel-2) 82%, transparent)) !important;
            border-color: color-mix(in srgb, var(--coach-border) 86%, var(--coach-accent) 10%) !important;
        }}
        .coach-insight-head {{
            padding: 12px 13px 10px !important;
            border-bottom-color: var(--coach-border) !important;
        }}
        .coach-insight-head h3 {{
            font-size: 14px !important;
            font-weight: 820 !important;
        }}
        .coach-insight-head span {{
            color: var(--coach-accent) !important;
            font-size: 10px !important;
            font-weight: 780 !important;
            font-variant-numeric: tabular-nums !important;
        }}
        .coach-insight-section {{
            padding: 12px 13px !important;
        }}
        .coach-insight-section h4 {{
            color: var(--coach-text) !important;
            font-size: 12.5px !important;
            font-weight: 780 !important;
        }}
        .coach-insight-section p,
        .coach-insight-section li {{
            color: var(--coach-soft) !important;
            font-size: 11.3px !important;
            line-height: 1.42 !important;
        }}
        .coach-insight-detail {{
            height: 336px !important;
            margin-top: 6px !important;
        }}
        .coach-score-line {{
            border-radius: 12px !important;
            background: color-mix(in srgb, var(--coach-panel-2) 78%, transparent) !important;
            border-color: var(--coach-border) !important;
        }}
        .coach-score-line-head strong,
        .coach-score-line-head span {{
            font-size: 10.8px !important;
        }}
        .coach-voice-tools-card {{
            border-radius: 16px !important;
            max-height: 46px !important;
        }}
        div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
        div[data-testid="stSegmentedControl"] button[aria-selected="true"] {{
            background: var(--coach-accent-soft) !important;
            color: var(--coach-text) !important;
        }}

        /* Compact navigation rail, modeled after the reference sidebar. */
        .block-container > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-child > div[data-testid="stColumn"]:first-child > div {{
            overflow-y: auto !important;
            overflow-x: hidden !important;
            padding-right: 2px !important;
            scrollbar-width: thin !important;
            scrollbar-color: color-mix(in srgb, var(--coach-accent) 34%, transparent) transparent !important;
        }}
        .block-container > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-child > div[data-testid="stColumn"]:last-child > div {{
            overflow: hidden !important;
        }}
        .block-container > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-child {{
            column-gap: 0.58rem !important;
        }}
        .coach-left-rail {{
            margin-bottom: 5px !important;
            padding: 8px !important;
            border-radius: 15px !important;
            text-align: left !important;
        }}
        .coach-brand-card {{
            min-height: 58px !important;
        }}
        .coach-brand-row {{
            gap: 6px !important;
        }}
        .coach-logo-line {{
            gap: 7px !important;
        }}
        .coach-logo-mark,
        .coach-collapsed-logo {{
            width: 28px !important;
            height: 28px !important;
            border-radius: 9px !important;
            font-size: 10px !important;
        }}
        .coach-brand-title {{
            font-size: 11.6px !important;
            line-height: 1.16 !important;
            white-space: normal !important;
            overflow-wrap: anywhere !important;
        }}
        .coach-brand-subtitle {{
            font-size: 8.8px !important;
            line-height: 1.18 !important;
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }}
        .coach-status-pill {{
            flex: 0 0 auto !important;
            padding: 3px 5px !important;
            font-size: 8.6px !important;
        }}
        .coach-nav-label,
        .coach-rail-label {{
            margin: 3px 2px 4px !important;
            font-size: 9px !important;
            text-align: left !important;
        }}
        .coach-mode-card {{
            margin-top: 5px !important;
            padding: 7px 8px !important;
            border-radius: 12px !important;
            text-align: left !important;
        }}
        .coach-mode-card strong {{
            font-size: 10.5px !important;
        }}
        .coach-mode-card span {{
            font-size: 8.8px !important;
            white-space: normal !important;
            overflow-wrap: anywhere !important;
        }}
        .coach-goal-card {{
            padding: 8px !important;
            max-height: none !important;
            border-radius: 13px !important;
            text-align: left !important;
        }}
        .coach-goal-card .coach-card-head,
        .coach-goal-card .coach-stage-head {{
            margin-bottom: 4px !important;
        }}
        .coach-goal-card .coach-card-head strong,
        .coach-stage-head strong {{
            font-size: 11px !important;
            line-height: 1.14 !important;
        }}
        .coach-goal-card .coach-card-head span,
        .coach-stage-head span {{
            font-size: 8.8px !important;
        }}
        .coach-goal-card p {{
            margin-top: 5px !important;
            font-size: 9.4px !important;
            line-height: 1.24 !important;
            display: block !important;
            -webkit-line-clamp: unset !important;
            overflow: visible !important;
            overflow-wrap: anywhere !important;
        }}
        .block-container > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-child > div[data-testid="stColumn"]:first-child .stButton > button {{
            justify-content: flex-start !important;
            text-align: left !important;
            height: auto !important;
            min-height: 27px !important;
            padding: 5px 9px !important;
            border-radius: 12px !important;
        }}
        .block-container > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-child > div[data-testid="stColumn"]:first-child .stButton > button p {{
            width: 100% !important;
            text-align: left !important;
            white-space: normal !important;
            line-height: 1.12 !important;
            overflow-wrap: anywhere !important;
        }}
        .block-container > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-child > div[data-testid="stColumn"]:first-child [data-testid="stSelectbox"] {{
            margin-bottom: 3px !important;
        }}
        .block-container > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-child > div[data-testid="stColumn"]:first-child [data-baseweb="select"] > div {{
            min-height: 30px !important;
            border-radius: 11px !important;
        }}
        .block-container > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-child > div[data-testid="stColumn"]:first-child label {{
            text-align: left !important;
            font-size: 9px !important;
        }}
        div[data-testid="stColumn"]:has(.coach-brand-card) > div[data-testid="stVerticalBlock"] {{
            overflow-y: auto !important;
            overflow-x: hidden !important;
            scrollbar-width: thin !important;
            scrollbar-color: color-mix(in srgb, var(--coach-accent) 34%, transparent) transparent !important;
        }}
        div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child > div[data-testid="stVerticalBlock"] {{
            overflow: hidden !important;
        }}
        div[data-testid="stColumn"]:has(.coach-brand-card) .stButton > button {{
            justify-content: flex-start !important;
            text-align: left !important;
            height: auto !important;
            min-height: 27px !important;
            padding: 5px 9px !important;
        }}
        div[data-testid="stColumn"]:has(.coach-brand-card) .stButton > button p {{
            width: 100% !important;
            text-align: left !important;
            white-space: normal !important;
            line-height: 1.12 !important;
            overflow-wrap: anywhere !important;
        }}
        div[data-testid="stColumn"]:has(.coach-brand-card) .stButton > button[data-testid="stBaseButton-primary"] {{
            box-shadow:
                inset 3px 0 0 color-mix(in srgb, var(--coach-primary-text) 42%, transparent),
                0 10px 24px color-mix(in srgb, var(--coach-primary) 18%, transparent) !important;
        }}
        div[data-testid="stColumn"]:has(.coach-brand-card) label {{
            text-align: left !important;
            font-size: 9px !important;
        }}

        /* Taste Skill redesign pass: double-bezel surfaces and cockpit hierarchy. */
        .coach-left-rail,
        .coach-goal-card,
        .coach-statusbar,
        .coach-input-shell,
        .coach-insight-panel,
        .coach-voice-tools-card {{
            position: relative !important;
            isolation: isolate !important;
            overflow: hidden !important;
        }}
        .coach-left-rail::before,
        .coach-goal-card::before,
        .coach-statusbar::before,
        .coach-input-shell::before,
        .coach-insight-panel::before,
        .coach-voice-tools-card::before {{
            content: "" !important;
            position: absolute !important;
            inset: 1px !important;
            z-index: 0 !important;
            pointer-events: none !important;
            border-radius: calc(1em - 1px) !important;
            border: 1px solid color-mix(in srgb, var(--coach-text) 3.5%, transparent) !important;
            box-shadow:
                inset 0 1px 0 color-mix(in srgb, var(--coach-text) 8%, transparent),
                inset 0 0 22px color-mix(in srgb, var(--coach-accent) 3.5%, transparent) !important;
        }}
        .coach-left-rail > *,
        .coach-goal-card > *,
        .coach-statusbar > *,
        .coach-input-shell > *,
        .coach-insight-panel > *,
        .coach-voice-tools-card > * {{
            position: relative !important;
            z-index: 1 !important;
        }}
        .coach-statusbar {{
            grid-template-columns: minmax(0, 1fr) minmax(292px, auto) !important;
            padding-top: 16px !important;
        }}
        .coach-window-chrome {{
            position: absolute !important;
            top: 8px !important;
            left: 12px !important;
            display: inline-flex !important;
            gap: 5px !important;
            align-items: center !important;
            pointer-events: none !important;
        }}
        .coach-window-chrome span {{
            width: 6px !important;
            height: 6px !important;
            border-radius: 999px !important;
            background: color-mix(in srgb, var(--coach-muted) 42%, transparent) !important;
            border: 1px solid color-mix(in srgb, var(--coach-text) 6%, transparent) !important;
        }}
        .coach-window-chrome span:first-child {{
            background: color-mix(in srgb, var(--coach-accent) 72%, transparent) !important;
        }}
        .coach-topbar-kicker {{
            margin-top: 3px !important;
        }}
        .coach-topbar-meta span {{
            box-shadow:
                inset 0 1px 0 color-mix(in srgb, var(--coach-text) 4%, transparent),
                0 6px 16px rgba(0,0,0,0.10) !important;
        }}
        div[data-testid="stColumn"]:has(.coach-brand-card) .stButton > button p {{
            display: inline-flex !important;
            align-items: center !important;
            gap: 7px !important;
            letter-spacing: 0 !important;
        }}
        div[data-testid="stColumn"]:has(.coach-brand-card) .stButton > button[data-testid="stBaseButton-primary"] {{
            background:
                linear-gradient(90deg, color-mix(in srgb, var(--coach-primary) 96%, #fff 5%), color-mix(in srgb, var(--coach-primary) 82%, #000 8%)) !important;
        }}
        .coach-insight-head {{
            align-items: flex-start !important;
        }}
        .coach-insight-kicker {{
            display: block !important;
            margin-bottom: 4px !important;
            color: var(--coach-accent) !important;
            font-size: 8.8px !important;
            line-height: 1 !important;
            font-weight: 820 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
        }}
        .coach-insight-head h3 {{
            margin: 0 !important;
        }}
        .coach-insight-detail {{
            box-shadow:
                inset 0 1px 0 color-mix(in srgb, var(--coach-text) 4%, transparent),
                0 18px 46px rgba(0,0,0,0.18) !important;
        }}
        .coach-input-shell {{
            box-shadow:
                inset 0 1px 0 color-mix(in srgb, var(--coach-text) 4%, transparent),
                0 -10px 38px rgba(0,0,0,0.18) !important;
        }}
        .stTextInput input:focus,
        input[aria-label="用户英文输入"]:focus,
        textarea[aria-label="用户英文输入"]:focus {{
            border-color: color-mix(in srgb, var(--coach-accent) 42%, var(--coach-border)) !important;
            box-shadow:
                inset 0 1px 0 color-mix(in srgb, var(--coach-text) 6%, transparent),
                0 0 0 3px color-mix(in srgb, var(--coach-accent) 10%, transparent) !important;
        }}
        @media (prefers-reduced-transparency: reduce) {{
            .coach-shell-card,
            .coach-goal-card,
            .coach-stage-card,
            .coach-statusbar,
            .coach-input-shell,
            .coach-analysis-card,
            .coach-summary-card,
            .coach-insight-panel,
            .voice-lab-card,
            [data-testid="stAudioInput"],
            [data-testid="stFileUploader"] {{
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                background: var(--coach-panel) !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_left_brand(mode_label: str, collapsed: bool) -> None:
    short_mode = "API" if "API" in mode_label else "本地"
    if collapsed:
        st.markdown(
            """
            <div class="coach-shell-card coach-left-rail">
              <div class="coach-collapsed-brand">
                <div class="coach-collapsed-logo">EC</div>
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
            <div class="coach-logo-line">
              <div class="coach-logo-mark">EC</div>
              <div class="coach-logo-copy">
                <div class="coach-brand-title">AI-English Coach</div>
                <div class="coach-brand-subtitle">Speaking training terminal</div>
              </div>
            </div>
            <div class="coach-status-pill">{esc(short_mode)}</div>
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
            <strong>训练任务</strong>
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
          <div class="coach-window-chrome">
            <span></span><span></span><span></span>
          </div>
          <div class="coach-topbar-main">
            <div class="coach-topbar-kicker">AI4COACH 训练终端</div>
            <div class="coach-topbar-title">进入你的口语训练席位</div>
            <p>{esc(scenario.get("cn_label", ""))} · {esc(step.get("title", ""))} · Round {display_round} / {min_rounds}</p>
          </div>
          <div class="coach-topbar-meta">
            <span>场景 · {esc(scenario.get("cn_label", ""))}</span>
            <span>阶段 · {esc(step.get("title", ""))}</span>
            <span>{esc(status_text)} · {progress}%</span>
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
    chat_bg = "rgba(233,236,240,0.58)" if is_light else "rgba(7,11,16,0.74)"
    assistant_bg = "rgba(247,248,250,0.72)" if is_light else "rgba(19,29,38,0.84)"
    user_bg = "rgba(122,97,45,0.15)" if is_light else "rgba(217,168,79,0.16)"
    user_text = "#2a2111" if is_light else "#f3dfb6"
    user_meta = "rgba(68,52,21,0.62)" if is_light else "rgba(243,223,182,0.66)"
    text_color = "#20252b" if is_light else "#f2f3f0"
    muted_color = "#6f7780" if is_light else "#87919c"
    border_color = "rgba(35,40,48,0.11)" if is_light else "rgba(255,255,255,0.085)"
    accent_color = "#7a612d" if is_light else "#d9a84f"
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
            padding: 16px 17px 13px;
            background: {chat_bg};
            border: 1px solid {border_color};
            border-bottom: 0;
            border-radius: 16px 16px 0 0;
            scrollbar-color: rgba(148,163,184,0.42) transparent;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
            backdrop-filter: blur(28px) saturate(1.18);
            -webkit-backdrop-filter: blur(28px) saturate(1.18);
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
            background: rgba(255,255,255,0.045);
            color: {muted_color};
            font-size: 10px;
            font-weight: 800;
        }}
        .user .avatar {{
            order: 2;
            background: {user_bg};
            color: {user_text};
            border-color: rgba(217,168,79,0.28);
        }}
        .bubble {{
            max-width: min(74%, 680px);
            padding: 10px 12px 11px;
            border-radius: 15px;
            border: 1px solid {border_color};
            box-shadow: 0 14px 30px rgba(0,0,0,0.14);
        }}
        .assistant .bubble {{
            background: {assistant_bg};
            color: {text_color};
            border-bottom-left-radius: 6px;
        }}
        .user .bubble {{
            order: 1;
            background: {user_bg};
            color: {user_text};
            border-color: rgba(217,168,79,0.24);
            border-bottom-right-radius: 6px;
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
            font-size: 10.5px;
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
            font-size: 13px;
            line-height: 1.46;
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
            border-radius: 15px;
            padding: 22px;
            background: rgba(255,255,255,0.025);
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
        .empty-state strong::after {{
            content: "";
            display: block;
            width: 34px;
            height: 2px;
            margin: 8px auto 0;
            border-radius: 999px;
            background: {accent_color};
            opacity: 0.72;
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
    ai_text = esc(_short_text(ai_reply, 220)) if ai_reply else "等待 AI 开场。"
    view_labels = {
        "correction": "纠错",
        "score": "评分",
        "suggestion": "建议",
    }
    if st.session_state.get("analysis_view") not in view_labels:
        st.session_state.analysis_view = "correction"

    if feedback:
        issues = _list_html(feedback.get("issue_explanation", []), limit=2, max_chars=110)
        alternatives = _list_html(feedback.get("alternative_expressions", []), limit=2, max_chars=110)
        feedback_html = f"""
          <div class="coach-insight-field"><span>原句</span><p>{esc(_short_text(feedback.get("original_sentence", ""), 160))}</p></div>
          <div class="coach-insight-field"><span>修改后</span><p>{esc(_short_text(feedback.get("corrected_sentence", ""), 160))}</p></div>
          <div class="coach-insight-field"><span>错误原因</span>{issues}</div>
          <div class="coach-insight-field"><span>更自然表达</span><p>{esc(_short_text(feedback.get("natural_expression", ""), 170))}</p></div>
          <div class="coach-insight-field"><span>替代表达</span>{alternatives}</div>
        """
    else:
        feedback_html = """
          <div class="coach-empty coach-insight-empty">
            <strong>等待回答</strong>
            <span>提交英文回答后显示原句、修改句、错误原因和自然表达。</span>
          </div>
        """

    if score:
        total_score = _safe_score(score.get("total_score"))
        dimensions = score.get("dimensions", {})
        rows = []
        for key, fallback_label in DIMENSION_ORDER:
            item = dimensions.get(key, {})
            value = _safe_score(item.get("score"))
            label = str(item.get("label") or fallback_label)
            explanation = "演示发音评分，非真实音素级评测。" if key == "pronunciation" else _short_text(
                item.get("explanation", ""), 95
            )
            rows.append(
                f"""
                <div class="coach-score-line">
                  <div class="coach-score-line-head">
                    <strong>{esc(label)}</strong>
                    <span>{value}/100</span>
                  </div>
                  <div class="coach-progress-track">
                    <div class="coach-progress-fill" style="width: {value}%;"></div>
                  </div>
                  <p>{esc(explanation)}</p>
                </div>
                """
            )
        score_html = (
            f'<div class="coach-insight-total"><strong>{total_score}</strong><span>Overall Score / 100</span></div>'
            f'<div class="coach-score-lines">{"".join(rows)}</div>'
        )
    else:
        score_html = """
          <div class="coach-empty coach-insight-empty">
            <strong>等待评分</strong>
            <span>完成本轮回答后显示 Overall Score 和五维评分。</span>
          </div>
        """

    if not suggestion:
        suggestion = {}
    suggestion_html = f"""
      <div class="coach-insight-field"><span>主要问题</span><p>{esc(_short_text(suggestion.get("main_issue", "等待本轮反馈。"), 150))}</p></div>
      <div class="coach-insight-field"><span>跟读句</span><p>{esc(_short_text(suggestion.get("practice_sentence", "提交回答后生成跟读句。"), 150))}</p></div>
      <div class="coach-insight-field"><span>下一轮提示</span><p>{esc(_short_text(suggestion.get("next_tip", "先回答 AI 当前问题，再补充一个原因或例子。"), 150))}</p></div>
    """

    st.html(
        f"""
        <div class="coach-insight-panel">
          <div class="coach-insight-head">
            <div>
              <span class="coach-insight-kicker">Coach Review</span>
              <h3>学习雷达</h3>
            </div>
            <span>{esc(average) + "/100" if average is not None else "待评分"}</span>
          </div>
          <div class="coach-insight-section">
            <h4>当前追问</h4>
            <p>{ai_text}</p>
          </div>
        </div>
        """
    )
    if hasattr(st, "segmented_control"):
        selected = st.segmented_control(
            "分析视图",
            options=list(view_labels),
            format_func=lambda key: view_labels[key],
            key="analysis_view",
            label_visibility="collapsed",
        )
    else:
        tab_cols = st.columns(3)
        selected = st.session_state.analysis_view
        for col, (view_key, label) in zip(tab_cols, view_labels.items(), strict=True):
            if col.button(
                label,
                key=f"analysis_view_{view_key}",
                type="primary" if st.session_state.analysis_view == view_key else "secondary",
                width="stretch",
            ):
                st.session_state.analysis_view = view_key
                selected = view_key
    selected = selected or st.session_state.get("analysis_view", "correction")
    detail_map = {
        "correction": ("纠错反馈", feedback_html),
        "score": ("五维评分", score_html),
        "suggestion": ("下一步建议", suggestion_html),
    }
    title, detail_html = detail_map[selected]
    st.html(
        f"""
        <div class="coach-insight-panel coach-insight-detail">
          <div class="coach-insight-section">
            <h4>{esc(title)}</h4>
            {detail_html}
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
