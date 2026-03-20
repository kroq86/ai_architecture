# Telegram AI App

Python application for Telegram-based interaction with an OpenAI-backed coordinator.

## Project Structure

```text
src/telegram_ai_app/
  adapters/
  api/
  domain/
  llm/
  observability/
  utils/
```

## Requirements

- Python 3.9+
- valid `.env` file in the project root

## Setup

Run everything from the project root:

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Then edit `.env` and put in your real credentials.

## Main Run Mode: Polling

This is the default and recommended way to run the app locally.

```bash
source .venv/bin/activate
export TELEGRAM_MODE=polling
PYTHONPATH=src python -m telegram_ai_app
```

Expected startup log:

```text
starting polling mode
```

## Alternative Run Mode: Webhook

```bash
source .venv/bin/activate
export TELEGRAM_MODE=webhook
export WEBHOOK_BASE_URL=https://your-public-domain.example
PYTHONPATH=src python -m telegram_ai_app
```

In webhook mode the process keeps running as an HTTP server.
Expected startup log:

```text
webhook server listening on http://0.0.0.0:8080
```

Webhook mode requires a public base URL so Telegram can reach your app.
If `WEBHOOK_BASE_URL` is missing, the app now exits immediately with an error.

## Run Tests

```bash
source .venv/bin/activate
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Environment

Expected configuration is loaded from `.env`.
Use `.env.example` as the template.

Required variables:

- `OPENAI_API_KEY`
- `OPENAI_MODEL` or `OAPENAI_MODEL`
- `TELEGRAM_BOT_TOKEN`

Optional variables:

- `OPENAI_SYSTEM_PROMPT`
- `PROGRAMMING_LANGUAGE`
- `TELEGRAM_CHAT_ID`
- `TELEGRAM_MODE`
- `WEBHOOK_BASE_URL`
- `HOST`
- `PORT`
- `POLL_TIMEOUT_SEC`
- `DATABASE_PATH`
- `LOG_LEVEL`

## Notes

- The app stores chat history in a local SQLite database.
- The main local runtime mode is `polling`.
- Long responses are split into Telegram-safe chunks.
- In Telegram groups, regular messages may be hidden from the bot by privacy mode. Direct chat is the simplest way to test message handling.
