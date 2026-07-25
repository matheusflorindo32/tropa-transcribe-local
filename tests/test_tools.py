from __future__ import annotations

from pathlib import Path

import pytest

from tools.check_environment import inspect_environment
from tools.download_model import download_model
from tools.generate_supply_chain import cyclonedx_licenses


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


def test_model_download_delegates_to_trusted_service(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "ggml-base.bin"
    seen: list[object] = []

    def fake_service(
        name: str,
        directory: Path,
        *,
        force: bool,
        progress: object,
    ) -> Path:
        seen.extend((name, directory, force, progress))
        return target

    monkeypatch.setattr("tools.download_model.download_model_service", fake_service)
    assert download_model("base", tmp_path, True) == target
    assert seen[:3] == ["base", tmp_path, True]
    assert callable(seen[3])


def test_sbom_uses_named_license_for_non_spdx_exception() -> None:
    assert "license" in cyclonedx_licenses("GPL-2.0-or-later WITH Bootloader-exception")[0]
    assert cyclonedx_licenses("MIT") == [{"expression": "MIT"}]
