from __future__ import annotations

import pytest

from tools.ai_advisors.clients.ollama_client import OllamaClient, parse_ollama_output


def test_parse_well_formed_response() -> None:
    text = (
        "VERDICT: OK\n"
        "ESCALATE: false\n"
        "SUMMARY: No issues found.\n"
        "FINDINGS:\n"
        "- minor style nit\n"
        "- consider renaming variable\n"
    )

    result = parse_ollama_output(text, source="ollama")

    assert result.source == "ollama"
    assert result.verdict == "OK"
    assert result.escalate is False
    assert result.summary == "No issues found."
    assert result.findings == ["minor style nit", "consider renaming variable"]
    assert result.raw_response == text
    assert result.error is None


def test_parse_escalation_response() -> None:
    text = (
        "VERDICT: NEEDS_ESCALATION\n"
        "ESCALATE: true\n"
        "SUMMARY: Touches risk guard rules, needs deeper review.\n"
        "FINDINGS:\n"
        "- modifies circuit_breaker_rules.py\n"
    )

    result = parse_ollama_output(text)

    assert result.verdict == "NEEDS_ESCALATION"
    assert result.escalate is True
    assert result.findings == ["modifies circuit_breaker_rules.py"]


def test_parse_malformed_response_defaults_to_escalate() -> None:
    text = "The diff looks okay to me, nothing to report."

    result = parse_ollama_output(text)

    assert result.verdict == "UNKNOWN"
    assert result.escalate is True
    assert result.summary == text
    assert result.findings == []


def test_parse_empty_response() -> None:
    result = parse_ollama_output("")

    assert result.escalate is True
    assert result.summary == "Ollama 未回傳可解析內容"


@pytest.mark.asyncio
async def test_ollama_client_review_success(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OllamaClient(host="http://fake-host:11434", model="fake-model")

    def fake_call(prompt: str) -> str:
        assert "hello" in prompt
        return "VERDICT: OK\nESCALATE: false\nSUMMARY: fine\n"

    monkeypatch.setattr(client, "_call_ollama_sync", fake_call)

    result = await client.review("hello world diff")

    assert result.source == "ollama"
    assert result.verdict == "OK"
    assert result.escalate is False
    assert result.error is None


@pytest.mark.asyncio
async def test_ollama_client_review_connection_error(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OllamaClient(host="http://fake-host:11434", model="fake-model")

    def fake_call(prompt: str) -> str:
        raise ConnectionError("connection refused")

    monkeypatch.setattr(client, "_call_ollama_sync", fake_call)

    result = await client.review("some diff")

    assert result.verdict == "ERROR"
    assert result.escalate is True
    assert result.error == "connection refused"
