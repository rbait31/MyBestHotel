"""
GET /api/profile — получить профиль по user_id.
POST /api/profile — сохранить профиль.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Any

from backend.database import (
    get_engine,
    session_scope,
    get_profile_from_cache,
    set_profile_in_cache,
)
from backend.models.profile import UserProfile

router = APIRouter(prefix="/api/profile", tags=["profile"])

DEFAULT_PROFILE = {
    "trip_type": "leisure",
    "budget_min": None,
    "budget_max": None,
    "with_car": False,
    "with_pets": False,
    "comfort_level": "comfort",
    "themes": ["cleanliness", "location", "noise", "internet"],
}


class ProfileSave(BaseModel):
    user_id: str
    profile: dict[str, Any]


@router.get("")
def get_profile(user_id: str = Query(..., description="UUID пользователя")):
    """Получить профиль. user_id — UUID, генерируется на фронте при первом заходе."""
    if not user_id or len(user_id) > 64:
        raise HTTPException(status_code=400, detail="user_id обязателен")

    import json

    # PostgreSQL
    engine = get_engine()
    if engine:
        with session_scope() as session:
            if session is not None:
                row = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
                if row:
                    data = json.loads(row.profile_json)
                    return {"profile": {**DEFAULT_PROFILE, **data}}

    # In-memory fallback (локальная разработка без БД)
    cached = get_profile_from_cache(user_id)
    if cached:
        return {"profile": {**DEFAULT_PROFILE, **cached}}

    return {"profile": DEFAULT_PROFILE.copy()}


@router.post("")
def save_profile(body: ProfileSave):
    """Сохранить профиль в БД."""
    if not body.user_id or len(body.user_id) > 64:
        raise HTTPException(status_code=400, detail="user_id обязателен")

    import json
    from datetime import datetime

    profile_data = {**DEFAULT_PROFILE, **(body.profile or {})}

    # PostgreSQL
    engine = get_engine()
    if engine:
        with session_scope() as session:
            if session is not None:
                row = session.query(UserProfile).filter(UserProfile.user_id == body.user_id).first()
                if row:
                    row.profile_json = json.dumps(profile_data)
                    row.updated_at = datetime.utcnow()
                else:
                    row = UserProfile(
                        user_id=body.user_id,
                        profile_json=json.dumps(profile_data),
                    )
                    session.add(row)
                return {"ok": True}

    # In-memory fallback (локальная разработка без БД)
    set_profile_in_cache(body.user_id, profile_data)
    return {"ok": True}
