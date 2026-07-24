#!/usr/bin/env python3
"""Baixa modelos oficiais do ecossistema whisper.cpp com escrita atômica."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.error
import urllib.request
import uuid
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
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _trusted_sha256(headers: Message) -> str | None:
    value = headers.get("x-linked-etag", "").strip('"').lower()
    if SHA256_RE.fullmatch(value):
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


def _fetch_remote_metadata(url: str) -> tuple[str | None, int]:
    request = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "TropaTranscribeLocal/0.2.0-beta"},
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


def download_model(name: str, directory: Path, force: bool = False) -> Path:
    normalized = validate_model_name(name)
    filename = model_filename(normalized)
    models_directory = directory.expanduser().resolve()
    destination = models_directory / filename
    models_directory.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        validate_model_file(destination, normalized)
        print(f"Modelo existente e íntegro; download dispensado: {destination}")
        return destination
    url = f"{BASE_URL}/{filename}"
    temporary = models_directory / f".{filename}.{uuid.uuid4().hex}.part"
    manifest_temporary: Path | None = None
    digest = hashlib.sha256()
    expected_hash, expected_size = _fetch_remote_metadata(url)
    try:
        request = urllib.request.Request(
            url, headers={"User-Agent": "TropaTranscribeLocal/0.2.0-beta"}
        )
        with (
            urllib.request.urlopen(request, timeout=60) as response,
            temporary.open("wb") as output,
        ):
            expected_hash = expected_hash or _trusted_sha256(response.headers)
            expected_size = expected_size or _expected_size(response.headers)
            received = 0
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
                digest.update(chunk)
                received += len(chunk)
                if expected_size:
                    print(
                        f"\rBaixando: {received * 100 // expected_size:3d}%",
                        end="",
                        flush=True,
                    )
        print()
        if expected_size and received != expected_size:
            raise RuntimeError(
                f"Download incompleto: esperado {expected_size} bytes; recebido {received}."
            )
        minimum = minimum_model_bytes(normalized)
        if temporary.stat().st_size < minimum:
            raise RuntimeError(
                "Download incompleto: "
                f"{temporary.stat().st_size / 1024**2:.1f} MiB recebidos; "
                f"mínimo plausível {minimum // 1024**2} MiB."
            )
        actual_hash = digest.hexdigest()
        if expected_hash and actual_hash != expected_hash:
            raise RuntimeError("SHA-256 não corresponde ao ETag LFS publicado.")
        temporary.replace(destination)
        manifest = destination.with_suffix(".sha256.json")
        manifest_temporary = manifest.with_suffix(f".{uuid.uuid4().hex}.tmp")
        manifest_temporary.write_text(
            json.dumps(
                {
                    "file": filename,
                    "size_bytes": destination.stat().st_size,
                    "expected_size_bytes": expected_size or None,
                    "sha256": actual_hash,
                    "source": url,
                    "expected_sha256": expected_hash,
                    "verified_against_lfs_etag": bool(expected_hash),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        manifest_temporary.replace(manifest)
        validate_model_file(destination, normalized)
        return destination
    except (OSError, urllib.error.URLError):
        temporary.unlink(missing_ok=True)
        if manifest_temporary:
            manifest_temporary.unlink(missing_ok=True)
        raise
    except Exception:
        temporary.unlink(missing_ok=True)
        if manifest_temporary:
            manifest_temporary.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", help="Ex.: tiny, base, small ou large-v3-turbo.")
    parser.add_argument("--directory", type=Path, default=default_models_dir())
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        path = download_model(args.model, args.directory, args.force)
        print(f"Modelo disponível em: {path}")
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Erro: {exc}\n")


if __name__ == "__main__":
    main()
