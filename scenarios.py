"""Scenario definitions for AI English speaking practice."""

SCENARIOS = {
    "interview": {
        "label": "Interview",
        "cn_label": "面试 Interview",
        "ai_role": "You are an interviewer for an English-speaking technology company.",
        "user_goal": "Practice answering interview questions clearly and professionally.",
        "default_difficulty": "中等",
        "common_questions": [
            "Could you introduce yourself briefly?",
            "What was your most important project experience?",
            "How do you handle pressure or conflict at work?",
            "Why are you interested in this position?",
        ],
        "recommended_expressions": [
            "In my previous project, I was responsible for...",
            "One challenge I faced was...",
            "I solved this problem by...",
            "I believe my experience matches this role because...",
        ],
        "fallback_replies": [
            "Could you tell me more about your previous project experience?",
            "That sounds interesting. What was the biggest challenge in that project?",
            "How did you measure whether your work was successful?",
            "Could you give a specific example to support your answer?",
        ],
    },
    "restaurant": {
        "label": "Restaurant Ordering",
        "cn_label": "点餐 Restaurant Ordering",
        "ai_role": "You are a friendly waiter in an English-speaking restaurant.",
        "user_goal": "Practice ordering food, asking questions, and responding politely.",
        "default_difficulty": "简单",
        "common_questions": [
            "Are you ready to order?",
            "Would you like anything to drink?",
            "Do you have any food allergies?",
            "Would you like dessert after the meal?",
        ],
        "recommended_expressions": [
            "I would like to order...",
            "Could you recommend something popular?",
            "May I have the bill, please?",
            "Does this dish contain any nuts?",
        ],
        "fallback_replies": [
            "Sure. Would you like anything to drink with your meal?",
            "Of course. Would you prefer chicken, beef, or a vegetarian option?",
            "No problem. Would you like the sauce on the side?",
            "Great choice. Would you like anything else?",
        ],
    },
    "meeting": {
        "label": "Business Meeting",
        "cn_label": "会议 Business Meeting",
        "ai_role": "You are a business colleague discussing a proposal in a meeting.",
        "user_goal": "Practice explaining opinions, risks, plans, and decisions in English.",
        "default_difficulty": "困难",
        "common_questions": [
            "What is your opinion about this proposal?",
            "What risks should we consider?",
            "How should we divide the work?",
            "What is the next action item?",
        ],
        "recommended_expressions": [
            "From my perspective, the main issue is...",
            "I suggest that we prioritize...",
            "The potential risk is...",
            "The next step should be...",
        ],
        "fallback_replies": [
            "That is a useful point. Could you explain the main risk of this proposal?",
            "I understand your position. What action should we take next?",
            "Could you clarify the expected timeline for this plan?",
            "How would you convince the team to support this proposal?",
        ],
    },
}

DIFFICULTIES = ["简单", "中等", "困难"]


def list_scenarios():
    """Return all scenario keys in display order."""
    return list(SCENARIOS.keys())


def get_scenario(key):
    """Return a scenario configuration by key."""
    return SCENARIOS[key]


def scenario_label(key):
    """Return the Chinese and English display label for a scenario."""
    return SCENARIOS[key]["cn_label"]
