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


def _promote_model_transactionally(incoming: Path, destination: Path, name: str) -> Path:
    """Promove modelo e sidecar como um conjunto, restaurando o anterior em falha."""
    token = uuid.uuid4().hex
    incoming_record = incoming.with_suffix(".sha256.json")
    destination_record = destination.with_suffix(".sha256.json")
    backup_model = destination.with_name(f".{destination.name}.{token}.bak")
    backup_record = destination_record.with_name(f".{destination_record.name}.{token}.bak")

    had_model = destination.exists()
    had_record = destination_record.exists()
    try:
        if had_model:
            destination.replace(backup_model)
        if had_record:
            destination_record.replace(backup_record)

        incoming.replace(destination)
        incoming_record.replace(destination_record)
        validated = validate_model_file(
            destination,
            name,
            require_trusted_record=True,
        )
        backup_model.unlink(missing_ok=True)
        backup_record.unlink(missing_ok=True)
        return validated
    except Exception:
        destination.unlink(missing_ok=True)
        destination_record.unlink(missing_ok=True)
        if backup_model.exists():
            backup_model.replace(destination)
        if backup_record.exists():
            backup_record.replace(destination_record)
        raise
    finally:
        incoming.unlink(missing_ok=True)
        incoming_record.unlink(missing_ok=True)
        backup_model.unlink(missing_ok=True)
        backup_record.unlink(missing_ok=True)


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
            return validate_model_file(
                destination,
                normalized,
                require_trusted_record=True,
            )
        except ValueError:
            # Mantém o arquivo anterior até o novo conjunto ser validado e promovido.
            pass

    required = spec.size_bytes + MODEL_DISK_MARGIN_BYTES
    if shutil.disk_usage(target_dir).free < required:
        raise OSError(
            f"Espaço livre insuficiente. São necessários ao menos {required / 1024**2:.0f} MiB."
        )

    token = uuid.uuid4().hex
    incoming = target_dir / f".{destination.name}.{token}.incoming"
    try:
        result = download_verified_file(
            url=spec.url,
            sha256=spec.sha256,
            size_bytes=spec.size_bytes,
            destination=incoming,
            allowed_hosts=manifest.allowed_download_hosts,
            cancel_event=cancel_event,
            progress=progress,
        )
        _write_model_record(result, normalized)
        validate_model_file(
            result,
            normalized,
            require_trusted_record=True,
        )
        return _promote_model_transactionally(result, destination, normalized)
    except Exception:
        incoming.unlink(missing_ok=True)
        incoming.with_suffix(".sha256.json").unlink(missing_ok=True)
        raise


def delete_model(name: str, *, in_use: bool = False, directory: Path | None = None) -> None:
    if in_use:
        raise RuntimeError("O modelo está em uso e não pode ser excluído.")
    normalized = validate_model_name(name)
    target_dir = (directory or default_models_dir()).expanduser().resolve()
    path = target_dir / model_filename(normalized)
    path.unlink(missing_ok=True)
    path.with_suffix(".sha256.json").unlink(missing_ok=True)
