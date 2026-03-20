import aiohttp
from typing import Optional
import logging

from telegram_ai_app.domain.models import InboundMessage, OutboundMessage

logger = logging.getLogger(__name__)


class TelegramClient:
    def __init__(self, config) -> None:
        self.base_url = f"https://api.telegram.org/bot{config.telegram_bot_token}"
        self.timeout_sec = config.poll_timeout_sec

    async def get_updates(self, offset: Optional[int]) -> list:
        payload = {"timeout": self.timeout_sec}
        if offset is not None:
            payload["offset"] = offset
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/getUpdates", json=payload) as response:
                data = await response.json()
        return data.get("result", [])

    async def send_message(self, message: OutboundMessage) -> None:
        payload = {"chat_id": message.chat_id, "text": message.text}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/sendMessage", json=payload) as response:
                response.raise_for_status()

    async def set_webhook(self, webhook_url: str) -> None:
        payload = {"url": webhook_url}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/setWebhook", json=payload) as response:
                response.raise_for_status()

    async def delete_webhook(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/deleteWebhook", json={"drop_pending_updates": False}) as response:
                response.raise_for_status()

    def parse_update(self, update: dict) -> Optional[InboundMessage]:
        message = update.get("message") or {}
        text = message.get("text")
        chat = message.get("chat") or {}
        user = message.get("from") or {}
        if not text or "id" not in chat or "id" not in user:
            return None
        chat_id = str(chat["id"])
        user_id = str(user["id"])
        return InboundMessage(
            chat_id=chat_id,
            user_id=user_id,
            message_id=str(message.get("message_id", "")),
            text=text,
            session_key=f"telegram:{chat_id}:{user_id}",
        )
