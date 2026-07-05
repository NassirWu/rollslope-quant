from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.request

from tools.ai_advisors.review_result import AdvisorReviewResult

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder:14b"


def parse_ollama_output(text: str, source: str = "ollama") -> AdvisorReviewResult:
    """
    解析 Ollama 回覆的純文字內容為 AdvisorReviewResult。

    預期格式（見 prompts/quick_local_review.md）：
        VERDICT: OK 或 NEEDS_ESCALATION
        ESCALATE: true 或 false
        SUMMARY: 一句話總結
        FINDINGS:
        - finding 1
        - finding 2

    安全預設：
        若模型未依格式回覆或缺漏 ESCALATE 欄位，一律視為需要升級
        （escalate=True），避免因解析失誤而漏審重要變更。
    """
    verdict = "UNKNOWN"
    escalate = True
    summary = ""
    findings: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        upper_line = line.upper()
        if upper_line.startswith("VERDICT:"):
            verdict = line.split(":", 1)[1].strip().upper()
        elif upper_line.startswith("ESCALATE:"):
            value = line.split(":", 1)[1].strip().lower()
            escalate = value in {"true", "yes", "1"}
        elif upper_line.startswith("SUMMARY:"):
            summary = line.split(":", 1)[1].strip()
        elif line.startswith("-"):
            finding = line.lstrip("-").strip()
            if finding:
                findings.append(finding)

    if not summary:
        stripped = text.strip()
        summary = stripped[:200] if stripped else "Ollama 未回傳可解析內容"

    return AdvisorReviewResult(
        source=source,
        verdict=verdict,
        summary=summary,
        findings=findings,
        raw_response=text,
        escalate=escalate,
    )


class OllamaClient:
    """本機 Ollama 初審客戶端，透過 OLLAMA_HOST 呼叫本機 Ollama API。"""

    name = "ollama"

    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
        timeout: int = 60,
    ) -> None:
        self.host = (host or os.getenv("OLLAMA_HOST", DEFAULT_OLLAMA_HOST)).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
        self.timeout = timeout

    async def review(self, prompt: str) -> AdvisorReviewResult:
        try:
            raw_text = await asyncio.to_thread(self._call_ollama_sync, prompt)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            return AdvisorReviewResult(
                source=self.name,
                verdict="ERROR",
                summary="Ollama 呼叫失敗，請確認本機 Ollama 服務是否已啟動。",
                escalate=True,
                error=str(exc),
            )
        return parse_ollama_output(raw_text, source=self.name)

    def _call_ollama_sync(self, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            url=f"{self.host}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = response.read().decode("utf-8")
        data = json.loads(body)
        return str(data.get("response", ""))
