from typing import List

from telegram_ai_app.config import AppConfig
from telegram_ai_app.domain.models import ConversationTurn, InboundMessage


class PromptBuilder:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def build_messages(
        self,
        inbound: InboundMessage,
        history: List[ConversationTurn],
    ) -> List[dict]:
        system = (
            f"{self.config.openai_system_prompt}\n"
            f"Programming language context: {self.config.programming_language}.\n"
            "Answer for Telegram chat. Keep it concise, clear, and useful."
        )
        messages = [{"role": "system", "content": system}]
        for turn in history[-10:]:
            messages.append({"role": turn.role, "content": turn.content})
        messages.append({"role": "user", "content": inbound.text})
        return messages
