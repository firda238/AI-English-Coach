"""Export lesson summaries to lightweight HTML reports."""

from __future__ import annotations

import html
import re
from pathlib import Path

import storage


def markdown_to_html(markdown: str) -> str:
    """Convert a small Markdown subset used by this project to HTML."""
    lines = []
    in_list = False
    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.startswith("# "):
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_list:
                lines.append("<ul>")
                in_list = True
            content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html.escape(line[2:]))
            lines.append(f"<li>{content}</li>")
        elif not line:
            if in_list:
                lines.append("</ul>")
                in_list = False
        else:
            if in_list:
                lines.append("</ul>")
                in_list = False
            content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html.escape(line))
            lines.append(f"<p>{content}</p>")
    if in_list:
        lines.append("</ul>")
    return "\n".join(lines)


def build_html_report(markdown: str, title: str = "AI 英语口语陪练学习报告") -> str:
    """Wrap converted Markdown in a print-friendly HTML template."""
    body = markdown_to_html(markdown)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 40px; color: #1f2933; line-height: 1.65; }}
    h1 {{ font-size: 30px; margin-bottom: 16px; }}
    h2 {{ font-size: 20px; margin-top: 28px; border-bottom: 1px solid #d9e2ec; padding-bottom: 6px; }}
    ul {{ padding-left: 22px; }}
    li {{ margin: 6px 0; }}
    p {{ margin: 10px 0; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def save_html_report(markdown: str) -> Path:
    """Save a generated lesson summary as HTML."""
    storage.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = storage.OUTPUT_DIR / f"lesson_report_{storage.timestamp_slug()}.html"
    path.write_text(build_html_report(markdown), encoding="utf-8")
    return path
