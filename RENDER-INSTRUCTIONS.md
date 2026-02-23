# Инструкция: деплой бэкенда на Render

## Что уже подготовлено в репозитории

- `Procfile` — команда запуска для Render
- `requirements.txt` — зависимости Python
- `runtime.txt` — версия Python
- `render.yaml` — Blueprint (опционально)

---

## Шаг 1. Запушить изменения в GitHub

Если вы только что добавили `render.yaml` и `runtime.txt`, выполните:

```powershell
cd c:\Work\MyBestHotel
git add .
git commit -m "Добавлены конфиги для Render"
git push origin main
```

---

## Шаг 2. Создать Web Service на Render

1. Откройте [dashboard.render.com](https://dashboard.render.com)
2. Нажмите **New +** → **Web Service**
3. Подключите репозиторий GitHub (если ещё не подключён — авторизуйте Render в GitHub)
4. Выберите репозиторий `MyBestHotel` (или как называется ваш проект)
5. Нажмите **Connect**

---

## Шаг 3. Настроить Build & Deploy

| Поле | Значение |
|------|----------|
| **Name** | `mybesthotel-api` (или любое) |
| **Region** | Frankfurt (или ближайший) |
| **Root Directory** | оставить пустым (корень репо) |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |

---

## Шаг 4. Добавить PostgreSQL (для хранения профиля пользователя)

1. В Render Dashboard нажмите **New +** → **PostgreSQL**
2. **Name:** `mybesthotel-db` (или любое)
3. **Region:** тот же, что у Web Service
4. **Plan:** Free
5. Нажмите **Create Database**
6. После создания откройте БД → вкладка **Info** → скопируйте **Internal Database URL** (или **External Database URL** для доступа с локальной машины)
7. Вернитесь в ваш Web Service → **Environment** → **Add Environment Variable**
8. Key: `DATABASE_URL`, Value: вставьте скопированный URL

   Либо нажмите **Link Resource** в Web Service и выберите созданную БД — Render подставит `DATABASE_URL` автоматически.

**Без PostgreSQL** профиль будет храниться в памяти (теряется при перезапуске) и в localStorage в браузере.

---

## Шаг 5. Добавить остальные переменные окружения

В разделе **Environment** добавьте:

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | ваш ключ с [console.groq.com](https://console.groq.com) |
| `ALLOWED_ORIGINS` | `https://mybesthotel.vercel.app` (URL вашего фронта на Vercel) |

Если у вас другой домен фронта — укажите его. Через запятую можно несколько:  
`https://mybesthotel.vercel.app,https://www.mybesthotel.com`

---

## Шаг 6. Создать сервис

Нажмите **Create Web Service**. Render начнёт сборку и деплой. Подождите 2–5 минут.

---

## Шаг 7. Скопировать URL бэкенда

После успешного деплоя Render покажет URL. Он зависит от имени сервиса:
- Сервис **MyBestHotel** → `https://mybesthotel.onrender.com`
- Сервис **mybesthotel-api** → `https://mybesthotel-api.onrender.com`

Скопируйте ваш реальный URL.

---

## Шаг 8. Обновить config.js на фронтенде

Откройте `frontend/js/config.js` и задайте `API_BASE`:

```javascript
window.API_BASE = "https://mybesthotel.onrender.com";
```

(подставьте ваш реальный URL из Шага 7)

**Обязательно:** `config.js` должен подключаться на странице `requirements.html` (перед `profile.js`), иначе профиль будет обращаться к `127.0.0.1:8000`.

---

## Шаг 9. Задеплоить изменения фронта на Vercel

Если фронт уже на Vercel — просто запушьте изменения:

```powershell
git add frontend/js/config.js
git commit -m "Обновлён URL API для production"
git push origin main
```

Vercel автоматически пересоберёт и задеплоит проект.

---

## Проверка

1. Откройте `https://mybesthotel.onrender.com` — должна вернуться JSON: `{"message":"My Best Hotel API","docs":"/docs"}`
2. Откройте `https://mybesthotel.onrender.com/docs` — Swagger UI
3. Откройте фронт на Vercel и выполните поиск отелей
4. На странице «Требования к гостинице» измените профиль и нажмите «Сохранить» — данные сохраняются в PostgreSQL и доступны с любого устройства

---

## Важно

- **Бесплатный план Render:** сервис «засыпает» после ~15 минут без запросов. Первый запрос после пробуждения занимает 30–60 секунд.
- **CORS:** `ALLOWED_ORIGINS` должен точно совпадать с доменом фронта (включая `https://`).
- **config.js:** подключать на всех страницах (`index.html`, `requirements.html`). Без него `profile.js` использует fallback `127.0.0.1:8000` и вы увидите «Сервер недоступен».
