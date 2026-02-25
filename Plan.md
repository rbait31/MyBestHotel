# План реализации My Best Hotel (MVP)

## Фаза 0. Подготовка (≈1 ч)
- [x] Создать `.env` из `.env.example`, получить GROQ_API_KEY
- [x] Установить зависимости backend: `pip install -r backend/requirements.txt`
- [x] Проверить запуск: `uvicorn backend.main:app --reload`
- [x] Дополнить `backend/data/hotels.json` и `reviews.json` тестовыми данными (Paris, Barcelona, Madrid; 30+ отелей, 100+ отзывов)

## Фаза 1. Backend — данные и цены (≈2–3 ч)
- [x] Реализовать `review_loader.py`: загрузка hotels.json, reviews.json, выбор по city/country
- [x] Реализовать `price_engine.py`: формула с сезонностью, выходными, рейтингом, ±10% шум
- [x] Подключить роут `GET /api/hotels?city=...&country=...`
- [x] Проверить расчёт цен по датам через Postman/curl

## Фаза 2. Backend — AI и скоринг (≈6–8 ч)
- [x] Реализовать `ai_analysis.py`: вызов Groq, промпты для метрик (cleanliness, noise, comfort, location), рисков, плюсов/минусов, consistency
- [x] Реализовать `scoring.py`: формула final_score с весами
- [x] Собрать pipeline в `search.py`: фильтр по датам/бюджету → 3–4 отеля → AI по каждому → scoring
- [x] Реализовать `POST /api/search` (body: city, country, check_in, check_out, profile)
- [x] Опционально: `POST /api/analyze` для одного отеля (выбранного пользователем)
- [x] Зарегистрировать все роуты в `main.py`

## Фаза 3. Frontend (≈3–4 ч)
- [x] Форма поиска: город, страна, даты, кнопка «Найти»
- [x] Город → автоподстановка страны; селектор страны — только для городов в нескольких странах
- [x] Страница «Требования к гостинице» (requirements.html): тип поездки, бюджет, машина, питомцы; предпочтения (0–5); завтрак, состав; критичные red flags; шестерёнка в форме поиска
- [x] Export/import профиля в JSON (profile.js)
- [x] Вызов API из api.js, отображение списка отелей
- [x] Карточка отеля: цена, рейтинг, quality/value/риски/verdict
- [x] Базовая вёрстка (style.css)

## Запуск фронтенда
- `cd frontend` → `python -m http.server 5500` — обычный сервер
- `cd frontend` → `python serve.py` — без кеширования (свежие файлы при каждой загрузке)

## Фаза 4. Профиль и БД (≈2 ч)
- [x] PostgreSQL: модели UserProfile, database.py
- [x] API GET/POST /api/profile (user_id из localStorage)
- [x] Frontend: profile.js — API с fallback на localStorage
- [x] config.js подключать на index.html и requirements.html (иначе 127.0.0.1)

## Фаза 5. Интеграция и деплой (≈2–3 ч)
- [x] CORS: ALLOWED_ORIGINS (Render env)
- [x] Frontend: API_BASE в config.js
- [x] Конфиги: Procfile, requirements.txt, runtime.txt, render.yaml, RENDER-INSTRUCTIONS.md
- [x] Деплой backend на Render
- [x] PostgreSQL на Render, DATABASE_URL
- [x] Деплой frontend на Vercel
- [x] Проверка полного сценария в проде ✅

## Реализовано (расширение)
- [x] Интеграция полного профиля с AI и scoring: предпочтения (в т.ч. завтрак 0–5), red flags, with_car, with_pets, solo/couple/family/group
- [x] Веса скоринга по предпочтениям пользователя (0–5)
- [x] Штраф за совпадение red_flags отеля с критичными для пользователя

## Резерв (если время есть)
- [ ] Red Flag Detector: подсветка слов unsafe, dirty, scam, noise all night, broken в отзывах
- [ ] Consistency Score в ответе AI и в UI
- [ ] Подсказка «профиль гостей, которым подойдёт отель» для выбранного отеля
