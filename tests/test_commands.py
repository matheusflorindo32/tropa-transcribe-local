from __future__ import annotations

from pathlib import Path

from app.services.ffmpeg import build_ffmpeg_command
from app.transcription.whisper_cpp import build_whisper_command


def test_ffmpeg_command_is_argument_list_and_handles_spaces() -> None:
    command = build_ffmpeg_command(
        Path("C:/Program Files/ffmpeg.exe"),
        Path("C:/Mídia/áudio teste.ogg"),
        Path("C:/Temp/entrada.wav"),
    )
    assert command[0] == str(Path("C:/Program Files/ffmpeg.exe"))
    assert command[-1] == str(Path("C:/Temp/entrada.wav"))
    assert "-ar" in command and "16000" in command
    assert "-ac" in command and "1" in command


def test_whisper_command_has_verified_v191_flags() -> None:
    command = build_whisper_command(
        Path("C:/whisper-cli.exe"),
        Path("C:/models/ggml-base.bin"),
        Path("C:/Temp/entrada.wav"),
        Path("C:/Saída/reunião"),
        "pt",
        ("txt", "srt", "vtt", "json"),
        quiet=True,
    )
    assert "--model" in command
    assert "--output-file" in command
    assert "--output-json" in command
    assert "--no-prints" in command
    assert command.count(str(Path("C:/Saída/reunião"))) == 1
