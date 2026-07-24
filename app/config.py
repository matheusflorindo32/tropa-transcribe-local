"""Configuração persistente não sensível."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

APP_NAME = "TropaTranscribeLocal"


def default_data_dir() -> Path:
    """Retorna um diretório local do usuário sem pacote externo."""
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return root / APP_NAME


@dataclass(slots=True)
class AppConfig:
    """Preferências locais. Nunca armazena conteúdo ou credenciais."""

    model: str = "base"
    language: str = "pt"
    outputs: tuple[str, ...] = ("txt", "srt", "vtt")
    output_dir: str = ""
    max_file_size_mb: int = 20_480

    def validate(self) -> None:
        from app.transcription.formats import validate_output_formats
        from app.transcription.validators import validate_model_name

        validate_model_name(self.model)
        validate_output_formats(self.outputs)
        if not self.language or len(self.language) > 16:
            raise ValueError("Idioma inválido.")
        if self.max_file_size_mb <= 0:
            raise ValueError("O limite de arquivo deve ser positivo.")


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or default_data_dir() / "config.json"
    if not config_path.exists():
        return AppConfig()
    try:
        raw: dict[str, Any] = json.loads(config_path.read_text(encoding="utf-8"))
        raw["outputs"] = tuple(raw.get("outputs", ("txt", "srt", "vtt")))
        config = AppConfig(**raw)
        config.validate()
        return config
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ValueError(f"Configuração inválida em {config_path.name}.") from exc


def save_config(config: AppConfig, path: Path | None = None) -> Path:
    config.validate()
    config_path = path or default_data_dir() / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = config_path.with_suffix(".tmp")
    payload = asdict(config)
    payload["outputs"] = list(config.outputs)
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(config_path)
    return config_path
