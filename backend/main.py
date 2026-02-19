"""
My Best Hotel — FastAPI Backend
Точка входа приложения.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import hotels, search, analyze

app = FastAPI(title="My Best Hotel API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для MVP; в prod — указать домен Vercel
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
