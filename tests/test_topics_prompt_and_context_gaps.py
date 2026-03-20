"""Prompt/context architecture traceability tests for Docs/topics/.

The goal of this file is to keep the architecture promises visible as tests:
implemented behavior stays green, missing behavior is encoded as explicit
expected failures with matrix IDs in the test names.
"""

from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


from telegram_ai_app.config import AppConfig
from telegram_ai_app.domain.coordinator import Coordinator
from telegram_ai_app.domain.models import ConversationTurn, InboundMessage
from telegram_ai_app.domain.prompt_builder import PromptBuilder
from telegram_ai_app.domain.session_store import SessionStore


def make_config(**overrides):
    data = dict(
        openai_api_key="test-key",
        openai_model="gpt-4o-mini",
        openai_system_prompt="Give a brief and useful answer.",
        programming_language="python",
        telegram_bot_token="telegram-token",
        telegram_chat_id="-1",
        telegram_mode="polling",
        webhook_base_url="",
        host="0.0.0.0",
        port=8080,
        poll_timeout_sec=30,
        database_path="app.db",
        log_level="INFO",
    )
    data.update(overrides)
    return AppConfig(**data)


def make_inbound(text="hello"):
    return InboundMessage(
        chat_id="10",
        user_id="20",
        message_id="30",
        text=text,
        session_key="telegram:10:20",
    )


class PromptArchitectureTests(unittest.TestCase):
    def test_TOP_PROMPT_001_system_prompt_and_recent_context_window(self):
        builder = PromptBuilder(
            make_config(
                openai_system_prompt="Follow the rules exactly.",
                programming_language="python",
            )
        )
        history = [ConversationTurn(role="user", content=f"turn-{i}") for i in range(12)]
        messages = builder.build_messages(make_inbound("current"), history)

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Follow the rules exactly.", messages[0]["content"])
        self.assertIn("Programming language context: python.", messages[0]["content"])
        self.assertIn(
            "Answer for Telegram chat. Keep it concise, clear, and useful.",
            messages[0]["content"],
        )
        self.assertEqual([item["content"] for item in messages[1:-1]], [t.content for t in history[-10:]])
        self.assertEqual(messages[-1]["role"], "user")
        self.assertEqual(messages[-1]["content"], "current")

    @unittest.expectedFailure
    def test_TOP_PROMPT_002_structured_output_contract_is_explicit(self):
        builder = PromptBuilder(make_config())
        messages = builder.build_messages(make_inbound(), [])
        self.assertIn("response_format", messages[0])

    @unittest.expectedFailure
    def test_TOP_PROMPT_003_nullable_schema_fields_are_exposed(self):
        builder = PromptBuilder(make_config())
        self.assertTrue(hasattr(builder, "output_schema"))

    @unittest.expectedFailure
    def test_TOP_PROMPT_004_validation_retry_loop_is_present(self):
        self.assertTrue(hasattr(Coordinator, "retry_with_validation_error"))

    @unittest.expectedFailure
    def test_TOP_PROMPT_005_few_shot_examples_can_be_injected(self):
        builder = PromptBuilder(make_config())
        self.assertTrue(hasattr(builder, "build_examples"))


class ContextArchitectureTests(unittest.TestCase):
    def test_TOP_CONTEXT_001_session_store_round_trip_persists_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "app.db")
            store = SessionStore(db_path)
            turns = [
                ConversationTurn(role="user", content="hello"),
                ConversationTurn(role="assistant", content="world"),
            ]
            store.save_turns("telegram:10:20", turns)
            self.assertEqual(store.load_history("telegram:10:20"), turns)

    def test_TOP_CONTEXT_006_history_is_truncated_to_recent_window(self):
        builder = PromptBuilder(make_config())
        history = [ConversationTurn(role="assistant", content=f"old-{i}") for i in range(12)]
        messages = builder.build_messages(make_inbound("fresh"), history)

        self.assertEqual([item["content"] for item in messages[1:-1]], [turn.content for turn in history[-10:]])
        self.assertEqual(messages[-1]["content"], "fresh")

    @unittest.expectedFailure
    def test_TOP_CONTEXT_002_persistent_facts_api_is_separate_from_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = SessionStore(str(Path(tmp) / "app.db"))
        self.assertTrue(hasattr(store, "save_facts"))
        self.assertTrue(hasattr(store, "load_facts"))

    @unittest.expectedFailure
    def test_TOP_CONTEXT_003_escalation_policy_is_rule_based(self):
        config = make_config()
        self.assertTrue(hasattr(config, "escalation_policy"))

    @unittest.expectedFailure
    def test_TOP_CONTEXT_004_structured_error_payloads_include_partial_results(self):
        self.assertTrue(hasattr(Coordinator, "build_error_payload"))

    @unittest.expectedFailure
    def test_TOP_CONTEXT_005_access_failure_is_distinct_from_empty_result(self):
        self.assertTrue(hasattr(Coordinator, "distinguish_empty_result_from_failure"))

    @unittest.expectedFailure
    def test_TOP_CONTEXT_006_scratchpad_and_manifest_support_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = SessionStore(str(Path(tmp) / "app.db"))
        self.assertTrue(hasattr(store, "save_manifest"))
        self.assertTrue(hasattr(store, "load_manifest"))

    @unittest.expectedFailure
    def test_TOP_CONTEXT_007_segmented_metrics_are_available(self):
        self.assertTrue(hasattr(Coordinator, "record_segmented_metrics"))

    @unittest.expectedFailure
    def test_TOP_CONTEXT_008_confidence_thresholds_are_configurable(self):
        config = make_config()
        self.assertTrue(hasattr(config, "confidence_thresholds"))

    @unittest.expectedFailure
    def test_TOP_CONTEXT_009_provenance_is_preserved_through_synthesis(self):
        self.assertTrue(hasattr(Coordinator, "preserve_provenance"))

    @unittest.expectedFailure
    def test_TOP_CONTEXT_010_conflicting_sources_are_retained(self):
        self.assertTrue(hasattr(Coordinator, "retain_conflicting_sources"))


if __name__ == "__main__":
    unittest.main()
