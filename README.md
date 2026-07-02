# Telegram Face Analysis Bot

This is a comprehensive face geometry analysis bot for Telegram. It combines facial landmarks detection, algorithmic metric analysis, AI-generated text synthesis, and PDF report generation.

## Project Structure
- `face_analysis/`: Stage 1 - MediaPipe landmarks, validation, and math models.
- `report/`: Stage 2 - OpenAI text generation and WeasyPrint PDF layout.
- `bot/`: Stage 3 - aiogram 3.x Telegram interface, background queue, database.

## Prerequisites
- Python 3.11+
- PostgreSQL
- Redis
- An OpenAI API Key
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- A Payment Provider Token (e.g. Telegram Stars or Stripe, from BotFather)

## Setup Instructions

1. **Environment Variables**
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Fill in all the required tokens (`TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, etc.).

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Running in Development (Polling Mode)**
   Ensure `WEBHOOK_URL` in `.env` is empty.
   ```bash
   PYTHONPATH=. python bot/main.py
   ```
   This will automatically create the database tables using SQLAlchemy async engine.

4. **Running in Production (Webhook Mode)**
   Set your `WEBHOOK_URL` in `.env` (e.g. `https://your-domain.com/webhook`).
   Run the bot. It will launch an aiohttp server on `WEBHOOK_PORT`.

5. **Using Docker**
   You can easily launch the database, redis, and the bot using Docker Compose:
   ```bash
   docker-compose up --build -d
   ```
