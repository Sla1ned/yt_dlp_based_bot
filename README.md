# Telegram Video Downloader Bot

[🇬🇧 English](#english) | [🇷🇺 Русский](#русский)

---

<a id="english"></a>
## 🇬🇧 English

`aiogram 3` bot for downloading short videos from YouTube, TikTok, and Instagram.

### Features
- Download videos by link
- Paid subscription via Telegram Stars
- PostgreSQL for users and subscriptions
- Works in private chats and groups

### Setup

1. **Clone the repo:**
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Copy `.env.example` to `.env` and fill in:
   - `BOT_TOKEN` — get it from [@BotFather](https://t.me/BotFather)
   - `DB_URL` — PostgreSQL connection string
   - `REDIS_URL` — Redis connection string

4. **Start PostgreSQL and Redis:**
   ```bash
   docker compose up -d
   ```

5. **Run the bot:**
   ```bash
   python main.py
   ```

### Requirements
- Python 3.10+
- PostgreSQL 14+ & Redis 7+ (or Docker)
- `ffmpeg` (installed automatically via `imageio-ffmpeg`)

---

<a id="русский"></a>
## 🇷🇺 Русский

Telegram-бот на `aiogram 3` для скачивания коротких видео с YouTube, TikTok и Instagram.

### Возможности
- Скачивание видео по ссылке
- Платная подписка через Telegram Stars
- PostgreSQL для хранения пользователей и подписок
- Работа в личных сообщениях и группах

### Установка

1. **Клонируй репозиторий:**
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   ```

2. **Создай виртуальное окружение и установи зависимости:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Настрой переменные окружения:**
   Скопируй `.env.example` в `.env` и заполни:
   - `BOT_TOKEN` — получи у [@BotFather](https://t.me/BotFather)
   - `DB_URL` — строка подключения к PostgreSQL
   - `REDIS_URL` — строка подключения к Redis

4. **Запусти PostgreSQL и Redis:**
   ```bash
   docker compose up -d
   ```

5. **Запусти бота:**
   ```bash
   python main.py
   ```

### Требования
- Python 3.10+
- PostgreSQL 14+ и Redis 7+ (или Docker)
- `ffmpeg` (ставится автоматически через `imageio-ffmpeg`)

---

## License / Лицензия

MIT