"""
Mock Price Engine (Подход 1-2).
JSON dataset + формула с сезонностью + random factor.
"""
import random
from datetime import datetime, timedelta


def _season_multiplier(month: int) -> float:
    """Коэффициент сезона по месяцу."""
    if month in (1, 2):
        return 0.8  # Низкий сезон
    if month in (3, 4, 5):
        return 1.0  # Средний
    if month in (6, 7, 8):
        return 1.4  # Высокий
    if month in (9, 10):
        return 1.1  # Средний
    return 1.6  # Нояб–дек, праздники


def _weekend_multiplier(date: datetime) -> float:
    """Выходные: пт, сб = ×1.2."""
    if date.weekday() in (4, 5):  # пятница, суббота
        return 1.2
    return 1.0


def _rating_factor(rating: float) -> float:
    """Рейтинг 4.5+ → ×1.2, иначе 1.0."""
    return 1.2 if rating >= 4.5 else 1.0


def _noise_factor() -> float:
    """Случайный шум ±10%."""
    return 1.0 + random.uniform(-0.1, 0.1)


def calculate_price_per_night(
    base_price: float,
    rating: float,
    check_in: datetime,
) -> float:
    """
    Рассчитать цену за ночь по формуле.
    price = base_price × season × weekend × rating_factor × noise
    """
    season = _season_multiplier(check_in.month)
    weekend = _weekend_multiplier(check_in)
    rating_f = _rating_factor(rating)
    noise = _noise_factor()

    price = base_price * season * weekend * rating_f * noise
    return round(price, 2)


def calculate_price_for_stay(
    base_price: float,
    rating: float,
    check_in: datetime,
    check_out: datetime,
) -> tuple[float, float]:
    """
    Рассчитать цену за весь период.
    Возвращает (price_per_night, total_price).
    """
    total = 0.0
    current = check_in
    nights = 0
    while current < check_out:
        night_price = calculate_price_per_night(base_price, rating, current)
        total += night_price
        nights += 1
        # следующий день
        current += timedelta(days=1)

    avg_per_night = total / nights if nights else 0.0
    return (round(avg_per_night, 2), round(total, 2))
