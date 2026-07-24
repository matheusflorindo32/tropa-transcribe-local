"""Operações seguras de caminhos."""

from __future__ import annotations

import re
from pathlib import Path

_UNSAFE_STEM = re.compile(r"[\x00-\x1f<>:\"/\\|?*]")


def safe_stem(path: Path) -> str:
    """Gera nome de saída portável preservando Unicode legível."""
    value = _UNSAFE_STEM.sub("_", path.stem).strip(" .")
    return value or "transcricao"


def ensure_output_dir(path: Path) -> Path:
    path = path.expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    if not path.is_dir():
        raise NotADirectoryError(f"Destino inválido: {path}")
    return path


def unique_output_base(directory: Path, stem: str) -> Path:
    candidate = directory / stem
    counter = 2
    while any(candidate.with_suffix(f".{ext}").exists() for ext in ("txt", "srt", "vtt", "json")):
        candidate = directory / f"{stem}-{counter}"
        counter += 1
    return candidate
