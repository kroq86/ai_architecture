import asyncio
import logging

logger = logging.getLogger(__name__)


class PollingRunner:
    def __init__(self, config, coordinator, telegram) -> None:
        self.coordinator = coordinator
        self.telegram = telegram
        self.offset = None

    async def run(self) -> None:
        await self.telegram.delete_webhook()
        logger.info("starting polling mode")
        while True:
            updates = await self.telegram.get_updates(self.offset)
            if updates:
                logger.info("received %s telegram update(s)", len(updates))
            for update in updates:
                self.offset = update["update_id"] + 1
                inbound = self.telegram.parse_update(update)
                if inbound is None:
                    continue
                logger.info("processing message chat_id=%s text=%r", inbound.chat_id, inbound.text)
                for outbound in await self.coordinator.handle(inbound):
                    await self.telegram.send_message(outbound)
                    logger.info("sent reply to chat_id=%s", outbound.chat_id)
            await asyncio.sleep(1)
