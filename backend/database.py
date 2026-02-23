"""
Подключение к PostgreSQL. Без DATABASE_URL — in-memory fallback для локальной разработки.
"""
import os
from contextlib import contextmanager
from typing import Generator

DATABASE_URL = os.getenv("DATABASE_URL")
# Render передаёт postgres:// — SQLAlchemy ожидает postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# In-memory fallback при отсутствии DATABASE_URL (локальная разработка)
_profiles_cache: dict[str, dict] = {}


def get_engine():
    """Создать engine только если DATABASE_URL задан."""
    if not DATABASE_URL:
        return None
    from sqlalchemy import create_engine
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def get_session():
    """Сессия SQLAlchemy. None если БД недоступна."""
    engine = get_engine()
    if not engine:
        return None
    from sqlalchemy.orm import sessionmaker, Session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def init_db(engine) -> None:
    """Создать таблицы."""
    from backend.models.profile import Base
    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope() -> Generator:
    """Контекстный менеджер для сессии БД."""
    engine = get_engine()
    if not engine:
        yield None
        return
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_profile_from_cache(user_id: str) -> dict | None:
    """Получить профиль из in-memory кэша (fallback без БД)."""
    return _profiles_cache.get(user_id)


def set_profile_in_cache(user_id: str, profile: dict) -> None:
    """Сохранить профиль в in-memory кэш (fallback без БД)."""
    _profiles_cache[user_id] = profile.copy()
