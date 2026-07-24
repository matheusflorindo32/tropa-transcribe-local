from __future__ import annotations

from pathlib import Path

import pytest

from app.transcription.validators import (
    collect_batch_files,
    validate_input_file,
    validate_model_name,
)


@pytest.mark.parametrize("suffix", [".ogg", ".OPUS", ".mp3", ".wav", ".m4a", ".mp4", ".webm"])
def test_supported_extensions(tmp_path: Path, suffix: str) -> None:
    media = tmp_path / f"áudio com espaço{suffix}"
    media.write_bytes(b"artificial")
    assert validate_input_file(media) == media.resolve()


def test_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        validate_input_file(Path("inexistente.ogg"))


def test_empty_and_unsupported_files(tmp_path: Path) -> None:
    empty = tmp_path / "vazio.wav"
    empty.touch()
    with pytest.raises(ValueError, match="vazio"):
        validate_input_file(empty)
    text = tmp_path / "arquivo.txt"
    text.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="Extensão"):
        validate_input_file(text)


def test_file_size_limit(tmp_path: Path) -> None:
    media = tmp_path / "grande.wav"
    media.write_bytes(b"xx")
    with pytest.raises(ValueError, match="limite"):
        validate_input_file(media, max_size_mb=0)


@pytest.mark.parametrize("model", ["tiny", "base", "small", "medium", "large-v3", "base-q5_1"])
def test_valid_models(model: str) -> None:
    assert validate_model_name(model.upper()) == model


def test_invalid_model() -> None:
    with pytest.raises(ValueError):
        validate_model_name("../../segredo")


def test_collect_batch_is_filtered_and_sorted(tmp_path: Path) -> None:
    (tmp_path / "b.mp3").write_bytes(b"x")
    (tmp_path / "á.wav").write_bytes(b"x")
    (tmp_path / "ignore.txt").write_text("x", encoding="utf-8")
    assert [path.name for path in collect_batch_files(tmp_path)] == ["b.mp3", "á.wav"]


def test_collect_batch_requires_directory(tmp_path: Path) -> None:
    with pytest.raises(NotADirectoryError):
        collect_batch_files(tmp_path / "não-existe")
