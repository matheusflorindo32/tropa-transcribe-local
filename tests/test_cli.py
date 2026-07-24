from __future__ import annotations

from pathlib import Path

from app.cli import EXIT_ARGUMENT, run


def test_cli_rejects_directory_without_batch(tmp_path: Path) -> None:
    assert run([str(tmp_path)]) == EXIT_ARGUMENT


def test_cli_rejects_empty_batch(tmp_path: Path) -> None:
    assert run([str(tmp_path), "--batch"]) == EXIT_ARGUMENT
