from __future__ import annotations

import hashlib
import json
from email.message import Message
from pathlib import Path

import pytest

from tools.check_environment import inspect_environment
from tools.download_model import download_model


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


class FakeDownload:
    def __init__(self, content: bytes) -> None:
        self.content = content
        self.position = 0
        self.headers = Message()
        self.headers["Content-Length"] = str(len(content))
        self.headers["x-linked-etag"] = hashlib.sha256(content).hexdigest()

    def __enter__(self) -> FakeDownload:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, size: int) -> bytes:
        chunk = self.content[self.position : self.position + size]
        self.position += len(chunk)
        return chunk


def test_model_download_is_atomic_and_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = b"modelo-artificial"
    monkeypatch.setattr("tools.download_model.minimum_model_bytes", lambda _: len(content))
    monkeypatch.setattr("app.services.models.minimum_model_bytes", lambda _: len(content))
    monkeypatch.setattr(
        "tools.download_model._fetch_remote_metadata",
        lambda _url: (hashlib.sha256(content).hexdigest(), len(content)),
    )
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *_args, **_kwargs: FakeDownload(content),
    )

    downloaded = download_model("base", tmp_path)
    assert downloaded == tmp_path / "ggml-base.bin"
    assert downloaded.read_bytes() == content
    metadata = json.loads(downloaded.with_suffix(".sha256.json").read_text(encoding="utf-8"))
    assert metadata["verified_against_lfs_etag"] is True
    assert metadata["size_bytes"] == len(content)
    assert not list(tmp_path.glob("*.part"))

    assert download_model("base", tmp_path) == downloaded


def test_download_rejects_implausible_size_and_cleans_temporary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("tools.download_model.minimum_model_bytes", lambda _: 100)
    monkeypatch.setattr(
        "tools.download_model._fetch_remote_metadata",
        lambda _url: (None, len(b"curto")),
    )
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *_args, **_kwargs: FakeDownload(b"curto"),
    )
    with pytest.raises(RuntimeError, match="mínimo plausível"):
        download_model("base", tmp_path)
    assert not (tmp_path / "ggml-base.bin").exists()
    assert not list(tmp_path.glob("*.part"))
