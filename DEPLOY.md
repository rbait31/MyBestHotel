# Деплой My Best Hotel

> ✅ Программа проверена на Vercel — работает.

---

## Backend (Render / Railway)

### Render (рекомендуется для хакатона)

1. [render.com](https://render.com) → New → Web Service
2. Подключите репозиторий GitHub
3. **Settings → Build & Deploy:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. **Settings → Environment** → Add Environment Variable:
   - `GROQ_API_KEY` — ключ с [console.groq.com](https://console.groq.com)
   - `ALLOWED_ORIGINS` — URL фронтенда (например `https://mybesthotel.vercel.app`)

### Где в Render вводить Build/Start Command

Dashboard → ваш Web Service → вкладка **Settings** → раздел **Build & Deploy** → поля **Build Command** и **Start Command**.

### Railway

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Environment → добавьте `GROQ_API_KEY`, `ALLOWED_ORIGINS`
3. Railway обнаруживает Procfile автоматически

### Render или Railway?

| Параметр | Render | Railway |
|----------|--------|---------|
| Бесплатный тариф | Да (сервис засыпает ~15 мин без запросов) | Да (лимит трафика) |
| Пробуждение | 30–60 сек | Не засыпает |
| Для хакатона | ✅ Проще настроить | ✅ Быстрый отклик |

**Для MVP:** Render. Для стабильной работы без «засыпания» — Railway.

---

## Frontend (Vercel)

1. [vercel.com](https://vercel.com) → Import Project → GitHub
2. **Root Directory:** обязательно укажите `frontend` (иначе 404)
3. Build Command — пусто или `echo "static"`
4. Output Directory — пусто
5. Deploy
6. Скопируйте URL (например `https://mybesthotel.vercel.app`)

### 404 NOT_FOUND на Vercel

1. Dashboard → проект → **Settings** → **General**
2. **Root Directory** → Edit → введите `frontend`
3. Save → **Redeploy** (Deployments → ⋮ → Redeploy)

Причина: без Root Directory Vercel ищет `index.html` в корне репо, а он лежит в `frontend/`.

### Настройка API URL

Перед деплоем в `frontend/js/config.js` укажите URL бэкенда:

```javascript
window.API_BASE = "https://YOUR-BACKEND.onrender.com";
```

---

## Порядок деплоя

1. **Backend** — задеплойте первым, скопируйте URL
2. **Frontend** — в `config.js` укажите URL бэкенда
3. **Backend** — в `ALLOWED_ORIGINS` добавьте URL Vercel (CORS)

---

## Запуск локально

1. **Backend** (из корня проекта):  
   `uvicorn backend.main:app --reload`
2. **Frontend:**  
   `cd frontend` → `python serve.py`
3. Открыть http://127.0.0.1:5500
