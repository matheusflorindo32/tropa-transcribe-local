"""Ciclo de vida de arquivos temporários."""

from __future__ import annotations

import shutil
import tempfile
from contextlib import AbstractContextManager
from pathlib import Path
from types import TracebackType


class TemporaryWorkspace(AbstractContextManager["TemporaryWorkspace"]):
    """Workspace isolado, removido por padrão e preservável para diagnóstico."""

    def __init__(self, root: Path | None = None, keep: bool = False) -> None:
        if root:
            root.mkdir(parents=True, exist_ok=True)
        self.path = Path(tempfile.mkdtemp(prefix="tropa-", dir=root))
        self.keep = keep

    def __enter__(self) -> TemporaryWorkspace:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self.keep:
            shutil.rmtree(self.path, ignore_errors=True)
