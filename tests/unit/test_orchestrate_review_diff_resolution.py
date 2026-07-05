from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.ai_advisors.orchestrate_review import (
    GitDiffUnavailableError,
    resolve_diff_content,
)


def test_diff_file_takes_priority(tmp_path: Path) -> None:
    diff_file = tmp_path / "sample.diff"
    diff_file.write_text("diff content from file", encoding="utf-8")

    content = resolve_diff_content(
        diff_file=str(diff_file),
        staged=False,
        cwd=tmp_path,
        piped_stdin="stdin content should be ignored",
    )

    assert content == "diff content from file"


def test_missing_diff_file_raises_file_not_found_error(tmp_path: Path) -> None:
    missing_path = tmp_path / "does_not_exist.diff"

    with pytest.raises(FileNotFoundError):
        resolve_diff_content(
            diff_file=str(missing_path),
            staged=False,
            cwd=tmp_path,
        )


def test_piped_stdin_used_when_no_diff_file(tmp_path: Path) -> None:
    content = resolve_diff_content(
        diff_file=None,
        staged=False,
        cwd=tmp_path,
        piped_stdin="content piped via stdin",
    )

    assert content == "content piped via stdin"


def test_blank_piped_stdin_falls_through_to_git(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="git diff output", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    content = resolve_diff_content(
        diff_file=None,
        staged=False,
        cwd=tmp_path,
        piped_stdin="   \n  ",
    )

    assert content == "git diff output"


def test_git_diff_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="+added line\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    content = resolve_diff_content(diff_file=None, staged=False, cwd=tmp_path)

    assert content == "+added line\n"


def test_git_diff_not_a_repo_raises_clear_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise subprocess.CalledProcessError(
            returncode=128,
            cmd=args[0] if args else ["git", "diff"],
            stderr="fatal: not a git repository (or any of the parent directories): .git",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(GitDiffUnavailableError, match="not a git repository or git error"):
        resolve_diff_content(diff_file=None, staged=False, cwd=tmp_path)


def test_git_executable_missing_raises_clear_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise FileNotFoundError("git not found")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(GitDiffUnavailableError, match="git executable not found"):
        resolve_diff_content(diff_file=None, staged=False, cwd=tmp_path)


def test_staged_flag_passed_to_git_diff(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    captured_args: list[str] = []

    def fake_run(args, **kwargs):  # type: ignore[no-untyped-def]
        captured_args.extend(args)
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    resolve_diff_content(diff_file=None, staged=True, cwd=tmp_path)

    assert captured_args == ["git", "diff", "--staged"]
