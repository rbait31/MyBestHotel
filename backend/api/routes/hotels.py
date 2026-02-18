"""
GET /api/hotels, GET /api/hotels/{id} — список и детали отелей.
"""
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from backend.services.review_loader import get_hotels_by_location, get_hotel_by_id, get_reviews_for_hotel
from backend.services.price_engine import calculate_price_per_night

router = APIRouter(prefix="/api/hotels", tags=["hotels"])


@router.get("")
def list_hotels(
    city: str | None = Query(None, description="Город"),
    country: str | None = Query(None, description="Страна"),
    check_in: str | None = Query(None, description="Дата заезда (YYYY-MM-DD)"),
):
    """
    Список отелей по городу/стране.
    Если указан check_in — добавляется цена за ночь.
    """
    if not city and not country:
        raise HTTPException(status_code=400, detail="Укажите city или country")

    hotels = get_hotels_by_location(city=city, country=country)
    result = []

    check_in_dt = None
    if check_in:
        try:
            check_in_dt = datetime.strptime(check_in, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="check_in в формате YYYY-MM-DD")

    for h in hotels:
        item = {**h}
        if check_in_dt:
            price = calculate_price_per_night(
                base_price=h["base_price"],
                rating=h.get("rating", 4.0),
                check_in=check_in_dt,
            )
            item["price_per_night"] = price
        result.append(item)

    return {"hotels": result, "count": len(result)}


@router.get("/{hotel_id}")
def get_hotel(
    hotel_id: str,
    check_in: str | None = Query(None, description="Дата заезда (YYYY-MM-DD)"),
    check_out: str | None = Query(None, description="Дата выезда (YYYY-MM-DD)"),
):
    """Детали отеля. Опционально — цена за период."""
    hotel = get_hotel_by_id(hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Отель не найден")

    result = {**hotel}
    result["reviews_count"] = len(get_reviews_for_hotel(hotel_id))

    if check_in and check_out:
        try:
            check_in_dt = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_dt = datetime.strptime(check_out, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Даты в формате YYYY-MM-DD")

        if check_out_dt <= check_in_dt:
            raise HTTPException(status_code=400, detail="check_out должен быть позже check_in")

        from backend.services.price_engine import calculate_price_for_stay
        price_per_night, total = calculate_price_for_stay(
            base_price=hotel["base_price"],
            rating=hotel.get("rating", 4.0),
            check_in=check_in_dt,
            check_out=check_out_dt,
        )
        result["price_per_night"] = price_per_night
        result["total_price"] = total

    return result
