"""
Pydantic-модели запросов и ответов API.
"""
from typing import Any

from pydantic import BaseModel, Field


class ProfileSchema(BaseModel):
    trip_type: str = Field(default="leisure", description="leisure | business | family | group")
    budget_min: float | None = Field(default=None, description="Мин бюджет €/ночь")
    budget_max: float | None = Field(default=None, description="Макс бюджет €/ночь")
    with_car: bool = False
    with_pets: bool = False
    comfort_level: str = Field(default="comfort", description="budget | comfort")
    themes: list[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    city: str = Field(default="", description="Город")
    country: str = Field(default="", description="Страна")
    check_in: str = Field(..., description="Дата заезда YYYY-MM-DD")
    check_out: str = Field(..., description="Дата выезда YYYY-MM-DD")
    profile: ProfileSchema | None = Field(default=None)


class AnalyzeRequest(BaseModel):
    hotel_id: str = Field(..., description="ID отеля")
    check_in: str | None = Field(default=None)
    check_out: str | None = Field(default=None)
    profile: ProfileSchema | None = Field(default=None)
