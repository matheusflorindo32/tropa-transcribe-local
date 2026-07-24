from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from types import MappingProxyType, SimpleNamespace

import pytest

from app.services.model_download import delete_model, download_model
from app.services.runtime_manifest import ModelSpec


def _model(content: bytes) -> ModelSpec:
    return ModelSpec(
        name="base",
        filename="ggml-base.bin",
        url="https://huggingface.co/example/ggml-base.bin",
        sha256=hashlib.sha256(content).hexdigest(),
        size_bytes=len(content),
        license="MIT",
        homepage="https://huggingface.co/example",
        source="https://github.com/example/source",
        revision="a" * 40,
    )


def _patch_manifest(
    monkeypatch: pytest.MonkeyPatch,
    content: bytes,
) -> ModelSpec:
    spec = _model(content)
    manifest = SimpleNamespace(
        models=MappingProxyType({"base": spec}),
        digest="b" * 64,
        allowed_download_hosts=frozenset({"huggingface.co"}),
    )
    monkeypatch.setattr("app.services.model_download.load_runtime_manifest", lambda: manifest)
    monkeypatch.setattr("app.services.runtime_manifest.load_runtime_manifest", lambda: manifest)
    monkeypatch.setattr("app.services.runtime_manifest.model_spec", lambda _name: spec)
    monkeypatch.setattr("app.services.models.minimum_model_bytes", lambda _: 1)
    monkeypatch.setattr("app.services.model_download.MODEL_DISK_MARGIN_BYTES", 0)
    return spec


def test_download_validates_hash_and_is_atomic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = b"modelo-seguro"
    spec = _patch_manifest(monkeypatch, content)

    def fake_download(**kwargs: object) -> Path:
        destination = kwargs["destination"]
        assert isinstance(destination, Path)
        assert kwargs["sha256"] == spec.sha256
        destination.write_bytes(content)
        return destination

    monkeypatch.setattr("app.services.model_download.download_verified_file", fake_download)

    result = download_model("base", tmp_path)

    assert result.read_bytes() == content
    assert result.with_suffix(".sha256.json").is_file()
    assert not list(tmp_path.glob("*.part"))
    assert not list(tmp_path.glob("*.incoming"))


def test_download_cancel_removes_partial(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_manifest(monkeypatch, b"model")

    def canceled(**_kwargs: object) -> Path:
        raise InterruptedError("Download cancelado; arquivo parcial removido.")

    monkeypatch.setattr("app.services.model_download.download_verified_file", canceled)
    with pytest.raises(InterruptedError):
        download_model("base", tmp_path, cancel_event=threading.Event())
    assert not (tmp_path / "ggml-base.bin").exists()


def test_corrupt_existing_model_is_repaired_atomically(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = b"trusted-model"
    _patch_manifest(monkeypatch, content)
    destination = tmp_path / "ggml-base.bin"
    destination.write_bytes(b"corrupt")
    destination.with_suffix(".sha256.json").write_text(
        '{"sha256":"' + ("0" * 64) + '"}',
        encoding="utf-8",
    )

    def fake_download(**kwargs: object) -> Path:
        path = kwargs["destination"]
        assert isinstance(path, Path)
        path.write_bytes(content)
        return path

    monkeypatch.setattr("app.services.model_download.download_verified_file", fake_download)
    assert download_model("base", tmp_path).read_bytes() == content


def test_repair_restores_previous_model_when_sidecar_write_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    new_content = b"trusted-model"
    old_content = b"previous-model"
    _patch_manifest(monkeypatch, new_content)
    destination = tmp_path / "ggml-base.bin"
    record = destination.with_suffix(".sha256.json")
    destination.write_bytes(old_content)
    record.write_text(
        json.dumps({"schema_version": 1, "sha256": hashlib.sha256(old_content).hexdigest()}),
        encoding="utf-8",
    )

    def fake_download(**kwargs: object) -> Path:
        path = kwargs["destination"]
        assert isinstance(path, Path)
        path.write_bytes(new_content)
        return path

    def fail_record(_path: Path, _name: str) -> None:
        raise OSError("falha controlada no sidecar")

    monkeypatch.setattr("app.services.model_download.download_verified_file", fake_download)
    monkeypatch.setattr("app.services.model_download._write_model_record", fail_record)

    with pytest.raises(OSError, match="falha controlada"):
        download_model("base", tmp_path, force=True)

    assert destination.read_bytes() == old_content
    assert record.is_file()
    assert not list(tmp_path.glob("*.incoming"))
    assert not list(tmp_path.glob("*.bak"))


def test_download_rejects_low_disk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_manifest(monkeypatch, b"model")
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
