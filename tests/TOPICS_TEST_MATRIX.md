# Topics Test Matrix

Scope of this matrix:

- only files under `Docs/topics/`
- no requirements from `Docs/` root-level documents

Purpose:

- turn topic architecture requirements into traceable test targets
- assign stable IDs for future tests
- separate `implemented`, `partial`, and `missing` behavior

Status meanings:

- `implemented`: behavior exists and can be tested now
- `partial`: some behavior exists, but coverage is incomplete
- `missing`: requirement not implemented yet

## Source Files

- `Docs/topics/IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM.md`
- `Docs/topics/TOOL_DESIGN_AND_MCP_INTEGRATION.md`
- `Docs/topics/PROMPT_ENGINEERING_AND_STRUCTURED_OUTPUT.md`
- `Docs/topics/CONTEXT_MANAGEMENT_AND_RELIABILITY.md`

## Matrix

| ID | Source | Requirement Target | Planned Test Focus | Status |
| --- | --- | --- | --- | --- |
| TOP-IMP-001 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Telegram inbound message is accepted | polling/webhook adapter accepts update | implemented |
| TOP-IMP-002 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Request is passed into Python coordinator runtime | adapter -> coordinator handoff | implemented |
| TOP-IMP-003 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | OpenAI is used as primary reasoning engine | OpenAI client invocation | implemented |
| TOP-IMP-004 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Response is returned back to Telegram | outbound send_message path | implemented |
| TOP-IMP-005 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | State is stored outside prompt history | SQLite persistence of turns | implemented |
| TOP-IMP-006 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | App is modular, not one root file | package/module layout assertions | implemented |
| TOP-IMP-007 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Local development uses polling | polling runner startup/default mode | implemented |
| TOP-IMP-008 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Production path supports webhook mode | webhook startup and route exposure | partial |
| TOP-IMP-009 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Telegram adapter validates update shape | invalid update ignored safely | implemented |
| TOP-IMP-010 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Telegram adapter normalizes chat/user/message IDs | inbound normalization contract | implemented |
| TOP-IMP-011 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Telegram command messages are accepted | `/start` style input path | partial |
| TOP-IMP-012 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Session key uses `telegram:{chat_id}:{user_id}` | session-key format | implemented |
| TOP-IMP-013 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Session history loads and persists | load/save round-trip | implemented |
| TOP-IMP-014 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Coordinator classifies and processes request | coordinator main flow | partial |
| TOP-IMP-015 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Coordinator supports tool-assisted flow | tool call loop | missing |
| TOP-IMP-016 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | OpenAI client encapsulates provider interaction | provider hidden behind client module | implemented |
| TOP-IMP-017 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | OpenAI client handles retries/timeouts/rate limits | provider retry policy | missing |
| TOP-IMP-018 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Tool gateway exists as a separate layer | tool registry/executor module | missing |
| TOP-IMP-019 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Validation layer exists | dedicated validation module | missing |
| TOP-IMP-020 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Renderer chunks long Telegram-safe responses | chunking and message limits | implemented |
| TOP-IMP-021 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Renderer escapes Telegram formatting correctly | markdown/html escaping | missing |
| TOP-IMP-022 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Config is env-driven, not hardcoded | config loader behavior | implemented |
| TOP-IMP-023 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Config supports `OAPENAI_MODEL` compatibility alias | alias fallback behavior | implemented |
| TOP-IMP-024 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Missing required env vars fail fast | startup config failure | partial |
| TOP-IMP-025 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Secrets are not logged raw | redaction discipline | missing |
| TOP-IMP-026 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Structured logging exists | log bootstrap behavior | implemented |
| TOP-IMP-027 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Metrics/tracing layer exists | observability modules and hooks | missing |
| TOP-IMP-028 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Telegram dedupe/idempotency exists | duplicate update suppression | missing |
| TOP-IMP-029 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Error fallback message is safe | safe user-facing fallback | missing |
| TOP-IMP-030 | IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM | Webhook requires public base URL | startup failure without `WEBHOOK_BASE_URL` | implemented |
| TOP-TOOL-001 | TOOL_DESIGN_AND_MCP_INTEGRATION | Tool descriptions clearly define purpose and boundaries | tool descriptions quality assertions | missing |
| TOP-TOOL-002 | TOOL_DESIGN_AND_MCP_INTEGRATION | Tool misrouting should be reduced by better descriptions | routing regression fixture | missing |
| TOP-TOOL-003 | TOOL_DESIGN_AND_MCP_INTEGRATION | Tool errors must distinguish failure from empty result | result/error contract tests | missing |
| TOP-TOOL-004 | TOOL_DESIGN_AND_MCP_INTEGRATION | Retryable vs permanent tool errors are classified | error taxonomy tests | missing |
| TOP-TOOL-005 | TOOL_DESIGN_AND_MCP_INTEGRATION | Agents should have small scoped toolsets | allowed tool scope checks | missing |
| TOP-TOOL-006 | TOOL_DESIGN_AND_MCP_INTEGRATION | Forced/optional tool choice modes are supported | loop/tool-choice behavior | missing |
| TOP-TOOL-007 | TOOL_DESIGN_AND_MCP_INTEGRATION | Pre-execution hooks enforce policy | interception hook tests | missing |
| TOP-TOOL-008 | TOOL_DESIGN_AND_MCP_INTEGRATION | Post-execution hooks normalize tool outputs | normalization hook tests | missing |
| TOP-TOOL-009 | TOOL_DESIGN_AND_MCP_INTEGRATION | Secrets are not embedded in shared tool config | config hygiene checks | partial |
| TOP-TOOL-010 | TOOL_DESIGN_AND_MCP_INTEGRATION | Codebase exploration uses incremental discovery | repository exploration workflow tests | missing |
| TOP-PROMPT-001 | PROMPT_ENGINEERING_AND_STRUCTURED_OUTPUT | System instructions use explicit criteria | prompt builder includes explicit constraints | partial |
| TOP-PROMPT-002 | PROMPT_ENGINEERING_AND_STRUCTURED_OUTPUT | Structured output uses machine-readable contracts | schema-driven extraction path | missing |
| TOP-PROMPT-003 | PROMPT_ENGINEERING_AND_STRUCTURED_OUTPUT | Optional/nullable fields prevent fabrication | schema field behavior | missing |
| TOP-PROMPT-004 | PROMPT_ENGINEERING_AND_STRUCTURED_OUTPUT | Validation-retry loop exists for fixable errors | semantic retry tests | missing |
| TOP-PROMPT-005 | PROMPT_ENGINEERING_AND_STRUCTURED_OUTPUT | Few-shot examples can stabilize output | prompt example injection tests | missing |
| TOP-PROMPT-006 | PROMPT_ENGINEERING_AND_STRUCTURED_OUTPUT | Batch mode reserved for latency-tolerant workflows | batch vs sync routing tests | missing |
| TOP-PROMPT-007 | PROMPT_ENGINEERING_AND_STRUCTURED_OUTPUT | Independent review uses separate invocation | independent review flow tests | missing |
| TOP-CONTEXT-001 | CONTEXT_MANAGEMENT_AND_RELIABILITY | Persistent facts are stored outside summary | facts vs history persistence tests | partial |
| TOP-CONTEXT-002 | CONTEXT_MANAGEMENT_AND_RELIABILITY | Critical IDs/dates/statuses survive compaction | persistent facts retention tests | missing |
| TOP-CONTEXT-003 | CONTEXT_MANAGEMENT_AND_RELIABILITY | Escalation is rule-based, not sentiment-based | escalation policy tests | missing |
| TOP-CONTEXT-004 | CONTEXT_MANAGEMENT_AND_RELIABILITY | Structured error propagation includes partial results | coordinator/subagent error payload tests | missing |
| TOP-CONTEXT-005 | CONTEXT_MANAGEMENT_AND_RELIABILITY | Access failure is distinct from valid empty result | error semantics tests | missing |
| TOP-CONTEXT-006 | CONTEXT_MANAGEMENT_AND_RELIABILITY | Context degradation is mitigated with scratchpads/manifests | scratchpad/state-manifest tests | missing |
| TOP-CONTEXT-007 | CONTEXT_MANAGEMENT_AND_RELIABILITY | Monitoring avoids aggregate-only metrics | segmented metrics tests | missing |
| TOP-CONTEXT-008 | CONTEXT_MANAGEMENT_AND_RELIABILITY | Confidence thresholds are calibrated before routing | calibration gate tests | missing |
| TOP-CONTEXT-009 | CONTEXT_MANAGEMENT_AND_RELIABILITY | Claim provenance is preserved through synthesis | provenance mapping tests | missing |
| TOP-CONTEXT-010 | CONTEXT_MANAGEMENT_AND_RELIABILITY | Conflicting sources are preserved, not collapsed | conflict-preservation tests | missing |

## Immediate Next Test Buckets

1. `Tests/test_topics_implementation_runtime.py`
   Covers implemented and partial requirements from `IMPLEMENTATION_ARCHITECTURE_OPENAI_PYTHON_TELEGRAM.md`.

2. `Tests/test_topics_prompt_and_context_gaps.py`
   Encodes current red tests for missing prompt/context architecture.

3. `Tests/test_topics_tooling_gaps.py`
   Encodes current red tests for missing tool gateway and routing architecture.

## What Must Be Implemented To Turn Red Tests Green

### Implementation / Runtime

- `TOP-IMP-008`
  Do this:
  complete production webhook flow: webhook registration, public URL handling, startup validation, and update delivery coverage beyond local startup.

- `TOP-IMP-011`
  Do this:
  add explicit command handling for `/start`, `/help`, `/reset` instead of routing them through the generic LLM path.

- `TOP-IMP-014`
  Do this:
  introduce explicit coordinator intent/routing decisions instead of the current single-pass request -> prompt -> model -> reply flow.

- `TOP-IMP-015`
  Do this:
  implement a real tool loop: tool registry, tool selection, tool execution, tool result reinjection, and stop/continue control.

- `TOP-IMP-017`
  Do this:
  add bounded retry logic in the OpenAI client for transient errors, timeouts, and rate limits.

- `TOP-IMP-018`
  Do this:
  create a dedicated `tools/` layer with registry, executor, contracts, and error normalization.

- `TOP-IMP-019`
  Do this:
  create a dedicated validation layer for input validation, semantic checks, and output contract enforcement.

- `TOP-IMP-021`
  Do this:
  add Telegram-safe escaping for Markdown/HTML rendering, not only chunking.

- `TOP-IMP-024`
  Do this:
  extend fail-fast coverage to all required startup/runtime conditions, not just env presence.

- `TOP-IMP-025`
  Do this:
  add secret redaction in logs, exceptions, and diagnostic output.

- `TOP-IMP-027`
  Do this:
  add metrics/tracing hooks and explicit observability modules beyond plain logging.

- `TOP-IMP-028`
  Do this:
  add dedupe/idempotency for Telegram updates using stored update IDs or a short-lived dedupe store.

- `TOP-IMP-029`
  Do this:
  add safe user fallback messages for provider/tool/runtime failures.

### Tooling / MCP

- `TOP-TOOL-001`
  Do this:
  add tool descriptions that include purpose, inputs, boundaries, and when not to use the tool.

- `TOP-TOOL-002`
  Do this:
  add routing logic or tool metadata fixtures that can be tested against misrouting scenarios.

- `TOP-TOOL-003`
  Do this:
  create a tool result contract that separates valid empty result from execution failure.

- `TOP-TOOL-004`
  Do this:
  create typed tool error classes or structured error payloads with retryability flags.

- `TOP-TOOL-005`
  Do this:
  define scoped toolsets per role/agent instead of a flat global tool universe.

- `TOP-TOOL-006`
  Do this:
  add explicit tool choice modes such as optional, any-required, and forced specific tool.

- `TOP-TOOL-007`
  Do this:
  add pre-execution hooks that can deny, mutate, or enforce tool calls.

- `TOP-TOOL-008`
  Do this:
  add post-execution hooks that normalize tool output before the coordinator consumes it.

- `TOP-TOOL-009`
  Do this:
  provide shared tool config rendering/validation that proves secrets are never embedded.

- `TOP-TOOL-010`
  Do this:
  implement an exploration/discovery workflow that encodes incremental search/read/edit behavior.

### Prompt / Structured Output

- `TOP-PROMPT-001`
  Do this:
  make prompt criteria more explicit and testable, not only general system wording.

- `TOP-PROMPT-002`
  Do this:
  add a machine-readable structured output contract or schema path for downstream logic.

- `TOP-PROMPT-003`
  Do this:
  model nullable/optional fields explicitly to avoid fabrication pressure.

- `TOP-PROMPT-004`
  Do this:
  implement validation-retry behavior for fixable semantic errors.

- `TOP-PROMPT-005`
  Do this:
  add few-shot/example injection capability in prompt building.

- `TOP-PROMPT-006`
  Do this:
  add explicit sync vs batch workflow routing if batch processing becomes part of the app.

- `TOP-PROMPT-007`
  Do this:
  add a separate independent-review invocation path rather than same-session self-review.

### Context / Reliability

- `TOP-CONTEXT-001`
  Do this:
  split persistent facts from plain message history instead of storing only chat turns.

- `TOP-CONTEXT-002`
  Do this:
  add APIs/storage for critical facts like IDs, dates, statuses, and constraints.

- `TOP-CONTEXT-003`
  Do this:
  implement explicit escalation rules based on policy and progress, not sentiment.

- `TOP-CONTEXT-004`
  Do this:
  implement structured error payloads with partial results and suggested next actions.

- `TOP-CONTEXT-005`
  Do this:
  encode error semantics so access failure and valid empty result are distinct states.

- `TOP-CONTEXT-006`
  Do this:
  add scratchpad and manifest persistence for long-running or multi-phase work.

- `TOP-CONTEXT-007`
  Do this:
  add segmented metrics rather than aggregate-only runtime counters.

- `TOP-CONTEXT-008`
  Do this:
  introduce configurable confidence thresholds and calibration-aware routing.

- `TOP-CONTEXT-009`
  Do this:
  add provenance fields and preservation through synthesis.

- `TOP-CONTEXT-010`
  Do this:
  preserve conflicting sources explicitly instead of collapsing them to one answer.

## Notes

- This is the first step only: matrix before broad test implementation.
- The matrix is intentionally scoped to `Docs/topics/`.
- On this filesystem, `tests/` and `Tests/` resolve to the same physical directory; git tracks the lowercase path `tests/`.
- Later steps should map each matrix ID to one concrete test file and test name.
