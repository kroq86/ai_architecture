import logging
from typing import List

from telegram_ai_app.domain.models import ConversationTurn, InboundMessage, OutboundMessage

logger = logging.getLogger(__name__)


class Coordinator:
    def __init__(self, builder, llm, renderer, store) -> None:
        self.builder = builder
        self.llm = llm
        self.renderer = renderer
        self.store = store

    async def handle(self, inbound: InboundMessage) -> List[OutboundMessage]:
        history = self.store.load_history(inbound.session_key)
        prompt = self.builder.build_messages(inbound, history)
        answer = await self.llm.create_response(prompt)
        self.store.save_turns(
            inbound.session_key,
            [
                ConversationTurn(role="user", content=inbound.text),
                ConversationTurn(role="assistant", content=answer),
            ],
        )
        logger.info("handled message", extra={"chat_id": inbound.chat_id})
        return [OutboundMessage(chat_id=inbound.chat_id, text=part) for part in self.renderer.render(answer)]
