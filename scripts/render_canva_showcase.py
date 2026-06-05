"""Render a report-ready showcase poster for AI-English-Coach.

The generated PNG is a local fallback for Canva-style presentation material.
It keeps the visual language aligned with the Streamlit app and Figma handoff.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "canva_showcase.png"
WIDTH = 1440
HEIGHT = 1000

COLORS = {
    "bg": "#0b1220",
    "sidebar": "#111827",
    "panel": "#101827",
    "panel_2": "#111f32",
    "panel_3": "#172033",
    "stroke": "#243244",
    "stroke_strong": "#334155",
    "text": "#f8fafc",
    "muted": "#cbd5e1",
    "subtle": "#94a3b8",
    "blue": "#38bdf8",
    "green": "#22c55e",
    "orange": "#f59e0b",
    "red": "#ff4b4b",
    "purple": "#a78bfa",
}

FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size=size, index=0)
        except OSError:
            continue
    return ImageFont.load_default()


FONT = {
    "title": load_font(58, True),
    "h1": load_font(42, True),
    "h2": load_font(30, True),
    "h3": load_font(22, True),
    "body": load_font(18),
    "body_bold": load_font(18, True),
    "small": load_font(15),
    "tiny": load_font(13),
    "score": load_font(48, True),
}


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in range(0, 6, 2))


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, radius: int = 18, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont, fill: str = COLORS["text"]) -> None:
    draw.text(xy, text, font=font, fill=fill)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines():
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for char in paragraph:
            test = current + char
            if text_size(draw, test, font)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = char
        if current:
            lines.append(current)
    return lines


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont, max_width: int, fill: str = COLORS["muted"], line_gap: int = 8) -> int:
    x, y = xy
    for line in wrap_text(draw, text, font, max_width):
        draw_text(draw, (x, y), line, font, fill)
        y += text_size(draw, line or " ", font)[1] + line_gap
    return y


def draw_gradient_background(img: Image.Image) -> None:
    top = hex_to_rgb(COLORS["bg"])
    bottom = hex_to_rgb("#111b2f")
    pixels = img.load()
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        color = tuple(int(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        for x in range(WIDTH):
            pixels[x, y] = color


def draw_chip(draw: ImageDraw.ImageDraw, xy: tuple[int, int], label: str, color: str) -> None:
    x, y = xy
    w, h = text_size(draw, label, FONT["small"])
    rounded(draw, (x, y, x + w + 28, y + 34), "#162238", 16, COLORS["stroke"])
    draw.ellipse((x + 12, y + 12, x + 20, y + 20), fill=color)
    draw_text(draw, (x + 28, y + 8), label, FONT["small"], COLORS["muted"])


def draw_metric_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, value: str, body: str, accent: str) -> None:
    rounded(draw, box, COLORS["panel_2"], 18, COLORS["stroke"])
    x1, y1, x2, _ = box
    draw.rounded_rectangle((x1 + 22, y1 + 22, x1 + 58, y1 + 58), radius=12, fill=accent)
    draw_text(draw, (x1 + 78, y1 + 20), title, FONT["h3"])
    max_value_width = x2 - x1 - 44
    value_font = FONT["score"] if text_size(draw, value, FONT["score"])[0] <= max_value_width else FONT["h1"]
    draw_text(draw, (x1 + 22, y1 + 76), value, value_font, COLORS["text"])
    draw_wrapped(draw, (x1 + 22, y1 + 136), body, FONT["small"], x2 - x1 - 44, COLORS["subtle"], 6)


def draw_mockup(draw: ImageDraw.ImageDraw) -> None:
    x, y, w, h = 892, 348, 320, 430
    rounded(draw, (x, y, x + w, y + h), "#0f172a", 22, COLORS["stroke_strong"], 2)
    rounded(draw, (x + 20, y + 22, x + w - 20, y + 88), COLORS["panel_2"], 16, COLORS["stroke"])
    draw_text(draw, (x + 42, y + 40), "练习中心", FONT["h3"])
    draw_chip(draw, (x + 204, y + 36), "本地演示", COLORS["green"])

    rounded(draw, (x + 20, y + 112, x + 172, y + 250), COLORS["panel_3"], 16, COLORS["stroke"])
    draw_text(draw, (x + 38, y + 132), "用户输入", FONT["body_bold"])
    draw_wrapped(draw, (x + 38, y + 168), "I suggest we discuss the main risk first.", FONT["small"], 116, COLORS["muted"], 6)
    rounded(draw, (x + 188, y + 112, x + w - 20, y + 250), COLORS["panel_3"], 16, COLORS["stroke"])
    draw_text(draw, (x + 206, y + 132), "AI 回复", FONT["body_bold"])
    draw_wrapped(draw, (x + 206, y + 168), "Could you explain one example?", FONT["small"], 86, COLORS["muted"], 6)

    rounded(draw, (x + 20, y + 272, x + w - 20, y + 348), "#12281e", 16, "#1f6f43")
    draw_text(draw, (x + 38, y + 292), "纠错反馈", FONT["body_bold"])
    draw_wrapped(draw, (x + 38, y + 320), "语法清晰，建议补充原因和例子。", FONT["small"], 278, "#bbf7d0", 6)

    rounded(draw, (x + 20, y + 370, x + w - 20, y + 408), "#0b1f35", 14, "#1e6091")
    draw.rectangle((x + 36, y + 390, x + 276, y + 398), fill="#1e293b")
    draw.rectangle((x + 36, y + 390, x + 232, y + 398), fill=COLORS["blue"])
    draw_text(draw, (x + 288, y + 382), "86", FONT["body_bold"], COLORS["text"])


def draw_process(draw: ImageDraw.ImageDraw) -> None:
    steps = [
        ("1", "选择场景", "面试 / 点餐 / 会议"),
        ("2", "输入回答", "文本或音频上传"),
        ("3", "角色回复", "AI 场景追问"),
        ("4", "纠错评分", "语法、表达、五维分"),
        ("5", "导出总结", "Markdown / HTML"),
    ]
    start_x, y = 96, 760
    for index, (num, title, desc) in enumerate(steps):
        x = start_x + index * 164
        draw.ellipse((x, y, x + 54, y + 54), fill=COLORS["blue"] if index < 3 else COLORS["green"])
        tw, th = text_size(draw, num, FONT["h3"])
        draw_text(draw, (x + 27 - tw // 2, y + 27 - th // 2 - 2), num, FONT["h3"], "#06121f")
        draw_text(draw, (x, y + 72), title, FONT["body_bold"], COLORS["text"])
        draw_wrapped(draw, (x, y + 102), desc, FONT["tiny"], 120, COLORS["subtle"], 4)
        if index < len(steps) - 1:
            draw.line((x + 62, y + 27, x + 148, y + 27), fill=COLORS["stroke_strong"], width=3)


def render() -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg"])
    draw_gradient_background(img)
    draw = ImageDraw.Draw(img)

    rounded(draw, (48, 48, 292, 952), COLORS["sidebar"], 26, COLORS["stroke"])
    draw_text(draw, (84, 92), "AI英语教练", FONT["h2"])
    draw_wrapped(draw, (84, 142), "场景化英语口语练习工具", FONT["small"], 160, COLORS["subtle"], 6)
    for y, label, value in [
        (224, "当前模式", "本地演示模式"),
        (314, "练习场景", "会议 / 面试 / 点餐"),
        (404, "核心反馈", "纠错 + 评分 + 总结"),
    ]:
        draw_text(draw, (84, y), label, FONT["small"], COLORS["subtle"])
        draw_text(draw, (84, y + 32), value, FONT["body_bold"], COLORS["text"])
    rounded(draw, (84, 558, 256, 648), "#13223a", 18, COLORS["stroke"])
    draw_text(draw, (108, 584), "比赛展示可用", FONT["body_bold"], COLORS["blue"])
    draw_text(draw, (108, 620), "PNG 展示图", FONT["small"], COLORS["muted"])

    draw_text(draw, (356, 72), "AI 英语口语陪练", FONT["title"])
    draw_wrapped(
        draw,
        (358, 148),
        "一个面向比赛展示的英语口语训练系统：支持场景对话、规则纠错、五维评分、课后总结、历史保存和报告导出。",
        FONT["body"],
        780,
        COLORS["muted"],
        8,
    )
    draw_chip(draw, (358, 218), "Streamlit 本地运行", COLORS["green"])
    draw_chip(draw, (548, 218), "无 API Key 可完整演示", COLORS["blue"])
    draw_chip(draw, (770, 218), "Figma / Canva 展示材料", COLORS["purple"])

    cards = [
        ((356, 304, 588, 524), "视觉设计", "深色界面", "深色科技风、统一色彩规范、评分卡高对比，适合截图展示。", COLORS["blue"]),
        ((612, 304, 844, 524), "交互设计", "5步流程", "选择场景、提交练习、查看反馈、生成总结、导出报告。", COLORS["green"]),
        ((356, 548, 588, 704), "信息架构", "5个标签", "练习、历史、统计、报告、设置分区清楚，降低页面混乱。", COLORS["orange"]),
        ((612, 548, 844, 704), "双模式", "API/本地", "有密钥时调用 API，无密钥时使用本地模板和规则。", COLORS["red"]),
    ]
    for card in cards:
        draw_metric_card(draw, *card)

    draw_process(draw)
    draw_mockup(draw)

    rounded(draw, (1228, 304, 1370, 790), COLORS["panel"], 22, COLORS["stroke"])
    draw_text(draw, (1246, 336), "核心指标", FONT["h3"])
    indicators = [("3", "练习场景"), ("5", "评分维度"), ("JSON", "历史保存"), ("MD", "总结导出")]
    y = 394
    for value, label in indicators:
        draw_text(draw, (1246, y), value, FONT["h1"], COLORS["blue"])
        draw_text(draw, (1248, y + 52), label, FONT["small"], COLORS["muted"])
        y += 104

    draw_text(draw, (356, 920), "本图由 scripts/render_canva_showcase.py 生成，可直接放入比赛项目说明或展示 PPT。", FONT["small"], COLORS["subtle"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT)
    print(f"saved {OUTPUT}")


if __name__ == "__main__":
    render()
