"""TokenTracker — capture LangChain LLM usage metadata.

Source: agent-harness-card-extractor/card_extractor/ai_client.py.
Canonical version. Designed to be a drop-in replacement for both
card-extractor's and chorus-csd-analyzer's inline TokenTracker
(the latter currently imports from upstream chorus_forms; the
chorus harness's v0.2.0 rework swaps that import for this package).
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TokenEvent(BaseModel):
    """One recorded LLM call's token usage."""

    source: str
    model: str
    ref: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: Optional[float] = None


class TokenTracker:
    """Accumulate token usage events across an agent run.

    Usage:
        tracker = TokenTracker()
        tracker.record(source="detect", model="gemini-2.5-pro",
                       input_tokens=120, output_tokens=45)
        print(tracker.totals())
        print(tracker.cost_estimate({"gemini-2.5-pro": {"input": 1.25, "output": 5.0}}))
    """

    def __init__(self) -> None:
        self._events: list[TokenEvent] = []

    def record(
        self,
        source: str,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        ref: str = "",
        latency_ms: Optional[float] = None,
    ) -> None:
        """Record one call's usage."""
        self._events.append(
            TokenEvent(
                source=source,
                model=model,
                ref=ref,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
            )
        )

    def record_from_response(
        self,
        source: str,
        model: str,
        raw_response: Any,
        ref: str = "",
        latency_ms: Optional[float] = None,
    ) -> None:
        """Record from a LangChain response message's `usage_metadata`."""
        um = getattr(raw_response, "usage_metadata", None)
        if not um:  # None or empty dict — nothing useful to record
            return
        self.record(
            source=source,
            model=model,
            input_tokens=um.get("input_tokens", 0),
            output_tokens=um.get("output_tokens", 0),
            ref=ref,
            latency_ms=latency_ms,
        )

    def totals(self) -> dict[str, dict[str, int]]:
        """Totals per source.

        Returns:
            {source: {"input_tokens": N, "output_tokens": M, "calls": K}}
        """
        by_source: dict[str, dict[str, int]] = defaultdict(
            lambda: {"input_tokens": 0, "output_tokens": 0, "calls": 0}
        )
        for ev in self._events:
            by_source[ev.source]["input_tokens"] += ev.input_tokens
            by_source[ev.source]["output_tokens"] += ev.output_tokens
            by_source[ev.source]["calls"] += 1
        return dict(by_source)

    def cost_estimate(
        self, pricing: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        """Estimate USD cost given a per-model pricing dict.

        Args:
            pricing: {model_id: {"input": $/1M tokens, "output": $/1M tokens}}

        Returns:
            {"input_usd": ..., "output_usd": ..., "total_usd": ...}
        """
        in_usd = 0.0
        out_usd = 0.0
        for ev in self._events:
            p = pricing.get(ev.model)
            if not p:
                continue
            in_usd += ev.input_tokens * p.get("input", 0) / 1_000_000
            out_usd += ev.output_tokens * p.get("output", 0) / 1_000_000
        input_usd = round(in_usd, 6)
        output_usd = round(out_usd, 6)
        return {
            "input_usd": input_usd,
            "output_usd": output_usd,
            "total_usd": round(input_usd + output_usd, 6),
        }

    def events(self) -> list[TokenEvent]:
        """Return all recorded events (read-only copy)."""
        return list(self._events)
