import os
from dataclasses import dataclass
from pathlib import Path

from telegram_ai_app.utils.env_loader import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    openai_api_key: str
    openai_model: str
    openai_system_prompt: str
    programming_language: str
    telegram_bot_token: str
    telegram_chat_id: str
    telegram_mode: str
    webhook_base_url: str
    host: str
    port: int
    poll_timeout_sec: int
    database_path: str
    log_level: str


def load_config() -> AppConfig:
    load_dotenv(Path(".env"))
    model = os.getenv("OPENAI_MODEL") or os.getenv("OAPENAI_MODEL")
    data = {
        "openai_api_key": _require("OPENAI_API_KEY"),
        "openai_model": model or _missing("OPENAI_MODEL"),
        "openai_system_prompt": os.getenv("OPENAI_SYSTEM_PROMPT", "Give a brief useful answer."),
        "programming_language": os.getenv("PROGRAMMING_LANGUAGE", "python"),
        "telegram_bot_token": _require("TELEGRAM_BOT_TOKEN"),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
        "telegram_mode": os.getenv("TELEGRAM_MODE", "polling"),
        "webhook_base_url": os.getenv("WEBHOOK_BASE_URL", ""),
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8080")),
        "poll_timeout_sec": int(os.getenv("POLL_TIMEOUT_SEC", "30")),
        "database_path": os.getenv("DATABASE_PATH", "app.db"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }
    return AppConfig(**data)


def _require(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    return _missing(name)


def _missing(name: str) -> str:
    raise RuntimeError(f"Missing required environment variable: {name}")
