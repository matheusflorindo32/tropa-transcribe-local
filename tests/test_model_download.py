from __future__ import annotations

import hashlib
import threading
from email.message import Message
from pathlib import Path

import pytest

from app.services.model_download import delete_model, download_model


class FakeResponse:
    def __init__(self, content: bytes, cancel: threading.Event | None = None) -> None:
        self.content = content
        self.position = 0
        self.cancel = cancel
        self.headers = Message()
        self.headers["Content-Length"] = str(len(content))
        self.headers["x-linked-etag"] = hashlib.sha256(content).hexdigest()

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, size: int) -> bytes:
        chunk = self.content[self.position : self.position + size]
        self.position += len(chunk)
        if self.cancel and self.position:
            self.cancel.set()
        return chunk


def test_download_validates_hash_and_is_atomic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = b"modelo-seguro"
    monkeypatch.setattr("app.services.model_download.minimum_model_bytes", lambda _: 1)
    monkeypatch.setattr("app.services.models.minimum_model_bytes", lambda _: 1)
    monkeypatch.setattr(
        "app.services.model_download.required_free_bytes",
        lambda _: 1,
    )
    monkeypatch.setattr(
        "app.services.model_download._remote_metadata",
        lambda _url: (hashlib.sha256(content).hexdigest(), len(content)),
    )
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *_args, **_kwargs: FakeResponse(content),
    )

    result = download_model("base", tmp_path)

    assert result.read_bytes() == content
    assert result.with_suffix(".sha256.json").is_file()
    assert not list(tmp_path.glob("*.part"))


def test_download_cancel_removes_partial(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cancel = threading.Event()
    monkeypatch.setattr("app.services.model_download.minimum_model_bytes", lambda _: 1)
    monkeypatch.setattr("app.services.model_download.required_free_bytes", lambda _: 1)
    monkeypatch.setattr(
        "app.services.model_download._remote_metadata",
        lambda _url: (None, 2 * 1024**2),
    )
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *_args, **_kwargs: FakeResponse(b"x" * (2 * 1024**2), cancel),
    )
    with pytest.raises(InterruptedError):
        download_model("base", tmp_path, cancel_event=cancel)
    assert not list(tmp_path.glob("*.part"))
    assert not (tmp_path / "ggml-base.bin").exists()


def test_download_rejects_low_disk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    usage = type("Usage", (), {"free": 0})()
    monkeypatch.setattr("app.services.model_download.shutil.disk_usage", lambda _: usage)
    with pytest.raises(OSError, match="Espaço livre insuficiente"):
        download_model("base", tmp_path)


def test_delete_blocks_model_in_use(tmp_path: Path) -> None:
    model = tmp_path / "ggml-base.bin"
    model.write_bytes(b"x")
    with pytest.raises(RuntimeError, match="em uso"):
        delete_model("base", in_use=True, directory=tmp_path)
    assert model.exists()
