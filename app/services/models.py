"""Catálogo e resolução de modelos ggml."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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

# Limites conservadores, abaixo dos tamanhos oficiais, mas altos o bastante para
# rejeitar páginas HTML, ponteiros Git LFS e downloads interrompidos.
MINIMUM_MODEL_BYTES = {
    "tiny": 70 * 1024**2,
    "base": 130 * 1024**2,
    "small": 430 * 1024**2,
    "medium": 1400 * 1024**2,
    "large-v1": 2700 * 1024**2,
    "large-v2": 2700 * 1024**2,
    "large-v3": 2700 * 1024**2,
    "large-v3-turbo": 1500 * 1024**2,
    "tiny-q5_1": 28 * 1024**2,
    "base-q5_1": 52 * 1024**2,
    "small-q5_1": 165 * 1024**2,
    "medium-q5_0": 500 * 1024**2,
}


def default_models_dir() -> Path:
    return default_data_dir() / "models"


def model_filename(name: str) -> str:
    return f"ggml-{validate_model_name(name)}.bin"


def minimum_model_bytes(name: str) -> int:
    return MINIMUM_MODEL_BYTES[validate_model_name(name)]


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _load_checksum_manifest(path: Path) -> dict[str, Any] | None:
    manifest_path = path.with_suffix(".sha256.json")
    if not manifest_path.is_file():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Metadados de integridade inválidos: {manifest_path.name}.") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Metadados de integridade inválidos: {manifest_path.name}.")
    return payload


def _is_managed_model_path(path: Path) -> bool:
    try:
        return path.parent.resolve() == default_models_dir().expanduser().resolve()
    except OSError:
        return False


def validate_model_file(
    path: Path,
    name: str,
    *,
    verify_recorded_sha256: bool = True,
    require_trusted_record: bool | None = None,
) -> Path:
    candidate = path.expanduser().resolve()
    normalized = validate_model_name(name)
    if not candidate.is_file():
        raise FileNotFoundError(f"Modelo '{normalized}' não encontrado em: {candidate}")
    minimum = minimum_model_bytes(normalized)
    actual_size = candidate.stat().st_size
    if actual_size < minimum:
        minimum_mib = minimum // 1024**2
        actual_mib = actual_size / 1024**2
        raise ValueError(
            f"O modelo '{normalized}' parece incompleto: {actual_mib:.1f} MiB; "
            f"mínimo plausível {minimum_mib} MiB."
        )

    trusted_record_required = (
        _is_managed_model_path(candidate)
        if require_trusted_record is None
        else require_trusted_record
    )
    metadata = _load_checksum_manifest(candidate)
    if trusted_record_required and metadata is None:
        raise ValueError(
            f"O modelo gerenciado '{normalized}' não possui registro de integridade confiável. "
            "Repare ou baixe o modelo novamente."
        )
    if not verify_recorded_sha256 or metadata is None:
        return candidate

    recorded = metadata.get("sha256")
    if not isinstance(recorded, str) or len(recorded) != 64:
        raise ValueError("O SHA-256 registrado para o modelo é inválido.")
    recorded = recorded.lower()

    if trusted_record_required:
        if metadata.get("schema_version") != 2:
            raise ValueError("O registro do modelo gerenciado não usa o esquema confiável atual.")
        from app.services.runtime_manifest import load_runtime_manifest, model_spec

        trusted_manifest = load_runtime_manifest()
        trusted = model_spec(normalized)
        if (
            recorded != trusted.sha256
            or actual_size != trusted.size_bytes
            or metadata.get("file") != trusted.filename
            or metadata.get("size_bytes") != trusted.size_bytes
            or metadata.get("runtime_manifest_sha256") != trusted_manifest.digest
            or metadata.get("verified_exact_size") is not True
            or metadata.get("verified_sha256") is not True
        ):
            raise ValueError("O registro local diverge do manifesto confiável do modelo.")

    if calculate_sha256(candidate) != recorded:
        raise ValueError("O SHA-256 do modelo não corresponde ao registro local.")
    return candidate


def resolve_model(name: str, explicit_path: Path | None = None) -> Path:
    normalized = validate_model_name(name)
    candidate = (
        explicit_path.expanduser().resolve()
        if explicit_path
        else default_models_dir() / model_filename(normalized)
    )
    try:
        return validate_model_file(
            candidate,
            normalized,
            require_trusted_record=explicit_path is None,
        )
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Modelo '{normalized}' não encontrado. "
            f"Use: python tools/download_model.py {normalized}"
        ) from exc
