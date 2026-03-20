import asyncio
import logging

from aiohttp import web

logger = logging.getLogger(__name__)


class WebhookRunner:
    def __init__(self, config, coordinator, telegram) -> None:
        self.config = config
        self.coordinator = coordinator
        self.telegram = telegram

    async def run(self) -> None:
        if not self.config.webhook_base_url:
            raise RuntimeError("WEBHOOK_BASE_URL is required when TELEGRAM_MODE=webhook")
        app = web.Application()
        app.router.add_get("/health", self.handle_health)
        app.router.add_post("/telegram/webhook", self.handle_update)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=self.config.host, port=self.config.port)
        await site.start()
        if self.config.webhook_base_url:
            webhook_url = f"{self.config.webhook_base_url.rstrip('/')}/telegram/webhook"
            await self.telegram.set_webhook(webhook_url)
            logger.info("webhook registered at %s", webhook_url)
        logger.info("webhook server listening on http://%s:%s", self.config.host, self.config.port)
        await asyncio.Event().wait()

    async def handle_update(self, request: web.Request) -> web.Response:
        update = await request.json()
        inbound = self.telegram.parse_update(update)
        if inbound is not None:
            logger.info("received webhook message chat_id=%s text=%r", inbound.chat_id, inbound.text)
            for outbound in await self.coordinator.handle(inbound):
                await self.telegram.send_message(outbound)
                logger.info("sent reply to chat_id=%s", outbound.chat_id)
        return web.json_response({"ok": True})

    async def handle_health(self, request: web.Request) -> web.Response:
        return web.json_response({"ok": True, "mode": "webhook"})
