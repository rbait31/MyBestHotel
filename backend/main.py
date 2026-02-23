"""
My Best Hotel — FastAPI Backend
Точка входа приложения.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import hotels, search, analyze, profile
from backend.database import get_engine, init_db

app = FastAPI(title="My Best Hotel API", version="0.1.0")


@app.on_event("startup")
def on_startup():
    """Создать таблицы БД при старте (если PostgreSQL подключён)."""
    engine = get_engine()
    if engine:
        init_db(engine)

# CORS: ALLOWED_ORIGINS — через запятую (например https://mybesthotel.vercel.app)
# Для разработки: "*" или не задано
_origins = os.getenv("ALLOWED_ORIGINS", "*")
_allowed = _origins.split(",") if _origins else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hotels.router)
app.include_router(search.router)
app.include_router(analyze.router)
app.include_router(profile.router)


@app.get("/")
def root():
    return {"message": "My Best Hotel API", "docs": "/docs"}
