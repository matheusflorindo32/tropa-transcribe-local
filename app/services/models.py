"""Catálogo e resolução de modelos ggml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config import default_data_dir
from app.transcription.validators import validate_model_name


@dataclass(frozen=True, slots=True)
class ModelInfo:
    name: str
    disk: str
    memory: str
    speed: str
    quality: str
    multilingual: bool = True


MODEL_CATALOG = {
    "tiny": ModelInfo("tiny", "75 MiB", "~273 MB", "muito alta", "básica"),
    "base": ModelInfo("base", "142 MiB", "~388 MB", "alta", "boa"),
    "small": ModelInfo("small", "466 MiB", "~852 MB", "média", "muito boa"),
    "medium": ModelInfo("medium", "1,5 GiB", "~2,1 GB", "baixa", "superior"),
    "large-v1": ModelInfo("large-v1", "2,9 GiB", "~3,9 GB", "muito baixa", "alta"),
    "large-v2": ModelInfo("large-v2", "2,9 GiB", "~3,9 GB", "muito baixa", "alta"),
    "large-v3": ModelInfo("large-v3", "2,9 GiB", "~3,9 GB", "muito baixa", "máxima"),
    "large-v3-turbo": ModelInfo("large-v3-turbo", "1,6 GiB", "~2,5 GB", "média", "muito alta"),
    "tiny-q5_1": ModelInfo("tiny-q5_1", "~31 MiB", "~200 MB", "muito alta", "básica"),
    "base-q5_1": ModelInfo("base-q5_1", "~57 MiB", "~300 MB", "alta", "boa"),
    "small-q5_1": ModelInfo("small-q5_1", "~181 MiB", "~650 MB", "média", "boa"),
    "medium-q5_0": ModelInfo("medium-q5_0", "~539 MiB", "~1,5 GB", "baixa", "muito boa"),
}


def default_models_dir() -> Path:
    return default_data_dir() / "models"


def model_filename(name: str) -> str:
    return f"ggml-{validate_model_name(name)}.bin"


def resolve_model(name: str, explicit_path: Path | None = None) -> Path:
    candidate = (
        explicit_path.expanduser().resolve()
        if explicit_path
        else default_models_dir() / model_filename(name)
    )
    if not candidate.is_file():
        raise FileNotFoundError(
            f"Modelo '{name}' não encontrado. Use: python tools/download_model.py {name}"
        )
    if candidate.stat().st_size < 1024:
        raise ValueError("O arquivo do modelo parece incompleto.")
    return candidate
