from __future__ import annotations

from pathlib import Path

import pytest

from app.services.ffmpeg import resolve_ffmpeg
from app.services.files import TemporaryWorkspace
from app.services.models import model_filename, resolve_model, validate_model_file
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


def test_missing_executables(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("shutil.which", lambda _: None)
    monkeypatch.setattr("app.services.ffmpeg.default_data_dir", lambda: tmp_path)
    monkeypatch.setattr("app.transcription.whisper_cpp._installed_whisper_candidates", list)
    with pytest.raises(FileNotFoundError, match="FFmpeg"):
        resolve_ffmpeg("ffmpeg")
    with pytest.raises(FileNotFoundError, match="whisper-cli"):
        resolve_whisper_cli("whisper-cli")


def test_ffmpeg_falls_back_to_installation_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    executable = tmp_path / "ffmpeg.exe"
    executable.write_bytes(b"x")
    (tmp_path / "installation.json").write_text(
        '{"ffmpeg": "' + str(executable).replace("\\", "\\\\") + '"}',
        encoding="utf-8",
    )
    monkeypatch.setattr("shutil.which", lambda _: None)
    monkeypatch.setattr("app.services.ffmpeg.default_data_dir", lambda: tmp_path)
    assert resolve_ffmpeg() == executable.resolve()


def test_model_resolution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.models.minimum_model_bytes", lambda _: 1024)
    model = tmp_path / model_filename("base")
    model.write_bytes(b"x" * 2048)
    assert resolve_model("base", model) == model.resolve()


def test_missing_or_incomplete_model(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.models.minimum_model_bytes", lambda _: 1024)
    with pytest.raises(FileNotFoundError):
        resolve_model("base", tmp_path / "missing.bin")
    tiny = tmp_path / "tiny.bin"
    tiny.write_bytes(b"x")
    with pytest.raises(ValueError, match="incompleto"):
        resolve_model("tiny", tiny)


def test_model_rejects_recorded_sha256_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.services.models.minimum_model_bytes", lambda _: 1)
    model = tmp_path / "ggml-base.bin"
    model.write_bytes(b"modelo")
    model.with_suffix(".sha256.json").write_text(
        '{"sha256":"' + ("0" * 64) + '"}', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="SHA-256"):
        validate_model_file(model, "base")


def test_whisper_cli_falls_back_to_installed_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    executable = tmp_path / "build" / "bin" / "Release" / "whisper-cli.exe"
    executable.parent.mkdir(parents=True)
    executable.write_bytes(b"x")
    monkeypatch.setattr("shutil.which", lambda _: None)
    monkeypatch.setattr(
        "app.transcription.whisper_cpp._installed_whisper_candidates",
        lambda: [executable],
    )
    assert resolve_whisper_cli() == executable.resolve()
