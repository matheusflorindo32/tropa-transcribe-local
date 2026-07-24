"""Eventos de progresso independentes da interface."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Stage(StrEnum):
    VALIDATING = "validando"
    CONVERTING = "convertendo"
    TRANSCRIBING = "transcrevendo"
    FINALIZING = "finalizando"
    COMPLETED = "concluído"


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    stage: Stage
    percent: int
    message: str
