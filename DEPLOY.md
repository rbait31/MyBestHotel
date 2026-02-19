# Деплой My Best Hotel

## Backend (Render / Railway)

### Render

1. Создайте аккаунт на [render.com](https://render.com)
2. New → Web Service
3. Подключите репозиторий GitHub
4. Настройки:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables:**
     - `GROQ_API_KEY` — ваш ключ Groq
     - `ALLOWED_ORIGINS` — URL фронтенда (например `https://mybesthotel.vercel.app`)

### Railway

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Добавьте переменные: `GROQ_API_KEY`, `ALLOWED_ORIGINS`
3. Railway автоматически обнаружит Procfile

---

## Frontend (Vercel)

1. [vercel.com](https://vercel.com) → Import Project → GitHub
2. **Root Directory:** укажите `frontend`
3. Deploy (сборка не требуется — статический сайт)
4. После деплоя скопируйте URL (например `https://mybesthotel.vercel.app`)

### Настройка API URL

Перед деплоем отредактируйте `frontend/js/config.js`:

```javascript
window.API_BASE = "https://YOUR-BACKEND.onrender.com";
```

Замените на URL вашего бэкенда (Render или Railway).

---

## Порядок деплоя

1. **Backend** — задеплойте первым, скопируйте URL
2. **Frontend** — в `config.js` укажите URL бэкенда
3. **Backend** — в `ALLOWED_ORIGINS` укажите URL Vercel (чтобы CORS разрешал запросы)
