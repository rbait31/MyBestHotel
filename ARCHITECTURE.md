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
│  • Форма поиска (город, даты, профиль)                                       │
│  • Профиль путешественника (localStorage + JSON export/import)               │
│  • Результаты (отели, scores, риски, плюсы/минусы)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ REST API
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI)                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ /search      │  │ /hotels      │  │ /analyze     │  │ /profile         │ │
│  │ /zones       │  │ /reviews     │  │ /score       │  │ (optional)       │ │
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
│  final_score = cleanliness*0.3 + location*0.2 + value*0.2 + comfort*0.2     │
│                - risk*0.1                                                    │
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
| Профиль | localStorage | + export/import JSON |
| Деплой | Vercel (frontend) + Railway/Render (backend) | Бесплатные планы |

---

## 3. Поток данных (User Flow)

```
1. Пользователь вводит:
   - Город, страна
   - Даты заезда/выезда
   - Профиль (тип поездки, бюджет, темы интересов) — из localStorage или ввод

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
   e) Groq AI → анализ каждого отеля (метрики, риски, плюсы/минусы, consistency)
   f) Scoring Engine → итоговый score
   g) Персонализация под профиль (AI или веса формулы)

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
│   ├── index.html               # Главная страница
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── app.js               # Логика приложения
│   │   ├── profile.js           # Профиль: localStorage, export/import
│   │   └── api.js               # Вызовы к backend
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
│   │   │   └── analyze.py       # POST /api/analyze (отдельный анализ отеля)
│   │   └── schemas.py           # Pydantic модели запросов/ответов
│   │
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

### 5.3 Профиль путешественника (localStorage / API)

```json
{
  "trip_type": "business",
  "budget_min": 100,
  "budget_max": 250,
  "with_car": false,
  "with_pets": false,
  "comfort_level": "comfort",
  "themes": ["noise", "cleanliness", "location", "internet"]
}
```

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
2. **Risk detection:** наличие unsafe, dirty, scam, noise all night, broken
3. **Плюсы/минусы:** список из отзывов
4. **Consistency:** согласованность отзывов (высокая/низкая)
5. **Verdict:** краткий вывод с учётом профиля путешественника

**Модель:** `llama-3.1-8b-instant` (быстро, в рамках бесплатного лимита).

---

## 8. Scoring Engine

```python
final_score = (
    cleanliness * 0.3 +
    location * 0.2 +
    value_score * 0.2 +
    comfort * 0.2 -
    risk_weight * 0.1
)
```

Веса могут подстраиваться под `trip_type` (бизнес → меньше noise_weight, больше location).

---

## 9. API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/search` | Поиск отелей по городу, датам, профилю |
| GET | `/api/hotels` | Список отелей по городу |
| GET | `/api/hotels/{id}` | Детали отеля |
| POST | `/api/analyze` | Анализ одного отеля (для выбранного пользователем) |

---

## 10. Деплой

- **Frontend:** `frontend/` → Vercel (static site)
- **Backend:** `backend/` → Railway или Render (Docker/Procfile)
- **CORS:** Backend должен разрешать запросы с домена Vercel
- **API URL:** Переменная окружения во frontend, например `VITE_API_URL` или хардкод для MVP

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
