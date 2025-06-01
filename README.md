# Sustrecha - Telegram Dating Bot

A Telegram bot for networking, communication and dating among students (18-25 years old) with an invite-only system. (specifically in Belarus)

## Features

- Invite-only system with personal invite codes
- Profile management with required fields
- Random matching system
- Exchange of contacts for mutual sympathy
- Ai chatting feature
- Moderation tools

## Setup

1. Clone the repository
2. Create a `.env` file with the following variables:
   ```
   BOT_TOKEN=your_telegram_bot_token
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sustrecha
   etc...
   ```
3. Run with Docker:
   ```bash
   docker-compose up -d
   ```
