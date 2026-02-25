"""
Scoring Engine — формула итогового score.
"""
from typing import Any


def _get_pref(profile, key: str, default: int = 3) -> int:
    v = getattr(profile, key, default) if profile else default
    return max(0, min(5, int(v) if v is not None else default))


def compute_final_score(
    cleanliness: float,
    location: float,
    comfort: float,
    staff: float,
    noise: float,
    risk_weight: float,
    value_score: float,
    trip_type: str = "leisure",
    profile=None,
) -> float:
    """
    Итоговый score: веса по предпочтениям пользователя (0-5).
    noise: 0-10 (10=quiet). Добавлен как 5-я метрика качества.
    """
    p_clean = _get_pref(profile, "preference_cleanliness")
    p_center = _get_pref(profile, "preference_center")
    p_nature = _get_pref(profile, "preference_nature")
    p_quiet = _get_pref(profile, "preference_quiet")
    p_wifi = _get_pref(profile, "preference_wifi")

    # Веса из предпочтений (нормализация: сумма quality_weights + value + risk = 1)
    w_clean = 0.12 + 0.06 * (p_clean / 5)
    w_location = 0.12 + 0.06 * ((p_center + p_nature) / 10)
    w_comfort = 0.12 + 0.06 * (p_wifi / 5)
    w_staff = 0.12
    w_noise = 0.12 + 0.06 * (p_quiet / 5)
    w_value = 0.2
    w_risk = 0.1
    total_q = w_clean + w_location + w_comfort + w_staff + w_noise
    scale = 0.7 / total_q
    w_clean *= scale
    w_location *= scale
    w_comfort *= scale
    w_staff *= scale
    w_noise *= scale

    if trip_type == "business":
        w_location *= 1.2
        w_comfort *= 0.9
    family = profile and (getattr(profile, "family", False) or getattr(profile, "group", False))
    if family:
        w_clean *= 1.2
        w_comfort *= 1.1
        w_location *= 0.9

    score = (
        cleanliness * w_clean
        + location * w_location
        + comfort * w_comfort
        + staff * w_staff
        + noise * w_noise
        + value_score * w_value
        - risk_weight * 10 * w_risk
    )
    return round(max(0, min(10, score)), 1)


def compute_value_score(price_per_night: float, quality_score: float, avg_price: float) -> float:
    """
    Value for money: чем ниже цена при том же качестве — тем выше.
    Упрощённо: quality / (price / avg_price), нормализовано в 0-10.
    """
    if not avg_price or avg_price <= 0:
        return 7.0
    ratio = price_per_night / avg_price
    # ratio < 1 → дешевле среднего → выше value
    value = quality_score / max(0.3, ratio)
    return round(max(0, min(10, value)), 1)


# Маппинг red_flags отеля на ключи профиля пользователя
RED_FLAG_TO_PROFILE = {
    "safety": "red_flag_safety",
    "unsafe": "red_flag_safety",
    "security": "red_flag_safety",
    "dirty": "red_flag_dirt",
    "dirt": "red_flag_dirt",
    "cleanliness": "red_flag_dirt",
    "noise": "red_flag_noise_night",
    "noisy": "red_flag_noise_night",
    "wifi": "red_flag_weak_wifi",
    "wi-fi": "red_flag_weak_wifi",
    "internet": "red_flag_weak_wifi",
    "access": "red_flag_no_car_access",
    "car": "red_flag_no_car_access",
    "parking": "red_flag_no_car_access",
    "insects": "red_flag_insects",
    "bugs": "red_flag_insects",
    "scam": "red_flag_scam",
    "hidden": "red_flag_scam",
    "charges": "red_flag_scam",
}


def score_hotel(
    ai_metrics: dict[str, Any],
    price_per_night: float | None,
    avg_price: float,
    trip_type: str = "leisure",
    profile=None,
) -> dict[str, Any]:
    """
    По метрикам AI и цене считает quality_score и final_score.
    Учитывает предпочтения профиля и штрафует за совпадение red_flags.
    """
    c = ai_metrics.get("cleanliness", 7)
    loc = ai_metrics.get("location", 7)
    comfort = ai_metrics.get("comfort", 7)
    staff = ai_metrics.get("staff", 7)
    noise = ai_metrics.get("noise", 7)
    risk = ai_metrics.get("risk_weight", 0.1)
    hotel_red_flags = [str(f).lower() for f in ai_metrics.get("red_flags", [])]

    # Штраф: если пользователь отметил red_flag_X и отель имеет соответствующий флаг
    red_penalty = 0
    if profile and hotel_red_flags:
        for hf in hotel_red_flags:
            for keyword, pf_key in RED_FLAG_TO_PROFILE.items():
                if keyword in hf and getattr(profile, pf_key, False):
                    red_penalty += 1.5
                    break
    risk = min(1.0, risk + 0.15 * red_penalty)

    quality_score = round((c + loc + comfort + staff + noise) / 5, 1)
    price = price_per_night if price_per_night is not None else 0
    value_for_money = compute_value_score(price, quality_score, avg_price) if avg_price else 7.0

    final_score = compute_final_score(
        cleanliness=c,
        location=loc,
        comfort=comfort,
        staff=staff,
        noise=noise,
        risk_weight=risk,
        value_score=value_for_money,
        trip_type=trip_type,
        profile=profile,
    )

    return {
        **ai_metrics,
        "risk_weight": risk,
        "quality_score": quality_score,
        "value_for_money": value_for_money,
        "final_score": final_score,
    }
