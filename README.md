# MyBestHotel

Система, которая собирает отзывы о гостиницах из разных источников, анализирует их и помогает выбрать лучшую с учётом профиля путешественника.

## Запуск локально

1. **Backend** (из корня): `uvicorn backend.main:app --reload`
2. **Frontend:** `cd frontend` → `python serve.py`
3. Открыть http://127.0.0.1:5500

> Backend и frontend запускаются в разных терминалах. Backend — из корня `MyBestHotel`, иначе `ModuleNotFoundError: No module named 'backend'`.

## Деплой

См. [DEPLOY.md](DEPLOY.md) — Render, Railway, Vercel. Проект проверен на Vercel.
