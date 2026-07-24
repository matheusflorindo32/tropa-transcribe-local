"""Formatos de saída do whisper.cpp."""

from __future__ import annotations

SUPPORTED_OUTPUTS = ("txt", "srt", "vtt", "json")
OUTPUT_FLAGS = {
    "txt": "--output-txt",
    "srt": "--output-srt",
    "vtt": "--output-vtt",
    "json": "--output-json",
}


def validate_output_formats(formats: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    normalized = tuple(dict.fromkeys(item.lower().strip() for item in formats))
    if not normalized:
        raise ValueError("Selecione ao menos um formato de saída.")
    unsupported = set(normalized) - set(SUPPORTED_OUTPUTS)
    if unsupported:
        raise ValueError(f"Formato(s) de saída não suportado(s): {', '.join(sorted(unsupported))}")
    return normalized


def output_flags(formats: tuple[str, ...] | list[str]) -> list[str]:
    return [OUTPUT_FLAGS[item] for item in validate_output_formats(formats)]
