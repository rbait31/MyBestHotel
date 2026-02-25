"""
POST /api/analyze — анализ одного отеля по ID.
POST /api/check-hotel — оценка отеля по названию для профиля пользователя.
"""
from datetime import datetime

from fastapi import APIRouter, HTTPException

from backend.api.schemas import AnalyzeRequest, CheckHotelRequest
from backend.services.review_loader import get_hotel_by_id, get_hotel_by_name, get_reviews_for_hotel
from backend.services.price_engine import calculate_price_for_stay, calculate_price_per_night
from backend.services.ai_analysis import analyze_reviews
from backend.services.scoring import score_hotel

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze")
def analyze_one(body: AnalyzeRequest):
    """
    Анализ одного отеля по ID. Опционально: даты и профиль для цены и персонализации.
    """
    hotel = get_hotel_by_id(body.hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Отель не найден")

    trip_type = "leisure"
    if body.profile:
        trip_type = getattr(body.profile, "trip_type", None) or "leisure"

    price_per_night = None
    check_in_dt = None
    if body.check_in:
        try:
            check_in_dt = datetime.strptime(body.check_in, "%Y-%m-%d")
            price_per_night = calculate_price_per_night(
                base_price=hotel["base_price"],
                rating=hotel.get("rating", 4.0),
                check_in=check_in_dt,
            )
        except ValueError:
            pass

    if body.check_in and body.check_out and check_in_dt:
        try:
            check_out_dt = datetime.strptime(body.check_out, "%Y-%m-%d")
            if check_out_dt > check_in_dt:
                price_per_night, _ = calculate_price_for_stay(
                    base_price=hotel["base_price"],
                    rating=hotel.get("rating", 4.0),
                    check_in=check_in_dt,
                    check_out=check_out_dt,
                )
        except ValueError:
            pass

    reviews = get_reviews_for_hotel(body.hotel_id)
    ai_metrics = analyze_reviews(reviews, trip_type=trip_type, profile=body.profile)
    avg_price = price_per_night or hotel.get("base_price") or 100
    scored = score_hotel(
        ai_metrics,
        price_per_night=price_per_night,
        avg_price=avg_price,
        trip_type=trip_type,
        profile=body.profile,
    )

    return {
        "id": hotel["id"],
        "name": hotel["name"],
        "city": hotel.get("city"),
        "country": hotel.get("country"),
        "district": hotel.get("district"),
        "rating": hotel.get("rating"),
        "location_score": hotel.get("location_score"),
        "price_per_night": price_per_night,
        "reviews_count": len(reviews),
        "quality_score": scored.get("quality_score"),
        "value_for_money": scored.get("value_for_money"),
        "final_score": scored.get("final_score"),
        "red_flags": scored.get("red_flags", []),
        "risks": {"risk_weight": scored.get("risk_weight")},
        "pros": scored.get("pros", []),
        "cons": scored.get("cons", []),
        "consistency_score": scored.get("consistency_score"),
        "verdict": scored.get("verdict"),
    }


@router.post("/check-hotel")
def check_hotel(body: CheckHotelRequest):
    """
    Оценка отеля по названию: найти отель и выдать карточку с анализом по профилю.
    """
    hotel = get_hotel_by_name(
        name=body.hotel_name.strip(),
        city=body.city.strip() or None,
        country=body.country.strip() or None,
    )
    if not hotel:
        raise HTTPException(status_code=404, detail="Отель не найден. Проверьте название, город и страну.")

    trip_type = "leisure"
    profile = body.profile
    if profile:
        trip_type = getattr(profile, "trip_type", None) or "leisure"

    reviews = get_reviews_for_hotel(hotel["id"])
    ai_metrics = analyze_reviews(reviews, trip_type=trip_type, profile=profile)
    price_per_night = hotel.get("base_price") or 100
    scored = score_hotel(
        ai_metrics,
        price_per_night=price_per_night,
        avg_price=price_per_night,
        trip_type=trip_type,
        profile=profile,
    )

    return {
        "id": hotel["id"],
        "name": hotel["name"],
        "city": hotel.get("city"),
        "country": hotel.get("country"),
        "district": hotel.get("district"),
        "rating": hotel.get("rating"),
        "location_score": hotel.get("location_score"),
        "price_per_night": price_per_night,
        "quality_score": scored.get("quality_score"),
        "value_for_money": scored.get("value_for_money"),
        "final_score": scored.get("final_score"),
        "red_flags": scored.get("red_flags", []),
        "risks": {"risk_weight": scored.get("risk_weight")},
        "pros": scored.get("pros", []),
        "cons": scored.get("cons", []),
        "consistency_score": scored.get("consistency_score"),
        "verdict": scored.get("verdict"),
    }
