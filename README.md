# Sustrecha - Telegram Dating Bot

A Telegram bot for dating and networking among students (18-25 years old) with an invite-only system.

## Features

- Invite-only system with personal invite codes
- Profile management with required fields
- Random matching system
- Direct messaging after mutual interest
- Activity badges and gamification
- Moderation tools

## Setup

1. Clone the repository
2. Create a `.env` file with the following variables:
   ```
   BOT_TOKEN=your_telegram_bot_token
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sustrecha
   ```
3. Run with Docker:
   ```bash
   docker-compose up -d
   ```

## Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

4. Run the bot:
   ```bash
   python src/main.py
   ```
