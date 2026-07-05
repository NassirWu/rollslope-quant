from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AdvisorReviewResult:
    """單一 AI 顧問的審查結果。

    escalate 是初審（例如 Ollama）最重要的輸出：判斷這次變更是否需要
    升級給更強的模型（GPT / Gemini）進一步審查。無法確定時應以
    escalate=True 為安全預設值。
    """

    source: str
    verdict: str
    summary: str
    findings: list[str] = field(default_factory=list)
    escalate: bool = False
    error: str | None = None
    raw_response: str = ""
