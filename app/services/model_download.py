"""Download cancelável de modelos fixados no manifesto confiável."""

from __future__ import annotations

import json
import os
import shutil
import threading
import uuid
from collections.abc import Callable
from pathlib import Path

from app.services.models import default_models_dir, model_filename, validate_model_file
from app.services.runtime_manifest import load_runtime_manifest, model_spec
from app.services.runtime_provisioning import download_verified_file
from app.transcription.validators import validate_model_name

ProgressCallback = Callable[[int, str], None]
MODEL_DISK_MARGIN_BYTES = 256 * 1024**2


def required_free_bytes(name: str) -> int:
    """Reserva o arquivo temporário do modelo e margem operacional."""
    normalized = validate_model_name(name)
    return model_spec(normalized).size_bytes + MODEL_DISK_MARGIN_BYTES


def _write_model_record(path: Path, name: str) -> None:
    manifest = load_runtime_manifest()
    spec = manifest.models[name]
    record = path.with_suffix(".sha256.json")
    temporary = record.with_name(f".{record.name}.{uuid.uuid4().hex}.tmp")
    payload = {
        "schema_version": 2,
        "file": spec.filename,
        "size_bytes": spec.size_bytes,
        "sha256": spec.sha256,
        "source": spec.url,
        "source_revision": spec.revision,
        "license": spec.license,
        "runtime_manifest_sha256": manifest.digest,
        "verified_exact_size": True,
        "verified_sha256": True,
    }
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as output:
            json.dump(payload, output, ensure_ascii=False, indent=2)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(record)
    finally:
        temporary.unlink(missing_ok=True)


def download_model(
    name: str,
    directory: Path | None = None,
    *,
    force: bool = False,
    cancel_event: threading.Event | None = None,
    progress: ProgressCallback | None = None,
) -> Path:
    normalized = validate_model_name(name)
    manifest = load_runtime_manifest()
    spec = manifest.models[normalized]
    target_dir = (directory or default_models_dir()).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / model_filename(normalized)
    if destination.exists() and not force:
        try:
            return validate_model_file(destination, normalized)
        except ValueError:
            # Mantém o arquivo anterior até o novo download ser totalmente validado.
            pass
    required = spec.size_bytes + MODEL_DISK_MARGIN_BYTES
    if shutil.disk_usage(target_dir).free < required:
        raise OSError(
            f"Espaço livre insuficiente. São necessários ao menos {required / 1024**2:.0f} MiB."
        )
    result = download_verified_file(
        url=spec.url,
        sha256=spec.sha256,
        size_bytes=spec.size_bytes,
        destination=destination,
        allowed_hosts=manifest.allowed_download_hosts,
        cancel_event=cancel_event,
        progress=progress,
    )
    try:
        _write_model_record(result, normalized)
        return validate_model_file(result, normalized)
    except Exception:
        result.unlink(missing_ok=True)
        result.with_suffix(".sha256.json").unlink(missing_ok=True)
        raise


def delete_model(name: str, *, in_use: bool = False, directory: Path | None = None) -> None:
    if in_use:
        raise RuntimeError("O modelo está em uso e não pode ser excluído.")
    normalized = validate_model_name(name)
    target_dir = (directory or default_models_dir()).expanduser().resolve()
    path = target_dir / model_filename(normalized)
    path.unlink(missing_ok=True)
    path.with_suffix(".sha256.json").unlink(missing_ok=True)
