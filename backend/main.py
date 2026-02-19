"""
My Best Hotel — FastAPI Backend
Точка входа приложения.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import hotels, search, analyze

app = FastAPI(title="My Best Hotel API", version="0.1.0")

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


@app.get("/")
def root():
    return {"message": "My Best Hotel API", "docs": "/docs"}
