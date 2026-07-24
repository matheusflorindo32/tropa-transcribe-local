"""Assistente não bloqueante para preparar runtimes e modelo no primeiro uso."""

from __future__ import annotations

import shutil
import sys
import threading

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)

from app.config import default_data_dir
from app.services.model_download import download_model, required_free_bytes
from app.services.models import (
    MODEL_CATALOG,
    default_models_dir,
    model_filename,
    validate_model_file,
)
from app.services.runtime_manifest import load_runtime_manifest
from app.services.runtime_provisioning import (
    default_runtime_dir,
    install_component,
    is_component_ready,
    run_component_diagnostic,
)


def needs_first_run(model: str = "small") -> bool:
    """Retorna True se o pacote ainda precisa de componente ou modelo."""
    if not all(is_component_ready(name) for name in ("ffmpeg", "whisper_cpp")):
        return True
    try:
        validate_model_file(default_models_dir() / model_filename(model), model)
        return False
    except (FileNotFoundError, OSError, ValueError):
        return True


class ProvisioningWorker(QObject):
    progress = Signal(int, str)
    component = Signal(str, str)
    completed = Signal()
    canceled = Signal(str)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, model: str, repair: bool) -> None:
        super().__init__()
        self.model = model
        self.repair = repair
        self.cancel_event = threading.Event()

    @Slot()
    def run(self) -> None:
        try:
            jobs = (("ffmpeg", 0, 20), ("whisper_cpp", 20, 40))
            for identifier, start, end in jobs:
                if self.cancel_event.is_set():
                    raise InterruptedError("Preparação cancelada; arquivos parciais removidos.")
                self.component.emit(identifier, "verificando")
                install_component(
                    identifier,
                    repair=self.repair,
                    cancel_event=self.cancel_event,
                    progress=lambda percent, message, lower=start, upper=end: self.progress.emit(
                        lower + int(percent * (upper - lower) / 100), message
                    ),
                )
                result = run_component_diagnostic(identifier)
                if result.returncode != 0:
                    raise RuntimeError(
                        f"O diagnóstico de {identifier} terminou com código {result.returncode}."
                    )
                self.component.emit(identifier, "íntegro")
            self.component.emit("model", "verificando")
            download_model(
                self.model,
                force=self.repair,
                cancel_event=self.cancel_event,
                progress=lambda percent, message: self.progress.emit(
                    40 + int(percent * 0.6), f"Modelo {self.model}: {message}"
                ),
            )
            self.component.emit("model", "íntegro")
            self.progress.emit(100, "Componentes instalados e validados.")
            self.completed.emit()
        except InterruptedError as exc:
            self.canceled.emit(str(exc))
        except (OSError, ValueError, RuntimeError) as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()

    @Slot()
    def cancel(self) -> None:
        self.cancel_event.set()


class ConsentPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Plano local e licenças")
        layout = QVBoxLayout(self)
        message = QLabel(
            "O aplicativo baixará binários e um modelo somente após sua confirmação. "
            "A transcrição continuará totalmente local: sem conta, telemetria ou upload."
        )
        message.setWordWrap(True)
        layout.addWidget(message)
        form = QFormLayout()
        self.model = QComboBox()
        self.model.addItems(MODEL_CATALOG)
        self.model.setCurrentText("small")
        self.model.currentTextChanged.connect(self._refresh)
        form.addRow("Modelo:", self.model)
        self.storage = QLabel()
        self.storage.setWordWrap(True)
        form.addRow("Armazenamento:", self.storage)
        self.space = QLabel()
        self.space.setWordWrap(True)
        form.addRow("Espaço:", self.space)
        layout.addLayout(form)
        self.notices = QLabel(
            "Licenças: FFmpeg LGPL-3.0-or-later (build shared do FFmpeg-Builds); "
            "whisper.cpp e pesos Whisper MIT. Os avisos completos acompanham o aplicativo."
        )
        self.notices.setWordWrap(True)
        layout.addWidget(self.notices)
        self.acceptance = QCheckBox(
            "Li os avisos e autorizo os downloads externos listados neste assistente."
        )
        self.acceptance.toggled.connect(self.completeChanged)
        layout.addWidget(self.acceptance)
        self.repair = QCheckBox(
            "Reparar: baixar novamente e substituir componentes existentes após validação"
        )
        self.repair.setToolTip("O estado anterior é preservado até a nova cópia ser validada.")
        layout.addWidget(self.repair)
        self._refresh(self.model.currentText())

    def _refresh(self, name: str) -> None:
        manifest = load_runtime_manifest()
        runtime_download = sum(item.size_bytes for item in manifest.components.values())
        runtime_install = sum(item.installed_size_bytes for item in manifest.components.values())
        model = manifest.models[name]
        root = default_data_dir()
        root.mkdir(parents=True, exist_ok=True)
        free = shutil.disk_usage(root).free
        required = runtime_download + runtime_install + required_free_bytes(name)
        self.storage.setText(
            f"{default_runtime_dir()} (runtimes) · {default_models_dir()} (modelos). "
            "Não exige administrador nem altera o PATH global."
        )
        self.space.setText(
            f"Download: {(runtime_download + model.size_bytes) / 1024**2:.0f} MiB · "
            f"necessidade conservadora: {required / 1024**2:.0f} MiB · "
            f"livre: {free / 1024**3:.1f} GiB."
        )
        self.completeChanged.emit()

    def isComplete(self) -> bool:
        return self.acceptance.isChecked()


class InstallPage(QWizardPage):
    def __init__(self, wizard: FirstRunWizard) -> None:
        super().__init__()
        self.owner = wizard
        self.setTitle("Baixar, validar e instalar")
        layout = QVBoxLayout(self)
        self.table = QTableWidget(3, 2)
        self.table.setHorizontalHeaderLabels(["Componente", "Estado"])
        for row, label in enumerate(("FFmpeg", "whisper.cpp", "Modelo")):
            self.table.setItem(row, 0, QTableWidgetItem(label))
            self.table.setItem(row, 1, QTableWidgetItem("aguardando"))
        self.table.setAccessibleName("Estado dos componentes")
        layout.addWidget(self.table)
        self.progress = QProgressBar()
        self.progress.setAccessibleName("Progresso da preparação")
        layout.addWidget(self.progress)
        self.status = QLabel("Aguardando.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.retry = QPushButton("Tentar novamente")
        self.retry.setEnabled(False)
        self.retry.clicked.connect(self.owner.start_provisioning)
        layout.addWidget(self.retry)

    def initializePage(self) -> None:
        self.owner.start_provisioning()

    def isComplete(self) -> bool:
        return self.owner.provisioned

    def set_component(self, identifier: str, status: str) -> None:
        row = {"ffmpeg": 0, "whisper_cpp": 1, "model": 2}[identifier]
        self.table.setItem(row, 1, QTableWidgetItem(status))


class SuccessPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Preparação concluída")
        layout = QVBoxLayout(self)
        message = QLabel(
            "FFmpeg, whisper.cpp e o modelo foram localizados, validados e testados. "
            "Você já pode adicionar uma mídia e iniciar a transcrição local."
        )
        message.setWordWrap(True)
        layout.addWidget(message)


class FirstRunWizard(QWizard):
    def __init__(self, parent: object | None = None) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self.setWindowTitle("Configurar Tropa Transcribe Local")
        self.resize(760, 560)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.thread: QThread | None = None
        self.worker: ProvisioningWorker | None = None
        self.provisioned = False
        self.cancel_pending = False

        welcome = QWizardPage()
        welcome.setTitle("Tudo pronto para uma configuração privada")
        welcome_layout = QVBoxLayout(welcome)
        welcome_text = QLabel(
            "<h3>Processamento 100% local</h3>"
            "<p>Este assistente instala os componentes no seu perfil de usuário. "
            "Não instala Python, Git, CMake, Visual Studio ou compiladores; não exige "
            "administrador; não desativa o Microsoft Defender.</p>"
            "<p>Nenhum áudio, vídeo ou texto é enviado para a internet. A rede é usada "
            "somente para baixar os componentes escolhidos.</p>"
        )
        welcome_text.setWordWrap(True)
        welcome_layout.addWidget(welcome_text)
        self.addPage(welcome)

        self.consent = ConsentPage()
        self.addPage(self.consent)
        self.install_page = InstallPage(self)
        self.addPage(self.install_page)
        self.addPage(SuccessPage())

    @Slot()
    def start_provisioning(self) -> None:
        if self.thread is not None:
            return
        self.provisioned = False
        self.install_page.completeChanged.emit()
        self.install_page.retry.setEnabled(False)
        self.install_page.status.setText("Preparando downloads seguros...")
        self.thread = QThread(self)
        self.worker = ProvisioningWorker(
            self.consent.model.currentText(),
            self.consent.repair.isChecked(),
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._progress)
        self.worker.component.connect(self.install_page.set_component)
        self.worker.completed.connect(self._completed)
        self.worker.canceled.connect(self._failed)
        self.worker.failed.connect(self._failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self._reset_worker)
        self.thread.start()

    @Slot(int, str)
    def _progress(self, percent: int, message: str) -> None:
        self.install_page.progress.setValue(percent)
        self.install_page.status.setText(message)

    @Slot()
    def _completed(self) -> None:
        self.provisioned = True
        self.install_page.status.setText("Preparação concluída com integridade verificada.")
        self.install_page.completeChanged.emit()

    @Slot(str)
    def _failed(self, message: str) -> None:
        self.install_page.status.setText(message)
        self.install_page.retry.setEnabled(True)

    @Slot()
    def _reset_worker(self) -> None:
        self.worker = None
        self.thread = None
        if self.cancel_pending:
            super().reject()

    def reject(self) -> None:
        if self.worker is not None:
            self.cancel_pending = True
            self.worker.cancel()
            self.install_page.status.setText(
                "Cancelamento solicitado. Limpando arquivos parciais com segurança..."
            )
            self.button(QWizard.WizardButton.CancelButton).setEnabled(False)
            return
        super().reject()


def should_open_automatically() -> bool:
    """Evita interromper execução de desenvolvimento e testes."""
    return sys.platform == "win32" and bool(getattr(sys, "frozen", False))
