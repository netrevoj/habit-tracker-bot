# Telegram Habit Tracker Bot

A simple and efficient Habit Tracker Bot built with Python using `aiogram 3.x` and `SQLite`.

## Features

- **Habit Management**: Add, list, and delete habits.
- **Daily Tracking**: Mark habits as completed each day.
- **Streaks**: Tracks current and best streaks for each habit.
- **Statistics**: View completion percentage and total completions.
- **User Friendly**: Interactive UI using Inline Keyboards.

## Prerequisites

- Python 3.8+
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd habit-tracker-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your `BOT_TOKEN`.

## Running the Bot

Run the bot using the following command:
```bash
python bot.py
```

## Project Structure

- `bot.py`: Entry point of the application.
- `config.py`: Configuration and environment variable management.
- `database/`: Database schema and asynchronous operations.
- `handlers/`: Telegram command and callback handlers.
- `keyboards/`: Inline keyboard definitions.
- `utils/`: Utility functions and FSM states.
