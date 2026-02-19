"""
AI Analysis через Groq API.
Анализ отзывов: метрики, риски, плюсы/минусы, consistency.
"""
import json
import re

from backend.config import GROQ_API_KEY

SYSTEM_PROMPT = """You are an impartial travel review analyst.
Your task is to analyze reviews from multiple platforms.
You must:
- avoid marketing language
- avoid copying review text
- focus on practical implications for travelers
- detect risks, contradictions, and hidden constraints
- base conclusions only on provided reviews
If data is insufficient, explicitly say so."""

GROQ_MODEL = "llama-3.1-8b-instant"


def _build_analysis_prompt(reviews_text: str, trip_type: str = "leisure") -> str:
    return f"""Analyze these hotel reviews. Trip type: {trip_type}.

Reviews:
---
{reviews_text}
---

Respond with ONLY a valid JSON object (no markdown, no explanation), with these keys:
- cleanliness: number 0-10
- noise: number 0-10 (10 = quiet)
- comfort: number 0-10
- location: number 0-10
- staff: number 0-10
- risk_weight: number 0-1 (0=no risk, 1=high risk)
- red_flags: array of strings (e.g. ["noise", "dirty"] or [])
- pros: array of short strings (max 5)
- cons: array of short strings (max 5)
- consistency_score: number 0-1 (1=reviews agree)
- verdict: one short sentence in Russian for the traveler
If data is insufficient, use null for numbers and [] for arrays, and set verdict to "Недостаточно отзывов для вывода."
"""


def _parse_ai_response(text: str) -> dict:
    """Извлечь JSON из ответа модели (возможен код-блок)."""
    text = text.strip()
    # Убрать markdown code block если есть
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        text = m.group(1).strip()
    # Найти первый { и последний }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


def analyze_reviews(
    reviews: list[dict],
    trip_type: str = "leisure",
) -> dict:
    """
    Анализ списка отзывов через Groq.
    Возвращает dict с ключами: cleanliness, noise, comfort, location, staff,
    risk_weight, red_flags, pros, cons, consistency_score, verdict.
    """
    if not GROQ_API_KEY:
        return _fallback_analysis(reviews)

    reviews_text = "\n".join(
        (r.get("text") or "").strip() for r in reviews if r.get("text")
    )
    if not reviews_text.strip():
        return _fallback_analysis(reviews)

    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_analysis_prompt(reviews_text, trip_type)},
            ],
            temperature=0.2,
            max_tokens=800,
        )
        content = (response.choices[0].message.content or "").strip()
        if not content:
            return _fallback_analysis(reviews)
        data = _parse_ai_response(content)
        return _normalize_analysis(data)
    except Exception:
        return _fallback_analysis(reviews)


def _normalize_analysis(data: dict) -> dict:
    """Привести типы и значения к ожидаемому формату."""
    def num(v, default=0, low=0, high=10):
        if v is None: return default
        try:
            x = float(v)
            return max(low, min(high, x))
        except (TypeError, ValueError):
            return default

    def arr(v):
        if isinstance(v, list):
            return [str(x) for x in v[:10]]
        return []

    return {
        "cleanliness": num(data.get("cleanliness"), 7, 0, 10),
        "noise": num(data.get("noise"), 7, 0, 10),
        "comfort": num(data.get("comfort"), 7, 0, 10),
        "location": num(data.get("location"), 7, 0, 10),
        "staff": num(data.get("staff"), 7, 0, 10),
        "risk_weight": num(data.get("risk_weight"), 0.1, 0, 1),
        "red_flags": arr(data.get("red_flags")),
        "pros": arr(data.get("pros")),
        "cons": arr(data.get("cons")),
        "consistency_score": num(data.get("consistency_score"), 0.7, 0, 1),
        "verdict": str(data.get("verdict") or "Недостаточно отзывов для вывода.")[:500],
    }


def _fallback_analysis(reviews: list[dict]) -> dict:
    """Ответ без API: базовые значения по отзывам."""
    texts = " ".join((r.get("text") or "").lower() for r in reviews)
    red_flags = []
    for word in ["unsafe", "dirty", "scam", "broken", "noise all night"]:
        if word in texts:
            red_flags.append(word)
    risk = min(1.0, 0.1 + 0.15 * len(red_flags))
    return {
        "cleanliness": 7.0,
        "noise": 7.0,
        "comfort": 7.0,
        "location": 7.0,
        "staff": 7.0,
        "risk_weight": risk,
        "red_flags": red_flags,
        "pros": [],
        "cons": [],
        "consistency_score": 0.7,
        "verdict": "Недостаточно отзывов для вывода." if not texts.strip() else "Проверьте отзывы вручную.",
    }
