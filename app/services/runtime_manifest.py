"""Manifesto confiável e versionado para componentes externos no Windows."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any
from urllib.parse import urlparse

MANIFEST_RESOURCE = "runtime-windows-x64.json"
MANIFEST_SHA256 = "66ebdd9e90be6a4f84e66bd187faf27f3e08c281b4d257e881ad9fc10cfb1109"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ManifestError(ValueError):
    """O manifesto incorporado não é confiável ou não segue o contrato."""


@dataclass(frozen=True, slots=True)
class InstalledFile:
    archive_path: str
    path: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True, slots=True)
class ComponentSpec:
    identifier: str
    name: str
    version: str
    architecture: str
    url: str
    sha256: str
    size_bytes: int
    installed_size_bytes: int
    license: str
    license_file: str | None
    homepage: str
    source: str
    distribution: str
    entry_point: str
    diagnostic_command: tuple[str, ...]
    files: tuple[InstalledFile, ...]


@dataclass(frozen=True, slots=True)
class ModelSpec:
    name: str
    filename: str
    url: str
    sha256: str
    size_bytes: int
    license: str
    homepage: str
    source: str
    revision: str


@dataclass(frozen=True, slots=True)
class RuntimeManifest:
    schema_version: int
    release: str
    platform: str
    architecture: str
    verified_at: str
    digest: str
    allowed_download_hosts: frozenset[str]
    components: Mapping[str, ComponentSpec]
    models: Mapping[str, ModelSpec]


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ManifestError(f"{label} deve ser um objeto JSON.")
    return value


def _text(data: Mapping[str, Any], key: str, label: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{label}.{key} deve ser texto não vazio.")
    return value


def _positive_int(data: Mapping[str, Any], key: str, label: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ManifestError(f"{label}.{key} deve ser inteiro positivo.")
    return value


def _hash(data: Mapping[str, Any], key: str, label: str) -> str:
    value = _text(data, key, label).lower()
    if not _SHA256.fullmatch(value):
        raise ManifestError(f"{label}.{key} não contém SHA-256 válido.")
    return value


def _safe_relative_path(value: str, label: str) -> str:
    if "\\" in value:
        raise ManifestError(f"{label} deve usar separadores '/'.")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ManifestError(f"{label} contém caminho inseguro.")
    if ":" in path.parts[0]:
        raise ManifestError(f"{label} contém unidade de disco.")
    return value


def _https_url(value: str, label: str, allowed_hosts: frozenset[str]) -> str:
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.hostname.lower() not in allowed_hosts
        or parsed.username
        or parsed.password
        or parsed.fragment
    ):
        raise ManifestError(f"{label} deve ser HTTPS e usar origem permitida.")
    return value


def _parse_component(
    identifier: str,
    raw: object,
    allowed_hosts: frozenset[str],
) -> ComponentSpec:
    label = f"components.{identifier}"
    data = _mapping(raw, label)
    raw_files = data.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        raise ManifestError(f"{label}.files deve ser uma lista não vazia.")
    parsed_files: list[InstalledFile] = []
    destinations: set[str] = set()
    archive_paths: set[str] = set()
    for index, raw_file in enumerate(raw_files):
        file_label = f"{label}.files[{index}]"
        item = _mapping(raw_file, file_label)
        archive_path = _safe_relative_path(_text(item, "archive_path", file_label), file_label)
        destination = _safe_relative_path(_text(item, "path", file_label), file_label)
        if destination in destinations or archive_path in archive_paths:
            raise ManifestError(f"{file_label} repete caminho de arquivo.")
        destinations.add(destination)
        archive_paths.add(archive_path)
        parsed_files.append(
            InstalledFile(
                archive_path=archive_path,
                path=destination,
                size_bytes=_positive_int(item, "size_bytes", file_label),
                sha256=_hash(item, "sha256", file_label),
            )
        )
    installed_size = _positive_int(data, "installed_size_bytes", label)
    if installed_size != sum(item.size_bytes for item in parsed_files):
        raise ManifestError(f"{label}.installed_size_bytes diverge da lista de arquivos.")
    entry_point = _safe_relative_path(_text(data, "entry_point", label), f"{label}.entry_point")
    if entry_point not in destinations:
        raise ManifestError(f"{label}.entry_point não está na lista de arquivos.")
    raw_command = data.get("diagnostic_command")
    if (
        not isinstance(raw_command, list)
        or not raw_command
        or not all(isinstance(argument, str) and argument for argument in raw_command)
    ):
        raise ManifestError(f"{label}.diagnostic_command deve ser uma lista de argumentos.")
    command = tuple(raw_command)
    if _safe_relative_path(command[0], f"{label}.diagnostic_command[0]") != entry_point:
        raise ManifestError(f"{label}.diagnostic_command deve começar pelo entry_point.")
    license_file = data.get("license_file")
    if license_file is not None:
        if not isinstance(license_file, str):
            raise ManifestError(f"{label}.license_file deve ser texto.")
        license_file = _safe_relative_path(license_file, f"{label}.license_file")
        if license_file not in destinations:
            raise ManifestError(f"{label}.license_file não está na lista de arquivos.")
    return ComponentSpec(
        identifier=identifier,
        name=_text(data, "name", label),
        version=_text(data, "version", label),
        architecture=_text(data, "architecture", label),
        url=_https_url(_text(data, "url", label), f"{label}.url", allowed_hosts),
        sha256=_hash(data, "sha256", label),
        size_bytes=_positive_int(data, "size_bytes", label),
        installed_size_bytes=installed_size,
        license=_text(data, "license", label),
        license_file=license_file,
        homepage=_text(data, "homepage", label),
        source=_text(data, "source", label),
        distribution=_text(data, "distribution", label),
        entry_point=entry_point,
        diagnostic_command=command,
        files=tuple(parsed_files),
    )


def _parse_model(
    name: str,
    raw: object,
    origin: Mapping[str, Any],
    allowed_hosts: frozenset[str],
) -> ModelSpec:
    label = f"models.{name}"
    data = _mapping(raw, label)
    filename = _safe_relative_path(_text(data, "filename", label), f"{label}.filename")
    if len(PurePosixPath(filename).parts) != 1:
        raise ManifestError(f"{label}.filename deve conter somente o nome do arquivo.")
    template = _text(origin, "url_template", "model_origin")
    url = _https_url(template.replace("{filename}", filename), f"{label}.url", allowed_hosts)
    return ModelSpec(
        name=name,
        filename=filename,
        url=url,
        sha256=_hash(data, "sha256", label),
        size_bytes=_positive_int(data, "size_bytes", label),
        license=_text(origin, "license", "model_origin"),
        homepage=_text(origin, "homepage", "model_origin"),
        source=_text(origin, "source", "model_origin"),
        revision=_text(origin, "revision", "model_origin"),
    )


def load_runtime_manifest(
    path: Path | None = None,
    *,
    expected_sha256: str | None = MANIFEST_SHA256,
) -> RuntimeManifest:
    """Carrega e valida o manifesto antes de qualquer download ou execução."""
    try:
        raw_bytes = (
            path.read_bytes()
            if path is not None
            else files("app.resources").joinpath(MANIFEST_RESOURCE).read_bytes()
        )
    except OSError as exc:
        raise ManifestError("Manifesto de runtime não pôde ser lido.") from exc
    digest = hashlib.sha256(raw_bytes).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256.lower():
        raise ManifestError("Manifesto de runtime foi alterado ou corrompido.")
    try:
        root = _mapping(json.loads(raw_bytes), "manifest")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ManifestError("Manifesto de runtime não contém JSON UTF-8 válido.") from exc
    if root.get("schema_version") != 1:
        raise ManifestError("Versão de schema do manifesto não suportada.")
    raw_hosts = root.get("allowed_download_hosts")
    if (
        not isinstance(raw_hosts, list)
        or not raw_hosts
        or not all(isinstance(host, str) and host == host.lower() for host in raw_hosts)
    ):
        raise ManifestError("allowed_download_hosts deve conter hosts normalizados.")
    allowed_hosts = frozenset(raw_hosts)
    raw_components = _mapping(root.get("components"), "components")
    raw_models = _mapping(root.get("models"), "models")
    origin = _mapping(root.get("model_origin"), "model_origin")
    components = {
        identifier: _parse_component(identifier, value, allowed_hosts)
        for identifier, value in raw_components.items()
    }
    models = {
        name: _parse_model(name, value, origin, allowed_hosts) for name, value in raw_models.items()
    }
    if set(components) != {"ffmpeg", "whisper_cpp"}:
        raise ManifestError("O manifesto deve declarar FFmpeg e whisper.cpp.")
    return RuntimeManifest(
        schema_version=1,
        release=_text(root, "release", "manifest"),
        platform=_text(root, "platform", "manifest"),
        architecture=_text(root, "architecture", "manifest"),
        verified_at=_text(root, "verified_at", "manifest"),
        digest=digest,
        allowed_download_hosts=allowed_hosts,
        components=MappingProxyType(components),
        models=MappingProxyType(models),
    )


def model_spec(name: str) -> ModelSpec:
    try:
        return load_runtime_manifest().models[name]
    except KeyError as exc:
        raise ValueError(f"Modelo '{name}' não existe no manifesto confiável.") from exc
