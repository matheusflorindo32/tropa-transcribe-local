#!/usr/bin/env python3
"""Valida tamanho plausível e SHA-256 registrado de um modelo local."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.services.models import validate_model_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", help="Nome do modelo, por exemplo small.")
    parser.add_argument("path", type=Path, help="Caminho do arquivo ggml.")
    args = parser.parse_args()
    try:
        validated = validate_model_file(args.path, args.model)
        print(f"Modelo válido: {validated}")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Erro: {exc}\n")


if __name__ == "__main__":
    main()
