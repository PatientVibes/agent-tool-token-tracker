# agent-tool-token-tracker

Capture token usage from LangChain LLM responses, surface totals by source/model, optional cost estimation from a pricing dict.

## Install

```bash
uv tool install --editable .
# or as a library dependency:
# [tool.uv.sources] agent-tool-token-tracker = { git = "https://github.com/PatientVibes/agent-tool-token-tracker.git", rev = "<sha>" }
```

## What's inside

| Member | Use case |
|---|---|
| `TokenTracker.record` | "Record one LLM call's input/output token counts under a named source" |
| `TokenTracker.record_from_response` | "Pull `usage_metadata` off a LangChain response message — no-op if absent" |
| `TokenTracker.totals` | "Per-source rollup: `{source: {input_tokens, output_tokens, calls}}`" |
| `TokenTracker.cost_estimate` | "USD estimate from a `{model: {input, output}}` $/1M-tokens pricing dict" |
| `TokenTracker.events` | "Read-only copy of every recorded event" |
| `TokenEvent` | Pydantic model: `source`, `model`, `ref`, `input_tokens`, `output_tokens`, `latency_ms` |

## Usage

```python
from token_tracker import TokenTracker

tracker = TokenTracker()

# Record explicitly
tracker.record(source="detect", model="gemini-2.5-pro",
               input_tokens=120, output_tokens=45)

# Or pull from a LangChain response (no-op if usage_metadata missing)
resp = await chain.ainvoke({"x": 1})
tracker.record_from_response(source="extract", model="gemini-2.5-pro", raw_response=resp)

# Inspect
print(tracker.totals())
# {'detect': {'input_tokens': 120, 'output_tokens': 45, 'calls': 1}, ...}

# Cost estimate ($/1M tokens)
print(tracker.cost_estimate({
    "gemini-2.5-pro": {"input": 1.25, "output": 5.0},
}))
# {'input_usd': 0.00015, 'output_usd': 0.000225, 'total_usd': 0.000375}
```

## Provenance

Extracted 2026-05-12 from `agent-harness-card-extractor/card_extractor/ai_client.py`.

The canonical API here is broader than the source: adds `ref` / `latency_ms` per-event metadata, adds `cost_estimate()`, swaps `summary()` for `totals()` (per-source dict), and uses pydantic `TokenEvent` instead of dataclass `TokenRecord`. See `CHANGELOG.md` for the full diff and migration notes.

See `D:/ai-agents/docs/superpowers/specs/2026-05-12-agent-toolbox-extraction-design.md`.

## License

MIT. See `LICENSE`.
