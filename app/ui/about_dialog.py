"""Informações institucionais e de licenças."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from app import __version__


class AboutDialog(QDialog):
    def __init__(self, parent: object | None = None) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self.setWindowTitle("Sobre")
        layout = QVBoxLayout(self)
        text = QLabel(
            f"<h2>Tropa Transcribe Local {__version__}</h2>"
            "<p>Projeto independente da Tropa Científica, sem afiliação oficial com "
            "OpenAI, ggml-org, Qt ou FFmpeg.</p>"
            "<p>O código autoral usa MIT. PySide6/Qt usa LGPL-3.0/GPL-3.0 ou licença "
            "comercial; PyInstaller usa GPL-2.0 com exceção; whisper.cpp e Whisper usam "
            "MIT. A licença da build de FFmpeg depende da configuração específica.</p>"
            "<p>Sem conta, telemetria ou upload. O conteúdo permanece no computador.</p>"
        )
        text.setWordWrap(True)
        text.setOpenExternalLinks(False)
        layout.addWidget(text)
        close = QPushButton("Fechar")
        close.clicked.connect(self.accept)
        layout.addWidget(close)
