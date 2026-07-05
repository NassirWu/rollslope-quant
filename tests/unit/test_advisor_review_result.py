from __future__ import annotations

import dataclasses

import pytest

from tools.ai_advisors.review_result import AdvisorReviewResult


def test_default_values() -> None:
    result = AdvisorReviewResult(source="ollama", verdict="OK", summary="looks fine")

    assert result.findings == []
    assert result.escalate is False
    assert result.error is None
    assert result.raw_response == ""


def test_all_fields_can_be_set() -> None:
    result = AdvisorReviewResult(
        source="ollama",
        verdict="NEEDS_ESCALATION",
        summary="risk logic changed",
        findings=["touches circuit breaker rules"],
        escalate=True,
        error=None,
        raw_response="raw text",
    )

    assert result.source == "ollama"
    assert result.verdict == "NEEDS_ESCALATION"
    assert result.findings == ["touches circuit breaker rules"]
    assert result.escalate is True
    assert result.raw_response == "raw text"


def test_result_is_frozen() -> None:
    result = AdvisorReviewResult(source="ollama", verdict="OK", summary="fine")

    with pytest.raises(dataclasses.FrozenInstanceError):
        result.verdict = "CHANGED"  # type: ignore[misc]
