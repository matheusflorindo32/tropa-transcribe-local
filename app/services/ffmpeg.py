"""Conversão de mídia por FFmpeg, sem shell."""

from __future__ import annotations

import json
import shutil
import subprocess
import threading
from pathlib import Path

from app.config import default_data_dir


class FFmpegError(RuntimeError):
    """Falha controlada na conversão."""


def resolve_ffmpeg(candidate: str | Path = "ffmpeg") -> Path:
    value = str(candidate)
    resolved = shutil.which(value) if Path(value).name == value else value
    if not resolved and value == "ffmpeg":
        manifest_path = default_data_dir() / "installation.json"
        if manifest_path.is_file():
            try:
                payload = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
                manifest_ffmpeg = payload.get("ffmpeg")
                if isinstance(manifest_ffmpeg, str) and Path(manifest_ffmpeg).is_file():
                    resolved = manifest_ffmpeg
            except (OSError, json.JSONDecodeError):
                pass
    if not resolved or not Path(resolved).is_file():
        raise FileNotFoundError("FFmpeg não encontrado. Execute scripts/windows/verificar.ps1.")
    return Path(resolved).resolve()


def build_ffmpeg_command(executable: Path, source: Path, destination: Path) -> list[str]:
    return [
        str(executable),
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(source),
        "-vn",
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(destination),
    ]


def convert_to_wav(
    executable: Path,
    source: Path,
    destination: Path,
    cancel_event: threading.Event | None = None,
) -> Path:
    command = build_ffmpeg_command(executable, source, destination)
    process = subprocess.Popen(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True
    )
    while process.poll() is None:
        if cancel_event and cancel_event.wait(0.1):
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            raise InterruptedError("Conversão cancelada.")
    stderr = process.stderr.read() if process.stderr else ""
    if process.returncode != 0:
        detail = stderr.strip().splitlines()[-1] if stderr.strip() else "erro não detalhado"
        raise FFmpegError(f"FFmpeg não conseguiu converter o arquivo: {detail[:300]}")
    if not destination.is_file() or destination.stat().st_size == 0:
        raise FFmpegError("FFmpeg concluiu sem produzir áudio válido.")
    return destination
