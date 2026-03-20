import asyncio
import os
import sqlite3
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from telegram_ai_app.api.polling import PollingRunner
from telegram_ai_app.api.webhook import WebhookRunner
from telegram_ai_app.bootstrap import AppRuntime, create_runtime
from telegram_ai_app.config import AppConfig, load_config
from telegram_ai_app.domain.coordinator import Coordinator
from telegram_ai_app.domain.models import ConversationTurn, InboundMessage, OutboundMessage
from telegram_ai_app.domain.prompt_builder import PromptBuilder
from telegram_ai_app.domain.renderer import Renderer
from telegram_ai_app.domain.session_store import SessionStore
from telegram_ai_app.adapters.telegram_client import TelegramClient
from telegram_ai_app.llm.openai_client import OpenAIClient


class TopicsImplementationRuntimeTests(unittest.TestCase):
    def _make_config(self, **overrides):
        base = AppConfig(
            openai_api_key="key",
            openai_model="gpt-4o-mini",
            openai_system_prompt="Assist briefly.",
            programming_language="python",
            telegram_bot_token="token",
            telegram_chat_id="-100",
            telegram_mode="polling",
            webhook_base_url="",
            host="0.0.0.0",
            port=8080,
            poll_timeout_sec=30,
            database_path=":memory:",
            log_level="INFO",
        )
        return replace(base, **overrides)

    def test_top_imp_022_and_023_load_config_supports_alias_and_defaults(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {}, clear=True):
            Path(tmp, ".env").write_text(
                "\n".join(
                    [
                        "OPENAI_API_KEY=abc123",
                        "OAPENAI_MODEL=gpt-4o-mini",
                        "TELEGRAM_BOT_TOKEN=bot-token",
                        "OPENAI_SYSTEM_PROMPT=Custom prompt.",
                        "PROGRAMMING_LANGUAGE=python",
                    ]
                ),
                encoding="utf-8",
            )
            cwd = os.getcwd()
            try:
                os.chdir(tmp)
                config = load_config()
            finally:
                os.chdir(cwd)

        self.assertEqual(config.openai_model, "gpt-4o-mini")
        self.assertEqual(config.openai_system_prompt, "Custom prompt.")
        self.assertEqual(config.programming_language, "python")

    def test_top_imp_024_missing_required_env_fails_fast(self):
        with patch("telegram_ai_app.config.load_dotenv", lambda _: None), patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                load_config()

    def test_top_imp_006_create_runtime_builds_app_runtime(self):
        config = self._make_config()
        with patch("telegram_ai_app.bootstrap.load_config", return_value=config), patch(
            "telegram_ai_app.bootstrap.configure_logging"
        ) as configure_logging:
            runtime = create_runtime()

        self.assertIsInstance(runtime, AppRuntime)
        self.assertEqual(runtime.config.telegram_mode, "polling")
        configure_logging.assert_called_once_with("INFO")

    def test_top_imp_007_app_runtime_uses_polling_when_configured(self):
        config = self._make_config(telegram_mode="polling")
        with patch("telegram_ai_app.bootstrap.PollingRunner") as polling_runner, patch(
            "telegram_ai_app.bootstrap.WebhookRunner"
        ) as webhook_runner:
            polling_instance = MagicMock()
            polling_instance.run = AsyncMock()
            polling_runner.return_value = polling_instance
            webhook_runner.return_value = MagicMock()
            runtime = AppRuntime(config)
            asyncio.run(runtime.run())

        polling_runner.assert_called_once()
        webhook_runner.assert_called_once()
        webhook_runner.return_value.run.assert_not_called()
        polling_instance.run.assert_awaited_once()

    def test_top_imp_008_and_030_webhook_requires_public_url(self):
        config = self._make_config(telegram_mode="webhook", webhook_base_url="")
        runner = WebhookRunner(config, MagicMock(), MagicMock())
        with self.assertRaises(RuntimeError):
            asyncio.run(runner.run())

    def test_top_imp_005_session_store_round_trip_persists_turns(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "app.db")
            store = SessionStore(db_path)
            store.save_turns(
                "telegram:1:2",
                [
                    ConversationTurn(role="user", content="hello"),
                    ConversationTurn(role="assistant", content="world"),
                ],
            )
            history = store.load_history("telegram:1:2")

        self.assertEqual(history[0].role, "user")
        self.assertEqual(history[0].content, "hello")
        self.assertEqual(history[1].role, "assistant")
        self.assertEqual(history[1].content, "world")

    def test_top_imp_010_and_012_telegram_message_normalization_and_session_key(self):
        client = TelegramClient(self._make_config())
        inbound = client.parse_update(
            {
                "message": {
                    "message_id": 42,
                    "text": "Hello",
                    "chat": {"id": -752707591},
                    "from": {"id": 274703604},
                }
            }
        )

        self.assertIsNotNone(inbound)
        self.assertEqual(inbound.chat_id, "-752707591")
        self.assertEqual(inbound.user_id, "274703604")
        self.assertEqual(inbound.session_key, "telegram:-752707591:274703604")

    def test_top_imp_009_invalid_telegram_update_is_ignored(self):
        client = TelegramClient(self._make_config())
        self.assertIsNone(client.parse_update({"message": {"chat": {}, "from": {}}}))

    def test_top_imp_020_and_021_renderer_chunks_and_fallback(self):
        renderer = Renderer()
        self.assertEqual(renderer.render("")[0], "I could not produce a response.")

        chunks = renderer.render("a" * 9001)
        self.assertEqual(len(chunks), 3)
        self.assertTrue(all(len(chunk) <= 4000 for chunk in chunks))

    def test_top_imp_004_prompt_builder_uses_system_prompt_language_and_last_10_turns(self):
        builder = PromptBuilder(self._make_config(openai_system_prompt="Use concise responses."))
        history = [ConversationTurn(role="assistant" if i % 2 else "user", content=f"turn-{i}") for i in range(12)]
        messages = builder.build_messages(
            InboundMessage(
                chat_id="1",
                user_id="2",
                message_id="3",
                text="final question",
                session_key="telegram:1:2",
            ),
            history,
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Use concise responses.", messages[0]["content"])
        self.assertIn("Programming language context: python.", messages[0]["content"])
        self.assertEqual(messages[-1]["content"], "final question")
        self.assertEqual(len(messages), 1 + 10 + 1)

    def test_top_imp_002_and_003_coordinator_persists_and_calls_llm(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = SessionStore(str(Path(tmp) / "app.db"))
            builder = PromptBuilder(self._make_config())
            llm = SimpleNamespace(create_response=AsyncMock(return_value="reply"))
            renderer = Renderer()
            coordinator = Coordinator(builder, llm, renderer, store)
            outbound = asyncio.run(
                coordinator.handle(
                    InboundMessage(
                        chat_id="7",
                        user_id="8",
                        message_id="9",
                        text="ping",
                        session_key="telegram:7:8",
                    )
                )
            )
            history = store.load_history("telegram:7:8")

        self.assertEqual(len(outbound), 1)
        self.assertEqual(outbound[0], OutboundMessage(chat_id="7", text="reply"))
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].role, "user")
        self.assertEqual(history[1].role, "assistant")

    def test_top_imp_017_openai_client_delegates_to_openai_sdk(self):
        config = self._make_config()
        fake_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="short answer"))]
        )
        async_create = AsyncMock(return_value=fake_response)
        fake_api = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=async_create)))

        with patch("telegram_ai_app.llm.openai_client.AsyncOpenAI", return_value=fake_api) as client_cls:
            client = OpenAIClient(config)
            result = asyncio.run(client.create_response([{"role": "user", "content": "hi"}]))

        client_cls.assert_called_once_with(api_key="key")
        async_create.assert_awaited_once()
        self.assertEqual(result, "short answer")

    def test_top_imp_011_polling_runner_deletes_webhook_and_processes_updates(self):
        config = self._make_config()
        telegram = SimpleNamespace(
            delete_webhook=AsyncMock(),
            get_updates=AsyncMock(
                side_effect=[
                    [
                        {
                            "update_id": 5,
                            "message": {
                                "message_id": 11,
                                "text": "/start",
                                "chat": {"id": 1},
                                "from": {"id": 2},
                            },
                        }
                    ]
                ]
            ),
            parse_update=MagicMock(
                return_value=InboundMessage(
                    chat_id="1",
                    user_id="2",
                    message_id="11",
                    text="/start",
                    session_key="telegram:1:2",
                )
            ),
            send_message=AsyncMock(),
        )
        coordinator = SimpleNamespace(handle=AsyncMock(return_value=[OutboundMessage(chat_id="1", text="ok")]))
        runner = PollingRunner(config, coordinator, telegram)

        async def stop_after_first_sleep(*_args, **_kwargs):
            raise asyncio.CancelledError()

        with patch("telegram_ai_app.api.polling.asyncio.sleep", side_effect=stop_after_first_sleep):
            with self.assertRaises(asyncio.CancelledError):
                asyncio.run(runner.run())

        telegram.delete_webhook.assert_awaited_once()
        telegram.get_updates.assert_awaited()
        telegram.parse_update.assert_called_once()
        coordinator.handle.assert_awaited_once()
        telegram.send_message.assert_awaited_once()

    def test_top_imp_008_webhook_handle_update_sends_reply(self):
        config = self._make_config(telegram_mode="webhook", webhook_base_url="https://example.test")
        telegram = SimpleNamespace(
            set_webhook=AsyncMock(),
            send_message=AsyncMock(),
            parse_update=MagicMock(
                return_value=InboundMessage(
                    chat_id="10",
                    user_id="20",
                    message_id="30",
                    text="hello",
                    session_key="telegram:10:20",
                )
            ),
        )
        coordinator = SimpleNamespace(handle=AsyncMock(return_value=[OutboundMessage(chat_id="10", text="reply")]))
        runner = WebhookRunner(config, coordinator, telegram)

        class Request:
            async def json(self):
                return {"message": {"text": "hello"}}

        response = asyncio.run(runner.handle_update(Request()))

        self.assertEqual(response.status, 200)
        telegram.parse_update.assert_called_once()
        coordinator.handle.assert_awaited_once()
        telegram.send_message.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
