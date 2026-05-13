# Changelog

## 0.1.0 — 2026-05-12

Initial release. Extracted from `agent-harness-card-extractor/card_extractor/ai_client.py` as part of the 2026-05-12 agent-toolbox extraction (see `D:/ai-agents/docs/superpowers/specs/2026-05-12-agent-toolbox-extraction-design.md`). Designed as a drop-in replacement for both card-extractor's `TokenTracker` and chorus-csd-analyzer's `from chorus_forms.csd.token_tracker import TokenTracker` (the latter chorus harness rework is deferred to a future spec).

- `TokenTracker.record(source, model, input_tokens=0, output_tokens=0, ref="", latency_ms=None)` — record one LLM call's usage.
- `TokenTracker.record_from_response(source, model, raw_response, ref="", latency_ms=None)` — pull `usage_metadata` off a LangChain response message; no-op when absent.
- `TokenTracker.totals() -> {source: {input_tokens, output_tokens, calls}}` — per-source aggregates.
- `TokenTracker.cost_estimate(pricing) -> {input_usd, output_usd, total_usd}` — USD estimate from a `{model: {input, output}}` $/1M-tokens pricing dict; unknown models silently ignored.
- `TokenTracker.events() -> list[TokenEvent]` — read-only copy of all recorded events.
- `TokenEvent` — pydantic model: `source`, `model`, `ref`, `input_tokens`, `output_tokens`, `latency_ms`.

### Deviations from source

The source `TokenTracker` in `agent-harness-card-extractor/card_extractor/ai_client.py` exposed a different surface (`records` list attribute, `total_input` / `total_output` properties, `summary()` method, `TokenRecord` dataclass with `timestamp` field). The canonical API here is broader: adds `ref` / `latency_ms` per-event metadata, adds `cost_estimate()` for $/call accounting, swaps `summary()` for `totals()` (per-source dict with `input_tokens` / `output_tokens` / `calls` keys, vs source `input` / `output` / `calls`), and uses pydantic `TokenEvent` instead of dataclass `TokenRecord`. Call sites in card-extractor that used `tracker.record(...)` and `tracker.record_from_response(...)` still work unchanged; call sites using `tracker.records`, `tracker.total_input`, `tracker.total_output`, `tracker.summary()`, or importing `TokenRecord` will need to migrate to the new API when adopting this package.
