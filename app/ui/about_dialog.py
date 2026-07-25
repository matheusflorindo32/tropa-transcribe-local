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
            "<p><b>Componentes incorporados:</b> Python 3.11 (PSF-2.0), PySide6/Qt 6 "
            "(LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only) e bootloader PyInstaller "
            "(GPL-2.0-or-later com Bootloader Exception).</p>"
            "<p><b>Downloads opcionais:</b> whisper.cpp v1.9.1 e pesos Whisper (MIT); "
            "FFmpeg n8.1.2-31 shared do FFmpeg-Builds (LGPL-3.0-or-later conforme "
            "manifesto fixado).</p>"
            "<p>As bibliotecas Qt são distribuídas dinamicamente e não foram modificadas. "
            "Os avisos, inventário, SBOM e instruções de substituição acompanham o pacote.</p>"
            "<p>Sem conta, telemetria ou upload. O conteúdo permanece no computador.</p>"
        )
        text.setWordWrap(True)
        text.setOpenExternalLinks(False)
        layout.addWidget(text)
        close = QPushButton("Fechar")
        close.clicked.connect(self.accept)
        layout.addWidget(close)
