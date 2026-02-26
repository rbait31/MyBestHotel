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


def _profile_context(profile) -> str:
    """Собрать контекст профиля для промпта AI."""
    if not profile:
        return "Trip type: leisure."
    parts = [f"Trip type: {getattr(profile, 'trip_type', None) or 'leisure'}."]
    prefs = []
    if getattr(profile, "preference_center", 3) >= 4:
        prefs.append("city center proximity (very important)")
    if getattr(profile, "preference_cleanliness", 3) >= 4:
        prefs.append("cleanliness (very important)")
    if getattr(profile, "preference_quiet", 3) >= 4:
        prefs.append("quietness (very important)")
    if getattr(profile, "preference_wifi", 3) >= 4:
        prefs.append("Wi-Fi quality (very important)")
    if getattr(profile, "preference_nature", 3) >= 4:
        prefs.append("nature/parks proximity (very important)")
    if getattr(profile, "preference_breakfast", 3) >= 4:
        prefs.append("breakfast inclusion (very important)")
    if prefs:
        parts.append(f"User priorities: {', '.join(prefs)}.")
    if getattr(profile, "with_car", False):
        parts.append("Traveler has a car — parking/access matters.")
    if getattr(profile, "with_pets", False):
        parts.append("Traveler has pets — pet-friendly info matters.")
    group = []
    if getattr(profile, "solo", False):
        group.append("solo")
    if getattr(profile, "couple", False):
        group.append("couple")
    if getattr(profile, "family", False):
        group.append("family")
    if getattr(profile, "group", False):
        group.append("group")
    if group:
        parts.append(f"Traveler type: {', '.join(group)}.")
    red_avoid = []
    rf_map = {
        "red_flag_safety": "safety/security",
        "red_flag_dirt": "dirt/cleanliness issues",
        "red_flag_noise_night": "night noise",
        "red_flag_weak_wifi": "weak Wi-Fi",
        "red_flag_no_car_access": "poor access without car",
        "red_flag_insects": "insects in room",
        "red_flag_scam": "scam/hidden charges",
    }
    for key, label in rf_map.items():
        if getattr(profile, key, False):
            red_avoid.append(label)
    if red_avoid:
        parts.append(f"CRITICAL: traveler wants to AVOID: {', '.join(red_avoid)}. Detect these in red_flags if present in reviews.")
    return " ".join(parts)


def _build_analysis_prompt(reviews_text: str, trip_type: str = "leisure", profile=None) -> str:
    ctx = _profile_context(profile) if profile else f"Trip type: {trip_type}."
    return f"""Analyze these hotel reviews. {ctx}

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
- red_flags: array of strings — ONLY if reviews explicitly mention the issue (e.g. ["dirty"] if reviews say dirty). Do NOT add "noise" if reviews say "quiet at night".
- pros: array of short strings (max 5)
- cons: array of short strings (max 5)
IMPORTANT: red_flags and pros must be consistent. If reviews say "quiet at night", do NOT add "noise" to red_flags.
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
    profile=None,
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
                {"role": "user", "content": _build_analysis_prompt(reviews_text, trip_type, profile)},
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


# Противоречия: ключевые слова для noise в red_flags vs тишина в pros
_NOISE_RED_FLAG_TERMS = ("noise", "noisy", "noise all night", "night noise", "loud")
_QUIET_PRO_TERMS = ("quiet", "peaceful", "silent", "calm", "тихий", "спокойн")


def _resolve_contradictions(red_flags: list[str], pros: list[str], cons: list[str]) -> tuple[list[str], list[str], list[str]]:
    """
    Устранить взаимоисключающие утверждения: noise в red_flags и quiet в pros.
    Если в pros явно указана тишина — убираем noise из red_flags.
    """
    red_out = list(red_flags)
    pros_out = list(pros)
    cons_out = list(cons)

    pros_text = " ".join(p.lower() for p in pros_out)
    has_quiet_in_pros = any(q in pros_text for q in _QUIET_PRO_TERMS)

    if has_quiet_in_pros:
        red_out = [r for r in red_out if not any(n in r.lower() for n in _NOISE_RED_FLAG_TERMS)]

    red_text = " ".join(r.lower() for r in red_out)
    has_noise_in_red = any(n in red_text for n in _NOISE_RED_FLAG_TERMS)

    if has_noise_in_red:
        pros_out = [p for p in pros_out if not any(q in p.lower() for q in _QUIET_PRO_TERMS)]

    return red_out, pros_out, cons_out


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

    red_flags = arr(data.get("red_flags"))
    pros = arr(data.get("pros"))
    cons = arr(data.get("cons"))
    red_flags, pros, cons = _resolve_contradictions(red_flags, pros, cons)

    return {
        "cleanliness": num(data.get("cleanliness"), 7, 0, 10),
        "noise": num(data.get("noise"), 7, 0, 10),
        "comfort": num(data.get("comfort"), 7, 0, 10),
        "location": num(data.get("location"), 7, 0, 10),
        "staff": num(data.get("staff"), 7, 0, 10),
        "risk_weight": num(data.get("risk_weight"), 0.1, 0, 1),
        "red_flags": red_flags,
        "pros": pros,
        "cons": cons,
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
