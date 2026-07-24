"""Janela principal funcional e acessível."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, QUrl
from PySide6.QtGui import QDesktopServices, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.config import load_config
from app.services.models import MODEL_CATALOG, default_models_dir, model_filename
from app.transcription.engine import TranscriptionEngine, TranscriptionRequest
from app.transcription.validators import SUPPORTED_EXTENSIONS
from app.ui.workers import TranscriptionWorker

ACCURACY_NOTICE = (
    "A transcrição é gerada automaticamente e pode conter erros. Revise nomes, números, "
    "termos técnicos e informações críticas antes de utilizar ou publicar o conteúdo."
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Tropa Transcribe Local")
        self.resize(760, 620)
        self.setAcceptDrops(True)
        self.output_dir = Path.cwd() / "transcricoes"
        self.thread: QThread | None = None
        self.worker: TranscriptionWorker | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        config = load_config()
        root = QWidget()
        layout = QVBoxLayout(root)

        title = QLabel("Tropa Transcribe Local")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        title.setAccessibleName("Título da aplicação")
        layout.addWidget(title)
        local_notice = QLabel("🔒 Processamento local — nenhum arquivo é enviado.")
        local_notice.setStyleSheet("color: #116329; font-weight: 600;")
        layout.addWidget(local_notice)
        warning = QLabel(ACCURACY_NOTICE)
        warning.setWordWrap(True)
        layout.addWidget(warning)

        select_button = QPushButton("Selecionar arquivos")
        select_button.clicked.connect(self._select_files)
        layout.addWidget(select_button)
        self.files = QListWidget()
        self.files.setAccessibleName("Arquivos selecionados")
        self.files.setToolTip("Também é possível arrastar arquivos para esta janela.")
        layout.addWidget(self.files, 1)

        form = QFormLayout()
        self.model = QComboBox()
        self.model.addItems(MODEL_CATALOG)
        self.model.setCurrentText(config.model)
        self.model.currentTextChanged.connect(self._update_model_info)
        form.addRow("Modelo:", self.model)
        self.model_info = QLabel()
        self.model_info.setWordWrap(True)
        self.model_info.setAccessibleName("Detalhes e disponibilidade do modelo")
        form.addRow("Detalhes:", self.model_info)
        self.language = QComboBox()
        self.language.setEditable(True)
        self.language.addItems(["pt", "auto", "en", "es"])
        self.language.setCurrentText(config.language)
        form.addRow("Idioma:", self.language)
        formats = QWidget()
        format_layout = QHBoxLayout(formats)
        format_layout.setContentsMargins(0, 0, 0, 0)
        self.format_checks: dict[str, QCheckBox] = {}
        for name in ("txt", "srt", "vtt", "json"):
            check = QCheckBox(name.upper())
            check.setChecked(name in config.outputs)
            self.format_checks[name] = check
            format_layout.addWidget(check)
        form.addRow("Saídas:", formats)
        layout.addLayout(form)

        output_row = QHBoxLayout()
        self.output_label = QLabel(str(self.output_dir))
        choose_output = QPushButton("Escolher destino")
        choose_output.clicked.connect(self._select_output_dir)
        output_row.addWidget(self.output_label, 1)
        output_row.addWidget(choose_output)
        layout.addLayout(output_row)

        self.progress = QProgressBar()
        self.progress.setAccessibleName("Progresso da transcrição")
        layout.addWidget(self.progress)
        self.status = QLabel("Pronto.")
        layout.addWidget(self.status)

        actions = QHBoxLayout()
        self.transcribe_button = QPushButton("Transcrever")
        self.transcribe_button.clicked.connect(self._start)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel)
        open_button = QPushButton("Abrir pasta de saída")
        open_button.clicked.connect(self._open_output)
        actions.addWidget(self.transcribe_button)
        actions.addWidget(self.cancel_button)
        actions.addWidget(open_button)
        layout.addLayout(actions)
        self.setCentralWidget(root)
        self._update_model_info(self.model.currentText())

    def _update_model_info(self, name: str) -> None:
        info = MODEL_CATALOG[name]
        downloaded = (default_models_dir() / model_filename(name)).is_file()
        status = "baixado" if downloaded else "não baixado"
        language = "multilíngue; recomendado para pt-BR" if info.multilingual else "somente inglês"
        self.model_info.setText(
            f"{info.disk} em disco · {info.memory} de memória · velocidade {info.speed} · "
            f"qualidade {info.quality} · {language} · {status}. "
            "O desempenho varia conforme o computador."
        )

    def _add_paths(self, paths: list[str]) -> None:
        known = {self.files.item(index).text() for index in range(self.files.count())}
        for raw in paths:
            path = Path(raw)
            if (
                path.is_file()
                and path.suffix.lower() in SUPPORTED_EXTENSIONS
                and str(path) not in known
            ):
                self.files.addItem(str(path))

    def _select_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Selecionar mídias")
        self._add_paths(paths)

    def _select_output_dir(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Pasta de destino", str(self.output_dir))
        if selected:
            self.output_dir = Path(selected)
            self.output_label.setText(selected)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        self._add_paths([url.toLocalFile() for url in event.mimeData().urls()])
        event.acceptProposedAction()

    def _start(self) -> None:
        if not self.files.count():
            QMessageBox.warning(self, "Nenhum arquivo", "Selecione ao menos um arquivo.")
            return
        formats = tuple(name for name, box in self.format_checks.items() if box.isChecked())
        if not formats:
            QMessageBox.warning(self, "Formato obrigatório", "Selecione ao menos um formato.")
            return
        requests = [
            TranscriptionRequest(
                input_file=Path(self.files.item(index).text()),
                output_dir=self.output_dir,
                model=self.model.currentText(),
                language=self.language.currentText(),
                formats=formats,
            )
            for index in range(self.files.count())
        ]
        self.thread = QThread(self)
        self.worker = TranscriptionWorker(TranscriptionEngine(), requests)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_progress)
        self.worker.completed.connect(self._on_completed)
        self.worker.failed.connect(self._on_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self._reset)
        self.transcribe_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.thread.start()

    def _cancel(self) -> None:
        if self.worker:
            self.worker.cancel()
            self.status.setText("Cancelamento solicitado...")

    def _on_progress(self, percent: int, message: str) -> None:
        self.progress.setValue(percent)
        self.status.setText(message)

    def _on_completed(self, generated: list[str]) -> None:
        self.status.setText(f"Concluído: {len(generated)} arquivo(s) gerado(s).")
        QMessageBox.information(self, "Concluído", f"{len(generated)} arquivo(s) gerado(s).")

    def _on_failed(self, message: str) -> None:
        self.status.setText("Falha ou cancelamento.")
        QMessageBox.critical(self, "Não foi possível concluir", message)

    def _reset(self) -> None:
        self.transcribe_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.worker = None
        self.thread = None

    def _open_output(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.output_dir.resolve())))
