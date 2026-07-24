"""Diálogo de diagnóstico copiável e sem conteúdo privado."""

from __future__ import annotations

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QDialog, QHBoxLayout, QPlainTextEdit, QPushButton, QVBoxLayout

from app.services.diagnostics import build_diagnostic


class DiagnosticsDialog(QDialog):
    def __init__(self, model: str, parent: object | None = None) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self.setWindowTitle("Diagnóstico")
        self.resize(720, 520)
        self.report = build_diagnostic(model)
        layout = QVBoxLayout(self)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setAccessibleName("Relatório de diagnóstico seguro")
        self.text.setPlainText(self.report.safe_text())
        layout.addWidget(self.text)
        actions = QHBoxLayout()
        copy = QPushButton("Copiar diagnóstico")
        copy.clicked.connect(self._copy)
        close = QPushButton("Fechar")
        close.clicked.connect(self.accept)
        actions.addStretch()
        actions.addWidget(copy)
        actions.addWidget(close)
        layout.addLayout(actions)

    def _copy(self) -> None:
        QGuiApplication.clipboard().setText(self.report.safe_text())
