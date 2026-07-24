"""Gerenciador visual de modelos."""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from app.services.model_download import delete_model, required_free_bytes
from app.services.models import MODEL_CATALOG, default_models_dir, model_filename
from app.ui.workers import ModelDownloadWorker


class ModelManagerDialog(QDialog):
    models_changed = Signal()

    def __init__(self, active_model: str | None = None, parent: object | None = None) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self.active_model = active_model
        self.thread: QThread | None = None
        self.worker: ModelDownloadWorker | None = None
        self.setWindowTitle("Gerenciador de modelos")
        self.resize(620, 360)
        layout = QVBoxLayout(self)
        notice = QLabel(
            "Recomendação geral: small oferece bom equilíbrio para pt-BR. "
            "O download é externo, validado e promovido atomicamente. Downloads "
            "interrompidos são removidos; retomada não é oferecida sem garantia segura."
        )
        notice.setWordWrap(True)
        layout.addWidget(notice)
        self.selector = QComboBox()
        self.selector.addItems(MODEL_CATALOG)
        self.selector.setCurrentText("small")
        self.selector.currentTextChanged.connect(self._refresh)
        layout.addWidget(self.selector)
        self.details = QLabel()
        self.details.setWordWrap(True)
        layout.addWidget(self.details)
        self.progress = QProgressBar()
        self.progress.setAccessibleName("Progresso do download do modelo")
        layout.addWidget(self.progress)
        self.status = QLabel("Pronto.")
        layout.addWidget(self.status)
        actions = QHBoxLayout()
        self.download = QPushButton("Baixar e validar")
        self.download.clicked.connect(self._start_download)
        self.cancel = QPushButton("Interromper")
        self.cancel.setEnabled(False)
        self.cancel.clicked.connect(self._cancel)
        self.remove = QPushButton("Excluir modelo")
        self.remove.clicked.connect(self._delete)
        close = QPushButton("Fechar")
        close.clicked.connect(self.accept)
        actions.addWidget(self.download)
        actions.addWidget(self.cancel)
        actions.addWidget(self.remove)
        actions.addStretch()
        actions.addWidget(close)
        layout.addLayout(actions)
        self._refresh(self.selector.currentText())

    def _refresh(self, name: str) -> None:
        info = MODEL_CATALOG[name]
        installed = (default_models_dir() / model_filename(name)).is_file()
        required = required_free_bytes(name) / 1024**2
        self.details.setText(
            f"{info.disk} em disco · memória {info.memory} · velocidade {info.speed} · "
            f"qualidade {info.quality} · {'instalado' if installed else 'não instalado'}. "
            f"Espaço livre recomendado para baixar e validar: {required:.0f} MiB."
        )

    def _start_download(self) -> None:
        self.thread = QThread(self)
        self.worker = ModelDownloadWorker(self.selector.currentText())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._progress)
        self.worker.completed.connect(self._completed)
        self.worker.canceled.connect(self._failed)
        self.worker.failed.connect(self._failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self._reset)
        self.download.setEnabled(False)
        self.remove.setEnabled(False)
        self.cancel.setEnabled(True)
        self.thread.start()

    def _progress(self, percent: int, message: str) -> None:
        self.progress.setValue(percent)
        self.status.setText(message)

    def _completed(self, _path: str) -> None:
        self.status.setText("Modelo disponível e íntegro.")
        self.models_changed.emit()

    def _failed(self, message: str) -> None:
        self.status.setText(message)
        QMessageBox.warning(self, "Download não concluído", message)

    def _reset(self) -> None:
        self.worker = None
        self.thread = None
        self.download.setEnabled(True)
        self.remove.setEnabled(True)
        self.cancel.setEnabled(False)
        self._refresh(self.selector.currentText())

    def _cancel(self) -> None:
        if self.worker:
            self.worker.cancel()
            self.status.setText("Interrupção solicitada...")

    def _delete(self) -> None:
        name = self.selector.currentText()
        if (
            QMessageBox.question(
                self,
                "Excluir modelo",
                f"Excluir o modelo {name}? Transcrições existentes serão preservadas.",
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        try:
            delete_model(name, in_use=name == self.active_model)
            self.status.setText("Modelo excluído.")
            self.models_changed.emit()
        except (OSError, RuntimeError, ValueError) as exc:
            QMessageBox.warning(self, "Não foi possível excluir", str(exc))
        self._refresh(name)
