from telegram_ai_app.api.polling import PollingRunner
from telegram_ai_app.api.webhook import WebhookRunner
from telegram_ai_app.config import AppConfig, load_config
from telegram_ai_app.domain.coordinator import Coordinator
from telegram_ai_app.domain.prompt_builder import PromptBuilder
from telegram_ai_app.domain.renderer import Renderer
from telegram_ai_app.domain.session_store import SessionStore
from telegram_ai_app.llm.openai_client import OpenAIClient
from telegram_ai_app.observability.logging import configure_logging
from telegram_ai_app.adapters.telegram_client import TelegramClient


class AppRuntime:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.store = SessionStore(config.database_path)
        self.telegram = TelegramClient(config)
        self.llm = OpenAIClient(config)
        self.builder = PromptBuilder(config)
        self.renderer = Renderer()
        self.coordinator = Coordinator(self.builder, self.llm, self.renderer, self.store)

    async def run(self) -> None:
        runner = WebhookRunner(self.config, self.coordinator, self.telegram)
        if self.config.telegram_mode == "polling":
            runner = PollingRunner(self.config, self.coordinator, self.telegram)
        await runner.run()


def create_runtime() -> AppRuntime:
    config = load_config()
    configure_logging(config.log_level)
    return AppRuntime(config)
