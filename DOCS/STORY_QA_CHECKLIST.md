# Story QA Checklist

This checklist is used by the Story QA Agent during pre-implementation review.
Each item has an ID, a trigger condition, and the exact amendment to make.

---

## QA-001: DateTime Timezone Enforcement

**Trigger:** Any story that defines a Pydantic model with a `datetime` field,
or any story that receives datetime values from an external API, tool, or
database.

**Check:** Does the story explicitly require timezone-aware UTC datetimes and
specify enforcement via a `@field_validator`?

**If missing, add to Technical Notes:**
> All `datetime` fields must be timezone-aware UTC. Enforce via an explicit
> `@field_validator` that rejects `tzinfo is None` and normalizes non-UTC
> offsets to UTC via `.astimezone(timezone.utc)`. External date strings (e.g.
> EDGAR's `"2026-01-15"` with no time component) must be parsed as midnight UTC.
> Test must cover: naive datetime rejected, non-UTC datetime normalized, valid
> UTC datetime accepted.

---

## QA-002: Pydantic Mutable Default Arguments

**Trigger:** Any story that defines a Pydantic model with a `list`, `dict`,
or `set` field.

**Check:** Does the story specify `Field(default_factory=list)` (or equivalent)
for mutable fields? Does it avoid `= []` or `= {}`?

**If missing, add to Technical Notes:**
> All `list`, `dict`, and `set` fields on Pydantic models must use
> `Field(default_factory=list)` (or `dict`/`set`). Never use `= []` or `= {}`
> as defaults. Mutable defaults are shared across all instances in Python.

---

## QA-003: HTTP Client Singleton Pattern

**Trigger:** Any story that creates or uses an `httpx.AsyncClient`.

**Check:** Does the story explicitly require a module-level lazy singleton
with an `asyncio.Lock`? Does it forbid per-call instantiation?

**If missing, add to Technical Notes:**
> Use a module-level lazy singleton for `httpx.AsyncClient`:
> ```python
> _client: httpx.AsyncClient | None = None
> _client_lock: asyncio.Lock = asyncio.Lock()
> ```
> Initialize inside an async `_get_client()` function using double-checked
> locking. Never instantiate `httpx.AsyncClient` inside the function being
> called per request. Expose an `aclose()` function for process shutdown.
> Test must assert the same client instance is returned on successive calls.

---

## QA-004: Retry Policy Reuse

**Trigger:** Any story that implements retry logic or references `tenacity`.

**Check:** Does the story reference `tools/_http_retry.py` as the shared
retry module? Does it forbid constructing a new tenacity retry from scratch?

**If missing, add to Technical Notes:**
> Import and use `build_retrying` from `tools/_http_retry.py`. Do not
> construct a new tenacity retry policy from scratch. If `_http_retry.py`
> does not exist yet, establish it as the shared module in this story and
> reference it in all future tool stories. Retry on 5xx and transport errors.
> Never retry on 4xx. Use `reraise=True`.

---

## QA-005: Per-Item Exception Handling in Loops

**Trigger:** Any story that iterates over a list (companies, industries,
results) and calls an external tool or LLM inside the loop.

**Check:** Does the story explicitly require per-item try/except so one
failure does not abort the loop?

**If missing, add to Technical Notes:**
> Wrap each iteration in its own `try/except`. A single item failure must
> never abort the loop or drop the results of other items. Log the error
> with item context (e.g. company name), append to
> `state["run_metadata"].errors`, and continue to the next item.
> Test must cover: one item fails, remaining items succeed, error is recorded.

---

## QA-006: LLM JSON Output Per-Item Parsing

**Trigger:** Any story where an LLM returns a JSON object containing a list
of items (e.g. `{findings: [...]}`).

**Check:** Does the story specify that each list item is validated individually
via `Model.model_validate(item)` in its own try/except?

**If missing, add to Technical Notes:**
> When parsing LLM JSON output containing a list, iterate over the list and
> call `Model.model_validate(item)` on each element individually inside its
> own `try/except ValidationError`. One invalid item must drop only that item,
> not the entire batch. Log a warning for each dropped item including the
> raw item content for debugging.
> Test must cover: one invalid item in a list of three, assert two valid
> findings are returned and one warning is logged.

---

## QA-007: Source Field Consistency Across Boundaries

**Trigger:** Any story where an agent creates a domain model (`Finding` or
similar) from a tool result that already has a `source` field.

**Check:** Does the story specify that `Finding.source` is mapped from the
tool result's `source` field rather than hardcoded?

**If missing, add to Technical Notes:**
> Map `Finding.source` from the tool result's `source` field directly (e.g.
> `SearchResult.source`). Never hardcode a source string in the agent that
> duplicates or contradicts the value the tool already provides. If the tool
> result has no `source` field, define the source constant in the tool, not
> the agent.

---

## QA-008: Directory Creation Before File Writes

**Trigger:** Any story that writes to a configurable directory path from
config or a parameter.

**Check:** Does the story require `mkdir(parents=True, exist_ok=True)` before
the write?

**If missing, add to Technical Notes:**
> Before any file write to a configurable directory, call:
> `Path(directory).mkdir(parents=True, exist_ok=True)`
> This must happen inside the function, not at module import time, so it
> respects whatever path is configured at runtime.
> Test must cover: directory does not exist before call, directory is created,
> file is written successfully.

---

## QA-009: UUID Fallback for Optional Identifiers in Filenames

**Trigger:** Any story that uses an optional identifier (e.g. `run_id: str |
None`) as part of a filename, database key, or log correlation ID.

**Check:** Does the story specify a UUID4 fallback when the identifier is None?

**If missing, add to Technical Notes:**
> When an optional identifier is used in a filename or key, generate a UUID4
> fallback immediately at function entry:
> `run_id = run_id or str(uuid.uuid4())`
> Never use `None` as a filename component. Two `None` runs would produce
> `filename-None.ext` and silently overwrite each other.

---

## QA-010: Secondary Failure Isolation

**Trigger:** Any story that performs a cleanup, logging, or persistence
operation inside an `except` block.

**Check:** Does the story require the secondary operation to be wrapped in
its own try/except so it cannot hide the original exception?

**If missing, add to Technical Notes:**
> Any operation inside an `except` block (file persistence, notification,
> cleanup) must be wrapped in its own `try/except` with a `logger.warning`
> on failure. A secondary failure must never propagate and replace the
> original exception on the call stack. Pattern:
> ```python
> except PrimaryError as e:
>     try:
>         _cleanup_operation()
>     except Exception as secondary:
>         logger.warning(f"Cleanup failed: {secondary}")
>     raise
> ```

---

## QA-011: LangGraph Concurrent State Write Reducers

**Trigger:** Any story that wires multiple agents to write to the same
`GraphState` field concurrently (fan-out pattern).

**Check:** Does the story specify explicit reducers for all shared list fields
using `Annotated[list[T], operator.add]`?

**If missing, add to Technical Notes:**
> For any `GraphState` field that two or more agents write to concurrently,
> define an explicit reducer:
> ```python
> from typing import Annotated
> import operator
>
> class GraphState(TypedDict):
>     agents_completed: Annotated[list[str], operator.add]
>     errors: Annotated[list[str], operator.add]
> ```
> Without explicit reducers, LangGraph's default merge behavior may overwrite
> one agent's writes with the other's. Test must assert both agents'
> contributions appear in the merged state.

---

## QA-012: LangGraph Routing Functions as Extension Points

**Trigger:** Any story that adds a conditional edge to the LangGraph graph.

**Check:** Does the story require a named routing function even if it only
returns one value? Does it forbid hardcoding the destination in
`add_conditional_edges`?

**If missing, add to Technical Notes:**
> Always implement a named routing function for conditional edges, even if
> it currently returns only one possible value:
> ```python
> def route_after_orchestrator(state: GraphState) -> str:
>     return "news_scout"  # extended in US-018
> ```
> Never hardcode the destination string directly in `add_conditional_edges`.
> The routing function is the designated extension point for the LLM-driven
> router in US-018. A comment noting this must be present in the function.

---

## QA-013: Test Environment Isolation from Real .env Files

**Trigger:** Any story that adds new environment variables to `config.py`.

**Check:** Does the story reference the `_isolate_env` fixture pattern and
require that new variables are added to the isolation list?

**If missing, add to Technical Notes:**
> Add all new environment variable names to the `_OPTIONAL_ENV_TO_CLEAR`
> list in `tests/conftest.py`. This prevents the real `.env` file from
> injecting values into unit tests via `python-dotenv`'s `find_dotenv()`
> directory walk. Reference the `_isolate_env` fixture established in US-001.
> Test must confirm that missing the new variable raises the expected
> validation error rather than silently using the real `.env` value.

---

## QA-014: Compact LLM Payload Serialization

**Trigger:** Any story that passes domain model instances (Pydantic models,
`Finding` objects, etc.) to an LLM call.

**Check:** Does the story specify exactly which fields to include in the
prompt payload? Does it forbid serializing full Pydantic models?

**If missing, add to Technical Notes:**
> Never serialize full Pydantic models into an LLM prompt. Specify the exact
> fields to include and serialize compactly (one line per item where possible).
> For `Finding` objects, include only: `company`, `signal_type`, `summary`,
> `url`, `confidence`. Omit internal fields, raw metadata, and timestamps
> unless the prompt logic requires them. Group by industry before serializing
> to reduce LLM reasoning overhead. Estimate token usage: 25 findings at
> ~150 tokens each = ~3,750 tokens of input before system prompt.

---

## QA-015: LLM Hallucination Guard in Synthesis Prompts

**Trigger:** Any story where an LLM synthesizes, summarizes, or analyzes
provided data to produce output that will be presented as factual to end users.

**Check:** Does the system prompt specification include an explicit instruction
forbidding the LLM from inventing information not present in the input?

**If missing, add to Technical Notes:**
> The system prompt must include an explicit anti-hallucination instruction:
> "You may only reference information explicitly present in the provided data.
> Do not invent, infer, speculate about, or extrapolate any facts, signals,
> company actions, or market events that are not directly stated in the input.
> If the provided data is sparse, say so explicitly rather than filling gaps
> with plausible-sounding content."
> This is especially critical for competitive intelligence outputs where a
> fabricated signal (e.g. an invented acquisition rumor) could cause harm.

---

## QA-016: Error Class Attribute Completeness

**Trigger:** Any story that defines a custom exception class.

**Check:** Does the story specify explicit typed attributes on the exception
class (not just a message string)?

**If missing, add to Technical Notes:**
> Custom exception classes must expose typed attributes, not just a message
> string. At minimum: `status_code: int` and `message: str`. For HTTP errors,
> also include `request_summary: dict` (redacted, log-safe). This allows
> callers to inspect failures programmatically rather than parsing strings.
> Pattern:
> ```python
> class ServiceError(RuntimeError):
>     def __init__(self, message: str, status_code: int,
>                  request_summary: dict | None = None) -> None:
>         super().__init__(message)
>         self.message = message
>         self.status_code = status_code
>         self.request_summary = request_summary or {}
> ```

---

## QA-017: API Key and Secret Redaction in Logs and Errors

**Trigger:** Any story that makes authenticated HTTP calls or handles
credentials.

**Check:** Does the story require a `_redact_headers` helper and explicitly
test that the API key never appears in logs or error messages?

**If missing, add to Technical Notes:**
> Implement a `_redact_headers(headers: dict) -> dict` helper that replaces
> the value of `x-api-key`, `Authorization`, and similar credential headers
> with `"[REDACTED]"` before any logging or error construction. Test must
> assert: (1) the raw API key value does not appear in the logged output,
> (2) the raw API key value does not appear in the exception message or
> `request_summary` dict.

---

## QA-018: Integration Smoke Test Gating

**Trigger:** Any story that creates an integration test against a real
external service (API, database, SFTP, etc.).

**Check:** Does the story require the integration test to be skipped by
default and only enabled via an environment variable flag?

**If missing, add to Technical Notes:**
> Integration smoke tests must be skipped by default in CI and local test
> runs. Gate with a pytest skip decorator:
> ```python
> @pytest.mark.skipif(
>     not os.getenv("RUN_LIVE_{SERVICE}_TESTS"),
>     reason="Live {service} tests disabled. Set RUN_LIVE_{SERVICE}_TESTS=1."
> )
> ```
> Replace `{SERVICE}` with the service name (e.g. `LLM`, `WEB_SEARCH`,
> `EDGAR`). Document the flag in `.env.example` with a comment explaining
> when to enable it.

---

## QA-019: GraphState Field Serializer for Checkpointing

**Trigger:** Any story that adds a new Pydantic model field to `GraphState`
or adds a new `GraphState` field that contains a Pydantic model.

**Check:** Does the story require a `@field_serializer` for any `datetime`
or complex-type fields that will be checkpointed via SqliteSaver?

**If missing, add to Technical Notes:**
> SqliteSaver serializes `GraphState` to msgpack. Any `datetime` field on a
> model stored in state must have a `@field_serializer` that converts it to
> an ISO string. Any custom type that is not msgpack-native must have a
> serializer. Pattern:
> ```python
> @field_serializer("timestamp", "filed_at", "started_at")
> def serialize_dt(self, dt: datetime) -> str:
>     return dt.isoformat()
> ```
> Test must invoke the graph with a non-empty state containing the new field
> and assert that checkpointing does not raise a `TypeError`.

---

## QA-020: Logging Level and Structured Format Requirements

**Trigger:** Any story that specifies logging requirements.

**Check:** Does the story specify the log level for each significant event
and provide a format template for structured log lines?

**If missing, add to Technical Notes:**
> Specify log level for each event explicitly:
> - Run start / completion: INFO
> - Per-item success: DEBUG
> - Per-item recoverable failure: WARNING with item context
> - Agent-level failure (partial results): ERROR
> - Unrecoverable failure (no output produced): CRITICAL
> Final run summary line must be INFO with structured format:
> `"Run {run_id} complete: {finding_count} findings, {agent_count} agents,
> {error_count} errors"`
> No log line may contain API keys, passwords, or PII.

---

## QA-021: Multiple Findings Per Company for Distinct Signals

**Trigger:** Any agent story where an LLM is prompted to summarize
per-company data into findings (news_scout, job_signals, filings_monitor,
social_signals, or any future specialist agent).

**Check:** Does the system prompt specification instruct the LLM to emit
multiple findings when multiple distinct signals exist for one company,
rather than collapsing everything into a single finding?

**If missing, add to Technical Notes:**
> The system prompt must instruct the LLM to emit one finding per distinct
> signal, not one finding per company. If a company has both a hiring surge
> in engineering AND a product launch AND a regulatory filing, those are
> three findings, not one. A single finding per company is only acceptable
> when there is genuinely only one signal worth reporting. Example instruction
> to include in the system prompt: "Emit one finding per distinct competitive
> signal. Do not collapse multiple unrelated signals into a single finding."

---

## QA-022: Radon Code Quality Check in Definition of Done

**Trigger:** Any story that creates or modifies production Python files.

**Check:** Does the Definition of Done include a Radon cyclomatic complexity
and maintainability index check with the project threshold?

**If missing, add to Definition of Done:**
> - [ ] Radon CC check: all production functions grade A (CC ≤ 10). Any
>       function exceeding CC 10 must be refactored or justified in
>       `DOCS/CodeQualityChecks/US-XXX-quality.md`.
> - [ ] Radon MI check: all production files grade A (MI ≥ 20).
> - [ ] Quality report written to `DOCS/CodeQualityChecks/US-XXX-quality.md`.

---

## QA-023: Empty Result vs Provider Failure Distinction

**Trigger:** Any agent or tool story that calls an external provider and
must handle the case where no data is returned.

**Check:** Does the story explicitly distinguish between an empty result
(normal condition, no error) and a provider failure (error condition,
logged and recorded)?

**If missing, add to Technical Notes:**
> Explicitly distinguish between two conditions that produce zero results:
>
> 1. **Empty result** — the provider responded successfully but returned
>    no data (e.g. company has no recent filings, no job postings, no news).
>    This is a normal condition. Do not log an error. Do not append to
>    `run_metadata.errors`. Skip the LLM call. Return an empty list.
>
> 2. **Provider failure** — the provider returned an error, timed out, or
>    raised an exception. This is an error condition. Log at WARNING with
>    company context. Append a descriptive string to
>    `state["run_metadata"].errors`. Raise or catch `ProviderError`
>    depending on whether the caller or the tool handles it.
>
> Test must cover both cases explicitly with separate test functions named
> `test_{module}_empty_result_is_not_an_error` and
> `test_{module}_provider_failure_is_logged_and_recorded`.

---

## How to Use This Checklist

1. Read the story completely.
2. For each checklist item, identify the trigger condition.
3. If the trigger applies, check whether the story addresses it.
4. If not addressed, apply the amendment exactly as specified.
5. Add a QA-ADDED marker so the human reviewer can see what changed.
6. Produce the amended story and the QA Review Summary table.

When a new pattern is discovered during implementation review or production
incident, add a new QA-NNN item to this checklist following the same format.
The checklist is a living document that grows with every project.

