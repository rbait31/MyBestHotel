# План реализации My Best Hotel (MVP)

## Фаза 0. Подготовка (≈1 ч)
- [x] Создать `.env` из `.env.example`, получить GROQ_API_KEY
- [x] Установить зависимости backend: `pip install -r backend/requirements.txt`
- [x] Проверить запуск: `uvicorn backend.main:app --reload`
- [x] Дополнить `backend/data/hotels.json` и `reviews.json` тестовыми данными (5–10 отелей, 20–50 отзывов)

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
- [x] Блок профиля: тип поездки, бюджет мин/макс, темы; сохранение в localStorage
- [x] Export/import профиля в JSON (profile.js)
- [x] Вызов `GET /api/hotels` из api.js, отображение списка отелей
- [x] Карточка отеля: цена, рейтинг, локация (quality/value/риски/verdict — при появлении из /api/search)
- [x] Базовая вёрстка (style.css), адаптивность по желанию

## Запуск фронтенда
- `cd frontend` → `python -m http.server 5500` — обычный сервер
- `cd frontend` → `python serve.py` — без кеширования (свежие файлы при каждой загрузке)

## Фаза 4. Интеграция и деплой (≈2–3 ч)
- [ ] CORS: в backend указать origin фронта (Vercel URL)
- [ ] Frontend: вынести URL API в конфиг (env или константа)
- [ ] Деплой backend на Railway/Render
- [ ] Деплой frontend на Vercel
- [ ] Проверка полного сценария в проде

## Резерв (если время есть)
- [ ] Red Flag Detector: подсветка слов unsafe, dirty, scam, noise all night, broken
- [ ] Consistency Score в ответе AI и в UI
- [ ] Подсказка «профиль гостей, которым подойдёт отель» для выбранного отеля
