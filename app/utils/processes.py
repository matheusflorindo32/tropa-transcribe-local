"""Flags portáveis para subprocessos."""

from __future__ import annotations

import os

NO_WINDOW_CREATION_FLAGS = 0x08000000 if os.name == "nt" else 0
