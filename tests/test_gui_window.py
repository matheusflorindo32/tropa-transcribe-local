from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


@pytest.fixture
def application() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_window_adds_unicode_file_and_opens_output(
    application: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del application
    media = tmp_path / "áudio com espaço.ogg"
    media.write_bytes(b"x")
    window = MainWindow()
    window.output_dir = tmp_path / "saída com acento"
    opened: list[str] = []
    monkeypatch.setattr(
        "app.ui.main_window.QDesktopServices.openUrl",
        lambda url: opened.append(url.toLocalFile()) or True,
    )

    window._add_paths([str(media), str(media)])
    window._open_output()

    assert window.files.rowCount() == 1
    assert [Path(path) for path in opened] == [window.output_dir.resolve()]
    window.close()


def test_window_preview_is_bounded(
    application: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del application
    monkeypatch.setattr("app.ui.main_window.PREVIEW_LIMIT", 10)
    transcript = tmp_path / "transcrição.txt"
    transcript.write_text("x" * 20, encoding="utf-8")
    window = MainWindow()
    window.generated = [transcript]

    window._load_preview()

    assert "limitada" in window.preview.toPlainText()
    window.close()
