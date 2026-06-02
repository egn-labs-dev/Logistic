# Logistic AI Dispatcher (HITL)

Enterprise-рішення для автоматизації логістичних процесів зі штучним інтелектом (Gemini) та системою безпечного перехоплення сесій (Human-in-the-Loop) для диспетчерів.

## 🌟 Ключові можливості
- **AI Agent**: Автоматична комунікація з клієнтом щодо деталей вантажу, розрахунку габаритів та вимог.
- **Data Privacy**: Вбудований Data Scrubber анонімізує персональні дані (телефони, імена) перед відправкою до LLM.
- **HITL (Human-in-the-Loop)**: Якщо ШІ розпізнає стресову ситуацію або спеціальні вимоги (наприклад, складний ADR), система піднімає алерт.
- **Secure Dashboard**: Захищена (JWT + RLS) панель диспетчера з можливістю перехоплення керування чатом.
- **Live Deanonymization**: Диспетчер бачить оригінальні дані клієнтів лише після авторизації та входу в систему.
- **Real-time Feedback**: Зворотний зв'язок без затримок завдяки TanStack Query.

---

## 🚀 Деплой (Docker)

Система повністю ізольована та запакована в оптимізовані Docker-образи (Multi-stage build). Для запуску на сервері вам потрібні лише встановлені Docker та Docker Compose.

### 1. Підготовка оточення
Скопіюйте еталонний файл конфігурації:
```bash
cp .env.example .env
```
Відредагуйте `.env`, вказавши ваші реальні секрети (API ключі, надійні паролі для БД, та JWT секрет).

> **УВАГА:** Ніколи не використовуйте дефолтні секрети або `Base.metadata.create_all` на продакшені! Система автоматично виконає міграції через Alembic при старті.

### 2. Збірка та запуск
Виконайте команду для запуску системи (Production-ready з Gunicorn та Nginx SPA-роутингом):
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### 3. Доступ
Після успішного старту контейнерів:
- **Frontend (Dispatcher Console)**: `http://localhost` (або IP вашого сервера)
- **Backend (FastAPI)**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`

---

## 🛠 Технологічний стек
- **Backend**: FastAPI, SQLAlchemy (Async), PostgreSQL, Passlib/Bcrypt
- **Frontend**: React, Vite, TailwindCSS, Shadcn UI, Zustand, TanStack Query
- **AI**: Google Gemini (generative-ai)
- **Infrastructure**: Docker, Docker Compose, Nginx

## 🛡 Безпека
- **Row-Level Security (RLS)**: Ізоляція даних між різними організаціями.
- **Immutable Audit Logs**: Журнал подій, який неможливо видалити чи змінити (append-only), зберігає як анонімізовані, так і зашифровані оригінальні дані (Vault).
- **RBAC**: Доступ до ендпоінтів жорстко контролюється за ролями (`dispatcher`, `admin`).
