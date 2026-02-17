# План реализации My Best Hotel (MVP)

## Фаза 0. Подготовка (≈1 ч)
- [ ] Создать `.env` из `.env.example`, получить GROQ_API_KEY
- [ ] Установить зависимости backend: `pip install -r backend/requirements.txt`
- [ ] Проверить запуск: `uvicorn backend.main:app --reload`
- [ ] Дополнить `backend/data/hotels.json` и `reviews.json` тестовыми данными (5–10 отелей, 20–50 отзывов)

## Фаза 1. Backend — данные и цены (≈2–3 ч)
- [ ] Реализовать `review_loader.py`: загрузка hotels.json, reviews.json, выбор по city/country
- [ ] Реализовать `price_engine.py`: формула с сезонностью, выходными, рейтингом, ±10% шум
- [ ] Подключить роут `GET /api/hotels?city=...&country=...`
- [ ] Проверить расчёт цен по датам через Postman/curl

## Фаза 2. Backend — AI и скоринг (≈6–8 ч)
- [ ] Реализовать `ai_analysis.py`: вызов Groq, промпты для метрик (cleanliness, noise, comfort, location), рисков, плюсов/минусов, consistency
- [ ] Реализовать `scoring.py`: формула final_score с весами
- [ ] Собрать pipeline в `search.py`: фильтр по датам/бюджету → 3–4 отеля → AI по каждому → scoring
- [ ] Реализовать `POST /api/search` (body: city, country, check_in, check_out, profile)
- [ ] Опционально: `POST /api/analyze` для одного отеля (выбранного пользователем)
- [ ] Зарегистрировать все роуты в `main.py`

## Фаза 3. Frontend (≈3–4 ч)
- [ ] Форма поиска: город, страна, даты, кнопка «Найти»
- [ ] Блок профиля: тип поездки, бюджет мин/макс, темы; сохранение в localStorage
- [ ] Export/import профиля в JSON (profile.js)
- [ ] Вызов `POST /api/search` из api.js, отображение списка отелей
- [ ] Карточка отеля: цена, quality score, value, риски, плюсы/минусы, verdict
- [ ] Базовая вёрстка (style.css), адаптивность по желанию

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
