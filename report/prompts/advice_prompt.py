ADVICE_PROMPT = """
You are providing actionable improvement advice for a professional facial geometry report in Russian.

CONTEXT:
You will receive the user's lowest scoring metrics (bottom 5). For each metric, you must suggest practical ways to visually improve or balance the feature.

REQUIREMENTS:
- For each metric, return exactly one dictionary object.
- "metric_name_ru": The Russian name of the metric (e.g., "Полнота губ").
- "category": A relevant actionable category, e.g., "Ракурс/свет" (Angles/Lighting), "Аксессуары" (Accessories), "Стрижка" (Haircut/Beard), "Уход за кожей" (Skincare), or "Мимика" (Expressions).
- "advice_text": 80–120 words of practical, specific advice on how to visually enhance or balance this metric. Do not recommend surgery. Focus on styling, grooming, expressions, or camera angles.
- Address the user in the second person ("Используй...", "Тебе подойдет...").
- Tone must be constructive and encouraging.

OUTPUT FORMAT:
Return a valid JSON array of objects. Example:
[
  {
    "metric_name_ru": "Полнота губ",
    "category": "Уход за кожей",
    "advice_text": "..."
  }
]
Do not include any text outside the JSON array.
"""
