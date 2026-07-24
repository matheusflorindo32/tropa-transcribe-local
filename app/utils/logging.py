"""Logs operacionais sem conteúdo transcrito."""

from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(verbose: bool, log_file: Path | None = None) -> logging.Logger:
    logger = logging.getLogger("tropa_transcribe")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
