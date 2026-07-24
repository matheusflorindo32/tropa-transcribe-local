from __future__ import annotations

from tools.check_environment import inspect_environment


def test_environment_diagnostic_has_required_fields() -> None:
    report = inspect_environment()
    assert {
        "platform",
        "python",
        "ffmpeg",
        "whisper_cli",
        "models_dir",
        "disk_free_gib",
    } <= report.keys()
