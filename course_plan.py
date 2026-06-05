"""Course-style lesson planning helpers."""

from __future__ import annotations

from typing import Dict, List


COURSE_STEPS = {
    "interview": [
        {
            "title": "自我介绍",
            "goal": "用 2-3 句话介绍背景、专业和目标岗位。",
            "prompt": "Please introduce yourself briefly.",
            "target_expression": "I am currently studying... and I am interested in...",
            "evaluation_focus": "背景是否清楚，目标是否具体，句子是否完整。",
        },
        {
            "title": "项目经历",
            "goal": "说明项目背景、个人职责、遇到的问题和结果。",
            "prompt": "Could you describe one previous project experience?",
            "target_expression": "In this project, I was responsible for...",
            "evaluation_focus": "是否讲清项目背景、个人贡献和结果。",
        },
        {
            "title": "职责说明",
            "goal": "说明自己在项目或岗位中的职责边界。",
            "prompt": "What exactly were you responsible for in that project?",
            "target_expression": "My main responsibility was to...",
            "evaluation_focus": "职责是否具体，是否避免只说团队成果。",
        },
        {
            "title": "困难挑战",
            "goal": "用 STAR 思路解释挑战、行动和结果。",
            "prompt": "What was the biggest challenge and how did you solve it?",
            "target_expression": "The main challenge was... I solved it by...",
            "evaluation_focus": "是否包含挑战、行动、结果和反思。",
        },
        {
            "title": "总结收尾",
            "goal": "总结个人优势并说明为什么适合岗位。",
            "prompt": "Why do you think you are a good fit for this position?",
            "target_expression": "I believe I am a good fit because...",
            "evaluation_focus": "是否能用职业化表达完成收尾。",
        },
    ],
    "restaurant": [
        {
            "title": "入店问候",
            "goal": "礼貌说明人数、座位偏好或是否预订。",
            "prompt": "Good evening. Do you have a reservation?",
            "target_expression": "We have a reservation under the name...",
            "evaluation_focus": "礼貌程度、基本信息和回应是否自然。",
        },
        {
            "title": "选择主餐",
            "goal": "清楚表达想要的主食。",
            "prompt": "Are you ready to order?",
            "target_expression": "I would like to order...",
            "evaluation_focus": "主餐表达是否明确，量词和菜名是否自然。",
        },
        {
            "title": "询问饮品",
            "goal": "选择饮品或礼貌拒绝饮品。",
            "prompt": "Would you like anything to drink with that?",
            "target_expression": "May I have... / Just water, please.",
            "evaluation_focus": "请求表达是否礼貌，饮品选择是否清楚。",
        },
        {
            "title": "处理偏好",
            "goal": "说明过敏、辣度、酱料或其他偏好。",
            "prompt": "Do you have any allergies or special preferences?",
            "target_expression": "Could you make it less spicy?",
            "evaluation_focus": "偏好是否具体，请求是否得体。",
        },
        {
            "title": "确认订单",
            "goal": "确认订单内容并完成点餐。",
            "prompt": "Let me confirm your order. Is everything correct?",
            "target_expression": "Yes, that is correct. Thank you.",
            "evaluation_focus": "确认表达是否准确，结束语是否自然。",
        },
    ],
    "meeting": [
        {
            "title": "提出观点",
            "goal": "明确表达对提案的支持、保留或反对。",
            "prompt": "What is your opinion about this proposal?",
            "target_expression": "From my perspective, the main issue is...",
            "evaluation_focus": "观点是否明确，语气是否适合会议。",
        },
        {
            "title": "解释原因",
            "goal": "解释支持该观点的原因。",
            "prompt": "Could you explain the reason behind your opinion?",
            "target_expression": "The reason is that...",
            "evaluation_focus": "原因是否充分，逻辑连接是否清晰。",
        },
        {
            "title": "回应质疑",
            "goal": "回应同事的担忧或反对意见。",
            "prompt": "Some teammates are worried about the risk. How would you respond?",
            "target_expression": "I understand the concern, but...",
            "evaluation_focus": "是否先回应对方，再提出自己的理由。",
        },
        {
            "title": "补充方案",
            "goal": "提出下一步行动、负责人或时间安排。",
            "prompt": "What action plan would you suggest next?",
            "target_expression": "The next step should be...",
            "evaluation_focus": "方案是否可执行，是否包含下一步。",
        },
        {
            "title": "总结结论",
            "goal": "总结会议结论并确认后续安排。",
            "prompt": "Can you summarize our decision?",
            "target_expression": "To summarize, we agreed that...",
            "evaluation_focus": "总结是否清楚，是否覆盖结论和行动。",
        },
    ],
}


def get_course_steps(scenario_key: str) -> List[Dict]:
    """Return course steps for one scenario."""
    return COURSE_STEPS[scenario_key]


def current_step_index(history_count: int, total_steps: int = 5) -> int:
    """Return the current lesson step index based on completed turns."""
    if total_steps <= 0:
        return 0
    return min(history_count, total_steps - 1)


def progress_percent(history_count: int, total_steps: int = 5) -> int:
    """Return course progress as an integer percentage."""
    if total_steps <= 0:
        return 0
    return min(100, round((history_count / total_steps) * 100))


def lesson_status(history_count: int, scenario_key: str) -> Dict:
    """Return current step and course completion metadata."""
    steps = get_course_steps(scenario_key)
    index = current_step_index(history_count, len(steps))
    return {
        "steps": steps,
        "current_step": steps[index],
        "current_index": index,
        "progress": progress_percent(history_count, len(steps)),
        "completed": history_count >= len(steps),
    }
