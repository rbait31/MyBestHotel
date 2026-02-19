"""
Scoring Engine — формула итогового score.
"""
from typing import Any


def compute_final_score(
    cleanliness: float,
    location: float,
    comfort: float,
    staff: float,
    risk_weight: float,
    value_score: float,
    trip_type: str = "leisure",
) -> float:
    """
    Итоговый score по формуле.
    final_score = cleanliness*0.3 + location*0.2 + value*0.2 + comfort*0.2 - risk*0.1
    Для business можно усилить location, для leisure — comfort.
    """
    # Базовые веса (ARCHITECTURE)
    w_clean = 0.3
    w_location = 0.2
    w_value = 0.2
    w_comfort = 0.2
    w_risk = 0.1

    if trip_type == "business":
        w_location = 0.25
        w_comfort = 0.15
    elif trip_type == "family":
        w_clean = 0.35
        w_comfort = 0.25
        w_location = 0.15

    score = (
        cleanliness * w_clean
        + location * w_location
        + value_score * w_value
        + comfort * w_comfort
        - risk_weight * 10 * w_risk  # risk_weight 0-1 → вклад до 1 балла
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


def score_hotel(
    ai_metrics: dict[str, Any],
    price_per_night: float | None,
    avg_price: float,
    trip_type: str = "leisure",
) -> dict[str, Any]:
    """
    По метрикам AI и цене считает quality_score (из метрик) и final_score.
    Возвращает ai_metrics с добавленными quality_score, value_for_money, final_score.
    """
    c = ai_metrics.get("cleanliness", 7)
    loc = ai_metrics.get("location", 7)
    comfort = ai_metrics.get("comfort", 7)
    staff = ai_metrics.get("staff", 7)
    risk = ai_metrics.get("risk_weight", 0.1)

    quality_score = round((c + loc + comfort + staff) / 4, 1)
    price = price_per_night if price_per_night is not None else 0
    value_for_money = compute_value_score(price, quality_score, avg_price) if avg_price else 7.0

    final_score = compute_final_score(
        cleanliness=c,
        location=loc,
        comfort=comfort,
        staff=staff,
        risk_weight=risk,
        value_score=value_for_money,
        trip_type=trip_type,
    )

    return {
        **ai_metrics,
        "quality_score": quality_score,
        "value_for_money": value_for_money,
        "final_score": final_score,
    }
