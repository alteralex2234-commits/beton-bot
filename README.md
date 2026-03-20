# concrete_bot

Telegram + FastAPI проект для компании "Бетон Семей" (г. Семей).  
Бот консультирует по маркам бетона, отвечает на FAQ, собирает лиды и сохраняет их в Supabase с уведомлением менеджера в Telegram.

## Возможности на старте

- Telegram-бот с главным меню и русскоязычными сценариями
- Rule-based консультации по базе знаний и FAQ
- FSM-сценарий "Оставить заявку" (имя, телефон, объем, продукт, комментарий)
- Сохранение лидов в Supabase (`leads`)
- Уведомление менеджера в Telegram после новой заявки
- FastAPI endpoints:
  - `GET /health`
  - `POST /api/leads/test`
  - `POST /webhooks/meta` (заготовка)
  - `POST /webhooks/whatsapp` (заготовка)
- Архитектурные точки расширения под Instagram/WhatsApp/AI

## Требования

- Python 3.12+
- Telegram Bot Token
- Supabase проект

## Быстрый старт

1) Создайте и активируйте виртуальное окружение:

```bash
py -m venv .venv
.venv\Scripts\activate
```

2) Установите зависимости:

```bash
pip install -r requirements.txt
```

3) Скопируйте `.env.example` в `.env` и заполните:

```bash
copy .env.example .env
```

4) Заполните переменные в `.env`:

- `TELEGRAM_BOT_TOKEN` - токен бота из BotFather
- `TELEGRAM_MANAGER_CHAT_ID` - chat id менеджера для уведомлений
- `SUPABASE_URL` - URL проекта Supabase
- `SUPABASE_KEY` - API key (service role key для backend)
- `APP_ENV`, `APP_HOST`, `APP_PORT` - параметры FastAPI

5) Запустите проект:

```bash
py main.py
```

Приложение поднимет одновременно:
- Telegram polling-бота
- FastAPI сервер

## Как протестировать бота

- Откройте Telegram и найдите своего бота
- Нажмите `/start`
- Пройдите путь:
  - "Помощь в выборе" -> свободный текст
  - "Оставить заявку" -> заполните форму
- После отправки:
  - в Supabase должна появиться запись в `leads`
  - менеджер должен получить уведомление в Telegram

## Проверка сохранения через API

Отправьте тестовый запрос:

```bash
curl -X POST http://127.0.0.1:8000/api/leads/test ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Тест\",\"phone\":\"+77001112233\",\"volume\":\"2 куба\",\"desired_product\":\"Бетон В 22,5 (М300)\",\"comment\":\"Тест API\",\"source\":\"telegram\"}"
```

## Подключение Supabase (пошагово для новичка)

1. Зарегистрируйтесь на [Supabase](https://supabase.com/) и создайте новый проект.  
2. Откройте SQL Editor и выполните SQL:

```sql
create table if not exists public.leads (
  id bigserial primary key,
  name text not null,
  phone text not null,
  volume text not null,
  desired_product text not null,
  comment text,
  source text not null default 'telegram',
  created_at timestamptz not null default now()
);
```

3. Перейдите в `Project Settings -> API`:
   - скопируйте `Project URL` в `SUPABASE_URL`
   - скопируйте `service_role` key в `SUPABASE_KEY` (для backend, хранить только в `.env`)
4. Убедитесь, что `.env` заполнен и приложение перезапущено.
5. Отправьте тестовую заявку из бота или через `POST /api/leads/test`.
6. Проверьте таблицу `Table Editor -> leads`: там должна появиться новая строка.

## Структура

Проект разделен на слои: `core`, `data`, `models`, `repositories`, `services`, `bot`, `api`, `integrations`.
Это позволяет без полной переделки подключить Instagram/WhatsApp и AI-режим в следующих итерациях.
