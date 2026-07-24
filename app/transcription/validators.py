"""Validação de entrada antes de executar programas externos."""

from __future__ import annotations

from pathlib import Path

SUPPORTED_EXTENSIONS = frozenset(
    {".ogg", ".opus", ".mp3", ".wav", ".m4a", ".aac", ".flac", ".mp4", ".mov", ".mkv", ".webm"}
)
SUPPORTED_MODELS = frozenset(
    {
        "tiny",
        "base",
        "small",
        "medium",
        "large-v1",
        "large-v2",
        "large-v3",
        "large-v3-turbo",
        "tiny-q5_1",
        "base-q5_1",
        "small-q5_1",
        "medium-q5_0",
    }
)


def validate_input_file(path: Path, max_size_mb: int = 20_480) -> Path:
    candidate = path.expanduser().resolve()
    if not candidate.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path.name}")
    if not candidate.is_file():
        raise ValueError(f"O caminho não é um arquivo: {path.name}")
    if candidate.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Extensão não suportada: {candidate.suffix or '(sem extensão)'}")
    if candidate.stat().st_size <= 0:
        raise ValueError("O arquivo está vazio.")
    if candidate.stat().st_size > max_size_mb * 1024 * 1024:
        raise ValueError(f"O arquivo excede o limite configurado de {max_size_mb} MB.")
    return candidate


def validate_model_name(name: str) -> str:
    normalized = name.lower().strip()
    if normalized not in SUPPORTED_MODELS:
        raise ValueError(f"Modelo não suportado: {name}")
    return normalized


def collect_batch_files(directory: Path) -> list[Path]:
    root = directory.expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Pasta não encontrada: {directory}")
    return sorted(
        (
            path
            for path in root.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        key=lambda path: path.name.casefold(),
    )
