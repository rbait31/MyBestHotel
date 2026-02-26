# My Best Hotel

Система выбора отеля по отзывам и профилю путешественника. AI-анализ отзывов (Groq) с учётом предпочтений и критичных red flags, mock price engine, персонализированный scoring по весам профиля.

**Страницы:** поиск (`index.html`), требования к гостинице (`requirements.html`), мой выбор (`my-choice.html`).

## Production

- **Фронт:** [mybesthotel.vercel.app](https://mybesthotel.vercel.app)
- **Бэкенд:** [mybesthotel.onrender.com](https://mybesthotel.onrender.com)
- **Профиль:** сохраняется в PostgreSQL на Render, доступен с любого устройства

## Запуск локально

1. **Backend** (из корня): `uvicorn backend.main:app --reload`
2. **Frontend:** `cd frontend` → `python serve.py`
3. Открыть http://127.0.0.1:5500

> Backend и frontend запускаются в разных терминалах. Backend — из корня `MyBestHotel`, иначе `ModuleNotFoundError: No module named 'backend'`.

Для локальной разработки без PostgreSQL профиль сохраняется в памяти backend и в localStorage браузера.

## Деплой

- [DEPLOY.md](DEPLOY.md) — обзор (Render, Vercel)
- [RENDER-INSTRUCTIONS.md](RENDER-INSTRUCTIONS.md) — пошаговая инструкция Render + PostgreSQL
- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура системы
