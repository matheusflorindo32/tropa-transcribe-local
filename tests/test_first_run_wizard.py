from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from app.ui.first_run_wizard import ConsentPage, FirstRunWizard, ProvisioningWorker


@pytest.fixture
def application() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_consent_page_requires_explicit_acceptance(
    application: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del application
    monkeypatch.setattr("app.ui.first_run_wizard.default_data_dir", lambda: tmp_path)
    monkeypatch.setattr("app.ui.first_run_wizard.default_runtime_dir", lambda: tmp_path / "runtime")
    monkeypatch.setattr("app.ui.first_run_wizard.default_models_dir", lambda: tmp_path / "models")
    monkeypatch.setattr("app.ui.first_run_wizard.required_free_bytes", lambda _name: 1024)
    page = ConsentPage()
    assert not page.isComplete()
    assert "Não exige administrador" in page.storage.text()
    page.acceptance.setChecked(True)
    assert page.isComplete()
    page.close()


def test_wizard_exposes_four_clear_steps(application: QApplication) -> None:
    del application
    wizard = FirstRunWizard()
    assert len(wizard.pageIds()) == 4
    assert wizard.windowTitle() == "Configurar Tropa Transcribe Local"
    wizard.close()


def test_provisioning_worker_reports_success(monkeypatch: pytest.MonkeyPatch) -> None:
    installed: list[str] = []
    downloaded: list[str] = []

    def fake_install(identifier: str, **kwargs: object) -> Path:
        installed.append(identifier)
        progress = kwargs["progress"]
        progress(100, "ok")  # type: ignore[operator]
        return Path(f"{identifier}.exe")

    monkeypatch.setattr("app.ui.first_run_wizard.install_component", fake_install)
    monkeypatch.setattr(
        "app.ui.first_run_wizard.run_component_diagnostic",
        lambda _identifier: SimpleNamespace(returncode=0),
    )
    monkeypatch.setattr(
        "app.ui.first_run_wizard.download_model",
        lambda name, **_kwargs: downloaded.append(name) or Path("model.bin"),
    )
    worker = ProvisioningWorker("small", False)
    completed: list[bool] = []
    worker.completed.connect(lambda: completed.append(True))
    worker.run()
    assert installed == ["ffmpeg", "whisper_cpp"]
    assert downloaded == ["small"]
    assert completed == [True]


def test_provisioning_worker_cancel_is_not_success() -> None:
    worker = ProvisioningWorker("small", False)
    canceled: list[str] = []
    completed: list[bool] = []
    worker.canceled.connect(canceled.append)
    worker.completed.connect(lambda: completed.append(True))
    worker.cancel()
    worker.run()
    assert canceled
    assert not completed
