from __future__ import annotations

import io
import threading
from pathlib import Path

import pytest

from app.services.ffmpeg import FFmpegError, convert_to_wav
from app.transcription.whisper_cpp import WhisperCppError, run_whisper


class FakeProcess:
    def __init__(self, returncode: int = 0, stderr: str = "") -> None:
        self.returncode = returncode
        self.stderr = io.StringIO(stderr)
        self.terminated = False

    def poll(self) -> int:
        return self.returncode

    def terminate(self) -> None:
        self.terminated = True

    def wait(self, timeout: int) -> int:
        return self.returncode

    def kill(self) -> None:
        self.returncode = -9


def test_ffmpeg_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    destination = tmp_path / "out.wav"

    def factory(command: list[str], **_kwargs: object) -> FakeProcess:
        Path(command[-1]).write_bytes(b"wav")
        return FakeProcess()

    monkeypatch.setattr("app.services.ffmpeg.subprocess.Popen", factory)
    result = convert_to_wav(Path("ffmpeg"), Path("in.ogg"), destination)
    assert result == destination


def test_ffmpeg_failure_and_empty_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.services.ffmpeg.subprocess.Popen",
        lambda *_args, **_kwargs: FakeProcess(1, "codec inválido"),
    )
    with pytest.raises(FFmpegError, match="codec inválido"):
        convert_to_wav(Path("ffmpeg"), Path("in.ogg"), tmp_path / "out.wav")
    monkeypatch.setattr(
        "app.services.ffmpeg.subprocess.Popen",
        lambda *_args, **_kwargs: FakeProcess(),
    )
    with pytest.raises(FFmpegError, match="áudio válido"):
        convert_to_wav(Path("ffmpeg"), Path("in.ogg"), tmp_path / "out.wav")


def test_whisper_success_and_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.transcription.whisper_cpp.subprocess.Popen",
        lambda *_args, **_kwargs: FakeProcess(),
    )
    run_whisper(["whisper-cli"])
    monkeypatch.setattr(
        "app.transcription.whisper_cpp.subprocess.Popen",
        lambda *_args, **_kwargs: FakeProcess(2, "modelo inválido"),
    )
    with pytest.raises(WhisperCppError, match="modelo inválido"):
        run_whisper(["whisper-cli"])


def test_already_cancelled_process(monkeypatch: pytest.MonkeyPatch) -> None:
    event = threading.Event()
    event.set()

    class RunningProcess(FakeProcess):
        def poll(self) -> int | None:
            return None if not self.terminated else -15

    monkeypatch.setattr(
        "app.transcription.whisper_cpp.subprocess.Popen",
        lambda *_args, **_kwargs: RunningProcess(),
    )
    with pytest.raises(InterruptedError):
        run_whisper(["whisper-cli"], event)
