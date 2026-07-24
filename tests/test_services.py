from __future__ import annotations

from pathlib import Path

import pytest

from app.services.ffmpeg import resolve_ffmpeg
from app.services.files import TemporaryWorkspace
from app.services.models import model_filename, resolve_model
from app.transcription.whisper_cpp import resolve_whisper_cli


def test_temporary_workspace_cleanup(tmp_path: Path) -> None:
    with TemporaryWorkspace(tmp_path) as workspace:
        created = workspace.path
        (created / "arquivo").write_text("x", encoding="utf-8")
    assert not created.exists()


def test_temporary_workspace_can_be_kept(tmp_path: Path) -> None:
    with TemporaryWorkspace(tmp_path, keep=True) as workspace:
        created = workspace.path
    assert created.exists()


def test_missing_executables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("shutil.which", lambda _: None)
    with pytest.raises(FileNotFoundError, match="FFmpeg"):
        resolve_ffmpeg("ffmpeg")
    with pytest.raises(FileNotFoundError, match="whisper-cli"):
        resolve_whisper_cli("whisper-cli")


def test_model_resolution(tmp_path: Path) -> None:
    model = tmp_path / model_filename("base")
    model.write_bytes(b"x" * 2048)
    assert resolve_model("base", model) == model.resolve()


def test_missing_or_incomplete_model(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        resolve_model("base", tmp_path / "missing.bin")
    tiny = tmp_path / "tiny.bin"
    tiny.write_bytes(b"x")
    with pytest.raises(ValueError, match="incompleto"):
        resolve_model("tiny", tiny)
