#!/usr/bin/env python3
"""Gera SBOM CycloneDX e inventário SHA-256 para artefatos locais."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.metadata
import json
import platform
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_components(path: Path) -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("components"), list):
        raise ValueError("Manifesto de componentes inválido.")
    return payload


def create_sbom(manifest: dict[str, Any]) -> dict[str, Any]:
    components = []
    for item in manifest["components"]:
        license_expression = str(item["license"])
        version = str(item["version"])
        package = {
            "Python": None,
            "PySide6 / Qt for Python": "PySide6",
            "PyInstaller": "PyInstaller",
        }.get(item["name"])
        if item["name"] == "Python":
            version = platform.python_version()
        elif package:
            with contextlib.suppress(importlib.metadata.PackageNotFoundError):
                version = importlib.metadata.version(package)
        components.append(
            {
                "type": "application" if item["name"] == "Tropa Transcribe Local" else "library",
                "name": item["name"],
                "version": version,
                "licenses": [{"expression": license_expression}],
                "properties": [
                    {"name": "tropa:incorporated", "value": str(item["incorporated"]).lower()},
                    {"name": "tropa:purpose", "value": item["purpose"]},
                ],
            }
        )
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": "urn:uuid:c7b57a9f-a94d-57b4-884a-e243ae668d14",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "component": {
                "type": "application",
                "name": "Tropa Transcribe Local",
                "version": manifest["release"],
            },
        },
        "components": components,
    }


def create_hash_manifest(artifact_dir: Path) -> dict[str, Any]:
    files = []
    if artifact_dir.is_dir():
        for path in sorted(item for item in artifact_dir.rglob("*") if item.is_file()):
            files.append(
                {
                    "path": path.relative_to(artifact_dir).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    return {
        "algorithm": "SHA-256",
        "artifact_root": artifact_dir.name,
        "files": files,
        "total_size_bytes": sum(item["size_bytes"] for item in files),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--components", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest = load_components(args.components)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "sbom.cdx.json").write_text(
        json.dumps(create_sbom(manifest), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    hashes = create_hash_manifest(args.artifact_dir)
    if not hashes["files"]:
        raise FileNotFoundError("Nenhum artefato encontrado para gerar hashes.")
    (args.output_dir / "SHA256SUMS.json").write_text(
        json.dumps(hashes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
