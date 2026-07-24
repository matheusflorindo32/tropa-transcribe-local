"""Adaptador para whisper-cli v1.9.1."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
from pathlib import Path

from app.config import default_data_dir
from app.transcription.formats import output_flags


class WhisperCppError(RuntimeError):
    """Falha controlada do mecanismo."""


def _installed_whisper_candidates() -> list[Path]:
    install_root = default_data_dir()
    candidates: list[Path] = []
    manifest_path = install_root / "installation.json"
    if manifest_path.is_file():
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            manifest_cli = payload.get("whisper_cli")
            if isinstance(manifest_cli, str):
                candidates.append(Path(manifest_cli))
        except (OSError, json.JSONDecodeError):
            pass
    build_root = install_root / "runtime" / "whisper.cpp" / "build" / "bin"
    candidates.extend((build_root / "Release" / "whisper-cli.exe", build_root / "whisper-cli.exe"))
    return candidates


def resolve_whisper_cli(candidate: str | Path = "whisper-cli") -> Path:
    value = str(candidate)
    resolved: str | None = None
    if value == "whisper-cli":
        try:
            from app.services.runtime_provisioning import validate_component

            resolved = str(validate_component("whisper_cpp"))
        except (FileNotFoundError, OSError, ValueError, RuntimeError):
            pass
    if not resolved:
        resolved = shutil.which(value) if Path(value).name == value else value
    if not resolved and value == "whisper-cli":
        installed = next((path for path in _installed_whisper_candidates() if path.is_file()), None)
        resolved = str(installed) if installed else None
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
    executable = Path(command[0]).resolve()
    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        cwd=executable.parent,
        creationflags=creation_flags,
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
