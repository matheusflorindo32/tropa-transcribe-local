from __future__ import annotations

from pathlib import Path

from app.utils.logging import configure_logging


def test_logging_to_file_without_content(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "app.log"
    logger = configure_logging(True, log_file)
    logger.info("evento operacional")
    assert "evento operacional" in log_file.read_text(encoding="utf-8")
    assert logger.level == 10
