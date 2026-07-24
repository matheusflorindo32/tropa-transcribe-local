"""Download cancelável de modelos com validação e promoção atômica."""

from __future__ import annotations

import hashlib
import json
import shutil
import threading
import urllib.error
import urllib.request
import uuid
from collections.abc import Callable
from email.message import Message
from pathlib import Path

from app.services.models import (
    default_models_dir,
    minimum_model_bytes,
    model_filename,
    validate_model_file,
)
from app.transcription.validators import validate_model_name

BASE_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
ProgressCallback = Callable[[int, str], None]


def _trusted_sha256(headers: Message) -> str | None:
    value = headers.get("x-linked-etag", "").strip('"').lower()
    if len(value) == 64 and all(char in "0123456789abcdef" for char in value):
        return value
    return None


def _expected_size(headers: Message) -> int:
    for key in ("x-linked-size", "content-length"):
        value = headers.get(key, "")
        if value.isdigit() and int(value) > 0:
            return int(value)
    return 0


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        request: urllib.request.Request,
        file_pointer: object,
        code: int,
        message: str,
        headers: Message,
        new_url: str,
    ) -> None:
        return None


def _remote_metadata(url: str) -> tuple[str | None, int]:
    request = urllib.request.Request(  # noqa: S310 - URL HTTPS fixa
        url,
        method="HEAD",
        headers={"User-Agent": "TropaTranscribeLocal/0.3.0-alpha"},
    )
    try:
        with urllib.request.build_opener(_NoRedirect).open(request, timeout=60) as response:
            return _trusted_sha256(response.headers), _expected_size(response.headers)
    except urllib.error.HTTPError as exc:
        if 300 <= exc.code < 400:
            return _trusted_sha256(exc.headers), _expected_size(exc.headers)
        return None, 0
    except OSError:
        return None, 0


def required_free_bytes(name: str) -> int:
    """Reserva modelo + temporário + margem operacional de 256 MiB."""
    return minimum_model_bytes(name) * 2 + 256 * 1024**2


def download_model(
    name: str,
    directory: Path | None = None,
    *,
    force: bool = False,
    cancel_event: threading.Event | None = None,
    progress: ProgressCallback | None = None,
) -> Path:
    normalized = validate_model_name(name)
    target_dir = (directory or default_models_dir()).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / model_filename(normalized)
    if destination.exists() and not force:
        return validate_model_file(destination, normalized)
    if shutil.disk_usage(target_dir).free < required_free_bytes(normalized):
        raise OSError("Espaço livre insuficiente para download e validação segura do modelo.")

    temporary = target_dir / f".{destination.name}.{uuid.uuid4().hex}.part"
    url = f"{BASE_URL}/{destination.name}"
    digest = hashlib.sha256()
    expected_sha, expected_size = _remote_metadata(url)
    callback = progress or (lambda _percent, _message: None)
    try:
        request = urllib.request.Request(  # noqa: S310 - URL HTTPS fixa
            url, headers={"User-Agent": "TropaTranscribeLocal/0.3.0-alpha"}
        )
        with (
            urllib.request.urlopen(request, timeout=60) as response,  # noqa: S310
            temporary.open("wb") as out,
        ):
            expected_size = expected_size or _expected_size(response.headers)
            expected_sha = expected_sha or _trusted_sha256(response.headers)
            received = 0
            while chunk := response.read(1024 * 1024):
                if cancel_event and cancel_event.is_set():
                    raise InterruptedError("Download cancelado; arquivo parcial removido.")
                out.write(chunk)
                digest.update(chunk)
                received += len(chunk)
                percent = int(received * 100 / expected_size) if expected_size else 0
                callback(min(percent, 99), f"{received / 1024**2:.1f} MiB recebidos")
        if expected_size and temporary.stat().st_size != expected_size:
            raise RuntimeError("Download incompleto: o tamanho recebido diverge do servidor.")
        if temporary.stat().st_size < minimum_model_bytes(normalized):
            raise RuntimeError("Download incompleto: tamanho abaixo do mínimo plausível.")
        actual_sha = digest.hexdigest()
        if expected_sha and actual_sha != expected_sha:
            raise RuntimeError("SHA-256 não corresponde ao registro LFS da origem.")
        temporary.replace(destination)
        manifest = destination.with_suffix(".sha256.json")
        manifest_tmp = manifest.with_suffix(f".{uuid.uuid4().hex}.tmp")
        manifest_tmp.write_text(
            json.dumps(
                {
                    "file": destination.name,
                    "size_bytes": destination.stat().st_size,
                    "expected_size_bytes": expected_size or None,
                    "sha256": actual_sha,
                    "source": url,
                    "expected_sha256": expected_sha,
                    "verified_against_lfs_etag": bool(expected_sha),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        manifest_tmp.replace(manifest)
        callback(100, "Modelo baixado e validado.")
        return validate_model_file(destination, normalized)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def delete_model(name: str, *, in_use: bool = False, directory: Path | None = None) -> None:
    if in_use:
        raise RuntimeError("O modelo está em uso e não pode ser excluído.")
    normalized = validate_model_name(name)
    target_dir = (directory or default_models_dir()).expanduser().resolve()
    path = target_dir / model_filename(normalized)
    path.unlink(missing_ok=True)
    path.with_suffix(".sha256.json").unlink(missing_ok=True)
