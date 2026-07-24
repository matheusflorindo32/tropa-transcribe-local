"""Fila de mídia independente da interface gráfica."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from app.transcription.validators import SUPPORTED_EXTENSIONS


class QueueStatus(StrEnum):
    WAITING = "Aguardando"
    RUNNING = "Processando"
    COMPLETED = "Concluído"
    FAILED = "Falhou"
    CANCELED = "Cancelado"


@dataclass(slots=True)
class QueueItem:
    path: Path
    status: QueueStatus = QueueStatus.WAITING
    progress: int = 0
    detail: str = ""


class TranscriptionQueue:
    """Mantém ordem, deduplicação e estado da fila."""

    def __init__(self) -> None:
        self._items: list[QueueItem] = []

    @property
    def items(self) -> tuple[QueueItem, ...]:
        return tuple(self._items)

    def add(self, paths: list[str | Path]) -> tuple[int, list[str]]:
        known = {item.path for item in self._items}
        added = 0
        rejected: list[str] = []
        for raw in paths:
            path = Path(raw).expanduser().resolve()
            if (
                not path.is_file()
                or path.suffix.lower() not in SUPPORTED_EXTENSIONS
                or path in known
            ):
                rejected.append(str(raw))
                continue
            self._items.append(QueueItem(path))
            known.add(path)
            added += 1
        return added, rejected

    def remove(self, indexes: list[int]) -> None:
        for index in sorted(set(indexes), reverse=True):
            if 0 <= index < len(self._items):
                del self._items[index]

    def clear(self) -> None:
        self._items.clear()

    def update(
        self,
        index: int,
        *,
        status: QueueStatus | None = None,
        progress: int | None = None,
        detail: str | None = None,
    ) -> None:
        item = self._items[index]
        if status is not None:
            item.status = status
        if progress is not None:
            item.progress = min(100, max(0, progress))
        if detail is not None:
            item.detail = detail
