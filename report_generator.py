"""Lesson summary generation."""

from __future__ import annotations

import json
from collections import Counter
from typing import Dict, List

from api_client import api_mode_available, create_openai_client, current_openai_model


def _collect_user_turns(history: List[Dict]) -> List[str]:
    return [item.get("user", "") for item in history if item.get("user")]


def _try_openai_summary(history: List[Dict], scenario: Dict, difficulty: str, latest_score: Dict | None) -> str | None:
    if not api_mode_available():
        return None
    try:
        client = create_openai_client()
        model = current_openai_model()
        payload = {
            "scenario": scenario["label"],
            "difficulty": difficulty,
            "history": history,
            "latest_score": latest_score,
            "required_sections": [
                "场景",
                "难度",
                "对话轮数",
                "综合评分",
                "优势亮点",
                "主要问题",
                "高频错误",
                "推荐表达",
                "下一次练习建议",
            ],
        }
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an English speaking course report assistant. Write Markdown in Chinese."},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            temperature=0.4,
        )
        return response.choices[0].message.content
    except Exception:
        return None


def generate_lesson_summary(
    history: List[Dict],
    scenario: Dict,
    difficulty: str,
    latest_feedback: Dict | None = None,
    latest_score: Dict | None = None,
) -> str:
    """Generate a Markdown lesson summary."""
    api_summary = _try_openai_summary(history, scenario, difficulty, latest_score)
    if api_summary:
        return api_summary

    user_turns = _collect_user_turns(history)
    round_count = len(user_turns)
    feedback = latest_feedback or {}
    score = latest_score or {}
    total_score = score.get("total_score", 0)

    issues = feedback.get("issue_explanation") or []
    words = []
    for turn in user_turns:
        words.extend([w.lower().strip(".,!?") for w in turn.split() if len(w) > 3])
    common_words = [word for word, _ in Counter(words).most_common(5)]

    advantages = [
        "能够主动完成英文输入并参与场景对话。",
        "回答内容与当前练习场景基本相关。",
        "已经具备使用完整句表达想法的基础。",
    ]
    if round_count >= 3:
        advantages.append("能够进行多轮对话，说明持续表达能力较好。")

    problems = issues if issues else ["本地规则未发现明显语法错误，但仍建议增加例子和连接词。"]

    expressions = scenario.get("recommended_expressions", [])[:4]
    common_error_text = "\n".join(f"- {item}" for item in problems)
    expression_text = "\n".join(f"- {item}" for item in expressions)
    advantage_text = "\n".join(f"- {item}" for item in advantages)
    keywords = ", ".join(common_words) if common_words else "暂无明显高频词"

    return f"""# AI 英语口语陪练课后总结

## 场景
- 场景：{scenario['cn_label']}

## 难度
- 难度：{difficulty}
- AI 角色：{scenario['ai_role']}

## 对话轮数
本次共完成 {round_count} 轮用户输入。系统根据用户回答进行了角色扮演回复、语法纠错和五维评分。

## 综合评分
本次综合评分：**{total_score}/100**。

## 优势亮点
{advantage_text}

## 主要问题
{common_error_text}

## 高频错误
- 高频词或主题词：{keywords}
- 主要错误类型：语法搭配、句子完整度、表达自然度。
- 建议每次回答至少包含观点、原因和一个例子。

## 推荐表达
{expression_text}

## 下一次练习建议
- 先使用推荐表达组织回答，再根据 AI 追问补充细节。
- 尽量避免只回答一个短句，建议使用 2 到 4 个句子。
- 完成文本练习后，可以上传音频进行转写流程演示。

该评分用于课程设计 MVP 演示，其中 Pronunciation 发音分数在未接入真实发音评测服务时为模拟结果。
"""
