#!/usr/bin/env python3
"""Baixa modelo fixado no manifesto com tamanho e SHA-256 obrigatórios."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.services.model_download import download_model as download_model_service
from app.services.models import default_models_dir


def download_model(name: str, directory: Path, force: bool = False) -> Path:
    """Compatibilidade para scripts: delega ao mesmo serviço seguro usado pela GUI."""

    def report(percent: int, message: str) -> None:
        print(f"\r{percent:3d}% — {message}", end="" if percent < 100 else "\n", flush=True)

    return download_model_service(name, directory, force=force, progress=report)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", help="Ex.: tiny, base, small ou large-v3-turbo.")
    parser.add_argument("--directory", type=Path, default=default_models_dir())
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        path = download_model(args.model, args.directory, args.force)
        print(f"Modelo disponível e validado em: {path}")
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Erro: {exc}\n")


if __name__ == "__main__":
    main()
