# Архитектура My Best Hotel (MVP для хакатона)

## 1. Общая схема системы

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ПОЛЬЗОВАТЕЛЬ                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  FRONTEND (HTML + Alpine.js/Vanilla JS)                                      │
│  • Форма поиска (город, даты, профиль) + Проверить гостиницу                 │
│  • Требования к гостинице: API → PostgreSQL, fallback localStorage           │
│  • Результаты (отели, scores, риски, плюсы/минусы), Мой выбор, скачать .md   │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ REST API
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI)                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ /search      │  │ /hotels      │  │ /analyze     │  │ /profile         │ │
│  │ /zones       │  │ /reviews     │  │ /score       │  │ GET/POST         │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ MOCK PRICE      │         │ REVIEW DATA     │         │ AI ANALYSIS     │
│ ENGINE          │         │ (JSON)          │         │ (Groq API)      │
│                 │         │                 │         │                 │
│ • JSON dataset  │         │ • hotels.json   │         │ • sentiment     │
│ • seasonality   │         │ • reviews.json  │         │ • metrics       │
│ • formula       │         │                 │         │ • risk detect   │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SCORING ENGINE (Python logic)                                               │
│  Веса по предпочтениям профиля (0–5). Штраф за red_flags, отмеченные        │
│  пользователем. quality = (cleanliness + location + comfort + staff + noise)/5│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Стек технологий

| Компонент | Технология | Примечание |
|-----------|------------|------------|
| Frontend | HTML + Alpine.js (CDN) | Без сборки, деплой на Vercel |
| Backend | Python 3.11+ / FastAPI | Быстро, async, автодокументация |
| AI | Groq API (llama-3.1-8b-instant) | Бесплатный тариф, быстрый inference |
| Цены | Mock Price Engine | JSON + формула с сезонностью |
| Отзывы | JSON-файлы | hotels.json, reviews.json |
| Профиль | PostgreSQL (API) + localStorage fallback | GET/POST /api/profile |
| БД | PostgreSQL (Render) | Хранение профиля |
| Деплой | Vercel (frontend) + Render (backend + PostgreSQL) | Бесплатные планы |

---

## 3. Поток данных (User Flow)

```
1. Пользователь вводит:
   - Город, страна
   - Даты заезда/выезда
   - Профиль — загружается из API (PostgreSQL) или localStorage:
     тип поездки, бюджет, машина, питомцы; предпочтения (центр, чистота, тишина, Wi‑Fi, природа);
     завтрак, состав (solo/couple/family/group); критичные red flags

2. Frontend → POST /api/search
   {
     "city": "Paris",
     "country": "France",
     "check_in": "2025-04-14",
     "check_out": "2025-04-18",
     "profile": { ... }
   }

3. Backend:
   a) Price Engine → цены по отелям из JSON (формула: base × season × weekend × demand × rating)
   b) Фильтр по бюджету (min-max цена)
   c) Выбор 3–4 отелей в ценовом диапазоне
   d) Загрузка отзывов из reviews.json
   e) Groq AI → анализ каждого отеля с учётом профиля (метрики, риски, плюсы/минусы, consistency)
   f) Scoring Engine → итоговый score (веса по предпочтениям, штраф за совпадение red_flags)

4. Ответ → список отелей с:
   - price_per_night
   - AI quality score
   - value_for_money
   - red_flags (если есть)
   - risks (risk_weight)
   - pros / cons
   - consistency_score
   - verdict (текст от AI)
```

---

## 4. Структура репозитория

```
MyBestHotel/
│
├── frontend/                    # Статический фронтенд (Vercel)
│   ├── index.html               # Главная страница (поиск, «Проверить гостиницу», карточки)
│   ├── requirements.html        # Требования к гостинице (профиль)
│   ├── my-choice.html           # Мой выбор — сохранённые отели (localStorage)
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── config.js            # API_BASE (URL бэкенда)
│   │   ├── app.js               # Логика приложения (Alpine.js, autocomplete, myChoices)
│   │   ├── api.js               # Вызовы к backend
│   │   ├── profile.js           # Профиль: API (PostgreSQL), fallback localStorage
│   │   └── hotel-card.js        # hotelToMarkdown(), downloadHotelCard() — скачивание .md
│   └── assets/
│       └── (иконки при необходимости)
│
├── backend/                     # FastAPI приложение
│   ├── main.py                  # Точка входа, роуты
│   ├── config.py                # Настройки (GROQ_API_KEY, CORS и т.д.)
│   ├── requirements.txt
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── search.py        # POST /api/search
│   │   │   ├── hotels.py        # GET /api/hotels, GET /api/hotels/{id}
│   │   │   ├── analyze.py       # POST /api/analyze (отдельный анализ отеля)
│   │   │   └── profile.py       # GET/POST /api/profile (PostgreSQL)
│   │   └── schemas.py           # Pydantic модели запросов/ответов
│   │
│   ├── database.py              # PostgreSQL, fallback in-memory
│   ├── models/
│   │   ├── __init__.py
│   │   └── profile.py           # UserProfile
│   ├── services/
│   │   ├── __init__.py
│   │   ├── price_engine.py      # Mock price engine (Подход 1-2)
│   │   ├── review_loader.py     # Загрузка hotels.json, reviews.json
│   │   ├── ai_analysis.py       # Groq: анализ отзывов, метрики, риски
│   │   └── scoring.py           # Формула итогового score
│   │
│   └── data/                    # JSON-данные (в репо или .gitignore + sample)
│       ├── hotels.json          # Отели: id, name, city, country, district,
│       │                        # base_price, rating, location_score, etc.
│       └── reviews.json         # Отзывы: hotel_id, text, date, source
│
├── docs/                        # Документация (опционально)
│   ├── ARCHITECTURE.md          # Этот файл
│   └── API.md                  # Описание API
│
├── .env.example                 # Шаблон переменных (GROQ_API_KEY)
├── .gitignore
├── LICENSE
└── README.md
```

---

## 5. Форматы данных

### 5.1 hotels.json

```json
[
  {
    "id": "hotel_001",
    "name": "Grand Plaza",
    "city": "Paris",
    "country": "France",
    "district": "center",
    "base_price": 180,
    "rating": 4.5,
    "location_score": 9,
    "zone_type": "sights,shopping"
  }
]
```

### 5.2 reviews.json

```json
[
  {
    "hotel_id": "hotel_001",
    "text": "Great location but very noisy at night and room was small.",
    "date": "2024-01-15",
    "source": "mock"
  }
]
```

### 5.3 Профиль путешественника (API / localStorage)

Все поля учитываются при AI-анализе и скоринге.

```json
{
  "trip_type": "leisure",
  "budget_min": 50,
  "budget_max": 250,
  "with_car": false,
  "with_pets": false,
  "themes": ["cleanliness", "location", "noise", "internet"],
  "preference_center": 3,
  "preference_breakfast": 3,
  "preference_cleanliness": 3,
  "preference_quiet": 3,
  "preference_wifi": 3,
  "preference_nature": 3,
  "solo": false,
  "couple": false,
  "family": false,
  "group": false,
  "red_flag_safety": false,
  "red_flag_dirt": false,
  "red_flag_noise_night": false,
  "red_flag_weak_wifi": false,
  "red_flag_no_car_access": false,
  "red_flag_insects": false,
  "red_flag_scam": false
}
```

| Поле | Описание |
|------|----------|
| trip_type | `leisure` \| `business` |
| budget_min, budget_max | Фильтр по цене (€/ночь) |
| with_car, with_pets | Учёт парковки, pet-friendly |
| preference_* | Важность 0–5 (центр, завтрак, чистота, тишина, Wi‑Fi, природа) |
| solo, couple, family, group | Состав поездки |
| red_flag_* | Критично: избегать отели с этими проблемами |

### 5.4 Ответ поиска (упрощённо)

```json
{
  "hotels": [
    {
      "id": "hotel_001",
      "name": "Grand Plaza",
      "price_per_night": 220,
      "quality_score": 8.4,
      "value_for_money": 7.8,
      "red_flags": [],
      "risks": { "noise": 0.32, "small_rooms": 0.15 },
      "pros": ["Great location", "Clean"],
      "cons": ["Noisy at night", "Small rooms"],
      "consistency_score": 0.85,
      "verdict": "Подходит для бизнес-поездки благодаря локации..."
    }
  ]
}
```

---

## 6. Mock Price Engine (Подход 1–2)

**Формула:**

```
price = base_price × season_multiplier × weekend_multiplier × demand_factor × rating_factor + random(-10%, +10%)
```

**Коэффициенты (пример):**

| Фактор | Значение |
|--------|----------|
| Низкий сезон (янв–фев) | 0.8 |
| Средний (март–май, сен–окт) | 1.0 |
| Высокий (июнь–авг) | 1.4 |
| Праздники (нояб–дек) | 1.6 |
| Выходные | ×1.2 |
| Рейтинг отеля 4.5+ | ×1.2 |
| Случайный шум | ±10% |

---

## 7. AI Analysis (Groq)

**Промпт-задачи:**

1. **Извлечение метрик:** cleanliness, noise, comfort, location, staff (0–10)
2. **Risk detection:** red_flags (unsafe, dirty, scam, noise, weak wifi и т.д.)
3. **Плюсы/минусы:** список из отзывов
4. **Consistency:** согласованность отзывов (высокая/низкая)
5. **Verdict:** краткий вывод с учётом профиля путешественника

**Учёт профиля в промпте:**
- Приоритеты (предпочтения 4–5): центр, чистота, тишина, Wi‑Fi, природа
- with_car / with_pets: парковка, pet-friendly
- preference_breakfast (0–5), solo/couple/family/group
- **Критично:** red_flag_* — AI особо ищет и помечает в red_flags совпадения

**Модель:** `llama-3.1-8b-instant` (быстро, в рамках бесплатного лимита).

---

## 8. Scoring Engine

**Метрики качества:** cleanliness, location, comfort, staff, noise (0–10)

**Веса по предпочтениям профиля (0–5):**
- preference_cleanliness → w_cleanliness
- preference_center, preference_nature → w_location
- preference_wifi → w_comfort
- preference_quiet → w_noise
- staff — базовый вес (без ползунка на странице)

**Дополнительно:**
- `trip_type: business` — усиление location, ослабление comfort
- `family` / `group` — усиление cleanliness, comfort

**Штраф за red_flags:** если пользователь отметил `red_flag_*` (напр. dirt) и отель имеет соответствующий флаг в AI-ответе — `risk_weight` увеличивается, `final_score` снижается.

```python
# quality_score = (cleanliness + location + comfort + staff + noise) / 5
# final_score = взвешенная сумма метрик + value - risk (с учётом штрафа)
```

---

## 9. API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/search` | Поиск отелей по городу, датам, профилю |
| GET | `/api/hotels` | Список отелей по городу |
| GET | `/api/hotels/{id}` | Детали отеля |
| POST | `/api/analyze` | Анализ одного отеля (для выбранного пользователем) |
| GET | `/api/profile?user_id=...` | Получить профиль (PostgreSQL) |
| POST | `/api/profile` | Сохранить профиль (PostgreSQL) |

---

## 10. Деплой

- **Frontend:** `frontend/` → Vercel (Root Directory: `frontend`)
- **Backend:** корень репо → Render (Web Service)
- **PostgreSQL:** Render → New PostgreSQL, `DATABASE_URL` в Environment
- **CORS:** `ALLOWED_ORIGINS` = URL Vercel (например `https://mybesthotel.vercel.app`)
- **API URL:** в `frontend/js/config.js` задаётся `window.API_BASE`; `config.js` обязательно подключать на всех страницах (в т.ч. `requirements.html`)

---

## 11. Оценка времени реализации

| Компонент | Часы |
|-----------|------|
| Mock Price Engine + JSON data | 2–3 |
| AI Analysis (Groq integration) | 6–10 |
| Scoring Engine | 2 |
| Backend FastAPI | 4–6 |
| Frontend (форма, результаты, профиль) | 3–4 |
| Интеграция + деплой | 4 |
| **Итого** | **~24–30** |
