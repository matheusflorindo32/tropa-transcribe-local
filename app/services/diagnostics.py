"""Diagnóstico local com exportação deliberadamente redigida."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from app import __version__
from app.config import default_data_dir
from app.services.ffmpeg import resolve_ffmpeg
from app.services.models import default_models_dir, validate_model_file
from app.transcription.whisper_cpp import resolve_whisper_cli


@dataclass(frozen=True, slots=True)
class DiagnosticReport:
    values: dict[str, str]

    def safe_text(self) -> str:
        """Texto copiável sem mídia, credenciais, usuário ou caminhos privados."""
        lines = ["Tropa Transcribe Local — diagnóstico seguro"]
        for key, value in self.values.items():
            lines.append(f"{key}: {_redact(value)}")
        return "\n".join(lines)


def _redact(value: str) -> str:
    home = str(Path.home())
    result = value.replace(home, "%USERPROFILE%")
    for key in ("LOCALAPPDATA", "APPDATA", "TEMP", "TMP"):
        raw = os.environ.get(key)
        if raw:
            result = result.replace(raw, f"%{key}%")
    return result


def _memory_available() -> str:
    if os.name == "nt":
        try:
            powershell = shutil.which("powershell")
            if not powershell:
                return "indisponível"
            output = subprocess.run(
                [
                    powershell,
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory",
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            ).stdout.strip()
            return f"{int(output) * 1024 / 1024**3:.1f} GiB"
        except (OSError, ValueError, subprocess.SubprocessError):
            return "indisponível"
    meminfo = Path("/proc/meminfo")
    try:
        line = next(
            item
            for item in meminfo.read_text(encoding="ascii").splitlines()
            if item.startswith("MemAvailable:")
        )
        return f"{int(line.split()[1]) * 1024 / 1024**3:.1f} GiB"
    except (OSError, StopIteration, ValueError):
        return "indisponível"


def _component(label: str, resolver: object) -> tuple[str, Path | None]:
    try:
        path = resolver()  # type: ignore[operator]
        return f"disponível ({Path(path).name})", Path(path)
    except (FileNotFoundError, OSError, ValueError):
        return f"ausente — execute a verificação de {label}", None


def _whisper_version(executable: Path | None) -> str:
    if executable is None:
        return "indisponível"
    try:
        result = subprocess.run(
            [str(executable), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        text = (result.stdout or result.stderr).strip().splitlines()
        return text[0][:120] if text else "não informada"
    except (OSError, subprocess.SubprocessError):
        return "não informada"


def build_diagnostic(model: str) -> DiagnosticReport:
    data_dir = default_data_dir()
    models_dir = default_models_dir()
    disk = shutil.disk_usage(data_dir.parent if data_dir.parent.exists() else Path.home())
    ffmpeg_status, _ = _component("FFmpeg", resolve_ffmpeg)
    whisper_status, whisper_path = _component("whisper-cli", resolve_whisper_cli)
    model_path = models_dir / f"ggml-{model}.bin"
    try:
        validate_model_file(model_path, model)
        model_status = f"íntegro ({model})"
    except FileNotFoundError:
        model_status = f"ausente ({model})"
    except ValueError:
        model_status = f"corrompido ou incompleto ({model})"
    values = {
        "Aplicativo": __version__,
        "Instalação registrada": installation_version(),
        "Sistema": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "CPU": platform.processor() or "não informada",
        "Memória disponível": _memory_available(),
        "Espaço livre": f"{disk.free / 1024**3:.1f} GiB",
        "FFmpeg": ffmpeg_status,
        "whisper-cli": whisper_status,
        "whisper.cpp": _whisper_version(whisper_path),
        "Modelo": model_status,
        "Dados": str(data_dir),
        "Modelos": str(models_dir),
        "Configuração": str(data_dir / "config.json"),
        "Teste básico": (
            "aprovado"
            if "disponível" in ffmpeg_status
            and "disponível" in whisper_status
            and model_status.startswith("íntegro")
            else "reprovado — consulte os itens acima"
        ),
    }
    return DiagnosticReport(values)


def installation_version() -> str:
    manifest = default_data_dir() / "installation.json"
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return "não registrada"
    value = payload.get("version")
    return str(value) if value else "não registrada"
