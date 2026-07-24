from __future__ import annotations

import hashlib
import io
import json
import sys
import threading
import urllib.error
import zipfile
from email.message import Message
from pathlib import Path
from types import MappingProxyType

import pytest

from app.services.runtime_manifest import ComponentSpec, InstalledFile, RuntimeManifest
from app.services.runtime_provisioning import (
    ProvisioningError,
    _validate_archive_members,
    download_verified_file,
    install_component,
    is_component_ready,
    remove_component,
    run_component_diagnostic,
    validate_component,
)


class FakeResponse:
    def __init__(self, content: bytes, url: str = "https://github.com/file.zip") -> None:
        self.content = content
        self.position = 0
        self.url = url
        self.headers = Message()
        self.headers["Content-Length"] = str(len(content))

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def geturl(self) -> str:
        return self.url

    def read(self, size: int) -> bytes:
        chunk = self.content[self.position : self.position + size]
        self.position += len(chunk)
        return chunk


def test_verified_download_is_atomic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    content = b"archive"
    monkeypatch.setattr(
        "app.services.runtime_provisioning.urllib.request.urlopen",
        lambda *_args, **_kwargs: FakeResponse(content),
    )
    destination = tmp_path / "component.zip"
    result = download_verified_file(
        url="https://github.com/file.zip",
        sha256=hashlib.sha256(content).hexdigest(),
        size_bytes=len(content),
        destination=destination,
        allowed_hosts=frozenset({"github.com"}),
    )
    assert result.read_bytes() == content
    assert not list(tmp_path.glob("*.part"))


def test_download_rejects_bad_hash_and_redirect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "app.services.runtime_provisioning.urllib.request.urlopen",
        lambda *_args, **_kwargs: FakeResponse(b"archive"),
    )
    with pytest.raises(ProvisioningError, match="SHA-256"):
        download_verified_file(
            url="https://github.com/file.zip",
            sha256="0" * 64,
            size_bytes=7,
            destination=tmp_path / "bad.zip",
            allowed_hosts=frozenset({"github.com"}),
        )
    monkeypatch.setattr(
        "app.services.runtime_provisioning.urllib.request.urlopen",
        lambda *_args, **_kwargs: FakeResponse(b"x", "https://evil.example/file.zip"),
    )
    with pytest.raises(ProvisioningError, match="origem"):
        download_verified_file(
            url="https://github.com/file.zip",
            sha256=hashlib.sha256(b"x").hexdigest(),
            size_bytes=1,
            destination=tmp_path / "redirect.zip",
            allowed_hosts=frozenset({"github.com"}),
        )
    assert not list(tmp_path.glob("*.part"))


def test_download_cancel_cleans_partial(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    event = threading.Event()

    class CancelResponse(FakeResponse):
        def read(self, size: int) -> bytes:
            chunk = super().read(size)
            event.set()
            return chunk

    monkeypatch.setattr(
        "app.services.runtime_provisioning.urllib.request.urlopen",
        lambda *_args, **_kwargs: CancelResponse(b"x" * 10),
    )
    with pytest.raises(InterruptedError):
        download_verified_file(
            url="https://github.com/file.zip",
            sha256=hashlib.sha256(b"x" * 10).hexdigest(),
            size_bytes=10,
            destination=tmp_path / "cancel.zip",
            allowed_hosts=frozenset({"github.com"}),
            cancel_event=event,
        )
    assert not list(tmp_path.glob("*.part"))


def test_download_reports_network_or_proxy_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "app.services.runtime_provisioning.urllib.request.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(urllib.error.URLError("proxy recusou")),
    )
    with pytest.raises(ProvisioningError, match="proxy"):
        download_verified_file(
            url="https://github.com/file.zip",
            sha256="0" * 64,
            size_bytes=1,
            destination=tmp_path / "network.zip",
            allowed_hosts=frozenset({"github.com"}),
        )
    assert not list(tmp_path.glob("*.part"))


def test_zip_rejects_traversal_and_symlink() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("../escape.exe", b"x")
    buffer.seek(0)
    with zipfile.ZipFile(buffer) as archive, pytest.raises(ProvisioningError, match="traversal"):
        _validate_archive_members(archive)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        item = zipfile.ZipInfo("link.exe")
        item.external_attr = 0o120777 << 16
        archive.writestr(item, b"target")
    buffer.seek(0)
    with zipfile.ZipFile(buffer) as archive, pytest.raises(ProvisioningError, match="simbólico"):
        _validate_archive_members(archive)


def _fixture_manifest(content: bytes) -> tuple[RuntimeManifest, bytes]:
    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w") as archive:
        archive.writestr("Release/tool.exe", content)
    archive_bytes = archive_buffer.getvalue()
    file = InstalledFile(
        archive_path="Release/tool.exe",
        path="bin/tool.exe",
        size_bytes=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
    )
    component = ComponentSpec(
        identifier="ffmpeg",
        name="Fixture",
        version="1",
        architecture="x86_64",
        url="https://github.com/file.zip",
        sha256=hashlib.sha256(archive_bytes).hexdigest(),
        size_bytes=len(archive_bytes),
        installed_size_bytes=len(content),
        license="MIT",
        license_file=None,
        homepage="https://github.com/example",
        source="https://github.com/example/tree/1",
        distribution="teste",
        entry_point="bin/tool.exe",
        diagnostic_command=("bin/tool.exe", "--version"),
        files=(file,),
    )
    manifest = RuntimeManifest(
        schema_version=1,
        release="test",
        platform="windows",
        architecture="x86_64",
        verified_at="2026-07-24",
        digest="a" * 64,
        allowed_download_hosts=frozenset({"github.com"}),
        components=MappingProxyType({"ffmpeg": component}),
        models=MappingProxyType({}),
    )
    return manifest, archive_bytes


def test_component_install_validate_and_detect_dll_planting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, archive = _fixture_manifest(b"trusted")

    def fake_download(**kwargs: object) -> Path:
        destination = kwargs["destination"]
        assert isinstance(destination, Path)
        destination.write_bytes(archive)
        return destination

    monkeypatch.setattr(
        "app.services.runtime_provisioning.download_verified_file",
        fake_download,
    )
    monkeypatch.setattr(
        "app.services.runtime_provisioning.DISK_MARGIN_BYTES",
        0,
    )
    executable = install_component("ffmpeg", runtime_dir=tmp_path, manifest=manifest)
    assert executable.read_bytes() == b"trusted"
    assert validate_component("ffmpeg", runtime_dir=tmp_path, manifest=manifest) == executable

    planted = executable.parent / "malicious.dll"
    planted.write_bytes(b"x")
    with pytest.raises(ProvisioningError, match="inesperados"):
        validate_component("ffmpeg", runtime_dir=tmp_path, manifest=manifest)


def test_component_record_has_required_audit_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, archive = _fixture_manifest(b"trusted")
    monkeypatch.setattr(
        "app.services.runtime_provisioning.download_verified_file",
        lambda **kwargs: (
            Path(str(kwargs["destination"])).write_bytes(archive)
            and Path(str(kwargs["destination"]))
        ),
    )
    monkeypatch.setattr("app.services.runtime_provisioning.DISK_MARGIN_BYTES", 0)
    executable = install_component("ffmpeg", runtime_dir=tmp_path, manifest=manifest)
    state = json.loads((executable.parents[1] / "component.json").read_text(encoding="utf-8"))
    assert state["manifest_sha256"] == manifest.digest
    assert state["installed_files"][0]["sha256"]


def test_invalid_zip_preserves_existing_component(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, archive = _fixture_manifest(b"trusted")

    def copy_archive(**kwargs: object) -> Path:
        destination = kwargs["destination"]
        assert isinstance(destination, Path)
        destination.write_bytes(archive)
        return destination

    monkeypatch.setattr(
        "app.services.runtime_provisioning.download_verified_file",
        copy_archive,
    )
    monkeypatch.setattr("app.services.runtime_provisioning.DISK_MARGIN_BYTES", 0)
    executable = install_component("ffmpeg", runtime_dir=tmp_path, manifest=manifest)
    monkeypatch.setattr(
        "app.services.runtime_provisioning.download_verified_file",
        lambda **kwargs: (
            Path(str(kwargs["destination"])).write_bytes(b"not-a-zip")
            and Path(str(kwargs["destination"]))
        ),
    )
    with pytest.raises(ProvisioningError, match="ZIP válido"):
        install_component(
            "ffmpeg",
            runtime_dir=tmp_path,
            manifest=manifest,
            repair=True,
        )
    assert executable.read_bytes() == b"trusted"


def test_component_low_disk_and_unknown_identifier(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, _archive = _fixture_manifest(b"trusted")
    usage = type("Usage", (), {"free": 0})()
    monkeypatch.setattr("app.services.runtime_provisioning.shutil.disk_usage", lambda _: usage)
    with pytest.raises(ProvisioningError, match="Espaço livre"):
        install_component("ffmpeg", runtime_dir=tmp_path, manifest=manifest)
    with pytest.raises(ProvisioningError, match="desconhecido"):
        install_component("missing", runtime_dir=tmp_path, manifest=manifest)
    assert not is_component_ready("ffmpeg", runtime_dir=tmp_path, manifest=manifest)


def test_remove_component_stays_inside_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, _archive = _fixture_manifest(b"trusted")
    directory = tmp_path / "ffmpeg" / "1"
    directory.mkdir(parents=True)
    (directory / "file").write_text("x", encoding="utf-8")
    monkeypatch.setattr(
        "app.services.runtime_provisioning.load_runtime_manifest",
        lambda: manifest,
    )
    remove_component("ffmpeg", runtime_dir=tmp_path)
    assert not directory.exists()
    with pytest.raises(ProvisioningError, match="desconhecido"):
        remove_component("missing", runtime_dir=tmp_path)


def test_run_diagnostic_uses_trusted_argument_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest, _archive = _fixture_manifest(b"trusted")
    python_copy = Path(sys.executable)
    component = manifest.components["ffmpeg"]
    replacement = ComponentSpec(
        identifier=component.identifier,
        name=component.name,
        version=component.version,
        architecture=component.architecture,
        url=component.url,
        sha256=component.sha256,
        size_bytes=component.size_bytes,
        installed_size_bytes=component.installed_size_bytes,
        license=component.license,
        license_file=component.license_file,
        homepage=component.homepage,
        source=component.source,
        distribution=component.distribution,
        entry_point=component.entry_point,
        diagnostic_command=(component.entry_point, "--version"),
        files=component.files,
    )
    trusted = RuntimeManifest(
        schema_version=manifest.schema_version,
        release=manifest.release,
        platform=manifest.platform,
        architecture=manifest.architecture,
        verified_at=manifest.verified_at,
        digest=manifest.digest,
        allowed_download_hosts=manifest.allowed_download_hosts,
        components=MappingProxyType({"ffmpeg": replacement}),
        models=manifest.models,
    )
    monkeypatch.setattr(
        "app.services.runtime_provisioning.load_runtime_manifest",
        lambda: trusted,
    )
    monkeypatch.setattr(
        "app.services.runtime_provisioning.validate_component",
        lambda *_args, **_kwargs: python_copy,
    )
    result = run_component_diagnostic("ffmpeg")
    assert result.returncode == 0
    assert "Python" in result.stdout
