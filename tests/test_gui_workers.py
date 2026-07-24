from __future__ import annotations

import threading
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from app.transcription.engine import TranscriptionRequest
from app.transcription.progress import ProgressEvent, Stage
from app.ui.workers import TranscriptionWorker


class FakeEngine:
    def transcribe(
        self,
        request: TranscriptionRequest,
        progress: object,
        cancel_event: threading.Event,
    ) -> list[Path]:
        if cancel_event.is_set():
            raise InterruptedError("Operação cancelada.")
        progress(ProgressEvent(Stage.TRANSCRIBING, 50, "metade"))  # type: ignore[operator]
        return [request.output_dir / f"{request.input_file.stem}.txt"]


def test_worker_reports_per_file_and_total(tmp_path: Path) -> None:
    requests = [
        TranscriptionRequest(tmp_path / "áudio um.wav", tmp_path),
        TranscriptionRequest(tmp_path / "áudio dois.wav", tmp_path),
    ]
    worker = TranscriptionWorker(FakeEngine(), requests)  # type: ignore[arg-type]
    files: list[tuple[int, int, str]] = []
    totals: list[int] = []
    completed: list[list[str]] = []
    worker.file_progress.connect(
        lambda index, percent, message: files.append((index, percent, message))
    )
    worker.total_progress.connect(lambda percent, _message: totals.append(percent))
    worker.completed.connect(completed.append)

    worker.run()

    assert files == [(0, 50, "metade"), (1, 50, "metade")]
    assert totals == [25, 75]
    assert len(completed[0]) == 2


def test_worker_cancel_is_distinct_from_failure(tmp_path: Path) -> None:
    worker = TranscriptionWorker(
        FakeEngine(),  # type: ignore[arg-type]
        [TranscriptionRequest(tmp_path / "arquivo.wav", tmp_path)],
    )
    canceled: list[str] = []
    failed: list[str] = []
    worker.canceled.connect(canceled.append)
    worker.failed.connect(failed.append)
    worker.cancel()

    worker.run()

    assert canceled == ["Operação cancelada."]
    assert not failed
