"""Worker em thread para manter a interface responsiva."""

from __future__ import annotations

import threading
from functools import partial

from PySide6.QtCore import QObject, Signal, Slot

from app.transcription.engine import TranscriptionEngine, TranscriptionRequest
from app.transcription.progress import ProgressEvent


class TranscriptionWorker(QObject):
    progress = Signal(int, str)
    completed = Signal(list)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, engine: TranscriptionEngine, requests: list[TranscriptionRequest]) -> None:
        super().__init__()
        self.engine = engine
        self.requests = requests
        self.cancel_event = threading.Event()

    @Slot()
    def run(self) -> None:
        generated: list[str] = []
        try:
            total = len(self.requests)
            for index, request in enumerate(self.requests):
                if self.cancel_event.is_set():
                    raise InterruptedError("Operação cancelada.")
                generated.extend(
                    str(path)
                    for path in self.engine.transcribe(
                        request,
                        partial(self._report, index, total),
                        cancel_event=self.cancel_event,
                    )
                )
            self.completed.emit(generated)
        except (OSError, ValueError, RuntimeError, InterruptedError) as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()

    @Slot()
    def cancel(self) -> None:
        self.cancel_event.set()

    def _report(self, index: int, total: int, event: ProgressEvent) -> None:
        overall = int(((index + event.percent / 100) / total) * 100)
        self.progress.emit(overall, event.message)
