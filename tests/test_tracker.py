"""Tests for token_tracker."""
from token_tracker import TokenTracker


def test_record_and_totals():
    t = TokenTracker()
    t.record("detect", "model-a", input_tokens=100, output_tokens=50)
    t.record("detect", "model-a", input_tokens=200, output_tokens=80)
    t.record("verify", "model-a", input_tokens=50, output_tokens=20)
    tot = t.totals()
    assert tot["detect"]["input_tokens"] == 300
    assert tot["detect"]["output_tokens"] == 130
    assert tot["detect"]["calls"] == 2
    assert tot["verify"]["input_tokens"] == 50
    assert tot["verify"]["calls"] == 1


def test_record_from_response_with_usage_metadata():
    t = TokenTracker()

    class FakeResp:
        usage_metadata = {"input_tokens": 100, "output_tokens": 50}

    t.record_from_response("extract", "model-b", FakeResp())
    tot = t.totals()
    assert tot["extract"]["input_tokens"] == 100
    assert tot["extract"]["output_tokens"] == 50


def test_record_from_response_no_usage_metadata():
    t = TokenTracker()

    class FakeResp:
        pass

    t.record_from_response("extract", "model-b", FakeResp())
    assert t.totals() == {}


def test_cost_estimate():
    t = TokenTracker()
    t.record("detect", "gemini-2.5-pro", input_tokens=1_000_000, output_tokens=500_000)
    cost = t.cost_estimate({"gemini-2.5-pro": {"input": 1.25, "output": 5.0}})
    assert cost["input_usd"] == 1.25
    assert cost["output_usd"] == 2.5
    assert cost["total_usd"] == 3.75


def test_cost_estimate_unknown_model_ignored():
    t = TokenTracker()
    t.record("detect", "unknown-model", input_tokens=100, output_tokens=50)
    cost = t.cost_estimate({"gemini-2.5-pro": {"input": 1.0, "output": 5.0}})
    assert cost["total_usd"] == 0.0


def test_events_returns_copy():
    t = TokenTracker()
    t.record("a", "m", input_tokens=1, output_tokens=2)
    ev = t.events()
    assert len(ev) == 1
    ev.clear()
    assert len(t.events()) == 1
