from __future__ import annotations

from pathlib import Path

import pytest

from app.transcription.engine import TranscriptionEngine, TranscriptionRequest
from app.transcription.progress import ProgressEvent, Stage


def test_engine_complete_flow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "áudio com espaço.ogg"
    source.write_bytes(b"artificial")
    model = tmp_path / "ggml-base.bin"
    model.write_bytes(b"x" * 2048)
    executable = tmp_path / "tool.exe"
    executable.write_bytes(b"x")
    events: list[ProgressEvent] = []
    seen_command: list[str] = []

    monkeypatch.setattr("app.transcription.engine.resolve_ffmpeg", lambda _: executable)
    monkeypatch.setattr("app.transcription.engine.resolve_whisper_cli", lambda _: executable)
    monkeypatch.setattr("app.transcription.engine.resolve_model", lambda *_: model)

    def fake_convert(_exe: Path, _source: Path, destination: Path, _cancel: object) -> Path:
        destination.write_bytes(b"wav")
        return destination

    def fake_run(command: list[str], _cancel: object) -> None:
        seen_command.extend(command)
        output_base = Path(command[command.index("--output-file") + 1])
        for extension in ("txt", "srt", "vtt"):
            output_base.with_suffix(f".{extension}").write_text("artificial", encoding="utf-8")

    monkeypatch.setattr("app.transcription.engine.convert_to_wav", fake_convert)
    monkeypatch.setattr("app.transcription.engine.run_whisper", fake_run)

    generated = TranscriptionEngine().transcribe(
        TranscriptionRequest(source, tmp_path / "saída", model_path=model),
        events.append,
    )
    assert [path.suffix for path in generated] == [".txt", ".srt", ".vtt"]
    assert events[0].stage is Stage.VALIDATING
    assert events[-1].stage is Stage.COMPLETED
    assert "--language" in seen_command


def test_engine_detects_missing_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "input.wav"
    source.write_bytes(b"x")
    tool = tmp_path / "tool.exe"
    tool.write_bytes(b"x")
    model = tmp_path / "model.bin"
    model.write_bytes(b"x" * 2048)
    monkeypatch.setattr("app.transcription.engine.resolve_ffmpeg", lambda _: tool)
    monkeypatch.setattr("app.transcription.engine.resolve_whisper_cli", lambda _: tool)
    monkeypatch.setattr("app.transcription.engine.resolve_model", lambda *_: model)
    monkeypatch.setattr(
        "app.transcription.engine.convert_to_wav",
        lambda _a, _b, destination, _d: destination.write_bytes(b"wav"),
    )
    monkeypatch.setattr("app.transcription.engine.run_whisper", lambda *_: None)
    with pytest.raises(RuntimeError, match="não gerada"):
        TranscriptionEngine().transcribe(
            TranscriptionRequest(source, tmp_path / "output", formats=("txt",))
        )
