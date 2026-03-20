import importlib
from pathlib import Path
import unittest


MATRIX_PATH = Path(__file__).with_name("TOPICS_TEST_MATRIX.md")
TOOL_MATRIX_IDS = [
    "TOP-TOOL-001",
    "TOP-TOOL-002",
    "TOP-TOOL-003",
    "TOP-TOOL-004",
    "TOP-TOOL-005",
    "TOP-TOOL-006",
    "TOP-TOOL-007",
    "TOP-TOOL-008",
    "TOP-TOOL-009",
    "TOP-TOOL-010",
]


class ToolingMatrixTraceabilityTests(unittest.TestCase):
    def test_matrix_includes_all_tooling_ids(self) -> None:
        text = MATRIX_PATH.read_text(encoding="utf-8")
        for matrix_id in TOOL_MATRIX_IDS:
            with self.subTest(matrix_id=matrix_id):
                self.assertIn(matrix_id, text)


class ToolingArchitectureGapTests(unittest.TestCase):
    def _require_module(self, module_name: str, matrix_id: str):
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            self.fail(f"{matrix_id}: expected `{module_name}` to exist, but it is missing: {exc}")

    @unittest.expectedFailure
    def test_top_tool_001_descriptions_include_selection_boundaries(self) -> None:
        module = self._require_module("telegram_ai_app.tools.registry", "TOP-TOOL-001")
        descriptions = getattr(module, "TOOL_DESCRIPTIONS")
        self.assertTrue(
            any("do not use" in text.lower() or "when not to use" in text.lower() for text in descriptions.values())
        )

    @unittest.expectedFailure
    def test_top_tool_002_misrouting_is_prevented_by_description_quality(self) -> None:
        module = self._require_module("telegram_ai_app.tools.router", "TOP-TOOL-002")
        decision = module.route("lookup_order", {"query": "abc"})
        self.assertEqual(decision.tool_name, "lookup_order")

    @unittest.expectedFailure
    def test_top_tool_003_empty_result_is_not_treated_as_failure(self) -> None:
        module = self._require_module("telegram_ai_app.tools.errors", "TOP-TOOL-003")
        result = module.ToolResult(success=True, is_error=False, payload=[], metadata={})
        self.assertFalse(result.is_error)
        self.assertEqual(result.payload, [])

    @unittest.expectedFailure
    def test_top_tool_004_retryable_errors_are_classified(self) -> None:
        module = self._require_module("telegram_ai_app.tools.errors", "TOP-TOOL-004")
        error = module.ToolError(category="transient", is_retryable=True, message="temporary failure")
        self.assertTrue(error.is_retryable)
        self.assertEqual(error.category, "transient")

    @unittest.expectedFailure
    def test_top_tool_005_agents_receive_scoped_toolsets(self) -> None:
        module = self._require_module("telegram_ai_app.tools.policy", "TOP-TOOL-005")
        scoped = module.scope_tools_for_role("synthesis")
        self.assertLessEqual(len(scoped), 5)

    @unittest.expectedFailure
    def test_top_tool_006_tool_choice_modes_are_supported(self) -> None:
        module = self._require_module("telegram_ai_app.tools.policy", "TOP-TOOL-006")
        self.assertIn(module.ToolChoiceMode.FORCED, module.ToolChoiceMode)

    @unittest.expectedFailure
    def test_top_tool_007_pre_execution_hooks_enforce_policy(self) -> None:
        module = self._require_module("telegram_ai_app.tools.hooks", "TOP-TOOL-007")
        allowed = module.before_tool_execution({"name": "dangerous"}, {"allow": False})
        self.assertFalse(allowed)

    @unittest.expectedFailure
    def test_top_tool_008_post_execution_hooks_normalize_output(self) -> None:
        module = self._require_module("telegram_ai_app.tools.hooks", "TOP-TOOL-008")
        normalized = module.after_tool_execution({"date": "2026-03-20T00:00:00Z"})
        self.assertIn("date", normalized)

    @unittest.expectedFailure
    def test_top_tool_009_secrets_are_not_embedded_in_shared_config(self) -> None:
        module = self._require_module("telegram_ai_app.tools.config", "TOP-TOOL-009")
        config_text = module.render_shared_tool_config()
        self.assertNotIn("sk-", config_text)

    @unittest.expectedFailure
    def test_top_tool_010_incremental_discovery_is_used_for_exploration(self) -> None:
        module = self._require_module("telegram_ai_app.tools.discovery", "TOP-TOOL-010")
        plan = module.build_incremental_discovery_plan(["caller", "export", "wrapper"])
        self.assertEqual(plan[0], "grep")
