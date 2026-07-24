"""Janela principal funcional, acessível e não bloqueante."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread, QUrl
from PySide6.QtGui import QDesktopServices, QDragEnterEvent, QDropEvent, QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.config import load_config
from app.services.models import MODEL_CATALOG, default_models_dir, model_filename
from app.services.queue import QueueStatus, TranscriptionQueue
from app.transcription.engine import TranscriptionEngine, TranscriptionRequest
from app.ui.about_dialog import AboutDialog
from app.ui.diagnostics_dialog import DiagnosticsDialog
from app.ui.model_manager_dialog import ModelManagerDialog
from app.ui.workers import TranscriptionWorker

ACCURACY_NOTICE = (
    "Revisão humana obrigatória: a transcrição automática pode errar nomes, números, "
    "termos técnicos e informações críticas."
)
PREVIEW_LIMIT = 1024 * 1024


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Tropa Transcribe Local")
        self.resize(980, 760)
        self.setMinimumSize(720, 560)
        self.setAcceptDrops(True)
        self.output_dir = Path.cwd() / "transcricoes"
        self.queue = TranscriptionQueue()
        self.generated: list[Path] = []
        self.thread: QThread | None = None
        self.worker: TranscriptionWorker | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        config = load_config()
        if config.output_dir:
            self.output_dir = Path(config.output_dir)
        root = QWidget()
        layout = QVBoxLayout(root)

        title = QLabel("Tropa Transcribe Local")
        title.setObjectName("title")
        title.setAccessibleName("Título da aplicação")
        layout.addWidget(title)
        local_notice = QLabel("PROCESSAMENTO LOCAL • sem conta • sem telemetria • sem upload")
        local_notice.setObjectName("privacyNotice")
        local_notice.setWordWrap(True)
        layout.addWidget(local_notice)
        warning = QLabel(ACCURACY_NOTICE)
        warning.setObjectName("accuracyNotice")
        warning.setWordWrap(True)
        layout.addWidget(warning)

        file_actions = QHBoxLayout()
        select_button = QPushButton("&Selecionar arquivos")
        select_button.clicked.connect(self._select_files)
        self.remove_button = QPushButton("&Remover selecionados")
        self.remove_button.clicked.connect(self._remove_selected)
        self.clear_button = QPushButton("Limpar &fila")
        self.clear_button.clicked.connect(self._clear_queue)
        file_actions.addWidget(select_button)
        file_actions.addWidget(self.remove_button)
        file_actions.addWidget(self.clear_button)
        file_actions.addStretch()
        layout.addLayout(file_actions)

        splitter = QSplitter(Qt.Orientation.Vertical)
        self.files = QTableWidget(0, 3)
        self.files.setHorizontalHeaderLabels(["Arquivo", "Status", "Progresso"])
        self.files.setAccessibleName("Fila de arquivos selecionados")
        self.files.setToolTip("Selecione ou arraste mídias. Duplicatas são ignoradas.")
        self.files.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.files.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.files.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.files.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.files.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.files.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        splitter.addWidget(self.files)

        preview_area = QWidget()
        preview_layout = QVBoxLayout(preview_area)
        preview_actions = QHBoxLayout()
        preview_actions.addWidget(QLabel("Prévia da transcrição"))
        preview_actions.addStretch()
        copy_preview = QPushButton("&Copiar texto")
        copy_preview.clicked.connect(self._copy_preview)
        preview_actions.addWidget(copy_preview)
        preview_layout.addLayout(preview_actions)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("A prévia TXT aparecerá aqui após a transcrição.")
        self.preview.setAccessibleName("Prévia da transcrição")
        preview_layout.addWidget(self.preview)
        splitter.addWidget(preview_area)
        splitter.setSizes([300, 220])
        layout.addWidget(splitter, 1)

        form = QFormLayout()
        self.model = QComboBox()
        self.model.addItems(MODEL_CATALOG)
        self.model.setCurrentText(config.model if config.model in MODEL_CATALOG else "small")
        self.model.currentTextChanged.connect(self._update_model_info)
        form.addRow("&Modelo:", self.model)
        self.model_info = QLabel()
        self.model_info.setWordWrap(True)
        self.model_info.setAccessibleName("Detalhes e disponibilidade do modelo")
        form.addRow("Detalhes:", self.model_info)
        self.language = QComboBox()
        self.language.setEditable(True)
        self.language.addItems(["pt", "auto", "en", "es"])
        self.language.setCurrentText(config.language)
        form.addRow("&Idioma:", self.language)
        formats = QWidget()
        format_layout = QHBoxLayout(formats)
        format_layout.setContentsMargins(0, 0, 0, 0)
        self.format_checks: dict[str, QCheckBox] = {}
        for name in ("txt", "srt", "vtt", "json"):
            check = QCheckBox(name.upper())
            check.setChecked(name in config.outputs)
            self.format_checks[name] = check
            format_layout.addWidget(check)
        format_layout.addStretch()
        form.addRow("Saídas:", formats)
        layout.addLayout(form)

        output_row = QHBoxLayout()
        self.output_label = QLabel(str(self.output_dir))
        self.output_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard)
        choose_output = QPushButton("Escolher &destino")
        choose_output.clicked.connect(self._select_output_dir)
        output_row.addWidget(QLabel("Destino:"))
        output_row.addWidget(self.output_label, 1)
        output_row.addWidget(choose_output)
        layout.addLayout(output_row)

        self.total_progress = QProgressBar()
        self.total_progress.setAccessibleName("Progresso total da transcrição")
        layout.addWidget(self.total_progress)
        self.status = QLabel("Pronto. Adicione um ou mais arquivos.")
        self.status.setAccessibleName("Estado atual")
        layout.addWidget(self.status)

        actions = QHBoxLayout()
        self.transcribe_button = QPushButton("&Transcrever")
        self.transcribe_button.setObjectName("primaryAction")
        self.transcribe_button.clicked.connect(self._start)
        self.cancel_button = QPushButton("&Cancelar")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel)
        open_button = QPushButton("&Abrir pasta de saída")
        open_button.clicked.connect(self._open_output)
        diagnostic = QPushButton("&Diagnóstico")
        diagnostic.clicked.connect(self._show_diagnostics)
        models = QPushButton("&Modelos")
        models.clicked.connect(self._show_models)
        about = QPushButton("S&obre")
        about.clicked.connect(self._show_about)
        actions.addWidget(self.transcribe_button)
        actions.addWidget(self.cancel_button)
        actions.addWidget(open_button)
        actions.addStretch()
        actions.addWidget(diagnostic)
        actions.addWidget(models)
        actions.addWidget(about)
        layout.addLayout(actions)
        self.setCentralWidget(root)
        self._update_model_info(self.model.currentText())
        self.setStyleSheet(
            """
            QLabel#title { font-size: 22px; font-weight: 700; }
            QLabel#privacyNotice {
                color: #0a4d24; background: #dff6e7; border: 1px solid #30824d;
                padding: 7px; font-weight: 700;
            }
            QLabel#accuracyNotice {
                color: #5b3600; background: #fff4ce; border: 1px solid #9a6700;
                padding: 7px;
            }
            QPushButton#primaryAction { font-weight: 700; padding: 7px 14px; }
            QPushButton:focus, QComboBox:focus, QTableWidget:focus,
            QPlainTextEdit:focus, QCheckBox:focus {
                border: 2px solid palette(highlight);
            }
            """
        )

    def _update_model_info(self, name: str) -> None:
        info = MODEL_CATALOG[name]
        downloaded = (default_models_dir() / model_filename(name)).is_file()
        status = "baixado" if downloaded else "não baixado"
        language = "multilíngue; recomendado para pt-BR" if info.multilingual else "somente inglês"
        recommendation = " Recomendado para uso geral." if name == "small" else ""
        self.model_info.setText(
            f"{info.disk} em disco · {info.memory} de memória · velocidade {info.speed} · "
            f"qualidade {info.quality} · {language} · {status}.{recommendation}"
        )

    def _add_paths(self, paths: list[str]) -> None:
        added, rejected = self.queue.add(paths)
        self._render_queue()
        if rejected:
            self.status.setText(
                f"{added} adicionado(s); {len(rejected)} inválido(s) ou duplicado(s) ignorado(s)."
            )
        elif added:
            self.status.setText(f"{added} arquivo(s) adicionado(s).")

    def _render_queue(self) -> None:
        self.files.setRowCount(len(self.queue.items))
        for row, item in enumerate(self.queue.items):
            self.files.setItem(row, 0, QTableWidgetItem(str(item.path)))
            self.files.setItem(row, 1, QTableWidgetItem(item.status.value))
            self.files.setItem(row, 2, QTableWidgetItem(f"{item.progress}%"))

    def _select_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Selecionar mídias")
        self._add_paths(paths)

    def _remove_selected(self) -> None:
        self.queue.remove([index.row() for index in self.files.selectionModel().selectedRows()])
        self._render_queue()

    def _clear_queue(self) -> None:
        self.queue.clear()
        self.generated.clear()
        self.preview.clear()
        self._render_queue()
        self.status.setText("Fila limpa.")

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
        if not self.queue.items:
            QMessageBox.warning(self, "Nenhum arquivo", "Selecione ao menos um arquivo.")
            return
        formats = tuple(name for name, box in self.format_checks.items() if box.isChecked())
        if not formats:
            QMessageBox.warning(self, "Formato obrigatório", "Selecione ao menos um formato.")
            return
        requests = [
            TranscriptionRequest(
                input_file=item.path,
                output_dir=self.output_dir,
                model=self.model.currentText(),
                language=self.language.currentText(),
                formats=formats,
            )
            for item in self.queue.items
        ]
        self.generated.clear()
        self.preview.clear()
        self.thread = QThread(self)
        self.worker = TranscriptionWorker(TranscriptionEngine(), requests)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.file_started.connect(self._on_file_started)
        self.worker.file_progress.connect(self._on_file_progress)
        self.worker.file_completed.connect(self._on_file_completed)
        self.worker.total_progress.connect(self._on_total_progress)
        self.worker.completed.connect(self._on_completed)
        self.worker.canceled.connect(self._on_canceled)
        self.worker.failed.connect(self._on_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self._reset)
        self._set_running(True)
        self.total_progress.setValue(0)
        self.thread.start()

    def _set_running(self, running: bool) -> None:
        self.transcribe_button.setEnabled(not running)
        self.cancel_button.setEnabled(running)
        self.remove_button.setEnabled(not running)
        self.clear_button.setEnabled(not running)
        self.model.setEnabled(not running)

    def _cancel(self) -> None:
        if self.worker:
            self.worker.cancel()
            self.status.setText("Cancelamento solicitado; finalizando o processo local...")
            self.cancel_button.setEnabled(False)

    def _on_file_started(self, index: int) -> None:
        self.queue.update(index, status=QueueStatus.RUNNING, progress=0)
        self._render_queue()

    def _on_file_progress(self, index: int, percent: int, message: str) -> None:
        self.queue.update(index, progress=percent, detail=message)
        self._render_queue()

    def _on_file_completed(self, index: int, generated: list[str]) -> None:
        self.queue.update(index, status=QueueStatus.COMPLETED, progress=100)
        self.generated.extend(Path(path) for path in generated)
        self._render_queue()

    def _on_total_progress(self, percent: int, message: str) -> None:
        self.total_progress.setValue(percent)
        self.status.setText(message)

    def _on_completed(self, generated: list[str]) -> None:
        self.total_progress.setValue(100)
        self.status.setText(f"Concluído: {len(generated)} arquivo(s) gerado(s). Revise o texto.")
        self._load_preview()

    def _on_canceled(self, message: str) -> None:
        for index, item in enumerate(self.queue.items):
            if item.status in (QueueStatus.WAITING, QueueStatus.RUNNING):
                self.queue.update(index, status=QueueStatus.CANCELED)
        self._render_queue()
        self.status.setText(message)

    def _on_failed(self, message: str) -> None:
        for index, item in enumerate(self.queue.items):
            if item.status is QueueStatus.RUNNING:
                self.queue.update(index, status=QueueStatus.FAILED, detail=message)
            elif item.status is QueueStatus.WAITING:
                self.queue.update(
                    index,
                    status=QueueStatus.CANCELED,
                    detail="Não processado após falha anterior.",
                )
        self._render_queue()
        self.status.setText("Falha: nenhuma conclusão foi presumida.")
        QMessageBox.critical(self, "Não foi possível concluir", message)

    def _reset(self) -> None:
        self._set_running(False)
        self.worker = None
        self.thread = None

    def _load_preview(self) -> None:
        txt = next((path for path in self.generated if path.suffix.lower() == ".txt"), None)
        if txt is None:
            self.preview.setPlainText("Selecione TXT para habilitar a prévia do texto.")
            return
        try:
            with txt.open("r", encoding="utf-8", errors="replace") as source:
                content = source.read(PREVIEW_LIMIT + 1)
            if len(content) > PREVIEW_LIMIT:
                content = content[:PREVIEW_LIMIT] + "\n\n[Prévia limitada a 1 MiB.]"
            self.preview.setPlainText(content)
        except OSError as exc:
            self.preview.setPlainText(f"Não foi possível abrir a prévia: {exc}")

    def _copy_preview(self) -> None:
        QGuiApplication.clipboard().setText(self.preview.toPlainText())
        self.status.setText("Texto da prévia copiado.")

    def _open_output(self) -> None:
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.output_dir.resolve()))):
                raise OSError("O Windows não aceitou a solicitação para abrir a pasta.")
        except OSError as exc:
            QMessageBox.warning(self, "Não foi possível abrir a pasta", str(exc))

    def _show_diagnostics(self) -> None:
        DiagnosticsDialog(self.model.currentText(), self).exec()

    def _show_models(self) -> None:
        dialog = ModelManagerDialog(
            self.model.currentText() if self.worker is not None else None,
            self,
        )
        dialog.models_changed.connect(lambda: self._update_model_info(self.model.currentText()))
        dialog.exec()

    def _show_about(self) -> None:
        AboutDialog(self).exec()
