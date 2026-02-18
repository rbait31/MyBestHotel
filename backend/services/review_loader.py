"""
Загрузка hotels.json и reviews.json.
"""
import json
import os

# Путь к data от корня backend (config лежит в backend/)
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_BACKEND_DIR, "data")


def _load_json(filename: str) -> list:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_hotels() -> list[dict]:
    """Загрузить все отели."""
    return _load_json("hotels.json")


def load_reviews() -> list[dict]:
    """Загрузить все отзывы."""
    return _load_json("reviews.json")


def get_hotels_by_location(city: str | None = None, country: str | None = None) -> list[dict]:
    """
    Получить отели по городу и/или стране.
    Фильтр по city и country (без учёта регистра).
    """
    hotels = load_hotels()
    city_lower = city.strip().lower() if city else None
    country_lower = country.strip().lower() if country else None

    result = []
    for h in hotels:
        match_city = not city_lower or (h.get("city", "") or "").lower() == city_lower
        match_country = not country_lower or (h.get("country", "") or "").lower() == country_lower
        if match_city and match_country:
            result.append(h)
    return result


def get_hotel_by_id(hotel_id: str) -> dict | None:
    """Получить отель по id."""
    hotels = load_hotels()
    for h in hotels:
        if h.get("id") == hotel_id:
            return h
    return None


def get_reviews_for_hotel(hotel_id: str) -> list[dict]:
    """Получить отзывы по hotel_id."""
    reviews = load_reviews()
    return [r for r in reviews if r.get("hotel_id") == hotel_id]
