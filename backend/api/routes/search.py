"""
POST /api/search — поиск отелей по городу, датам, профилю.
"""
from datetime import datetime

from fastapi import APIRouter, HTTPException

from backend.api.schemas import SearchRequest
from backend.services.review_loader import get_hotels_by_location, get_reviews_for_hotel
from backend.services.price_engine import calculate_price_for_stay, calculate_price_per_night
from backend.services.ai_analysis import analyze_reviews
from backend.services.scoring import score_hotel

router = APIRouter(prefix="/api", tags=["search"])


def _parse_dates(check_in: str, check_out: str) -> tuple[datetime, datetime]:
    try:
        ci = datetime.strptime(check_in, "%Y-%m-%d")
        co = datetime.strptime(check_out, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Даты в формате YYYY-MM-DD")
    if co <= ci:
        raise HTTPException(status_code=400, detail="check_out должен быть позже check_in")
    return ci, co


@router.post("/search")
def search(body: SearchRequest):
    """
    Поиск отелей: город/страна, даты, профиль.
    Возвращает до 4 отелей с ценами и AI-анализом (метрики, риски, pros/cons, verdict).
    """
    if not body.city.strip() and not body.country.strip():
        raise HTTPException(status_code=400, detail="Укажите city или country")

    check_in_dt, check_out_dt = _parse_dates(body.check_in, body.check_out)
    profile = body.profile
    trip_type = (profile.trip_type if profile else None) or "leisure"
    budget_min = profile.budget_min if profile else None
    budget_max = profile.budget_max if profile else None

    hotels = get_hotels_by_location(
        city=body.city.strip() or None,
        country=body.country.strip() or None,
    )
    if not hotels:
        return {"hotels": [], "count": 0}

    # Цены за период и фильтр по бюджету
    with_prices = []
    for h in hotels:
        price_per_night, _ = calculate_price_for_stay(
            base_price=h["base_price"],
            rating=h.get("rating", 4.0),
            check_in=check_in_dt,
            check_out=check_out_dt,
        )
        if budget_min is not None and budget_min > 0 and price_per_night < budget_min:
            continue
        if budget_max is not None and budget_max > 0 and price_per_night > budget_max:
            continue
        with_prices.append({**h, "price_per_night": price_per_night})

    # До 4 отелей (по возрастанию цены)
    with_prices.sort(key=lambda x: x["price_per_night"])
    selected = with_prices[:4]

    avg_price = sum(h["price_per_night"] for h in selected) / len(selected) if selected else 0

    result = []
    for h in selected:
        reviews = get_reviews_for_hotel(h["id"])
        ai_metrics = analyze_reviews(reviews, trip_type=trip_type)
        scored = score_hotel(
            ai_metrics,
            price_per_night=h["price_per_night"],
            avg_price=avg_price,
            trip_type=trip_type,
        )
        result.append({
            "id": h["id"],
            "name": h["name"],
            "city": h.get("city"),
            "country": h.get("country"),
            "district": h.get("district"),
            "rating": h.get("rating"),
            "location_score": h.get("location_score"),
            "price_per_night": h["price_per_night"],
            "quality_score": scored.get("quality_score"),
            "value_for_money": scored.get("value_for_money"),
            "final_score": scored.get("final_score"),
            "red_flags": scored.get("red_flags", []),
            "risks": {"risk_weight": scored.get("risk_weight")},
            "pros": scored.get("pros", []),
            "cons": scored.get("cons", []),
            "consistency_score": scored.get("consistency_score"),
            "verdict": scored.get("verdict"),
        })

    return {"hotels": result, "count": len(result)}
