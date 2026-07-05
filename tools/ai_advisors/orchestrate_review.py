from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.ai_advisors.clients.ollama_client import OllamaClient  # noqa: E402
from tools.ai_advisors.review_result import AdvisorReviewResult  # noqa: E402

PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parent / "prompts" / "quick_local_review.md"


class GitDiffUnavailableError(RuntimeError):
    """git diff 無法取得時拋出（非 git repo、git 未安裝、或其他 git 錯誤）。"""


def read_diff_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"diff file not found: {path}")
    return path.read_text(encoding="utf-8")


def read_git_diff(staged: bool, cwd: Path) -> str:
    args = ["git", "diff"]
    if staged:
        args.append("--staged")
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=True,
        )
    except FileNotFoundError as exc:
        raise GitDiffUnavailableError(
            "git executable not found. Install git or use --diff-file instead."
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else str(exc)
        raise GitDiffUnavailableError(
            f"git diff failed (not a git repository or git error): {stderr}"
        ) from exc
    return result.stdout


def resolve_diff_content(
    diff_file: str | None,
    staged: bool,
    cwd: Path,
    piped_stdin: str | None = None,
) -> str:
    """
    決定要送去審查的內容，優先順序：
        1. --diff-file 指定的檔案
        2. 已經 pipe 進來的 stdin 內容
        3. git diff（找不到 git repo 或 git 失敗時拋 GitDiffUnavailableError）
    """
    if diff_file:
        return read_diff_file(Path(diff_file))
    if piped_stdin is not None and piped_stdin.strip():
        return piped_stdin
    return read_git_diff(staged=staged, cwd=cwd)


def build_prompt(diff_content: str) -> str:
    template = PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
    return template.replace("{diff}", diff_content or "(no changes)")


def print_result(result: AdvisorReviewResult) -> None:
    print("=" * 72)
    print("Ollama Quick Local Review")
    print("=" * 72)
    print(f"Source    : {result.source}")
    print(f"Verdict   : {result.verdict}")
    print(f"Escalate  : {result.escalate}")
    print(f"Summary   : {result.summary}")
    if result.error:
        print(f"Error     : {result.error}")
    if result.findings:
        print("Findings  :")
        for finding in result.findings:
            print(f"  - {finding}")
    print("=" * 72)


async def run(diff_file: str | None, staged: bool, piped_stdin: str | None) -> int:
    try:
        diff_content = resolve_diff_content(
            diff_file=diff_file,
            staged=staged,
            cwd=PROJECT_ROOT,
            piped_stdin=piped_stdin,
        )
    except (FileNotFoundError, GitDiffUnavailableError) as exc:
        print(f"[orchestrate_review] Error: {exc}", file=sys.stderr)
        return 1

    if not diff_content.strip():
        print("No changes/content to review.")
        return 0

    prompt = build_prompt(diff_content)
    client = OllamaClient()
    result = await client.review(prompt)
    print_result(result)
    return 0 if result.error is None else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Ollama quick local review over a git diff or supplied content."
    )
    parser.add_argument(
        "--diff-file",
        default=None,
        help="Path to a plain-text diff or code file to review instead of git diff.",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Review staged changes (git diff --staged) instead of the working tree diff.",
    )
    args = parser.parse_args()

    piped_stdin = None
    if not sys.stdin.isatty():
        piped_stdin = sys.stdin.read()

    exit_code = asyncio.run(
        run(diff_file=args.diff_file, staged=args.staged, piped_stdin=piped_stdin)
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
