from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.runtime_manifest import MANIFEST_SHA256, ManifestError, load_runtime_manifest


def test_embedded_runtime_manifest_is_complete_and_trusted() -> None:
    manifest = load_runtime_manifest()
    assert manifest.digest == MANIFEST_SHA256
    assert manifest.release == "0.3.1-alpha"
    assert set(manifest.components) == {"ffmpeg", "whisper_cpp"}
    assert "small" in manifest.models
    assert all(component.url.startswith("https://") for component in manifest.components.values())
    assert all(model.sha256 and model.size_bytes > 0 for model in manifest.models.values())


def test_manifest_tampering_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ManifestError, match="alterado"):
        load_runtime_manifest(path)


def test_manifest_rejects_http_and_path_traversal(tmp_path: Path) -> None:
    source = Path("app/resources/runtime-windows-x64.json")
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["components"]["ffmpeg"]["url"] = "http://github.com/inseguro.zip"
    payload["components"]["ffmpeg"]["files"][0]["path"] = "../escape.txt"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ManifestError):
        load_runtime_manifest(path, expected_sha256=None)
