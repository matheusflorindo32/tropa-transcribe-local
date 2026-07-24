#!/usr/bin/env python3
"""Baixa modelos oficiais do ecossistema whisper.cpp com escrita atômica."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.error
import urllib.request
from email.message import Message
from pathlib import Path

from app.services.models import default_models_dir, model_filename
from app.transcription.validators import validate_model_name

BASE_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _trusted_sha256(headers: Message) -> str | None:
    for key in ("x-linked-etag", "etag"):
        value = headers.get(key, "").strip('"').lower()
        if SHA256_RE.fullmatch(value):
            return value
    return None


def download_model(name: str, directory: Path, force: bool = False) -> Path:
    normalized = validate_model_name(name)
    filename = model_filename(normalized)
    destination = directory.expanduser().resolve() / filename
    directory.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        raise FileExistsError(f"O modelo já existe: {destination}")
    url = f"{BASE_URL}/{filename}"
    temporary = destination.with_suffix(".part")
    digest = hashlib.sha256()
    expected_hash: str | None = None
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "TropaTranscribeLocal/0.1"})
        with (
            urllib.request.urlopen(request, timeout=60) as response,
            temporary.open("wb") as output,
        ):
            expected_hash = _trusted_sha256(response.headers)
            total = int(response.headers.get("Content-Length", "0"))
            received = 0
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
                digest.update(chunk)
                received += len(chunk)
                if total:
                    print(f"\rBaixando: {received * 100 // total:3d}%", end="", flush=True)
        print()
        if temporary.stat().st_size < 1024 * 1024:
            raise RuntimeError("Download incompleto: arquivo menor que 1 MiB.")
        actual_hash = digest.hexdigest()
        if expected_hash and actual_hash != expected_hash:
            raise RuntimeError("SHA-256 não corresponde ao ETag LFS publicado.")
        temporary.replace(destination)
        manifest = destination.with_suffix(".sha256.json")
        manifest.write_text(
            json.dumps(
                {
                    "file": filename,
                    "sha256": actual_hash,
                    "source": url,
                    "verified_against_lfs_etag": bool(expected_hash),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return destination
    except (OSError, urllib.error.URLError):
        temporary.unlink(missing_ok=True)
        raise
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", help="Ex.: tiny, base, small ou large-v3-turbo.")
    parser.add_argument("--directory", type=Path, default=default_models_dir())
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        path = download_model(args.model, args.directory, args.force)
        print(f"Modelo salvo em: {path}")
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Erro: {exc}\n")


if __name__ == "__main__":
    main()
