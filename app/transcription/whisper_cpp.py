"""Adaptador para whisper-cli v1.9.1."""

from __future__ import annotations

import shutil
import subprocess
import threading
from pathlib import Path

from app.transcription.formats import output_flags


class WhisperCppError(RuntimeError):
    """Falha controlada do mecanismo."""


def resolve_whisper_cli(candidate: str | Path = "whisper-cli") -> Path:
    value = str(candidate)
    resolved = shutil.which(value) if Path(value).name == value else value
    if not resolved or not Path(resolved).is_file():
        raise FileNotFoundError(
            "whisper-cli não encontrado. Execute o instalador ou informe --whisper-cli."
        )
    return Path(resolved).resolve()


def build_whisper_command(
    executable: Path,
    model: Path,
    wav_file: Path,
    output_base: Path,
    language: str,
    formats: tuple[str, ...],
    quiet: bool = False,
) -> list[str]:
    command = [
        str(executable),
        "--model",
        str(model),
        "--file",
        str(wav_file),
        "--language",
        language,
        "--output-file",
        str(output_base),
        "--print-progress",
        *output_flags(formats),
    ]
    if quiet:
        command.append("--no-prints")
    return command


def run_whisper(
    command: list[str],
    cancel_event: threading.Event | None = None,
) -> None:
    process = subprocess.Popen(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True
    )
    while process.poll() is None:
        if cancel_event and cancel_event.wait(0.1):
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            raise InterruptedError("Transcrição cancelada.")
    stderr = process.stderr.read() if process.stderr else ""
    if process.returncode != 0:
        detail = stderr.strip().splitlines()[-1] if stderr.strip() else "erro não detalhado"
        raise WhisperCppError(f"whisper.cpp falhou: {detail[:300]}")
