from __future__ import annotations

from typing import Protocol

from tools.ai_advisors.review_result import AdvisorReviewResult


class AdvisorClient(Protocol):
    """AI 顧問客戶端抽象介面。

    每個顧問（Ollama / 未來的 GPT / Gemini）都實作相同介面，
    orchestrate_review.py 只依賴這個 Protocol，不依賴特定 SDK。
    """

    name: str

    async def review(self, prompt: str) -> AdvisorReviewResult:
        ...
