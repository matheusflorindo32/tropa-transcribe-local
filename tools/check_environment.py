#!/usr/bin/env python3
"""Diagnóstico local sem enviar dados."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
from pathlib import Path
from typing import Any

from app.services.models import default_models_dir


def inspect_environment() -> dict[str, Any]:
    models_dir = default_models_dir()
    disk_root = models_dir.parent if models_dir.parent.exists() else Path.cwd()
    disk = shutil.disk_usage(disk_root)
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "ffmpeg": shutil.which("ffmpeg"),
        "whisper_cli": shutil.which("whisper-cli"),
        "git": shutil.which("git"),
        "cmake": shutil.which("cmake"),
        "models_dir": str(models_dir),
        "models": sorted(path.name for path in models_dir.glob("ggml-*.bin")),
        "disk_free_gib": round(disk.free / 1024**3, 2),
        "cpu_count": os.cpu_count(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = inspect_environment()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    for name, value in report.items():
        print(f"{name}: {value or 'NÃO ENCONTRADO'}")
    missing = [name for name in ("ffmpeg", "whisper_cli") if not report[name]]
    raise SystemExit(1 if missing else 0)


if __name__ == "__main__":
    main()
